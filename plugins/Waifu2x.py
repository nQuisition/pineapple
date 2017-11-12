from util import Events
import urllib.request
import urllib.parse
import os


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        #return [Events.Command("scale")]
        return []

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "scale":
            await self.scale(message_object, args[1])

    async def scale(self, message_object, url):
        """
        Execute the example_command command. All calls to self.pm.client should be asynchronous (await)!
        :param message_object: discord.Message object
        :param url: URL to the image
        """
        values = {"url": url,
                  "style": "art",
                  "noise": 1,
                  "scale": 2}
        params = urllib.parse.urlencode(values)
        encoded = params.encode('utf8')
        req = urllib.request.Request(
            "http://waifu2x.udp.jp/api", encoded)
        response = urllib.request.urlopen(req, timeout=60)
        img = response.read()
        with open("scale.png", 'wb+') as f:
            f.write(img)

        with open("scale.png", 'rb') as f:
            await self.pm.client.send_file(message_object.channel, f)
            f.close()
            os.remove("scale.png")
