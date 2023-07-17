#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This tool allows dates formatted like "mon 8:00-8:30AM,tue-sat 1:00-5:00PM"
"""
import typing
import datetime
import re
from rangeTools import Range
from paths import URLCompatible
from jsonSerializeable import JsonSerializeable
from rangeTools import Range,Ranges
import dateTools.miscFunctions as miscFunctions
from .calendarNames import *


RangeIndicatorReText=r"""(\s*(-|to|till|until|through)\s*)"""


ComparableDatetimeCompatible=typing.Union[datetime.datetime,int,float,"ComparableDatetime"]
ComparableDateTimeCompatible=ComparableDatetimeCompatible
def asComparableDatetime(cdt:ComparableDatetimeCompatible)->"ComparableDatetime":
    if isinstance(cdt,ComparableDatetime):
        return cdt
    return ComparableDatetime(cdt)
asComparableDateTime=asComparableDatetime

class ComparableDatetime:
    def __init__(self,cdt:ComparableDatetimeCompatible):
        if isinstance(cdt,(int,float)):
            cdt=datetime.datetime.fromtimestamp(cdt)
        elif isinstance(cdt,ComparableDatetime):
            cdt=cdt.datetime
        self.datetime:datetime.datetime=cdt

    @property
    def timestamp(self)->float:
        return datetime.datetime.timestamp(self.datetime)
    @timestamp.setter
    def timestamp(self,timestamp:float):
        self.datetime=datetime.datetime.fromtimestamp(timestamp)

    def __sub__(self,other:typing.Any)->"ComparableDatetime":
        return ComparableDatetime(self.timestamp-asComparableDatetime(other).timestamp)
    def __add__(self,other:typing.Any)->"ComparableDatetime":
        return ComparableDatetime(self.timestamp+asComparableDatetime(other).timestamp)
    def __mul__(self,other:typing.Any)->"ComparableDatetime":
        return ComparableDatetime(self.timestamp*asComparableDatetime(other).timestamp)
    def __truediv__(self,other:typing.Any)->"ComparableDatetime":
        return ComparableDatetime(self.timestamp/asComparableDatetime(other).timestamp)
    def __floordiv__(self,other:typing.Any)->"ComparableDatetime":
        return ComparableDatetime(self.timestamp//asComparableDatetime(other).timestamp)
    def __lt__(self, other:typing.Any) -> bool:
        return self.timestamp<asComparableDatetime(other).timestamp
    def __gt__(self, other:typing.Any) -> bool:
        return self.timestamp>asComparableDatetime(other).timestamp
    def __le__(self, other:typing.Any) -> bool:
        return self.timestamp<=asComparableDatetime(other).timestamp
    def __ge__(self, other:typing.Any) -> bool:
        return self.timestamp>=asComparableDatetime(other).timestamp

    def __repr__(self) -> str:
        return str(self.datetime)
ComparableDateTime=ComparableDatetime


DateRangeSimpleCompatible=typing.Union[ComparableDatetime,typing.Tuple[ComparableDatetime,ComparableDatetime],"DateRangeSimple"]
def asDateRangeSimple(dateRange:DateRangeSimpleCompatible)->"DateRangeSimple":
    if isinstance(dateRange,DateRangeSimple):
        return dateRange
    if isinstance(dateRange,tuple):
        return DateRangeSimple(dateRange[0],dateRange[1])
    return DateRangeSimple(dateRange)

class DateRangeSimple(Range[ComparableDatetime,DateRangeSimpleCompatible]):
    """
    TODO: merge with DateRange below
    """

    def __init__(self,
        low:typing.Union[ComparableDatetimeCompatible,typing.Tuple[ComparableDatetimeCompatible,ComparableDatetimeCompatible]],
        high:typing.Optional[ComparableDatetimeCompatible]=None,
        step:typing.Optional[ComparableDatetimeCompatible]=None,
        center:typing.Optional[ComparableDatetimeCompatible]=None,
        lowInclusive:bool=True,
        highInclusive:bool=False):
        """
        :low: the low value of the range
        :high: the high value of the range (if None, same as low)
        :lowInclusive: is comparison >low or >=low
        :highInclusive: is comparison <high or <=high
        """
        Range.__init__(self,low,high,step,center,lowInclusive,highInclusive,ComparableDatetime)

class DateRange(JsonSerializeable,Range[datetime.datetime]):
    """
    This tool allows dates formatted like:
        "tue-sat from 1:00 to 5:00PM"
        "1:00-5:00PM"
        "tuesdays"
        "every dec 25 at 12:00AM"

    TODO: once Range class is working, extend that!
    """

    DECODER:typing.Optional[typing.Pattern]=None
    def _CREATE_DECODER(self)->typing.Pattern:
        weekdays='('+('|'.join(WeekdayAbbrs))+')[a-z]*'
        months='('+('|'.join(MonthAbbrs))+')[a-z]*'
        time=r'[0-9]{1,2}:[0-9]{2}\s*(am|pm)?'
        rangeIndicator=RangeIndicatorReText+'?'
        monthday=miscFunctions.reWithoutNames(miscFunctions.numberDetectRe())
        regex=r"""
            (each|every|from|\s)*
            (
                (?P<weekday>"""+weekdays+r""")
                ("""+rangeIndicator+r"""(?P<toWeekday>"""+weekdays+r"""))?
            )?
            (in|from|\s)*
            (
                (?P<month>"""+months+r""")
                    (?P<monthDay>"""+monthday+r""")?
                ("""+rangeIndicator+r"""(?P<toMonth>"""+months+r""")
                    (?P<toMonthDay>"""+monthday+r""")?
                )?
            )?
            (from|at|\s)*
            (
                (?P<time>"""+time+r""")?
                ("""+rangeIndicator+r"""(?P<toTime>"""+time+"""))?
            )?"""
        #print(regex)
        self.DECODER=re.compile(regex.replace('\n','').replace(' ',''),re.IGNORECASE)
        return self.DECODER

    def __init__(self,
        rangestring:typing.Union[None,str]=None,
        filename:typing.Optional[URLCompatible]=None,
        jsonObj:typing.Union[str,typing.Dict,None]=None):
        """ """
        if self.DECODER is None:
            self._CREATE_DECODER()
        # these will be set to defaults by self.assign() caling self.reset()
        self.month=None
        self.toMonth=None
        self.monthDay=None
        self.toMonthDay=None
        self.weekday=None
        self.toWeekday=None
        self._time=None
        self._toTime=None
        self.timeFormat="%I:%M%p"
        JsonSerializeable.__init__(self,filename,jsonObj)
        Range[datetime.datetime].__init__(self,rangestring)
        if rangestring is not None:
            self.assign(rangestring)

    def clear(self)->None:
        """
        same as reset
        """
        self.reset()
    def reset(self)->None:
        """
        reset back to defaults
        (accept every time)
        """
        self.month=1 # unlike datetime, we start with day 1
        self.toMonth=12
        self.monthDay=1 # unlike datetime, we start with day 1
        self.toMonthDay=32 # This is allowed to be higher than the moth can handle
        self.weekday=0 # 0=Sunday,1=Monday, etc
        self.toWeekday=6
        self.time=datetime.time.min
        self.toTime=datetime.time.max

    @property
    def time(self)->datetime.time:
        """
        the starting time
        """
        if self._time is None:
            if self._toTime is None:
                return datetime.datetime.now().time()
            return self._toTime
        return self._time
    @time.setter
    def time(self,time:datetime.time):
        self._time=miscFunctions.toTime(time)

    @property
    def toTime(self)->datetime.time:
        """
        the ending time
        """
        return self._toTime
    @toTime.setter
    def toTime(self,toTime:datetime.time):
        self._toTime=miscFunctions.toTime(toTime)

    @property
    def jsonObj(self)->typing.Dict[str,typing.Any]:
        """
        this object as a json dict

        it can also be assigned to json string, which will go through assign() instead
        """
        ret={}
        if self.month>1 or self.toMonth<12:
            ret['month']=self.monthName
            if self.toMonth!=self.month:
                ret['toMonth']=self.toMonthName
            if self.month>1 or self.toMonthDay<31:
                ret['monthDay']=self.monthDay
                if self.toMonthDay!=self.monthDay:
                    ret['toMonthDay']=self.toMonthDay
        if self.weekday>0 or self.toWeekday<6:
            ret['weekday']=self.weekdayName
            if self.toWeekday!=self.weekday:
                ret['toWeekday']=self.toWeekdayName
        if self.time!=datetime.time.min or self.toTime!=datetime.time.max:
            ret['time']=self.time.strftime('%I:%M%p')
            if self.toTime!=self.time:
                ret['toTime']=self.toTime.strftime('%I:%M%p')
        return ret
    @jsonObj.setter
    def jsonObj(self,jsonObj:typing.Union[str,typing.Dict[str,typing.Any]]):
        """
        it can also be a json string, which will go through assign() instead
        """
        self.clear()
        if isinstance(jsonObj,str):
            self.assign(jsonObj)
            return
        for k,v in jsonObj:
            if k in ('month','toMonth','weekday','toWeekday'):
                setattr(self,k+'Name',v)
            elif k in ('monthDay','toMonthDay','time','toTime'):
                setattr(self,k,v)
            else:
                raise Exception('unknown field "%s"'%k)

    def assign(self,rangestring:str)->None:
        """
        assign the value of this date range
        """
        self.reset()
        m=self.DECODER.match(rangestring)
        if m is None:
            raise Exception('ERR: unable to decode date range "'+rangestring+'"')
        # decode months
        month=m.group('month')
        if month is not None:
            self.month=self.MONTHLIST.index(month[0:3].lower())+1
            monthDay=m.group('monthDay')
            if monthDay is not None:
                self.monthDay=int(miscFunctions.numberdecode(monthDay))
                self.toMonthDay=self.monthDay
            toMonth=m.group('toMonth')
            if toMonth is None:
                self.toMonth=self.month
            else:
                self.toMonth=self.MONTHLIST.index(toMonth[0:3].lower())
                toMonthDay=m.group('toMonthDay')
                if toMonthDay is not None:
                    self.toMonthDay=int(miscFunctions.numberdecode(toMonthDay))
        # decode days
        weekday=m.group('weekday')
        if weekday is not None:
            self.weekday=WeekdayAbbrs.index(weekday[0:2].lower())
            toWeekday=m.group('toWeekday')
            if toWeekday is None:
                self.toWeekday=self.weekday
            else:
                self.toWeekday=WeekdayAbbrs.index(toWeekday[0:2].lower())
        # decode times
        time=m.group('time')
        if time is not None:
            self.time=time
            toTime=m.group('toTime')
            if toTime is None:
                self.toTime=time
            else:
                self.toTime=toTime

    def next(self,
        afterDate:typing.Optional[datetime.date]=None
        )->datetime.date:
        """
        next occourance from the given date

        :property fromDate: if None, use now()

        returns a datetime object or None

        TODO: this is not working
        """
        if afterDate is None:
            afterDate=datetime.datetime.now()
        startDay=afterDate.weekday()
        onDay=startDay
        while True:
            if self.weekday<=onDay<=self.toWeekday:
                if onDay==startDay:
                    if afterDate.time()<=self.toTime:
                        if afterDate.time()>=self.time:
                            return afterDate # do it now!
                         # do it today, but awhile later
                        return datetime.datetime.combine(afterDate.date(),self.time)
                else:
                    nextDate=afterDate.date()
                    numdays=onDay-startDay
                    if numdays<0:
                        numdays+=7
                    nextDate=nextDate+datetime.timedelta(days=numdays)
                    return datetime.datetime.combine(nextDate,self.time)
            onDay=(onDay+1)%7 # try the next day
            if onDay==startDay: # we have checked every day
                break
        return None

    def timeUntilNext(self,
        fromDate:typing.Optional[datetime.date]=None,
        inUnits:typing.Optional[str]=None
        )->float:
        """
        how long until next occourance from the given date

        :property fromDate: if None, use now()
        :property inUnits: can be 'days', 'hours', 'minutes', 'seconds',
            or 'hms' for string format like "5h 3m 21s"
            (string format is very forgiving - anything that starts with 'd','h','m','s')
            if None, returns a datetime.timedelta

        returns how long until the next event
        """
        if fromDate is None:
            fromDate=datetime.datetime.now()
        nextInstance=self.next(fromDate)
        howLong=nextInstance-fromDate
        return miscFunctions.timeDeltaInUnits(howLong,inUnits)

    @property
    def weekdayName(self)->str:
        """
        name of the from weekday
        """
        return WeekdayAbbrs[self.weekday]
    @property
    def toWeekdayName(self)->str:
        """
        name of the to weekday
        """
        return WeekdayAbbrs[self.toWeekday]

    @property
    def monthName(self)->str:
        """
        name of the from month
        """
        return self.MONTHLIST[self.month-1]
    @property
    def toMonthName(self)->str:
        """
        name of the to month
        """
        return self.MONTHLIST[self.toMonth-1]

    @property
    def text(self)->str:
        """
        string representation of this object
        (setting this is the same as assign())
        """
        ret=[]
        ret.append(self.weekdayName)
        if self.weekday!=self.toWeekday:
            ret.append('..')
            ret.append(self.toWeekdayName)
        ret.append(' ')
        ret.append(self.time.strftime(self.timeFormat))
        if self.time!=self.toTime:
            ret.append('..')
            ret.append(self.toTime.strftime(self.timeFormat))
        return ''.join(ret)
    @text.setter
    def text(self,text:str):
        self.assign(text)

    @property
    def duration(self)->datetime.timedelta:
        return self.end-self.start
    @property
    def hours(self)->float:
        """
        total duration as hours

        :return: _description_
        :rtype: float
        """
        return self.duration.total_seconds()/(60*60)

    def __repr__(self)->str:
        """
        string representation of this object
        """
        return self.text
DatetimeRange=DateRange

class DateRanges(JsonSerializeable,Ranges):
    """
    A set of date range objects.

    This tool allows dates formatted like "mon 8:00-8:30AM,tue-sat 1:00-5:00PM"

    TODO: once Rangea class is working, extend that!
    """

    def __init__(self,
        rangestring:typing.Optional[str]=None,
        filename:typing.Optional[URLCompatible]=None,
        jsonObj:typing.Union[None,str,typing.Dict[str,typing.Any]]=None):
        """ """
        self.dateRanges:typing.List[DateRange]=[]
        Ranges.__init__(self)
        JsonSerializeable.__init__(self,filename,jsonObj)
        if rangestring:
            self.assign(rangestring)

    @property
    def jsonObj(self)->typing.Dict[str,typing.Any]:
        """
        this object as a json-compatible object
        """
        return [dr.jsonObj for dr in self.dateRanges]
    @jsonObj.setter
    def jsonObj(self,jsonObj:typing.Union[None,str,typing.Dict[str,typing.Any]]):
        """
        it can also be a json string, which will go through assign() instead
        """
        if isinstance(jsonObj,str):
            self.assign(jsonObj)
        self.dateRanges=[DateRange(jsonObj=o) for o in jsonObj]

    def assign(self,rangestring:str)->None:
        """
        assign the values of these date ranges
        """
        self.dateRanges=[DateRange(dr) for dr in rangestring.split(',')]

    def timeUntilNext(self,
        fromDate:typing.Optional[datetime.date]=None,
        inUnits:typing.Optional[str]=None
        )->float:
        """
        how long until next occourance from the given date

        :property fromDate: if None, use now()
        :property inUnits: can be 'days', 'hours', 'minutes', 'seconds',
            or 'hms' for string format like "5h 3m 21s"
            (string format is very forgiving - anything that starts with 'd','h','m','s')
            if None, returns a datetime.timedelta

        returns how long until the next event
        """
        if fromDate is None:
            fromDate=datetime.datetime.now()
        nextInstance=self.next(fromDate)
        howLong=nextInstance-fromDate
        return miscFunctions.timeDeltaInUnits(howLong,inUnits)

    def next(self,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.date:
        """
        next occourance from the given date

        :property fromDate: if None, use now()

        returns a datetime object or None
        """
        if fromDate is None:
            fromDate=datetime.datetime.now()
        smallest=None
        for dr in self.dateRanges:
            nocc=dr.next(fromDate)
            if smallest is None or nocc<smallest:
                smallest=nocc
        return smallest

    @property
    def text(self)->str:
        """
        string representation of this object
        (setting this is the same as assign())
        """
        return ', '.join([dr.text for dr in self.dateRanges])
    @text.setter
    def text(self,text:str):
        self.assign(text)

    def __repr__(self)->str:
        """
        string representation of this object
        """
        return self.text


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        dr=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--next':
                    print(dr.next())
                elif arg[0]=='--json':
                    print(dr.json)
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                dr=DateRanges(arg)
    if printhelp:
        print('Usage:')
        print('  dateRanges.py dateranges [options]')
        print('Options:')
        print('   --next ........... get next occourance of the date ranges')


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])