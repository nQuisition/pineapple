import datetime
from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Command("role")]

    async def handle_command(self, message_object, command, args):
        if command == "role":
            await self.role(message_object, )

    async def role(self, message_object):
        await self.pm.client.send_message(message_object.channel,
                                          str([role.name.replace("@", "(at)") for role in message_object.author.roles]))
