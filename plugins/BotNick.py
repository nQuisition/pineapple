class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["nick"]
		
	async def HandleCommand(self, messageObject, command, args):
		if command == "nick":
			await self.nick(messageObject, args[1])
			
	async def nick(self, messageObject, nick):
			await self.pm.client.change_nickname(messageObject.server.me, nick)