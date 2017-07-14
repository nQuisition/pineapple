from util import Events
import requests
import json

# Replace with the correct URL
url = "https://api.e-hentai.org/api.php"
headers = "{'content-type': 'application/json'}"

# print (myResponse.status_code)

# For successful API call, response code will be 200 (OK)

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Exhentai"

    @staticmethod
    def register_events():
        return [Events.Message("Exhentai")]

    async def handle_message(self, message_object):
        if message_object.content.startswith("https://exhentai.org/g/"):
            # if "https://exhentai.org/g/" in message_object.content:
            # lol the value parse needs to get better first before i can make the regex better
            temp = message_object.content.split("/")

            # Check if link is actually a valid exhentai link
            if temp[2] == "exhentai.org" and temp[3] == "g" and 5 < len(temp[4]) < 8 and len(temp[5]) == 10:

                gallery_id = temp[4]
                gallery_token = temp[5]

                payload = ('{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}')
                response = requests.post(url, payload, headers)

                await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                      "The gallery id is " + gallery_id + " and the gallery token is " + gallery_token)

                await self.pm.clientWrap.send_message(self.name, message_object.channel,json.dumps(response.json(),sort_keys=True, indent=4))
