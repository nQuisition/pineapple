from util import Events, Timezones
from datetime import datetime, time, timezone
from dateutil.tz import gettz
from dateutil.parser import parse
import pytz
import re
import random

class Plugin(object):
    def __init__(self, pm):
        self.pm = pm
        self.name = 'Timezone'
        self.output_timezones = [
            pytz.timezone('America/Los_Angeles'),
            pytz.timezone('America/New_York'), 
            pytz.timezone('Europe/London'),
            pytz.timezone('Europe/Amsterdam'),
            pytz.timezone('Asia/Tokyo'),
        ]
        self.output_format = '%b %d %Y- %H:%M **%Z**'


    def get_times(self, time_object):
        """
        Given a time object as a parameter, return a dictionary of timezones and times. 
        """
        if time_object.tzinfo == None:
            time_object = pytz.timezone('UTC').localize(time_object)
        time_strings = []
        for output_timezone in self.output_timezones:
            converted = time_object.astimezone(output_timezone)
            time_string = converted.strftime(self.output_format)
            time_strings.append(time_string)
        return '\n'.join(time_strings)


    @staticmethod
    def register_events():
        helptext = """Given a time in either 12 or 24 hour format, display time conversions in several timezones. 
        Example: '1:00PM', '13:00', '13:00 PST'. If no time is specified, the current time in UTC is used. 
        Default timezone is UTC."""
        return [Events.Command('time', desc=helptext)]

    async def handle_command(self, message_object, command, cmd_args):
        if cmd_args[1] == '':
            await self.time(message_object, None)
        elif not re.match(r"(\d{1,2}\:\d{2})|((?i)\d{1,2}(am|pm))", cmd_args[1]):
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  'Unable to parse time. Check format(e.g. 5:00pm/5pm instead of 500pm)')
        elif command == 'time':
            await self.time(message_object, cmd_args[1])

    async def time(self, message_object, base_time):
        try:
            if base_time is None:
                base_time_obj = datetime.now(timezone.utc)
            else:
                base_time = base_time.upper()
                base_time_obj = parse(base_time, tzinfos=Timezones.TIMEZONE_INFO)
            
            response_text = self.get_times(base_time_obj)
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  response_text)
        except Exception as e:
            print(e)
            await self.pm.clientWrap.send_message(self.name, message_object.channel,
                                                  'Unable to parse time.')



