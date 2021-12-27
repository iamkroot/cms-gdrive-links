from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from pathlib import Path
from datetime import datetime
import pickle

from cms import get_drive_links

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.readonly",
]
CLIENT_SECRET_FILE = "client_secret.json"
APPLICATION_NAME = "Lectures GDrive"
CREDENTIAL_PATH = Path.home() / '.local' / 'google-creds' / 'lec-drive.pickle'


def get_credentials():
    creds = None
    CREDENTIAL_PATH.parent.mkdir(exist_ok=True, parents=True)
    if CREDENTIAL_PATH.exists():
        with open(CREDENTIAL_PATH, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=46420)
        with open(CREDENTIAL_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return creds


def create_drive_serv(creds):
    return build("drive", "v3", credentials=creds)


def extract_id(link: str) -> str:
    """Extract ID from URL"""
    link = link.replace("?usp=sharing", "")
    file_id = link[link.find("1") :]
    end = file_id.find("/")
    if end != -1:
        file_id = file_id[:end]
    return file_id


def clean_name(name):
    paren = name.rfind("(")
    timestamp = name[paren + 1 : -1]
    try:
        dt = datetime.strptime(timestamp, "%Y-%m-%d at %H:%M GMT-7")
    except ValueError:
        print("couldn't find date from", name)
    else:
        name = dt.strftime("%Y-%m-%d")
    return name


def make_folder(serv, path):
    file_metadata = {
        'name': path,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    return serv.files().create(body=file_metadata, fields='id,parents').execute()


def add_to_drive(serv, file_id, prefix=""):
    FOLD_MIME = "application/vnd.google-apps.folder"
    file = serv.files().get(fileId=file_id).execute()
    name = file["name"]
    if file["mimeType"] != FOLD_MIME:
        name = clean_name(name)
    data = {
        'name': prefix + name,
        'mimeType': 'application/vnd.google-apps.shortcut',
        'shortcutDetails': {'targetId': file_id},
        'description': f"Original name: {file['name']}",
    }
    try:
        return serv.files().create(body=data, fields='id,parents').execute()
    except HttpError as e:
        print(e)


def move(serv, file: dict, folder_id):
    if "parents" not in file:
        file.update(serv.files().get(fileId=file["id"], fields="parents").execute())
    prev_parents = ",".join(file["parents"])
    return serv.files().update(
        fileId=file["id"],
        addParents=folder_id,
        removeParents=prev_parents,
        fields="id,parents"
    ).execute()


def main():
    dlinks = get_drive_links()
    creds = get_credentials()
    drive_serv = create_drive_serv(creds)
    root_folder_name = "Lectures"
    root_folder = make_folder(drive_serv, root_folder_name)
    for crs_name, links in dlinks.items():
        print(crs_name)
        crs_folder = make_folder(drive_serv, crs_name)
        for link in links:
            orig_file_id = extract_id(link)
            file = add_to_drive(drive_serv, orig_file_id)
            if not file:
                continue
            move(drive_serv, file, crs_folder["id"])
        move(drive_serv, crs_folder, root_folder["id"])


if __name__ == '__main__':
    main()
