from PluginManager import PluginManager
import discord
import sys

print("Starting UNNAMEDBOT")
print("Starting Discord Client")
client = discord.Client()
print("Loading plugins")
pm = PluginManager("plugins/", client)
pm.load_plugins()
pm.register_events()
print("Plugins loaded and registered")


@client.event
async def on_ready():
    print('Logged in as ' + client.user.name + " (" + client.user.id + ")")
    for instance in client.servers:
        await client.change_nickname(instance.me, pm.botPreferences.nickName)


@client.event
async def on_message(message):
    try:
        if message.content.startswith(pm.botPreferences.commandPrefix):
            words = message.content.partition(' ')
            await pm.handle_command(message, words[0][1:], words[1:])
    except Exception as e:
        await client.send_message(message.channel, "Error: " + str(e))


@client.event
async def on_typing(channel, user, when):
    try:
        await pm.handle_typing(channel, user, when)
    except Exception as e:
        await client.send_message(channel, "Error: " + str(e))


@client.event
async def on_message_delete(message):
    try:
        if message.author.name != "PluginBot":
            await pm.handle_message_delete(message)
    except Exception as e:
        await client.send_message(message.channel, "Error: " + str(e))

client.run(pm.botPreferences.token)
