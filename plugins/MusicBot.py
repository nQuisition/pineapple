from util import Events
from util.Ranks import Ranks
from discord import Channel


class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.player = None

    @staticmethod
    def register_events():
        return [Events.Command("play", desc="Play a song in voice chat"),
                Events.Command("stop", Ranks.Mod, desc="Stop the Music bot")]

    async def handle_command(self, message_object, command, args):
        if command == "play":
            await self.play(message_object, args[1])
        if command == "stop":
            await self.stop(message_object)

    async def play(self, message_object, url):

        await self.pm.client.delete_message(message_object)

        # Kill all playing connections before starting a new one
        if self.player is not None:
            self.player.stop()

        # Check if the user requesting is in a voice channel
        channel = message_object.author.voice.voice_channel
        if channel is not None and type(channel) is Channel:

            # Disconnect if we're connected without playing anything.
            if self.player is None:
                chan = self.pm.client.voice_client_in(message_object.server)
                if chan is not None:
                    await chan.disconnect()

            # Get current joined channel, if not available join user channel
            if len(self.pm.client.voice_clients) is 0:
                voice = await self.pm.client.join_voice_channel(channel)
            else:
                voice = self.pm.client.voice_client_in(message_object.server)
            self.player = await voice.create_ytdl_player(url, ytdl_options={"default_search": "ytsearch"})

            self.player.start()

            # Format stream duration
            m, s = divmod(self.player.duration, 60)
            h, m = divmod(m, 60)
            if h is 0:
                duration = str(m) + ":" + str(s)
            else:
                duration = str(h) + ":" + str(m) + ":" + str(s)

            await self.pm.client.send_message(message_object.channel, "Now playing **" + self.player.title +
                                              "** (" + duration + ") in " + channel.name)
        else:
            await self.pm.client.send_message(message_object.channel, message_object.author.mention +
                                              " please join a voice channel in order to start the bot!")

    async def stop(self, message_object):
        # Kill all playing connections
        if self.player is not None:
            self.player.stop()

        # Disconnect from voice
        chan = self.pm.client.voice_client_in(message_object.server)
        if chan is not None:
            await chan.disconnect()
