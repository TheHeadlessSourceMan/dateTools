"""
A series of functions that give you common date ranges you'll likely want,
eg thisMonth() or dayAfter(tomorrow())
"""
import typing
import datetime
from dateTools import DateRange


def yearRange(
    fromYear:typing.Union[int,None,datetime.datetime]=None,
    toYear:typing.Union[int,None,datetime.datetime]=None)->DateRange:
    """
    Get a range representing the entire year(s) for the date(s)
    That is, the entire range from 1:00:00AM jan 1 to 12:59:59PM on dec 31

    :fromYear: if not specified, use this year
    :toYear: if not specified, use fromYear
    """
    if fromYear is None:
        fromYear=datetime.datetime.now().year
    elif isinstance(fromYear,datetime.datetime):
        fromYear=fromYear.year
    if toYear is None:
        toYear=fromYear
    elif isinstance(fromYear,datetime.datetime):
        fromYear=fromYear.year
    return DateRange(
        (datetime.datetime(fromYear,1,1,0,0,0),
        datetime.datetime(toYear,12,31,23,59,59)))
def yearBefore(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire year before a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=yearRange(when).fromTime()
    elif isinstance(when,DateRange):
        when=yearRange(when).fromTime()
    return yearRange(when.year-1)
def lastYear()->DateRange:
    """
    return a range representing the entire last year
    """
    return yearRange(datetime.datetime.now().year-1)
def thisYear()->DateRange:
    """
    return a range representing this entire year
    """
    return yearRange()
def nextYear()->DateRange:
    """
    return a range representing the entire next year
    """
    return yearRange(datetime.datetime.now().year+1)
def yearAfter(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire year after a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=yearRange(when).fromTime()
    elif isinstance(when,DateRange):
        when=yearRange(when).fromTime()
    return yearRange(when.year+1)

def monthRange(
    fromMonth:typing.Union[int,None,datetime.datetime]=None,
    toMonth:typing.Union[int,None,datetime.datetime]=None)->DateRange:
    """
    Get a range representing the entire month(s) for the date(s)
    Eg: fromMonth=(date_in_july,date_in_august), the range will be july1-aug31.

    :fromMonth: if not specified, use this month
    :toMonth: if not specified, use fromMonth
    """
    if fromMonth is None:
        now=datetime.datetime.now()
        fromYear=now.year
        fromMonth=now.month
    elif isinstance(fromMonth,datetime.datetime):
        fromYear=fromMonth.year
        fromMonth=fromMonth.month
    else:
        fromYear=datetime.datetime.now().year
    if toMonth is None:
        toYear=fromYear
        toMonth=fromMonth
    elif isinstance(fromMonth,datetime.datetime):
        fromMonth=fromMonth.year
        toMonth=fromMonth.month
    else:
        toYear=fromYear
    return DateRange((
        datetime.datetime(fromYear,fromMonth,1,0,0,0),
        datetime.datetime(toYear,toMonth,31,23,59,59)))
def monthBefore(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire month before a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=monthRange(when).fromTime()
    elif isinstance(when,DateRange):
        when=monthRange(when).fromTime()
    return monthRange(when-datetime.timedelta(days=31))
def lastMonth()->DateRange:
    """
    return a range representing the entire last month
    """
    return monthRange(datetime.datetime.now()-datetime.timedelta(days=31))
def thisMonth()->DateRange:
    """
    return a range representing this entire month
    """
    return monthRange()
def nextMonth()->DateRange:
    """
    return a range representing the entire next month
    """
    return monthRange(datetime.datetime.now()+datetime.timedelta(days=31))
def monthAfter(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire month after a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=monthRange(when).toTime()
    elif isinstance(when,DateRange):
        when=monthRange(when).toTime()
    return monthRange(when+datetime.timedelta(days=31))

def oneWeek()->datetime.timedelta:
    """
    a timedelta representing one entire week
    """
    return datetime.timedelta(days=7)
def _datetimeOfWeekNumber(weekNum:int,year:typing.Optional[int]=None):
    """
    get a datetime from a week number
    """
    if year is None:
        year=datetime.datetime.now().year
    firstDayOfYear=datetime.datetime(year,1,1)
    return firstDayOfYear+datetime.timedelta(
        weeks=weekNum-1,days=-firstDayOfYear.weekday())
def weekRange(
    fromWeek:typing.Union[int,None,datetime.datetime]=None,
    toWeek:typing.Union[int,None,datetime.datetime]=None)->DateRange:
    """
    Get a range representing the entire week(s) for the date(s)
    That is, from Sunday 1:00:00AM - Saturday 12:59:59PM

    :fromWeek: if not specified, use this month
    :toWeek: if not specified, use fromDay
    """
    if fromWeek is None:
        fromWeek=datetime.datetime.now()
    elif not isinstance(fromWeek,datetime.datetime):
        fromWeek=_datetimeOfWeekNumber(fromWeek)
    if toWeek is None:
        toWeek=fromWeek
    elif not isinstance(toWeek,datetime.datetime):
        toWeek=_datetimeOfWeekNumber(fromWeek)
    # fromWeek,toWeek are now always a datetime
    start=(fromWeek-datetime.timedelta(days=fromWeek.weekday(),
        hours=fromWeek.hour,
        minutes=fromWeek.minute,
        seconds=fromWeek.second,
        microseconds=fromWeek.microsecond))
    end=(toWeek-datetime.timedelta(days=toWeek.weekday(),
        hours=toWeek.hour,
        minutes=toWeek.minute,
        seconds=toWeek.second,
        microseconds=toWeek.microsecond))\
        +oneWeek()-datetime.timedelta(microseconds=1)
    return DateRange((start,end))
def weekBefore(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire week before a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=weekRange(when).fromTime()
    elif isinstance(when,DateRange):
        when=weekRange(when).fromTime()
    return weekRange(when-datetime.timedelta(days=7))
def lastWeek()->DateRange:
    """
    return a range representing the entire last week
    """
    return weekRange(datetime.datetime.now()-datetime.timedelta(days=7))
def thisWeek()->DateRange:
    """
    return a range representing this entire week
    """
    return weekRange()
def nextWeek()->DateRange:
    """
    return a range representing the entire next week
    """
    return weekRange(datetime.datetime.now()+datetime.timedelta(days=31))
def weekAfter(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire week after a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=weekRange(when).toTime()
    elif isinstance(when,DateRange):
        when=weekRange(when).toTime()
    return weekRange(when+datetime.timedelta(days=7))

def dayRange(
    fromDay:typing.Union[int,None,datetime.datetime]=None,
    toDay:typing.Union[int,None,datetime.datetime]=None)->DateRange:
    """
    Get a range representing the entire day(s) for the date(s)
    That is, from 1:00:00AM - 12:59:59PM

    :fromDay: if not specified, use today
    :toDay: if not specified, use fromDay
    """
    if fromDay is None:
        now=datetime.datetime.now()
        fromYear=now.year
        fromMonth=now.month
        fromDay=now.day
    elif isinstance(fromDay,datetime.datetime):
        fromYear=fromDay.year
        fromMonth=fromDay.month
        fromDay=fromDay.day
    else:
        now=datetime.datetime.now()
        fromYear=now.year
        fromMonth=now.month
    if toDay is None:
        toYear=fromYear
        toMonth=fromMonth
        toDay=fromDay
    elif isinstance(fromDay,datetime.datetime):
        fromDay=fromDay.year
        toMonth=fromDay.month
        toDay=fromDay.day
    else:
        toYear=fromYear
        toMonth=fromMonth
    return DateRange(
        (datetime.datetime(fromYear,fromMonth,fromDay,0,0,0),
        datetime.datetime(toYear,toMonth,toDay,23,59,59)))
def dayBefore(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire day before a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=dayRange(when).fromTime()
    elif isinstance(when,DateRange):
        when=dayRange(when).fromTime()
    return dayRange(when-datetime.timedelta(days=1))
def yesterday()->DateRange:
    """
    return a range representing the entire day yesterday
    """
    return dayRange(datetime.datetime.now()-datetime.timedelta(days=1))
def today()->DateRange:
    """
    return a range representing the entire day today
    """
    return dayRange()
def tomorrow()->DateRange:
    """
    return a range representing the entire day tomorrow
    """
    return dayRange(datetime.datetime.now()+datetime.timedelta(days=1))
def dayAfter(
    when:typing.Union[None,int,datetime.datetime,"DateRange"]=None
    )->DateRange:
    """
    return a range representing the entire day after a given date
    """
    if when is None:
        when=datetime.datetime.now()
    elif isinstance(when,int):
        when=dayRange(when).toTime()
    elif isinstance(when,DateRange):
        when=dayRange(when).toTime()
    return dayRange(when+datetime.timedelta(days=1))
