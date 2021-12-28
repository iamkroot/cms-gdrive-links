# Lecture links scraper for Moodle

This is a pair of simple Python scripts to automate the scraping and organizing of weekly recorded lecture links that are posted on Moodle CMS.

## `cms.py`
This deals with scraping the links from CMS. It goes through all your enrolled courses and searches for gdrive links accompanied by text such as `video`, `lecture`, etc. (See [source](https://github.com/iamkroot/cms-gdrive-links/blob/master/cms.py#L65) for all keywords).

To set up, put your Moodle Mobile Web Service Key in place of `INSERT_TOKEN_HERE` [here](https://github.com/iamkroot/cms-gdrive-links/blob/master/cms.py#L13). It can be acquired from `Preferences -> Security Keys -> Mobile web service key` in the Moodle CMS website.

To run it, just do `poetry run python cms.py` (after doing `poetry install`).

## `gdrive.py`
This deals with consolidating all the lecture videos (which are assumed to be GMeet recordings) in a single folder on your GDrive. It will try to copy the original lectures into your gdrive, but be aware that this needs to be enabled by the BITS Admin who set up the recordings.

To set up, you'll need to create a Google application in order to be able to access the GDrive REST API. Refer to the [official docs](https://developers.google.com/drive/api) to get started. You need a `client_secret.json` file to be present in the same directory in order to run this.

To run, type `poetry run python gdrive.py` (after doing `poetry install`).

## Contributing
Feel free to improve and customize these scripts. Proper PRs are welcome.
