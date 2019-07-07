from util import Events
import glob
import os
import random
import asyncio
from util.Ranks import Ranks
import logging
import discord


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("setmodlogchannel", rank=Ranks.Mod,
                               desc="Set the channel to post mod log messages to.")]

    async def handle_command(self, message_object, command, args):
        if command == "setmodlogchannel":
            await self.set_modlog_channel(message_object)

    async def set_modlog_channel(self, message_object):
        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "modlog_channel",
                                                         message_object.channel.id)
        await self.pm.client.send_message(message_object.channel,
                                          "Set mod log channel to: #" + message_object.channel.name)