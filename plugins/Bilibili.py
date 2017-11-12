import pprint
import requests
import re
import discord
from util import Events
import os
import urllib
from PIL import Image

# API-URL and type of headers sent by POST-request
api_url = "http://vocadb.net/api/pvs?pvUrl=http://acg.tv/"
json_request_headers = "{'content-type': 'application/json'}"


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
            request_data = requests.get(api_url + video_id)

            if request_data.status_code is 200:
                json_data = request_data.json()

                # Fetch and process thumbnail
                filename = await self.download_thumbnail(json_data)
                await self.resize_thumbnail(filename)

                # Send raw bilibili info
                await self.pm.client.send_file(message_object.channel, filename,
                                               content="**Title:** " + json_data["name"] +
                                                       "\n**Author:** " + json_data["author"] +
                                                       "\n**Date:** " + json_data["publishDate"])

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
