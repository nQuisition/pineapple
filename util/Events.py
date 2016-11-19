class Command(object):
    def __init__(self, name):
        self.name = name


class UserJoin(object):
    def __init__(self, name):
        self.name = name


class UserLeave(object):
    def __init__(self, name):
        self.name = name


class BotJoin(object):
    def __init__(self, name):
        self.name = name


class MessageDelete(object):
    def __init__(self, name):
        self.name = name


class MessageEdit(object):
    def __init__(self, name):
        self.name = name


class Typing(object):
    def __init__(self, name):
        self.name = name
