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
        return [Events.UserJoin("welcome_msg"),
                Events.UserLeave("leave_msg"),
                Events.Command("togglewelcome", rank=Ranks.Mod, desc="Toggle the join/leave messages"),
                Events.Command("setdefaultchannel", rank=Ranks.Mod,
                               desc="Set the channel to use when posting join/leave messages"),
                Events.Command("setwelcomemessage", rank=Ranks.Mod,
                               desc="Set the message to display when a user joins the discord server. "
                                    "Insert {0} where you want to mention the new user"),
                Events.Command("ban", rank=Ranks.Mod),
                Events.Command("shadowban", rank=Ranks.Mod)]

    async def handle_member_join(self, member):
        enabled = await self.get_welcome_messages_config(member.server.id)
        logging.info("User joined " + member.display_name)
        if enabled:
            files = glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "join" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(1)

            default_channel = self.pm.botPreferences.get_database_config_value(member.server.id, "default_channel")
            if default_channel is not None:
                channel = discord.utils.find(lambda m: m.id == default_channel, member.server.channels)

                welcome_message = self.pm.botPreferences.get_database_config_value(member.server.id,
                                                                                   "welcome_message")
                if welcome_message is None:
                    welcome_message = "Welcome to the server {0}".format(member.mention)
                else:
                    welcome_message = welcome_message.format(member.mention)

                await self.pm.client.send_file(channel, file,
                                               content=welcome_message)

    async def handle_member_leave(self, member):
        enabled = await self.get_welcome_messages_config(member.server.id)
        if enabled:
            files = glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.gif')
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.png'))
            files.extend(glob.glob(os.getcwd() + "/images/" + "leave" + "/" + '*.jpg'))
            file = random.choice(files)
            await asyncio.sleep(1)

            default_channel = self.pm.botPreferences.get_database_config_value(member.server.id, "default_channel")
            if default_channel is not None:
                channel = discord.utils.find(lambda m: m.id == default_channel, member.server.channels)
                await self.pm.client.send_file(channel, file, content="Bye " + member.display_name)

    async def handle_command(self, message_object, command, args):
        if command == "togglewelcome":
            await self.toggle_welcome(message_object)

        if command == "ban" and len(message_object.mentions) == 1:
            await self.fake_ban(message_object)

        if command == "shadowban" and len(message_object.mentions) == 1:
            await self.shadow_ban(message_object)

        if command == "setdefaultchannel":
            await self.set_default_channel(message_object)

        if command == "setwelcomemessage":
            await self.set_welcome_message(message_object, args[1])

    async def toggle_welcome(self, message_object):
        logging.info("Welcome/leave messages toggled by "
                     + message_object.author.name + "#" + str(message_object.author.discriminator))
        await self.pm.client.delete_message(message_object)

        enabled = await self.get_welcome_messages_config(message_object.server.id)
        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "welcome_messages",
                                                         not enabled)

        await self.pm.client.send_message(message_object.channel,
                                          "Welcome/leave messages: **{0}**".format(str(
                                              self.pm.botPreferences.get_database_config_value(message_object.server.id,
                                                                                               "welcome_messages"))))

    async def shadow_ban(self, message_object):
        logging.info("Shadow ban on " + message_object.mentions[0].display_name + " executed by "
                     + message_object.author.name + "#" + str(message_object.author.discriminator))

        cache_enabled = await self.get_welcome_messages_config(message_object.server.id)
        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "welcome_messages",
                                                         False)

        await self.pm.client.ban(message_object.mentions[0])
        await self.pm.client.delete_message(message_object)
        await asyncio.sleep(5)

        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "welcome_messages",
                                                         cache_enabled)

    async def fake_ban(self, message_object):
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

    async def set_default_channel(self, message_object):
        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "default_channel",
                                                         message_object.channel.id)
        await self.pm.client.send_message(message_object.channel,
                                          "Set default channel to: #" + message_object.channel.name)

    async def set_welcome_message(self, message_object, text):
        self.pm.botPreferences.set_database_config_value(message_object.server.id,
                                                         "welcome_message",
                                                         text)
        await self.pm.client.send_message(message_object.channel,
                                          "Set welcome message to: " + text)

    async def get_welcome_messages_config(self, server_id):
        db_enabled = self.pm.botPreferences.get_database_config_value(server_id, "welcome_messages")
        if db_enabled == "False":
            return False
        else:
            return True
