import os
import urllib.request

import discord
from PIL import Image, ImageFont, ImageDraw

from util import Events
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "TheJoke")

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        return [Events.Command("thejoke")]

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "thejoke":
            await self.the_joke(message_object, args[1])

    async def the_joke(self, message_object, txt):
        template = Image.open("images/thejoke.png")
        template = template.convert("RGBA")
        font = ImageFont.truetype("images/LemonMilk.otf", 26)
        draw = ImageDraw.Draw(template)

        if len(message_object.mentions) > 0:
            name = message_object.mentions[0].display_name
        elif txt != "":
            name = txt
        else:
            name = message_object.author.display_name

        text_x, text_y = font.getsize(name)
        x = (512 - text_x) / 2 - 10
        y = (512 - text_y) / 2 + 200

        draw.text((x,y), name, (255, 255, 255), font=font)
        # combines images horizontally
        with open("thejoke.png", 'wb+') as f:
            new_im = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
            new_im.paste(template, (0, 0))
            new_im.save(f, "PNG")

        with open("thejoke.png", 'rb') as f:
            await message_object.channel.send(file=discord.File(f), content="")
            f.close()
            temp_images = [img for img in os.listdir(".") if img.endswith(".png") or img.endswith(".jpg")]
            for img in temp_images:
                os.remove(img)

    @staticmethod
    def get_avatar(user):
        if not os.path.exists("cache/"):
            os.makedirs("cache")
        if user.avatar_url == "" or None:
            url = user.default_avatar_url
            path = "cache/avatar/default_" + user.id + ".png"
        else:
            url = user.avatar_url
            path = "cache/avatar/" + user.avatar + ".png"
        if os.path.isfile(path):
            return path
        else:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=hdr)
            page = urllib.request.urlopen(req)
            data = page.read()
            f = open(path, 'wb+')
            f.write(data)
            f.close()

            return path
