import pprint
import requests
import re

from util import Events

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
        # maybe broaden it up to match e-hentai / http / written www if still good performance-wise
        regex_result_list = re.findall(r'(https://exhentai.org/g/([0-9]+)/([0-9a-f]{10})/)', message_object.content)

        # loop over all found links that match genius RegEx
        # 3 API message api send requests per link, might get out of hand
        for link_tuple in regex_result_list:

            # TODO: (Core) Print error on wrong link
            # TODO: (Performance) Do not download API Data twice, maybe even cache API data but thats hardly worth the time
            # Key missing, or incorrect key provided.-Error has to catched
            # Gallery not found. If you just added this gallery, [...]-Error has to get catched
            # but everything matching the RegEx will never return something but HTTP 200
            # maybe if server is down 404 or the regex is broadened you will get 301 / 302 for moved if www/non-www forwarding happens

            # Setting the 2nd and 3rd tuple value of the RegEx to properly named variables.
            # These tuples are automatically generated from the re.findall-command with given RegEx
            # the regex_result_list contains of a tuple with the different substrings in it
            # link_tuple[0] is the whole string
            # link_tuple[1] and [2] are the first and second matched substrings

            gallery_id = link_tuple[1]
            gallery_token = link_tuple[2]

            response = requests.post(url, self.build_payload(gallery_id, gallery_token), json_request_headers)

            # create json from Response using built-in parser
            json_data = response.json()

            # Debug-Snippets

            # print whole json
            # await self.pm.client.send_message(message_object.channel,json.dumps(response.json(), sort_keys=True, indent=4))

            # print all json pretty
            # outstring = pprint.pformat(json_data, indent=4)
            # await self.pm.clientWrap.send_message(self.name, message_object.channel, outstring)

            # Build the title-message
            await self.pm.clientWrap.send_message(self.name, message_object.channel, self.build_title_string(
                json_data) + "\n" + self.build_title_jpn_string(json_data) + "\n")

            # Send the cover as its own String (non-embed) for preview
            await self.pm.client.send_message(message_object.channel, json_data['gmetadata'][0]['thumb'])

            # print message including tag-section
            await self.pm.clientWrap.send_message(self.name, message_object.channel, self.build_tag_section() + "\n")

    @staticmethod
    def build_payload(gallery_id, gallery_token):
        return '{"method": "gdata","gidlist": [[' + gallery_id + ',"' + gallery_token + '"]],"namespace": 1}'

    @staticmethod
    def build_title_string(json_data):
        return 'Title: ' + pprint.pformat(json_data['gmetadata'][0]['title'])

    @staticmethod
    def build_title_jpn_string(json_data):
        return 'Japanese Title: ' + pprint.pformat(json_data['gmetadata'][0]['title_jpn'])

    # TODO: (core) Make the taglist look pretty when printed
    @staticmethod
    def build_tag_section(json_data):
        return pprint.pformat(json_data['gmetadata'][0]['tags'])

