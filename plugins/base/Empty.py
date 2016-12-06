from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        """
        Define events that this plugin will listen to
        :return: A list of util.Events
        """
        return [Events.Command("example_command")]

    async def handle_command(self, message_object, command, args):
        """
        Handle Events.Command events
        :param message_object: discord.Message object containing the message
        :param command: The name of the command (first word in the message, without prefix)
        :param args: List of words in the message
        """
        if command == "example_command":
            await self.example_command(message_object)

    async def example_command(self, message_object):
        """
        Execute the example_command command. All calls to self.pm.client should be asynchronous (await)!
        :param message_object: discord.Message object
        """
        await self.pm.client.send_message(message_object.channel, 'Pong')
