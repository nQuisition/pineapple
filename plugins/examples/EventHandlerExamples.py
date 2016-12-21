from util import Events
import glob
import os
import random
import asyncio


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Typing("example_typing"), Events.MessageDelete("example_delete"), Events.UserJoin("welcome_msg")]

    async def handle_typing(self, channel, user, when):
        '''tmp = await self.pm.client.send_message(channel, user.name + " is typing, wow!")
        await asyncio.sleep(5)
        await self.pm.client.delete_message(tmp)'''

    async def handle_message_delete(self, message):
        '''tmp = await self.pm.client.send_message(message.channel,
                                                "Message deleted (" + message.author.name + "): " + message.content)
        await asyncio.sleep(5)
        await self.pm.client.delete_message(tmp)'''

    async def handle_member_join(self, member):
        '''welcome = glob.glob(os.getcwd() + "/images/" + 'hi.gif')
        file = random.choice(welcome)
        await asyncio.sleep(1)
        await self.pm.client.send_message(member.server.default_channel, "Welcome here " + member.mention)
        await self.pm.client.send_file(member.server.default_channel, file)'''