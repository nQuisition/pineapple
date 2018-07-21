from util import Events
from collections import defaultdict
import arrow


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.db = defaultdict(arrow.utcnow)
        self.name = "Timer"

    @staticmethod
    def register_events():
        return [Events.Command("timer"),Events.Command("reset")]

    async def handle_command(self, message_object, command, args):
        if command == "timer":
            await self.timer(message_object)
        if command == "reset":
            await self.reset(message_object)

    async def reset(self, message_object):
        delta = self.db[message_object.channel].humanize(only_distance = True)
        self.db[message_object.channel] = arrow.utcnow()
        await self.pm.clientWrap.send_message(self.name, message_object.channel, f"Timer reset after {delta}.")
        await self.pm.client.delete_message(message_object)

    async def timer(self, message_object):
        delta = self.db[message_object.channel].humanize(only_distance = True)
        await self.pm.clientWrap.send_message(name, message_object.channel, f"Timer has been running for {delta}.")
        await self.pm.client.delete_message(message_object)
