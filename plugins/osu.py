import requests
import urllib.request
import os
from util import Events


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.api_key = self.pm.botPreferences.get_config_value("OSU", "apikey")
        # base_url controls parameters for lammmy generation. Use python string format to change mode/username
        self.base_url = "http://lemmmy.pw/osusig/sig.php?mode={}&pp=0&removemargin&darktriangles&colour=pink&uname={}"

    @staticmethod
    def register_events():
        return [Events.Command("osu", desc="Get the osu!standard details for a user"),
                Events.Command("ctb", desc="Get the osu!catch the beat details for a user"),
                Events.Command("taiko", desc="Get the osu!taiko details for a user"),
                Events.Command("mania", desc="Get the osu!mania details for a user")]

    async def handle_command(self, message_object, command, args):
        if command == "osu":
            await self.osu(message_object, args[1])
        if command == "ctb":
            await self.taiko(message_object, args[1])
        if command == "taiko":
            await self.taiko(message_object, args[1])
        if command == "mania":
            await self.mania(message_object, args[1])

    async def osu(self, message_object, username):
        try:
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, username + "test.jpg")
            image_url = self.base_url.format(0, username)
            urllib.request.urlretrieve(image_url, filename)
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
            await self.pm.client.send_message(message_object.channel, "Error unknown user **" + username + "**")

    async def taiko(self, message_object, username):
        try:
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, username + "test.jpg")
            image_url = self.base_url.format(1, username)
            urllib.request.urlretrieve(image_url, filename)
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
            await self.pm.client.send_message(message_object.channel, "Error unknown user **" + username + "**")

    async def ctb(self, message_object, username):
        try:
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, username + "test.jpg")
            image_url = self.base_url.format(2, username)
            urllib.request.urlretrieve(image_url, filename)
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
            await self.pm.client.send_message(message_object.channel, "Error unknown user **" + username + "**")

    async def mania(self, message_object, username):
        try:
            directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
            if not os.path.exists(directory):
                os.makedirs(directory)
            filename = os.path.join(directory, username + "test.jpg")
            image_url = self.base_url.format(3, username)
            urllib.request.urlretrieve(image_url, filename)
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
            await self.pm.client.send_message(message_object.channel, "Error unknown user **" + username + "**")
