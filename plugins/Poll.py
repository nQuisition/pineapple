# -*- coding: utf-8 -*-
from util import Events
from AbstractPlugin import AbstractPlugin


class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "Poll")

    @staticmethod
    def register_events():
        return [Events.Command('poll')]

    async def handle_command(self, message_object, command, args):
        if command == "poll":
            await self.poll(message_object, args[1].strip())

    async def poll(self, message_object, prompt):
        if prompt.strip() is "":
            prompt = "Yay or Nay?"
        poll_msg = await self.pm.clientWrap.send_message(self.name, message_object.channel, "**Poll:**\n" + prompt)
        await poll_msg.add_reaction('\U00002714')
        await poll_msg.add_reaction('\U00002716')
