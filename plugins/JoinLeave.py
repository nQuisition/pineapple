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
        if self.enabled:
            welcome = glob.glob(os.getcwd() + "/images/" + 'hi.gif')
            file = random.choice(welcome)
            await asyncio.sleep(1)
            await self.pm.client.send_message(member.server.default_channel,
                                              "Welcome to the server " + member.mention +
                                              " Please read <#234865303442423814> and tell an admin/mod which role you would like")
            await self.pm.client.send_file(member.server.default_channel, file)

    async def handle_member_leave(self, member):
        if self.enabled:
            leave = glob.glob(os.getcwd() + "/images/" + "bye.gif")
            file = random.choice(leave)
            await asyncio.sleep(1)
            await self.pm.client.send_message(member.server.default_channel, "Bye " + member.name)
            await self.pm.client.send_file(member.server.default_channel, file)

    async def handle_command(self, message_object, command, args):
        if command == "togglewelcome":
            self.enabled = not self.enabled
            await self.pm.client.delete_message(message_object)
            await self.pm.client.send_message(message_object.channel, "Welcome messages: **" + str(self.enabled) + "**")
        if command == "ban":
            if len(message_object.mentions) == 1:
                leave = glob.glob(os.getcwd() + "/images/" + "bye.gif")
                file = random.choice(leave)
                await asyncio.sleep(1)
                msg1 = await self.pm.client.send_message(message_object.channel, "Bye " + message_object.mentions[0].name)
                msg2 = await self.pm.client.send_file(message_object.channel, file)

                await asyncio.sleep(5)
                await self.pm.client.delete_message(message_object)
                await self.pm.client.delete_message(msg1)
                await self.pm.client.delete_message(msg2)
                await self.pm.client.send_message(message_object.channel, "Nah, just kidding.")
