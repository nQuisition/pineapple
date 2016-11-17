from PluginManager import PluginManager
import discord
import asyncio
import sys
client = discord.Client()
pm = PluginManager("plugins/", client)

print("Starting UNNAMEDBOT")

print("Loading plugins")
pm.LoadPlugins()
pm.RegisterCommands()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
	if message.content.startswith(pm.botPreferences.commandPrefix):
		words = message.content.partition(' ')
		await pm.HandleCommand(message.channel, words[0][1:], words[1:])

client.run(sys.argv[1])