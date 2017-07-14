# from pprint import pprint
import json
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
