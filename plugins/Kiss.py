from util import Events
import glob
import os
import random


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("kiss")]

    async def handle_command(self, message_object, command, args):
        if command == "kiss":
            await self.kiss(message_object, args[1])

    async def kiss(self, message_object, user):
        files = glob.glob(os.getcwd() + "/images/kiss/" + '*.gif')
        files.extend(glob.glob(os.getcwd() + "/images/kiss/" + '*.png'))
        files.extend(glob.glob(os.getcwd() + "/images/kiss/" + '*.jpg'))
        file = random.choice(files)
        await self.pm.client.send_message(message_object.channel,
                                          "**" + user + "** you got a kiss from **" + message_object.author.name + "**")
        await self.pm.client.send_file(message_object.channel, file)
