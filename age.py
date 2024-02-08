"""
Calculate the age of a date
(mainly just: now - date)
"""
import typing
import datetime


def age(d:typing.Union[datetime.timedelta,datetime.datetime]
    )->datetime.timedelta:
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


def ageCmp(
    a:typing.Union[datetime.datetime,datetime.timedelta],
    b:typing.Union[datetime.datetime,datetime.timedelta]
    )->datetime.timedelta:
    """
    compare two date ages and return a timedelta
    """
    return age(a)-age(b)


def minAge(
    a:typing.Union[None,datetime.datetime,datetime.timedelta],
    b:typing.Union[None,datetime.datetime,datetime.timedelta]
    )->typing.Union[None,datetime.datetime,datetime.timedelta]:
    """
    a min() function for date ages
    """
    if a is None:
        result=b
    elif b is None:
        result=a
    elif age(a)<age(b):
        result=a
    else:
        result=b
    return result


def maxAge(
    a:typing.Union[None,datetime.datetime,datetime.timedelta],
    b:typing.Union[None,datetime.datetime,datetime.timedelta]
    )->typing.Union[None,datetime.datetime,datetime.timedelta]:
    """
    a max() function for date ages
    """
    if a is None:
        result=b
    elif b is None:
        result=a
    elif age(a)>age(b):
        result=a
    else:
        result=b
    return result
