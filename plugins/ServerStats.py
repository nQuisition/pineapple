import operator
import time
from asyncio import Lock
from typing import Dict
from datetime import datetime
import traceback
from peewee import Model, IntegerField, ForeignKeyField, CompositeKey

import discord

from util import Events
from util.Ranks import Ranks
from AbstractPlugin import AbstractPlugin


# TODO move these into config
# Aggregate message stats for periods of this duration
LOGGING_PERIOD_DURATION = 3 * 60 * 60
# Write stats to database every X seconds
DATABASE_WRITE_PERIOD = 60


class Plugin(AbstractPlugin):

    locks_by_guild: Dict[int, Lock]
    # what a name!
    messages_by_channel_by_guild: Dict[int, Dict[int, int]]
    logging_period_start_by_guild: Dict[int, int]
    last_database_write_by_guild: Dict[int, int]
    logging_period_duration: int
    database_write_period: int

    def __init__(self, pm):
        super().__init__(pm, "ServerStats")
        self.messages_by_channel_by_guild = {}
        self.logging_period_start_by_guild = {}
        self.last_database_write_by_guild = {}
        self.logging_period_duration = LOGGING_PERIOD_DURATION
        self.database_write_period = DATABASE_WRITE_PERIOD
        self.locks_by_guild = {}

    def get_models(self):
        return [LoggingPeriod, ChannelStats]

    @staticmethod
    def register_events():
        return [Events.Message("ServerStats"),
                Events.Loop("ServerStats"),
                Events.Command("rolestat", Ranks.Mod,
                               desc="Shows the amount of users in each role"),
                Events.Command("serverinfo", desc="Shows information about the server"),
                Events.Command("joined", desc="Shows the date a user joined the server")]

    # pass now_time just to be completely synchronized
    def init_guild_params(self, guild_id: int, now_time: int):
        self.messages_by_channel_by_guild[guild_id] = {}
        self.logging_period_start_by_guild[guild_id] = now_time
        self.last_database_write_by_guild[guild_id] = now_time
        if guild_id not in self.locks_by_guild:
            self.locks_by_guild[guild_id] = Lock()

    async def handle_message(self, message_object: discord.Message):
        if self.pm.client.user.id == message_object.author.id:
            return
        guild_id = message_object.guild.id
        channel_id = message_object.channel.id
        if guild_id not in self.messages_by_channel_by_guild:
            self.init_guild_params(guild_id, int(time.time()))
        async with self.locks_by_guild[guild_id]:
            messages_by_channel = self.messages_by_channel_by_guild[guild_id]
            if channel_id not in messages_by_channel:
                messages_by_channel[channel_id] = 0
            messages_by_channel[channel_id] += 1

    async def handle_loop(self):
        for guild_id in self.messages_by_channel_by_guild:
            try:
                now = int(time.time())
                logging_period_start = self.logging_period_start_by_guild[guild_id]
                last_database_write = self.last_database_write_by_guild[guild_id]
                if now - logging_period_start >= self.logging_period_duration:
                    async with self.locks_by_guild[guild_id]:
                        self.write_stats_to_database(guild_id, now)
                        self.last_database_write_by_guild[guild_id] = now
                        self.logging_period_start_by_guild[guild_id] = now
                        self.messages_by_channel_by_guild[guild_id] = {}
                elif now - last_database_write >= self.database_write_period:
                    async with self.locks_by_guild[guild_id]:
                        self.write_stats_to_database(guild_id, now)
                        self.last_database_write_by_guild[guild_id] = now
            except:
                traceback.print_exc()

    # pass now_time just to be completely synchronized
    def write_stats_to_database(self, guild_id, now_time):
        with self.pm.dbManager.lock(guild_id, self.get_name()):
            # TODO move transaction management to the database manager?
            with self.pm.dbManager.db.atomic():
                start = self.logging_period_start_by_guild[guild_id]
                messages_by_channel = self.messages_by_channel_by_guild[guild_id]
                LoggingPeriod.insert(start=start, end=now_time).on_conflict_replace().execute()
                for channel_id in messages_by_channel:
                    message_count = messages_by_channel[channel_id]
                    ChannelStats.insert(logging_period=start, channel_id=channel_id,
                                        message_count=message_count).on_conflict_replace().execute()

    async def handle_command(self, message_object, command, args):
        if command == "serverinfo":
            await self.server_info(message_object)
        if command == "rolestat":
            await self.rolestat(message_object)
        if command == "joined":
            await self.joined(message_object)

    async def rolestat(self, message_object):
        server = message_object.guild
        msg = "Role stats for this server (" + str(server.member_count) + " users in total):\n"

        roles = dict()

        for member in server.members:
            for member_role in member.roles:
                if member_role.name != "@everyone":
                    if member_role.name in roles:
                        roles[member_role.name] += 1
                    else:
                        roles[member_role.name] = 1
        sorted_x = sorted(roles.items(), key=operator.itemgetter(1))
        for role, count in reversed(sorted_x):
            msg += role + ": " + str(count) + " users\n"

        await self.pm.clientWrap.send_message(self.name, message_object.channel, msg)

    async def server_info(self, message_object):
        server = message_object.guild
        msg = "**Name:** " + server.name + " (" + str(server.id) + ")\n"
        msg += "**Total members:** " + str(server.member_count) + "\n"
        msg += "**Server owner:** " + server.owner.name + "\n"
        msg += "**Server region:** " + str(server.region) + "\n"
        msg += "**Created at:** " + server.created_at.strftime("%B %d, %Y")

        em = discord.Embed(description=msg, colour=self.pm.clientWrap.get_color(self.name))
        em.set_image(url=server.icon_url)
        await message_object.channel.send(embed=em)

    async def joined(self, message_object):
        user = message_object.author
        if len(message_object.mentions) >= 1:
            user = message_object.mentions[0]

        joined = user.joined_at
        now = datetime.now()
        diff = now - joined
        await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                              user.display_name + " joined this server " + str(diff.days) +
                                              " days ago on: " + joined.strftime("%H:%M:%S %d-%m-%Y"))


# PKs on these models are somewhat questionable, but they make upserts much easier
class LoggingPeriod(Model):
    start = IntegerField(primary_key=True)
    end = IntegerField()

    class Meta:
        table_name = 'logging_period'


class ChannelStats(Model):
    logging_period = ForeignKeyField(LoggingPeriod, to_field='start')
    channel_id = IntegerField()
    message_count = IntegerField()

    class Meta:
        table_name = 'channel_stats'
        primary_key = CompositeKey('logging_period', 'channel_id')
