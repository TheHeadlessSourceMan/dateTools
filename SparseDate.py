#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This is a utility class for a incrementable date object that
allows skipping over certain weekdays, holidays, and
user-specified days.

Written by K.C. Eilander
"""
import typing
import datetime


class SparseDate:
    """
    This is a utility class for a incrementable date object that
    allows skipping over certain weekdays, holidays, and
    user-specified days.
    """

    if typing.TYPE_CHECKING:
        from .timedelta import TimeDeltaCompatible

    def __init__(self,
        startDate:typing.Union[None,datetime.date,datetime.datetime]=None,
        skipWeekdays:typing.Iterable[int]=(5,6),
        daysOff:str="national",
        holidays:typing.Optional[typing.Iterable[datetime.date]]=None):
        """
        :param skipWeekdays: each day in this list will be skipped
            (where 0=Monday and 6=Sunday) default=weekends.
        """
        from dateTools.holidays import Holidays
        self.currentDate:typing.Optional[datetime.date]=None
        if skipWeekdays is None:
            skipWeekdays=[]
        self.skipWeekdays:typing.List[int]=list(skipWeekdays)
        self.daysOff:str=daysOff
        if holidays is None:
            holidays=Holidays() # default is holidays for our locale
        elif isinstance(holidays,str):
            holidays=Holidays(holidays) # load a specified holidays list
        self.holidays:typing.Optional[typing.Iterable[datetime.date]]=holidays
        self.setStartDate(startDate)

    def setStartDate(self,
        startDate:typing.Union[None,str,datetime.date,"SparseDate"],
        reset:bool=True
        )->None:
        """
        assign the start date
        """
        if startDate is None:
            self.startDate=datetime.date.today()
        elif isinstance(startDate,str):
            self.startDate=datetime.date.format(startDate)
        elif startDate.__class__ ==SparseDate:
            self.startDate=startDate.currentDate
        elif startDate.__class__ ==datetime.date:
            self.startDate=startDate
        else:
            self.startDate=datetime.date.today()
        if reset:
            self.reset()
        else:
            self.__nextValid__()

    def getDayOfWeekRegexString(self)->str:
        """
        returns a regex string that will get all weekdays or abbreviations and return
        group(1)=full name of week day

        It is recommended you use this with re.IGNORECASE.
        """
        return ''.join([
            r'(?:\s+(',
            r'(?:m(?:o(?:n(?:day)?)?)?)|',
            r'(?:t(?:u(?:e(?:s(?:day)?)?)?)?)|',
            r'(?:w(?:e(?:d(?:nesday)?)?)?)|',
            r'(?:th(?:u(?:r(?:s(?:day)?)?)?)?)|',
            r'(?:f(?:r(?:i(?:day)?)?)?)|',
            r'(?:s(?:a(?:t(?:urday)?)?)?)|',
            r'(?:su(?:n(?:day)?)?)',
            r')\s+)'])

    def setByStory(self,story:str)->None:
        """
        This can configure the object to match a user-readable story.  Examples:
           "every day except saturday"
           "every week day except bank holidays and every third wednesday"
           "every day except christmas, easter, the new moon, and every other friday starting today"

        TODO: this is currently experemental!
        """
        import re
        from .seasons._seasonsBase import ordinalIndicatorsRegexText
        exceptions=''
        counts=['other','odd','even']
        named_days=['christmas','easter',r'(?:(?:bank\s+)|(?:(?:major\s+)?us\s+))?holiday']
        sep=r"""(?:\s|[,]|and)+"""
        regexParts=['?:every',
            '|'.join(counts),
            ordinalIndicatorsRegexText,
            '('+self.getDayOfWeekRegexString()+'|'+'|'.join(named_days)+')(e?s)?',
            r"""(?P<day>\s+)?of\s+the\s+month""",
            r"""starting(?:\s+(?:at|on\s+))?\s+(.*?)"""
            ]
        regex='('+(sep+')?\n(').join(regexParts)+')?\n'
        #print(regex)
        regex=re.compile(regex,re.DOTALL|re.IGNORECASE)
        story=story.split('except')
        rules=story[0]
        if len(story)>1:
            exceptions=story[1]
        # TODO: decode both the rules and the exceptions

    def reset(self)->None:
        """
        reset the date
        """
        self.currentDate=self.startDate
        self.__nextValid__()

    def __nextValid__(self)->datetime.date:
        """
        get the next valid date
        """
        while True:
            if self.currentDate.weekday() in self.skipWeekdays:
                pass
            elif self.currentDate in self.holidays:
                pass
            elif self.holidays.isHoliday(self.currentDate,self.daysOff):
                pass
            else:
                return
            self.currentDate=self.currentDate+datetime.timedelta(days=1)

    def __repr__(self)->str:
        """
        string representation of this object
        """
        return str(self.currentDate)

    def __int__(self)->int:
        """
        int representation of this object
        """
        return int(self.currentDate)

    def __sub__(self,
        somethingElse:"TimeDeltaCompatible"
        )->None:
        """
        subtraction operator
        """
        for _ in somethingElse:
            self.currentDate=self.currentDate-datetime.timedelta(days=1)
            if self.currentDate<self.startDate:
                self.currentDate=self.startDate
                break
        self.__nextValid__()
        return self.currentDate

    def __add__(self,
        somethingElse:"TimeDeltaCompatible"
        )->None:
        """
        addition operator
        """
        for _ in somethingElse:
            self.currentDate=self.currentDate+datetime.timedelta(days=1)
            self.__nextValid__()
        return self

    def __cmp__(self,
        somethingElse:"TimeDeltaCompatible"
        )->int:
        """
        comparison operator
        """
        numDays=0
        somethingElse=int(somethingElse)
        if somethingElse>self.currentDate:
            inc=SparseDate(self.currentDate,self.skipWeekdays,self.daysOff,self.holidays)
            while inc.currentDate<somethingElse:
                inc=inc+1
                numDays=numDays-1
        elif somethingElse<self.currentDate:
            inc=SparseDate(somethingElse,self.skipWeekdays,self.daysOff,self.holidays)
            while inc.currentDate<self.currentDate:
                inc=inc+1
                numDays=numDays+1
        return numDays