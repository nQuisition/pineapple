from util import Events
import glob
import os
import random
import asyncio
from util.Ranks import Ranks


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.enabled = True

    @staticmethod
    def register_events():
        return [Events.UserJoin("welcome_msg"), Events.UserLeave("leave_msg"),
                Events.Command("togglewelcome", rank=Ranks.Admin),
                Events.Command("ban", rank=Ranks.Mod)]

    async def handle_member_join(self, member):
        print("User joined")
        print(member.display_name)
        if self.enabled:
            print("Join message enabled")
            files = glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(1)
            await self.pm.client.send_file(member.server.default_channel, file,
                                           content="Welcome to the server " + member.mention +
                                                   " Please read <#234865303442423814> and tell an admin/mod which "
                                                   "role you would like")
            print("Message sent")

    async def handle_member_leave(self, member):
        if self.enabled:
            files = glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(1)
            await self.pm.client.send_file(member.server.default_channel, file, content="Bye " + member.display_name)

    async def handle_command(self, message_object, command, args):
        if command == "togglewelcome":
            self.enabled = not self.enabled
            await self.pm.client.delete_message(message_object)
            await self.pm.client.send_message(message_object.channel, "Welcome messages: **" + str(self.enabled) + "**")

        if command == "ban" and len(message_object.mentions) == 1:
            files = glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(1)
            msg1 = await self.pm.client.send_file(message_object.channel, file,
                                                  content="Bye " + message_object.mentions[0].display_name)

            await asyncio.sleep(10)
            try:
                await self.pm.client.delete_message(message_object)
            except:
                print("Failed to delete message")
            try:
                await self.pm.client.delete_message(msg1)
            except:
                print("Failed to delete message")

            files = glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(5)
            msg2 = await self.pm.client.send_file(message_object.channel, file,
                                           content="Welcome to the server " + message_object.mentions[0].mention +
                                                   " Please read <#234865303442423814> and tell an admin/mod which "
                                                   "role you would like")
            await asyncio.sleep(10)
            try:
                await self.pm.client.delete_message(msg2)
            except:
                print("Failed to delete message")
