class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["ping", "pong"]
		
	async def HandleCommand(self, messageObject, command, args):
		if command == "ping":
			await self.ping(messageObject)
			
	async def ping(self, messageObject):
		tmp = await self.pm.client.send_message(messageObject.channel, 'Pong')