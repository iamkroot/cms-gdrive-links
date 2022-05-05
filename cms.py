import requests
import json
import re

from collections import defaultdict
from functools import lru_cache

REST_URL = "https://cms.bits-hyderabad.ac.in/webservice/rest/server.php"


def make_req(verb, params={}, data=None):
    query_params = {
        "wstoken": "INSERT_TOKEN_HERE",
        "moodlewsrestformat": "json",
    }
    query_params.update(params)
    return requests.request(verb, REST_URL, params=query_params, data=data)


def get_query(wsfunc, params={}):
    params['wsfunction'] = wsfunc
    return make_req('get', params).json()


def post_query(wsfunc, params={}, data={}):
    params['wsfunction'] = wsfunc
    return make_req('post', params, data).json()


@lru_cache()
def get_siteinfo():
    return get_query('core_webservice_get_site_info')


@lru_cache()
def get_userid():
    return get_siteinfo()['userid']


def get_enrolled_courses():
    return get_query('core_enrol_get_users_courses', {'userid': get_userid()})


def get_forums():
    return get_query("mod_forum_get_forums_by_courses")


def get_forum_discussions(forum_id):
    data = get_query("mod_forum_get_forum_discussions_paginated", {"forumid": forum_id})

    for disc in data["discussions"]:
        yield disc


def get_url_modules(course):
    for topic in get_query("core_course_get_contents", {"courseid": course["id"]}):
        for module in topic.get("modules", []):
            for content in module.get("contents", []):
                if content["type"] == "url":
                    yield content


def get_drive_links():
    courses = {c["id"]: c for c in get_enrolled_courses()}
    keywords = ("video", "online", "lecture", "link")
    data = defaultdict(set)
    PAT = re.compile(r'https://drive\.google\.com/[^"<\s]*')
    for forum in get_forums():
        crs_name = courses[forum["course"]]['fullname']
        for disc in get_forum_discussions(forum["id"]):
            subject = disc["subject"].lower()
            body = disc["message"]

            if any(word in subject for word in keywords):
                for match in PAT.finditer(body):
                    data[crs_name].add(match.group(0))

    for course in courses.values():
        crs_name = course["fullname"]
        for content in get_url_modules(course):
            if any(word in content["filename"].lower() for word in keywords):
                if match := PAT.match(content["fileurl"]):
                    data[crs_name].add(match.group(0))
    return data


def main():
    data = get_drive_links()
    data = {k: list(v) for k, v in data.items()}  # make json serializable
    with open("dlinks.json", "w") as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    main()
