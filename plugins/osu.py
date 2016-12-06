import requests

from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.apikey = self.pm.botPreferences.get_config_value("OSU", "apikey")

    @staticmethod
    def register_events():
        return [Events.Command("osu")]

    async def handle_command(self, message_object, command, args):
        if command == "osu":
            await self.osu(message_object, args[1])

    async def osu(self, message_object, username):
        """Adds two numbers together."""
        apikey = self.apikey
        await self.pm.client.send_message(message_object.channel, 'Fetching data')
        url = 'https://osu.ppy.sh/api/get_user?k=' + apikey + '&u=' + username
        response = requests.get(url, verify=True)
        displayData = response.json()[0]
        await self.pm.client.send_message(message_object.channel,
                                          "country: " + displayData["country"] + "\n" + "username: " + displayData[
                                              "username"])
