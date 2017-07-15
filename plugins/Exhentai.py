import pprint
import json
import requests
import re

from util import Events

# TODO: FIND OUT HOW TO CREATE JSON OBJECT FROM REQUEST, ACCESS JSON DATA

# API-URL and type of headers sent by POST-request
url = "https://api.e-hentai.org/api.php"
json_request_headers = "{'content-type': 'application/json'}"


# json_request_headers = "{'content-type': 'application/json; charset=UTF-8'}"

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Exhentai"

    @staticmethod
    def register_events():
        return [Events.Message("Exhentai")]

    async def handle_message(self, message_object):
        # Genius RegEx for finding all exhentai-links formatted like copied from exh adressbar
        regex_result_list = re.findall(r'(https://exhentai.org/g/([0-9]+)/([0-9a-f]{10})/)', message_object.content)
        # loop over all found links that match genius RegEx
        for tuple in regex_result_list:
            # TODO: CACHE ALREADY DOWNLOADED HEADERS WITH TIMESTAMP
            # Key missing, or incorrect key provided.-Error has to catched
            # Gallery not found. If you just added this gallery, [...]-Error has to get catched
            # actually everything matching the RegEx will never return something but HTTP 200

            # Setting the 2nd and 3rd tuple value of the RegEx to properly named variables.
            # These tuples are automatically generated from the re.findall-command with given RegEx
            gallery_id = tuple[1]
            gallery_token = tuple[2]

            # TODO: IGNORE DOUBLE LOOKUP LIST ENTRIES WITH SAME HEADER / SAME ID&TOKEN
            # maybe even cache API results for some time

            # TODO: refactor
            # This is the required JSON-string for requesting data from the E-Hentai API

            response = requests.post(url, self.build_payload(gallery_id, gallery_token), json_request_headers)

            # create json from Response using built-in parser
            json_data = response.json()

            # print a pretty formatted JSON-String to chat containing info about the given galleries
            outstring = pprint.pformat(json_data, indent=4)

            # TODO: BUILD PRETTY LINK TEMPLATE


            # await self.pm.client.send_message(message_object.channel,json.dumps(response.json(), sort_keys=True, indent=4))
            # await self.pm.clientWrap.send_message(self.name, message_object.channel, outstring)
            await self.pm.clientWrap.send_message(self.name, message_object.channel, self.build_title_string(
                json_data) + "\n" + self.build_title_jpn_string(json_data) + "\n")
            await self.pm.client.send_message(message_object.channel, json_data['gmetadata'][0]['thumb'])
            await self.pm.clientWrap.send_message(self.name, message_object.channel, pprint.pformat(json_data['gmetadata'][0]['tags']))
            await self.pm.client.send_message(message_object.channel, "\n\n")
            # https://exhentai.org/g/66211541/d5c164c9b6/ error gallery not found
            # https://exhentai.org/g/108711/5f57a5eb11/ error wrong gallery token
            #
            #    await self.pm.clientWrap.send_message(self.name, message_object.channel, str(
            #        response.raise_for_status()) + "\n" + "Error while getting data from E-Hentai API.\n")

    @staticmethod
    def build_payload(gallery_id, gallery_token):
        return '{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}'

    @staticmethod
    def build_title_string(json_data):
        return 'Title: ' + pprint.pformat(json_data['gmetadata'][0]['title'])

    @staticmethod
    def build_title_jpn_string(json_data):
        return 'Japanese Title: ' + pprint.pformat(json_data['gmetadata'][0]['title_jpn'])
