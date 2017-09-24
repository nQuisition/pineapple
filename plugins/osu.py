import requests
import urllib.request
import os
from util import Events
import sqlite3
import traceback
import operator
import discord
import json
from PIL import Image
from tornado import ioloop, httpclient
import asyncio

# noinspection SpellCheckingInspection
class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.api_key = self.pm.botPreferences.get_config_value("OSU", "apikey")
        # base_url controls parameters for lammmy generation. Use python string format to change mode/username
        self.base_url = "http://lemmmy.pw/osusig/sig.php?mode={}&pp=0&removemargin&darktriangles&colour=pink&uname={}"
        self.name = "osu"
        self.leaderboard_lock = False
        self.request_count = 0
        self.leaderboard_data = dict()

    @staticmethod
    def register_events():
        return [Events.Command("osu", desc="Get the osu!standard details for a user"),
                Events.Command("ctb", desc="Get the osu!catch the beat details for a user"),
                Events.Command("taiko", desc="Get the osu!taiko details for a user"),
                Events.Command("mania", desc="Get the osu!mania details for a user"),
                Events.Command("leaderboard", desc="Get the server leaderboard for a mode (osu, ctb, taiko, mania)"),
                Events.Command("setosu", desc="Register your osu! username to your discord account. "
                                              "Will add you to the leaderboards"),
                Events.Command("deleteosu", desc="Staff command to remove a user from the leaderboard")]

    async def handle_command(self, message_object, command, args):
        if command == "osu":
            await self.osu_mode(message_object, args[1].strip(), 0)
        if command == "ctb":
            await self.osu_mode(message_object, args[1].strip(), 2)
        if command == "taiko":
            await self.osu_mode(message_object, args[1].strip(), 1)
        if command == "mania":
            await self.osu_mode(message_object, args[1].strip(), 3)
        if command == "leaderboard":
            await self.leaderboard(message_object, args[1].strip())
        if command == "setosu":
            await self.set_osu(message_object, args[1])
        if command == "deleteosu":
            if len(message_object.mentions) is 1:
                user_id = message_object.mentions[0].id
                await self.delete_osu(message_object.server.id, user_id)
                await self.pm.clientWrap.send_message(self.name, message_object.channel, "osu! username deleted for " +
                                                      message_object.mentions[0].display_name)
            else:
                await self.pm.clientWrap.send_message(self.name, message_object.channel, "Please mention ONE user to "
                                                                                         "delete")

    async def osu_mode(self, message_object, username, mode):
        try:
            if len(username) is 0 or username is "":
                username = await self.get_osu_name(message_object)
                if username is None:
                    return
            await self.get_badge(message_object.channel, username, mode)
            # display_data = await self.get_data(username, mode)
            # await self.pm.client.send_message(message_object.channel,
            #                                  "Username: " + display_data["username"] + "\n" + "Rank: " + display_data[
            #                                      "pp_rank"] + "\n" + "Accuracy: " + display_data[
            #                                      "accuracy"] + "\n" + "PP: " + display_data[
            #                                      "pp_raw"] + "\n" + "Country: " + display_data[
            #                                      "country"] + "\n" + "Rank in country: " + display_data[
            #                                      "pp_country_rank"])
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
        directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp")
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = os.path.join(directory, username + "test.jpg")
        image_url = self.base_url.format(id, username)
        urllib.request.urlretrieve(image_url, filename)

        # Check if image is valid
        try:
            im = Image.open(filename)
            im.close()
            await self.pm.client.send_file(channel, filename)
        except IOError:
            await self.pm.clientWrap.send_message(self.name, channel, "No stats found for this game mode.")
        os.remove(filename)

    async def get_data(self, username, game_mode_id):
        """
        Get a JSON object containing osu! user data
        :param username: Selected username
        :param game_mode_id: Game mode ID
        :return: JSON object
        """
        api_key = self.api_key
        url = 'https://osu.ppy.sh/api/get_user?m=' + str(game_mode_id) + '&k=' + api_key + '&u=' + username
        response = requests.get(url, verify=True)
        return response.json()[0]

    def handle_request(self, response):
        try:
            print(response.body)
            json_data = json.loads(response.body.decode('utf-8'))[0]
            self.leaderboard_data[json_data["username"]] = json_data
        except:
            print("Failed to fetch user data, http error")
        self.request_count -= 1
        if self.request_count == 0:
            ioloop.IOLoop.instance().stop()

    async def leaderboard(self, message_object, mode):
        """
        Print the osu! leaderboard for a specific game mode
        :param message_object: Message containing the leaderboard command
        :param mode: Game mode name
        :return: None
        """
        if self.leaderboard_lock:
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Leaderboard is currently being loaded. Please wait.")
            return
        else:
            self.leaderboard_lock = True
            self.leaderboard_data = dict()
            self.request_count = 0
        if not os.path.exists("cache/"):
            os.makedirs("cache")
        if mode is "":
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  "Please specify the game mode (osu, taiko, ctb, mania)")
            return
        try:
            lb_msg = await self.pm.clientWrap.send_message(self.name, message_object.channel, "Loading leaderboard...")
            if mode == "osu":
                game_mode_id = 0
            elif mode == "taiko":
                game_mode_id = 1
            elif mode == "ctb":
                game_mode_id = 2
            elif mode == "mania":
                game_mode_id = 3
            else:
                mode = "osu"
                game_mode_id = 0

            # Connect to SQLite file for server in cache/SERVERID.sqlite
            con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            with con:
                cur = con.cursor()
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS osu_users(Id TEXT PRIMARY KEY, Username TEXT)")
                cur.execute("SELECT * FROM osu_users")  # TODO: Improve loading to show more users
                rows = cur.fetchall()
                index = 1
                msg = "**Leaderboard for " + mode + ":**    \n"
                unsorted = list()

                users = dict()
                for row in rows:
                    users[row[1].lower().replace(" ", "_")] = row[0]
                print(users)

                await self.pm.clientWrap.edit_message(self.name, lb_msg, "Fetching data from osu! API...")

                self.request_count = 0
                http_client = httpclient.AsyncHTTPClient()
                for user in users:
                    self.request_count += 1
                    http_client.fetch(
                        'https://osu.ppy.sh/api/get_user?m=' + str(
                            game_mode_id) + '&k=' + self.api_key + '&u=' + user.lower(),
                        self.handle_request, method='GET')
                ioloop.IOLoop.instance().start()

                while self.request_count != 0:
                    print("Waiting for requests to finish...")

                await self.pm.clientWrap.edit_message(self.name, lb_msg, "Processing data from osu! API...")

                for user in self.leaderboard_data:
                    users_key = user.lower().replace(" ", "_")
                    if self.leaderboard_data[user]["pp_rank"] != "0" and self.leaderboard_data[user][
                        "pp_rank"] is not None \
                            and users_key in users:
                        self.leaderboard_data[user]["discord_id"] = users[users_key]
                        self.leaderboard_data[user]["discord_name"] = user
                        self.leaderboard_data[user]["pp_rank"] = int(self.leaderboard_data[user]["pp_rank"])
                        unsorted.append(self.leaderboard_data[user])
                sortedusers = sorted(unsorted, key=operator.itemgetter("pp_rank"))

                await self.pm.clientWrap.edit_message(self.name, lb_msg,
                                                      "Fetching information from Discord and building message")
                for data in sortedusers:
                    try:
                        user = await self.pm.client.get_user_info(data["discord_id"])
                        member = discord.utils.find(lambda m: m.name == user.name,
                                                    message_object.channel.server.members)
                        if member is None:
                            await self.delete_osu(message_object.server.id, data["discord_id"])
                            continue

                        # fetch correct display name
                        if hasattr(user, 'nick') and user.nick != "":
                            name = user.nick
                        else:
                            name = user.name

                        # get an emoji for top 3
                        if index is 1:
                            emoji = ":first_place:"
                        elif index is 2:
                            emoji = ":second_place:"
                        elif index is 3:
                            emoji = ":third_place:"
                        else:
                            emoji = str(index) + "#:"

                        msg += emoji + " " + data["username"] + "  #" + str(data["pp_rank"]) + " (" + str(
                            int(float(data[
                                          "pp_raw"]))) + "pp)" + " (" + name + ") \n"
                        index += 1
                    except Exception as e:
                        await self.pm.client.send_message(message_object.channel, "Error: " + str(e))
                        if self.pm.botPreferences.get_config_value("client", "debug") == "1":
                            traceback.print_exc()
                        self.leaderboard_lock = False
                        self.leaderboard_data = dict()
                        self.request_count = 0

                await self.pm.client.delete_message(lb_msg)

                if len(msg) > 1500:
                    lb_strings = list(map(''.join, zip(*[iter(msg)] * 1000)))
                    for string in lb_strings:
                        await self.pm.clientWrap.send_message(self.name, message_object.channel, string)
                        await asyncio.sleep(1)
                else:
                    await self.pm.clientWrap.send_message(self.name, message_object.channel, msg)

                self.leaderboard_lock = False
                self.leaderboard_data = dict()
                self.request_count = 0
        except Exception as e:
            await self.pm.client.send_message(message_object.channel, "Error: " + str(e))
            if self.pm.botPreferences.get_config_value("client", "debug") == "1":
                traceback.print_exc()
            self.leaderboard_lock = False
            self.leaderboard_data = dict()
            self.request_count = 0

    async def set_osu(self, message_object, name):
        """
        Registers a user into the osu! username database
        :param message_object: Message containing the setosu command
        :param name: osu! username
        :return: None
        """
        user_id = message_object.author.id
        if name is not "" and name is not None:
            if not os.path.exists("cache/"):
                os.makedirs("cache")
            try:
                # Connect to SQLite file for server in cache/SERVERID.sqlite
                con = sqlite3.connect("cache/" + message_object.server.id + ".sqlite",
                                      detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

                with con:
                    cur = con.cursor()
                    cur.execute(
                        "CREATE TABLE IF NOT EXISTS osu_users(Id TEXT PRIMARY KEY, Username TEXT)")
                    cur.execute(
                        'INSERT OR IGNORE INTO osu_users(Id, Username) VALUES(?, ?)',
                        (str(user_id), name))

                    cur.execute("UPDATE osu_users SET Username = ? WHERE Id = ?",
                                (name, str(user_id)))

                    await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                          message_object.author.display_name +
                                                          " your osu! username has been set to **" + name + "**")
            except:
                traceback.print_exc()
        else:
            await self.delete_osu(user_id)

    @staticmethod
    async def delete_osu(server_id, member_id):
        """
        Delete a user from the osu! user database
        :param server_id: Server ID
        :param member_id: User ID
        :return: None
        """
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")
        try:
            con = sqlite3.connect("cache/" + server_id + ".sqlite",
                                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            with con:
                cur = con.cursor()
                cur.execute("DELETE FROM osu_users WHERE Id=?", (member_id,))
        except:
            traceback.print_exc()

    async def get_osu_name(self, msg):
        """
        Fetches the osu! username for a specific discord user from the database
        :param msg: Message containing the command
        :return: osu! username as str
        """
        # Connect to SQLite file for server in cache/SERVERID.sqlite
        if not os.path.exists("cache/"):
            os.mkdir("cache/")

        con = sqlite3.connect("cache/" + msg.server.id + ".sqlite",
                              detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        with con:
            cur = con.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS osu_users(Id TEXT PRIMARY KEY, Username TEXT)")
            cur.execute("SELECT Username FROM osu_users WHERE Id = ?", (msg.author.id,))
            rows = cur.fetchall()

            for row in rows:
                return row[0]

            await self.pm.clientWrap.send_message(self.name, msg.channel,
                                                  "No username set for " + msg.author.display_name +
                                                  ". You can set one by using the `setosu <osu name>` command")
            return None
