import requests
import urllib.request
import os
from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.api_key = self.pm.botPreferences.get_config_value("OSU", "apikey")

    @staticmethod
    def register_events():
        return [Events.Command("osu", desc="Get the osu details for a user")]

    async def handle_command(self, message_object, command, args):
        if command == "osu":
            await self.osu(message_object, args[1])

    async def osu(self, message_object, username):
        try:
            """Adds two numbers together."""
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, username + "test.jpg")
            urllib.request.urlretrieve("http://lemmmy.pw/osusig/sig.php?colour=pink&uname=" + username, filename)
            api_key = self.api_key
            url = 'https://osu.ppy.sh/api/get_user?k=' + api_key + '&u=' + username
            response = requests.get(url, verify=True)
            display_data = response.json()[0]
            await self.pm.client.send_file(message_object.channel, filename)
            await self.pm.client.send_message(message_object.channel,
                                              "Username: " + display_data["username"] + "\n" + "Rank: " + display_data[
                                                  "pp_rank"] + "\n" + "Accuracy: " + display_data[
                                                  "accuracy"] + "\n" + "PP: " + display_data[
                                                  "pp_raw"] + "\n" + "Country: " + display_data[
                                                  "country"] + "\n" + "Rank in country: " + display_data[
                                                  "pp_country_rank"])
            os.remove(filename)
        except:
            await self.pm.client.send_message(message_object.channel, "Error unknown user")
