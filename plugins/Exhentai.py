# from pprint import pprint
import json
import requests
import re

from util import Events

# API-URL and type of headers sent by POST-request
url = "https://api.e-hentai.org/api.php"
json_request_headers = "{'content-type': 'application/json'}"


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Exhentai"

    @staticmethod
    def register_events():
        return [Events.Message("Exhentai")]

    async def handle_message(self, message_object):
        # Genius RegEx for finding all exhentai-links formatted like copied from exh adressbar
        exhentailinks = re.findall(r'(https://exhentai.org/g/([0-9]+)/([0-9a-f]{10})/)', message_object.content)
        # loop over all found links that match genius RegEx
        for entry in exhentailinks:
            # Trying to download the headers from the diary-page. When possible, link is considered valid.
            # TODO: CACHE ALREADY DOWNLOADED HEADERS WITH TIMESTAMP
            checkvalid = requests.head(entry[0])
            if checkvalid.ok:
                # Setting the 2nd and 3rd tuple value of the RegEx to properly named variables.
                # These tuples are automatically generated from the re.findall-command with given RegEx
                gallery_id = entry[1]
                gallery_token = entry[2]
                # TODO: IGNORE DOUBLE ENTRIES WITH SAME HEADER / SAME ID&TOKEN
                # maybe even cache API results for some time
                # This is the required JSON-string for requesting data from the E-Hentai API
                payload = (
                    '{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}')
                response = requests.post(url, payload, json_request_headers)
                # print a pretty formatted JSON-String to chat containing info about the given galleries
                if response.ok:
                    await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                          json.dumps(response.json(), sort_keys=True, indent=4))
                else:
                    await self.pm.send_message(self.name, message_object.channel,
                                               "Error while getting data from E-Hentai API.\n" + response.status_code)
