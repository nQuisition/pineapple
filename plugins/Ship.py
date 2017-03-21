from util import Events
from PIL import Image
import urllib.request
import re
import os
import unicodedata

# rudimentary regex match for finding syllables
SYLLABLE = "([aeiouyAEIOUY]|[0-9])"


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        return [Events.Command("ship")]

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "ship":
            await self.ship(message_object)

    async def ship(self, message_object):
        """
        Execute the example_command command. All calls to self.pm.client should be asynchronous (await)!
        :param message_object: discord.Message object
        :param user_IDs: IDs of users to ship
        """
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        if not os.path.exists("cache/avatar/"):
            os.mkdir("cache/avatar/")

        if len(message_object.mentions) is 2:
            user1 = message_object.mentions[0]
            user2 = message_object.mentions[1]
        elif len(message_object.mentions) is 1:
            user1 = message_object.mentions[0]
            user2 = message_object.mentions[0]
        else:
            await self.pm.client.send_message(message_object.channel,
                                              "Please **mention** two users!")
            return

        # generate ship name
        n1 = user1.display_name
        n2 = user2.display_name
        u1_parts = re.split(SYLLABLE, n1)
        # needed to maintain vowels in split
        u1_parts = [u1_parts[i] + u1_parts[i + 1] for i in range(len(u1_parts) - 1)[0::2]]
        u2_parts = re.split(SYLLABLE, n2)
        u2_parts = [u2_parts[i] + u2_parts[i + 1] for i in range(len(u2_parts) - 1)[0::2]]
        # concatenate half of u1 syllables with u2 syllables(integer division, ew...)

        # dumb fix for words that cannot be split (non-latin character sets?)
        if len(u1_parts) is 0:
            u1_parts = [n1]
        if len(u2_parts) is 0:
            u2_parts = [n2]

        name = u1_parts[:len(u1_parts) // 2] + u2_parts[len(u2_parts) // 2:]
        name = "".join(name)
        # checks if last letter is omitted(bug fix, can be made more elegant)
        if name[-1] is not user2.display_name[-1]:
            name = name + user2.display_name[-1]

        # Generate Ship Image(clean up)
        # download/access images first
        user1_img = self.get_avatar(user1)

        if user1 is user2:
            images = [Image.open(user1_img).resize((256, 256)), Image.open('images/ship/ship.png'),
                      Image.open('images/ship/hand.png')]
        else:
            user2_img = self.get_avatar(user2)
            images = [Image.open(user1_img).resize((256, 256)), Image.open('images/ship/ship.png'),
                      Image.open(user2_img).resize((256, 256))]

        # combines images horizontally
        with open("ship.png", 'wb+') as f:
            new_im = Image.new('RGBA', (768, 256), (0, 0, 0, 0))
            new_im.paste(images[0], (0, 0))
            new_im.paste(images[1], (256, 0), mask=images[1])
            new_im.paste(images[2], (512, 0))
            new_im.save(f, "PNG")

        with open("ship.png", 'rb') as f:
            await self.pm.client.send_file(
                message_object.channel, f, filename=None, content="""
                **{}** *The ship has sailed~!*""".format(name))
            f.close()
            temp_images = [img for img in os.listdir(".") if img.endswith(".png") or img.endswith(".jpg")]
            for img in temp_images:
                os.remove(img)

    @staticmethod
    def get_avatar(user):
        if not os.path.exists("cache/"):
            os.makedirs("cache")
        if user.avatar_url is "" or None:
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
