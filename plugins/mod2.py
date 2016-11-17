class Plugin(object):
	def __init__(self, pm):
		self.pm = pm
		
	def RegisterCommands(self):
		return ["ping", "pong"]
		
	def HandleCommand(self, command, args):
		print(command)