import requests
import re
from util import Events
import os
import urllib
import datetime
import dateutil.parser
from PIL import Image

# API-URL and type of headers sent by POST-request
bilibili_api_url = "http://vocadb.net/api/pvs?pvUrl=http://acg.tv/"
json_request_headers = "{'content-type': 'application/json'}"
vocadb_api_url = "http://vocadb.net/api/songs/bypv?pvService=Bilibili&lang=English&pvId="


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = "Bilibili"

    @staticmethod
    def register_events():
        return [Events.Message("Bilibili")]

    async def handle_message(self, message_object):
        """
        Prints video info when a message contains a (average formatted) bilibili-url
        :param message_object: discord.Message object containing the message
        """

        regex_result_list_unique = await self.find_bilibili_urls(message_object.content)

        for url_data in regex_result_list_unique:
            video_id = url_data[6]
            bilibili_api_response = requests.get(bilibili_api_url + video_id)

            if bilibili_api_response.status_code is 200:
                json_data = bilibili_api_response.json()

                # Fetch and process thumbnail
                filename = await self.download_thumbnail(json_data)
                await self.resize_thumbnail(filename)

                vocadb_api_response = requests.get(vocadb_api_url + video_id[2:])

                if vocadb_api_response.content == b'null':
                    # Send raw bilibili info
                    await self.pm.client.send_file(message_object.channel, filename,
                                                   content="**Title:** " + json_data["name"] +
                                                           "\n**Author:** " + json_data["author"] +
                                                           "\n**Date:** " + dateutil.parser.parse(
                                                       json_data["publishDate"]).strftime("%B %d, %Y"))
                else:
                    vocadb_data = vocadb_api_response.json()

                    vocadb_url = "\n**VocaDB:** <https://vocadb.net/S/" + str(vocadb_data["id"]) + ">"
                    if "originalVersionId" in vocadb_data:
                        vocadb_url += "\n**VocaDB (original):** <https://vocadb.net/S/" + str(
                            vocadb_data["originalVersionId"]) + ">"

                    if vocadb_data["songType"] == "Original":
                        song_type = ""
                    else:
                        song_type = " (" + vocadb_data["songType"] + ")"

                    msg = "**Title:** " + vocadb_data["name"] + song_type
                    msg += "\n**Author:** " + vocadb_data["artistString"]
                    msg += "\n**Date:** " + dateutil.parser.parse(vocadb_data["createDate"]).strftime("%B %d, %Y")
                    msg += vocadb_url

                    await self.pm.client.send_file(message_object.channel, filename,
                                                   content=msg)

                # Cleanup
                os.remove(filename)

    @staticmethod
    async def resize_thumbnail(filename):
        # Resize image
        base_width = 300
        img = Image.open(filename)
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), Image.ANTIALIAS)
        img.save(filename)
        img.close()

    @staticmethod
    async def download_thumbnail(json_data):
        # Download thumbnail
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp")
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, str(json_data["id"]) + ".png")
        urllib.request.urlretrieve(json_data["thumbUrl"], filename)
        return filename

    async def find_bilibili_urls(self, message):
        regex_result_list = re.findall(
            r'((?<=http)((?<=s)|)://|)((?<=www.)|)((?<=bilibili\.kankanews\.com/video)|'
            r'((?<=bilibili.tv)|((?<=bilibili.com/video)|(?<=acg.tv))))/(av[0-9a-f]*)',
            message)
        regex_result_list_unique = (tuple(self.return_unique_set(regex_result_list)))
        return regex_result_list_unique

    @staticmethod
    def return_unique_set(iterable, key=None):
        # taken from more_itertools.unique_everseen instead of importing an extra dependency
        seenset = set()
        seenset_add = seenset.add
        seenlist = []
        seenlist_add = seenlist.append
        if key is None:
            for element in iterable:
                try:
                    if element not in seenset:
                        seenset_add(element)
                        yield element
                except TypeError as e:
                    if element not in seenlist:
                        seenlist_add(element)
                        yield element
        else:
            for element in iterable:
                k = key(element)
                try:
                    if k not in seenset:
                        seenset_add(k)
                        yield element
                except TypeError as e:
                    if k not in seenlist:
                        seenlist_add(k)
                        yield element
        return seenlist
