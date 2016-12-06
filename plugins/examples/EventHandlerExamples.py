from util import Events
import asyncio


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Typing("example_typing"), Events.MessageDelete("example_delete")]

    async def handle_typing(self, channel, user, when):
        '''tmp = await self.pm.client.send_message(channel, user.name + " is typing, wow!")
        await asyncio.sleep(5)
        await self.pm.client.delete_message(tmp)'''

    async def handle_message_delete(self, message):
        '''tmp = await self.pm.client.send_message(message.channel,
                                                "Message deleted (" + message.author.name + "): " + message.content)
        await asyncio.sleep(5)
        await self.pm.client.delete_message(tmp)'''
