from util import Events
from trello import trelloclient


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.api_key = self.pm.botPreferences.get_config_value("Trello", "apikey")
        self.token = self.pm.botPreferences.get_config_value("Trello", "token")
        self.board = self.pm.botPreferences.get_config_value("Trello", "board")

    @staticmethod
    def register_events():
        return [Events.Command("feedback", desc="Suggest a feature to the bot owner (give us a small description "
                                                "of what you'd like to see)"),
                Events.Command("bug", desc="Report a bug to the bot owner (give us a description of the problem)")]

    async def handle_command(self, message_object, command, args):
        if command == "feedback":
            await self.feedback(message_object, "Feedback", args[1])
        if command == "bug":
            await self.feedback(message_object, "Bug", args[1])

    async def feedback(self, message_object, list_name, text):
        if text is None or text == "" or len(text) < 4:
            await self.pm.client.send_message(message_object.channel,
                                              message_object.author.mention + " please enter a description.")
            return

        trello = trelloclient.TrelloClient(self.api_key, token=self.token)

        board = trello.get_board(self.board)

        for list in board.get_lists(None):
            if list.name == list_name:
                list.add_card(text + " (by " + message_object.author.name + ")")
                await self.pm.client.send_message(message_object.channel,
                                                  message_object.author.mention + " your feedback has been submitted. ("
                                                  + text + ")")
