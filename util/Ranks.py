from enum import IntEnum


class Ranks(IntEnum):
    Default = 0
    Member = 1
    Mod = 2
    Admin = 3


class RankContainer:
    def __init__(self):
        self.admin = list()
        self.mod = list()
        self.member = list()
        self.default = list()

