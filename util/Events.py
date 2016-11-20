from util.Ranks import Ranks


class Command(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class UserJoin(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class UserLeave(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class BotJoin(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class MessageDelete(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class MessageEdit(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank


class Typing(object):
    def __init__(self, name, rank=Ranks.Default):
        self.name = name
        self.minimum_rank = rank
