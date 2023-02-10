"""
Calculate the age of a date
(mainly just: now - date)
"""
import typing
import datetime


def age(d:typing.Union[datetime.timedelta,datetime.datetime])->datetime.timedelta:
    """
    get the age of another date relative to now
    (if a timedelta is passed in, return it unchanged)

    :param d: _description_
    :type d: typing.Union[datetime.timedelta,datetime.datetime]
    :return: _description_
    :rtype: datetime.timedelta
    """
    if not isinstance(d,datetime.timedelta):
        d=datetime.datetime.now()-d
    return d