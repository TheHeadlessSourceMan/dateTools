"""
Common values for numbers
"""
import datetime
import re
from .dateFormatException import DateFormatException

NumberReText=r"""(?P<number>[0-9]+)"""

TimeReText=r"""(?P<hour>[0-9]{1,2}(:(?P<minute>[0-9]{1,2})(:(?P<second>[0-9]{1,2}))))(\s*(?P<ampm>am|pm))?""" # noqa: E501 # pylint: disable=line-too-long
TimeRe=re.compile(TimeReText,re.IGNORECASE)

def parseTime(t:str)->datetime.datetime:
    """
    Parse a simple time string of the form
        hour[:minute[:second]][am|pm]
    """
    m=TimeRe(t)
    if m is None:
        raise DateFormatException(t)
    hour=int(m.group('hour'))
    minute=0
    second=0
    if 'minute' in m.group_names():
        minute=int(m.group('hour'))
        if 'second' in m.group_names():
            second=int(m.group('second'))
    if 'ampm' in m.group_names() and m.group('ampm')[0].lower()=='p':
        hour+=12
    return datetime.datetime(hour=hour,minute=minute,second=second)
