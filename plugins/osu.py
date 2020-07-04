import os
import traceback
import urllib.request

import discord
from peewee import Model, TextField, DoesNotExist

from util import Events
from AbstractPlugin import AbstractPlugin


# noinspection SpellCheckingInspection
class Plugin(AbstractPlugin):
    def __init__(self, pm):
        super().__init__(pm, "osu")
        self.api_key = self.pm.botPreferences.get_config_value("OSU", "apikey")
        # base_url controls parameters for lammmy generation. Use python string format to change mode/username
        self.base_url = "http://lemmmy.pw/osusig/sig.php?mode={}&pp=0&removemargin&darktriangles&colour=pink&uname={}"
        self.request_count = 0

    @staticmethod
    def register_events():
        return [Events.Command("osu", desc="Get the osu!standard details for a user"),
                Events.Command("ctb", desc="Get the osu!catch the beat details for a user"),
                Events.Command("taiko", desc="Get the osu!taiko details for a user"),
                Events.Command("mania", desc="Get the osu!mania details for a user"),
                Events.Command("setosu", desc="Register your osu! username to your discord account."),
                Events.Command("deleteosu", desc="Staff command to remove a user's osu setting")]

    def get_models(self):
        return [OsuUser]

    async def handle_command(self, message_object, command, args):
        if command == "osu":
            await self.osu_mode(message_object, args[1].strip(), 0)
        if command == "ctb":
            await self.osu_mode(message_object, args[1].strip(), 2)
        if command == "taiko":
            await self.osu_mode(message_object, args[1].strip(), 1)
        if command == "mania":
            await self.osu_mode(message_object, args[1].strip(), 3)
        if command == "setosu":
            await self.set_osu(message_object, args[1])
        if command == "deleteosu":
            if len(message_object.mentions) == 1:
                user_id = message_object.mentions[0].id
                await self.delete_osu(message_object.guild.id, user_id)
                await self.pm.clientWrap.send_message(self.name, message_object.channel, "osu! username deleted for " +
                                                      message_object.mentions[0].display_name)
            else:
                await self.pm.clientWrap.send_message(self.name, message_object.channel, "Please mention ONE user to "
                                                                                         "delete")

    async def osu_mode(self, message_object, username, mode):
        try:
            if len(message_object.mentions) == 1:
                username = await self.get_osu_name(message_object, message_object.mentions[0])
                if username is None:
                    return
            elif len(username) == 0 or username == "":
                username = await self.get_osu_name(message_object, message_object.author)
                if username is None:
                    return
            await self.get_badge(message_object.channel, username, mode)
        except:
            traceback.print_exc()
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Error unknown user **" + username + "**")

    async def get_badge(self, channel, username, id):
        """
        Gets the osu! badge for the specified user and game mode
        :param channel: discord.Channel from where the command was ran
        :param username: Selected username
        :param id: Game mode ID
        :return: None
        """
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../temp")
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, username + "_profile.jpg")
        image_url = self.base_url.format(id, username)
        urllib.request.urlretrieve(image_url, filename)

        # Check if image is valid
        try:
            await channel.send(file=discord.File(filename), content="<https://osu.ppy.sh/u/" + username + ">")
        except IOError:
            await self.pm.clientWrap.send_message(self.name, channel, "No stats found for this game mode.")
        os.remove(filename)

    async def set_osu(self, message_object, name):
        """
        Registers a user into the osu! username database
        :param message_object: Message containing the setosu command
        :param name: osu! username
        :return: None
        """
        user_id = message_object.author.id
        if name != "" and name is not None:
            try:
                with self.pm.dbManager.lock(message_object.guild.id, self.get_name()):
                    OsuUser.insert(id=str(user_id), username=name).on_conflict_replace().execute()

                await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                      message_object.author.display_name +
                                                      " your osu! username has been set to **" + name + "**")
            except:
                traceback.print_exc()
        else:
            await self.delete_osu(message_object.guild.id, user_id)
            await self.pm.clientWrap.send_message(self.name, message_object.channel, "osu! username deleted for " +
                                                  message_object.author.display_name)

    async def delete_osu(self, server_id, member_id):
        """
        Delete a user from the osu! user database
        :param server_id: Server ID
        :param member_id: User ID
        :return: None
        """
        try:
            with self.pm.dbManager.lock(server_id, self.get_name()):
                OsuUser.delete_by_id(member_id)
        except:
            traceback.print_exc()

    async def get_osu_name(self, msg, user):
        """
        Fetches the osu! username for a specific discord user from the database
        :param user: The user to get the osu name from
        :param msg: Message containing the command
        :return: osu! username as str
        """
        try:
            with self.pm.dbManager.lock(msg.guild.id, self.get_name()):
                osu_user = OsuUser.get_by_id(user.id)
        except DoesNotExist:
            await self.pm.clientWrap.send_message(self.name, msg.channel,
                                                  "No username set for " + user.display_name +
                                                  ". That user can set one by using the `"
                                                  + self.pm.botPreferences.commandPrefix + "setosu <osu name>` command")
            return None

        return osu_user.username


class OsuUser(Model):
    id = TextField(primary_key=True, column_name='Id')
    username = TextField(column_name='Username')

    class Meta:
        table_name = 'osu_users'
