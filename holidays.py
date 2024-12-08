#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program allows opening lists of holidays and then
selectively testing whether a given date is a holiday/day off
"""
import typing
import os
import re
import datetime
from paths import URLCompatible
from jsonSerializeable import JsonSerializeable
from dateTools import DateRange


HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep


class Holiday(JsonSerializeable):
    """
    A single holiday
    """

    def __init__(self,
        name:str,
        match:typing.Optional[typing.Pattern]=None,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None):
        """ """
        self._name:str=name
        self._match:typing.Optional[typing.Pattern]=None
        self._matchre:typing.Optional[typing.Pattern]=None
        self.match:typing.Optional[typing.Pattern]=match # forces re compile
        self.date:typing.Optional[DateRange]=None
        if date is not None:
            self.date=DateRange(date)
        self.dayOff:typing.Optional[str]=dayOff
        JsonSerializeable.__init__(self)

    @property
    def jsonObj(self)->typing.Dict[str,typing.Any]:
        """
        a json-compatible dict
        """
        ret={}
        if self.match is not None:
            ret['match']=self.match
        if self.date is not None:
            ret['date']=self.date.jsonObj
        if self.dayOff is not None:
            ret['dayOff']=self.dayOff
        return ret
    @jsonObj.setter
    def jsonObj(self,jsonObj:typing.Dict[str,typing.Any]):
        self.match=jsonObj.get('match')
        self.date=jsonObj.get('date')
        if self.date is not None:
            self.date=DateRange(jsonObj=self.date)
        self.dayOff=jsonObj.get('dayOff')

    @property
    def name(self)->str:
        """
        Name of this holiday
        """
        return self._name
    @name.setter
    def name(self,name:str):
        self._name=name
        if self.match is None:
            self._matchre=re.escape(name).replace('\\\\s','\\s')

    @property
    def match(self)->typing.Optional[typing.Pattern]:
        """
        the match string or None
        """
        return self._match
    @match.setter
    def match(self,match:typing.Optional[typing.Pattern]):
        self._match=match
        if match is None:
            self.name=self.name
        else:
            self._matchre=self._matchre=re.compile(match,re.IGNORECASE)

    def matchesName(self,name:str)->bool:
        """
        returns True if the name passed in is the name of this holiday

        (uses more sophisticated matching than name==self.name)
        """
        return self.match.matches(name)

    def isHoliday(self,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None
        )->bool:
        """
        :property date: if None, use now()
        :property dayOff: limit to holidays that are this kind of day off
            ("national","bank")

        returns what holiday the date is, or None
            if it is not a holiday
        """
        if date is None:
            date=datetime.datetime.now()
        if date in self.date:
            if self.dayOff=="national" or dayOff is None:
                return True
            if dayOff=="bank" and self.dayOff=="bank":
                return True
        return False

    def next(self,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None
        )->typing.Optional[datetime.date]:
        """
        get the date of the next occourance of this holiday from the given date

        :property date: if None, use now()
        :property dayOff: limit to holidays that are this kind of day off
            ("national","bank")

        returns the next time this happens (could be now)
            None if this is not that kind of day off
        """
        if dayOff is not None:
            if dayOff=="national" and self.dayOff!="national":
                return None
            if self.dayOff is None:
                return None
        if self.date is None:
            return None
        return self.date.next(date)

    def __repr__(self)->str:
        return self.name


class Holidays(JsonSerializeable):
    """
    This program allows opening lists of holidays and then selectively
    testing whether a given date is a holiday/day off

    See also:
        http://en.wikipedia.org/wiki/Public_holidays_in_the_United_States
    and
        http://en.wikipedia.org/wiki/Federal_holidays_in_the_United_States
    """

    def __init__(self,
        filename:typing.Optional[URLCompatible]=None):
        """ """
        if filename is None:
            import locale
            currentLocale=locale.getdefaultlocale()
            if currentLocale is None:
                raise Exception("Unable to determine locale")
            localeString=currentLocale[0].lower().replace('_','-')
            filename='%sholidays%sholidays_%s.json'%(HERE,os.sep,localeString)
        self.holidays:typing.Dict[str,Holiday]={}
        JsonSerializeable.__init__(self,filename)

    @property
    def jsonObj(self)->typing.Dict[str,typing.Any]:
        """
        this object as a json-compatible dict
        """
        ret={}
        for holiday in self.holidays.values():
            ret[holiday.name]=holiday.jsonObj
        return ret
    @jsonObj.setter
    def jsonObj(self,jsonObj:typing.Dict[str,typing.Any]):
        for name,holiday in jsonObj.items():
            holiday=Holiday(name,**holiday)
            self.holidays[name]=holiday

    def isHoliday(self,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None
        )->typing.Optional[Holiday]:
        """
        :property date: if None, use now()
        :property dayOff: limit to holidays that are this kind of day off
            ("national","bank")

        returns what holiday the date is, or None
            if it is not a holiday
        """
        if date is None:
            date=datetime.datetime.now()
        for h in self.holidays.values():
            if h.isHoliday(date,dayOff):
                return h
        return None

    def nextHolidays(self,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None
        )->typing.Iterable[typing.Tuple[datetime.date,str]]:
        """
        gets the next occourance of all holidays (in order)

        :property date: if None, use now()
        :property dayOff: limit to holidays that are this kind of day off
            ("national","bank")

        returns [(date,holiday)]
        """
        if not self.holidays:
            return []
        if date is None:
            date=datetime.datetime.now()
        nextHolidays=[]
        for h in self.holidays.values():
            nextDate=h.next(date,dayOff)
            if nextDate is not None:
                nextHolidays.append((nextDate,h))
        nextHolidays.sort()
        return nextHolidays

    def nextHoliday(self,
        date:typing.Optional[datetime.date]=None,
        dayOff:typing.Optional[str]=None
        )->Holiday:
        """
        gets the next holiday (of dayOff type)

        :property date: if None, use now()
        :property dayOff: limit to holidays that are this kind of day off
            ("national","bank")
        """
        return self.nextHolidays(date,dayOff)[0][1]

    def __repr__(self)->str:
        """
        string representaiton of this object
        """
        ret=['Holidays:']
        for h in self.holidays.values():
            ret.append('%s (%s)'%(str(h),h.date))
        return '\n   '.join(ret)


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        holidays=Holidays()
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0] in ['--ls','--list']:
                    print(holidays)
                elif arg[0]=='--nextHoliday':
                    print('The next holiday is: %s'%holidays.nextHoliday())
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                holidays.load(arg)
    if printhelp:
        print('Usage:')
        print('  holidays.py [holidays_list.json] [options]')
        print('Options:')
        print('   --ls ................ list all holidays')
        print('   --list .............. list all holidays')
        print('   --nextHoliday ....... what is the next holiday?')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
