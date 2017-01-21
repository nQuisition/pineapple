# -*- coding: utf-8 -*-
from util import Events
from discord import Emoji

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command('poll')]

    async def handle_command(self, message_object, command, args):
        if command == "poll":
            await self.poll(message_object, args[1].strip())

    async def poll(self, message_object, prompt):
        if prompt.strip() is "":
            prompt = "Yay or Nay?"
        poll_msg = await self.pm.client.send_message(
            message_object.channel, prompt)
        await self.pm.client.add_reaction(poll_msg, '\U0001f1f4')
        await self.pm.client.add_reaction(poll_msg, '\U0001f1fd')
