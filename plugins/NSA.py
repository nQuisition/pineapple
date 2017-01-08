from util import Events
import sqlite3
import datetime
import discord

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm

    @staticmethod
    def register_events():
        return [Events.Message("nsa")]

    async def handle_message(self, message_object):
        try:
            con = sqlite3.connect("log.sqlite", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)

            with con:

                # Collect data
                date = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
                staff = 0
                staff_roles = self.pm.botPreferences.admin + self.pm.botPreferences.mod
                for member in message_object.server.members:
                    if member.status is discord.Status.online:
                        is_staff = False
                        for role in member.roles:
                            if role.name in staff_roles:
                                staff += 1
                                is_staff = True
                            if is_staff:
                                break

                cur = con.cursor()

                # Update channel table
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS " + message_object.channel.name + "(Time DATETIME PRIMARY KEY, "
                                                                                  "Count INT, Staff INT)")
                cur.execute(
                    'INSERT OR IGNORE INTO ' + message_object.channel.name + '(Time, Count, Staff) VALUES(?, ?, ?)',
                    (date, 1, 0))

                cur.execute("UPDATE " + message_object.channel.name + " SET Count = Count + 1 , "
                                                                      "Staff = MAX(Staff, ?) WHERE Time = ?",
                            (staff, date))

                # Update total table
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS total(Time DATETIME PRIMARY KEY, Count INT, Staff INT)")
                cur.execute(
                    'INSERT OR IGNORE INTO total(Time, Count, Staff) VALUES(?, ?, ?)',
                    (date, 1, 0))
                cur.execute("UPDATE total SET Count = Count + 1 , Staff = MAX(Staff, ?) WHERE Time = ?",
                            (staff, date))

        except:
            print("error?")
