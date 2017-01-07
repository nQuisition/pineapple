from util import Events
from PIL import Image
import discord.utils
import urllib.request
import re
import os

# rudimentary regex match for finding syllables
SYLLABLE = "([aeiou]|[0-9])"


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
            await self.ship(message_object, args[1])

    async def ship(self, message_object, user_IDs):
        """
        Execute the example_command command. All calls to self.pm.client should be asynchronous (await)!
        :param message_object: discord.Message object
        :param user_IDs: IDs of users to ship
        """
        ##Retrieve user information
        user_IDs = user_IDs.split()
        # isolates user ID numbers
        user_IDs = [re.sub("[^0-9]", "", id) for id in user_IDs]
        if len(user_IDs) < 2:
            await self.pm.client.send_message(message_object.channel,
                                              "Please mention two users!")
            return
        # assigns users to arguments
        # is there a way to get profile info without accessing the discord.py User class?
        user1 = discord.utils.get(message_object.server.members, id=user_IDs[0])
        user2 = discord.utils.get(message_object.server.members, id=user_IDs[1])
        
        if user1 is None or user2 is None:
            await self.pm.client.send_message(message_object.channel,
                                              "Please **mention** two users!")
            return
        ##generate ship name
        u1_parts = re.split(SYLLABLE, user1.display_name)
        # needed to maintain vowels in split
        u1_parts = [u1_parts[i] + u1_parts[i + 1] for i in range(len(u1_parts) - 1)[0::2]]
        u2_parts = re.split(SYLLABLE, user2.display_name)
        u2_parts = [u2_parts[i] + u2_parts[i + 1] for i in range(len(u2_parts) - 1)[0::2]]
        # concatenate half of u1 syllables with u2 syllables(integer division, ew...)
        name = u1_parts[:len(u1_parts) // 2] + u2_parts[len(u2_parts) // 2:]
        name = "".join(name)
        # checks if last letter is omitted(bugfix, can be made more elegant)
        if name[-1] is not user2.display_name[-1]:
            name = name + user2.display_name[-1]

        ##Generate Ship Image(clean up)
        # download/access images first
        hdr = {'User-Agent': 'Mozilla/5.0'}

        req = urllib.request.Request(user1.avatar_url, headers=hdr)
        page = urllib.request.urlopen(req)
        data = page.read()
        f = open("user1.png", 'wb+')
        f.write(data)
        f.close()

        if user1 is user2:
            images = [Image.open('user1.png').resize((256,256)), Image.open('images/ship/ship.png'), Image.open('images/ship/hand.png')]
        else:
            req = urllib.request.Request(user2.avatar_url, headers=hdr)
            page = urllib.request.urlopen(req)
            data = page.read()
            f = open("user2.png", 'wb+')
            f.write(data)
            f.close()
            images = [Image.open('user1.png').resize((256,256)), Image.open('images/ship/ship.png'), Image.open('user2.png').resize((256,256))]

        # combines images horizontally
        with open("ship.png", 'wb+') as f:
            
            widths, heights = zip(*(i.size for i in images))
            total_width = sum(widths)
            max_height = max(heights)
            

            new_im = Image.new('RGB', (total_width, max_height))

            x_offset = 0
            for im in images:
                new_im.paste(im, (x_offset, 0))
                x_offset += im.size[0]
            new_im.save(f)

        with open("ship.png", 'rb') as f:
            await self.pm.client.send_message(message_object.channel,
                                              "**{}** *The ship has sailed~!*".format(name))
            await self.pm.client.send_file(message_object.channel, f)
            f.close()
            temp_images = [img for img in os.listdir(".") if img.endswith(".png") or img.endswith(".jpg")]
            for img in temp_images:
                os.remove(img)

