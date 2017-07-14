import json
import posixpath
import urllib.parse
from pprint import pprint

import requests
import re

from util import Events

# Replace with the correct URL
url = "https://api.e-hentai.org/api.php"
json_request_headers = "{'content-type': 'application/json'}"


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Exhentai"

    @staticmethod
    def register_events():
        return [Events.Message("Exhentai")]

    def generate_sections_of_url(url):
        path = urllib.parse.urlparse(url).path
        sections = []
        temp = ""
        while path != '/':
            temp = posixpath.split(path)
            path = temp[0]
            sections.append(temp[1])
        return sections

    def valid_exhentai_link(self, exhentai_url):
        sections = self.generate_sections_of_url(exhentai_url)
        return False

    def get_exhentai_link(self, message):
        # regex to grep exh url from string
        if message:    return "https://exhentai.org/g/*inHex/10ZeichenHier"

    async def handle_message(self, message_object):
        exhentailinks = re.findall(r'(https://exhentai.org/g/([0-9]+)/([0-9a-f]{10})/)', message_object.content)

        for entry in exhentailinks:
            checkvalid = requests.head(entry[0])
            if checkvalid.ok:
                gallery_id = entry[1]
                gallery_token = entry[2]
                payload = (
                    '{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}')
                response = requests.post(url, payload, json_request_headers)
                if response.ok:
                    await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                          json.dumps(response.json(), sort_keys=True, indent=4))



                    # if message_object.content.startswith("https://exhentai.org/g/"):
                    #     # if
                    #     # lol the value parse needs to get better first before i can make the regex better
                    #     temp = message_object.content.split("/")
                    #
                    #     # Check if link is actually a valid exhentai link
                    #     if temp[2] == "exhentai.org" and temp[3] == "g" and 5 < len(temp[4]) < 8 and len(temp[5]) == 10:
                    #         gallery_id = temp[4]
                    #         gallery_token = temp[5]
                    #
                    #         payload = (
                    #             '{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}')
                    #         response = requests.post(url, payload, json_request_headers)
                    #
                    #         await self.pm.clientWrap.send_message(self.name, message_object.channel,
                    #                                               "The gallery id is " + gallery_id + " and the gallery token is " + gallery_token)
                    #
                    #         await self.pm.clientWrap.send_message(self.name, message_object.channel,
                    #                                               json.dumps(response.json(), sort_keys=True, indent=4))
