from util import Events
import discord
import asyncio
import random


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.race = self.Race()

    class Race(object):
        class Participant(object):
            def __init__(self, name, emoji):
                self.name = name
                self.emoji = emoji
                self.progress = 0

        participants = list()

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        return [Events.Command("race"), Events.Command("joinrace")]

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "race":
            await self.start_race(message_object)
        if command == "joinrace":
            await self.join_race(message_object, args)

    async def start_race(self, message_object: discord.Message):
        """
        :param message_object: discord.Message object
        """
        self.race = None
        self.race = self.Race()
        race_start = await self.pm.client.send_message(message_object.channel,
                                                       message_object.author.name + " has started a race! \n"
                                                                                    "Type !joinrace [emoji] to "
                                                                                    "join the race (10s)")
        # Give users time to join
        await asyncio.sleep(10)
        await self.pm.client.delete_message(message_object)
        await self.pm.client.delete_message(race_start)

        # If enough participants, start the race
        if len(self.race.participants) > 0:
            race_status = ":checkered_flag: :checkered_flag: :checkered_flag:\n"
            for p in self.race.participants:
                steps = round(p.progress / 5) - 1
                left = 20 - steps - 1
                race_status += p.name + " | " + self.repeat("X", steps) + p.emoji + self.repeat("O", left) + " (" + str(
                    p.progress) + ") \n"
            race_status += ":checkered_flag: :checkered_flag: :checkered_flag:"
            race_message = await self.pm.client.send_message(message_object.channel, race_status)

            running = True
            while running:
                running = False
                for p in self.race.participants:
                    p.progress = min(p.progress + random.randint(3, 15), 100)
                    if p.progress < 100:
                        running = True

                race_status = ":checkered_flag: :checkered_flag: :checkered_flag:\n"
                for p in self.race.participants:
                    steps = round(p.progress / 5) - 1
                    left = 20 - steps - 1
                    race_status += p.name + " | " + self.repeat("X", steps) + p.emoji + self.repeat("O",
                                                                                                    left) + " (" + str(
                        p.progress) + ") \n"
                race_status += ":checkered_flag: :checkered_flag: :checkered_flag:"
                race_message = await self.pm.client.edit_message(race_message, race_status)
                await asyncio.sleep(2)


    async def join_race(self, message_object: discord.Message, args):
        if args[1] != "":
            self.race.participants.append(self.Race.Participant(message_object.author.name, args[1]))
            user_join = await self.pm.client.send_message(message_object.channel,
                                                          message_object.author.name + " has joined the race as " +
                                                          args[1])
            await asyncio.sleep(3)
            await self.pm.client.delete_message(message_object)
            await self.pm.client.delete_message(user_join)

    @staticmethod
    def repeat(char, num):
        return ''.join([char for s in range(0, num)])
