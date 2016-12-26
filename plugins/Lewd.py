from util import Events
import glob
import os
import random


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("lewd")]

    async def handle_command(self, message_object, command, args):
        if command == "lewd":
            await self.lewd(message_object)

    async def lewd(self, message_object):
        files = glob.glob(os.getcwd() + "/images/lewd/" + '*.gif')
        files.extend(glob.glob(os.getcwd() + "/images/lewd/" + '*.png'))
        files.extend(glob.glob(os.getcwd() + "/images/lewd/" + '*.jpg'))
        file = random.choice(files)
        await self.pm.client.send_file(message_object.channel, file)
