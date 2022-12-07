#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program calculates lunar times
(requires the skyfield astronomy library)
"""
import typing
import datetime

from miscFunctions import findDay
try:
    import skyfield.almanac
    import skyfield.api
    import skyfield.timelib
    def skyfieldCheck():
        """
        check skyfield validity
        """
        return True
except ImportError as e:
    showedSkyfieldWarning=False
    skyfieldError=str(e)
    showedSkyfieldWarning=False
    def skyfieldCheck():
        """
        check skyfield validity
        """
        if not showedSkyfieldWarning:
            showedSkyfieldWarning=True
            msg='WARN: This function requires the skyfield astronomical library\n\
                install via:\n\
                    pip install skyfield'
            print(skyfieldError)
            print()
            print(msg)
        return False
from dateTools import FuzzyTime


class LunarTimes:
    """
    This program calculates lunar times

    (requires the skyfield astronomy library)

    See also:
        https://rhodesmill.org/skyfield/api.html
        https://rhodesmill.org/skyfield/planets.html
    """

    _ephemeris=None

    def __init__(self):
        pass

    @property
    def ephemeris(self):
        """
        Get the ephemeris tables for calculating lunar time
        """
        if self._ephemeris is None:
            self._ephemeris=skyfield.api.load('de440s.bsp')
        return self._ephemeris

    def _skyfieldTime(self,
        date:typing.Union[None,str,datetime.date,skyfield.timelib.Time]=None
        )->datetime.datetime:
        """
        always get a skyfield Time object

        :property date: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        if date is None:
            return self._skyfieldTime(datetime.datetime.now())
        if isinstance(date,skyfield.timelib.Time):
            return date
        if isinstance(date,str):
            import fuzzytime
            date=fuzzytime.FuzzyTime(str).startTime
        # assume it is a datetime.datetime object by now
        # first, the datetime needs a timezone or we are dead meat
        if date.tzinfo is None:
            # it doesn't have one, so assume the local system timezone
            date=date.astimezone()
        timescale=skyfield.api.load.timescale()
        return timescale.from_datetime(date)

    def phaseAngle(self,
        atDate:typing.Optional[datetime.date]=None
        )->typing.Optional[float]:
        """
        Get the lunar phase at a given date.

        :property atDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object

        return an angle in degrees (0=new,180=full)
        """
        if not skyfieldCheck():
            return None
        atDate=self._skyfieldTime(atDate)
        return skyfield.almanac.moon_phase(self.ephemeris,atDate).degrees

    def phase(self,
        atDate:typing.Optional[datetime.date]=None
        )->str:
        """
        Get the lunar phase at a given date.

        :property atDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object

        return what phase the moon is in 0-3
            corresponding to "new","waxing","full", or "waning"
            (see also phaseText() if you simply want this string)
        """
        angle=self.phaseAngle(atDate)
        if angle<45:
            return 0
        if angle<135:
            return 1
        if angle<225:
            return 2
        if angle<315:
            return 3
        return 0

    def phaseText(self,
        atDate:typing.Optional[datetime.date]=None
        )->str:
        """
        Get the lunar phase at a given date.

        :property atDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object

        return what phase the moon is in
            ("new","waxing","full", or "waning")
        """
        return ("new","waxing","full","waning")[self.phase(atDate)]

    def brightness(self,
        atDate:typing.Optional[datetime.date]=None
        )->float:
        """
        How full the moon is (and therefore how bright it is
        at night) at a given date.

        :property atDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object

        A percent between 0.0 and 1.0
        """
        return self.fullness(atDate)

    def fullness(self,
        atDate:typing.Optional[datetime.date]=None
        )->float:
        """
        How full the moon is (and therefore how bright it is
        at night) at a given date.

        :property atDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object

        A percent between 0.0 and 1.0
        """
        angle=self.phaseAngle(atDate)
        return abs(180-angle)/180.0

    def nextTimeLightIsGreaterThan(self,
        lightPercent:float=0.8,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        Useful if you are planning on doing things at night

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.fullness(day)>=lightPercent,False,fromDate)

    def nextTimeLightIsLessThan(self,
        lightPercent:float=0.2,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        Useful if you are planning on stargazing

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.fullness(day)<=lightPercent,False,fromDate)

    def nextFullMoon(self,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        returns when the next full moon is

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.phase(day)==2,False,fromDate)

    def previousFullMoon(self,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        returns when the previous full moon was

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.phase(day)==2,True,fromDate)

    def nextNewMoon(self,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        returns when the next new moon is

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.phase(day)==0,False,fromDate)

    def previousNewMoon(self,
        fromDate:typing.Optional[datetime.date]=None
        )->datetime.datetime:
        """
        returns when the previous new moon was

        :property fromDate: can be
            None (to get the present date/time)
            datetime.datetime object
            any string parseable by fuzzytime
            a proper skyfield Time object
        """
        return findDay(lambda day: self.phase(day)==0,True,fromDate)


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        lt=LunarTimes()
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--brightness':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.brightness(d))
                elif arg[0]=='--fullness':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.brightness(d))
                elif arg[0]=='--nextFullMoon':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.nextFullMoon(d))
                elif arg[0]=='--nextNewMoon':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.nextNewMoon(d))
                elif arg[0]=='--nextTimeLightIsGreaterThan':
                    d=None
                    percent=0.8
                    if len(arg)>1:
                        arg[1]=arg[1].split(',',1)
                        percent=float(arg[1][0])
                        if len(arg[1])>1:
                            d=FuzzyTime(arg[1][1])
                    print(lt.nextTimeLightIsGreaterThan(percent,d))
                elif arg[0]=='--nextTimeLightIsLessThan':
                    d=None
                    percent=0.2
                    if len(arg)>1:
                        arg[1]=arg[1].split(',',1)
                        percent=float(arg[1][0])
                        if len(arg[1])>1:
                            d=FuzzyTime(arg[1][1])
                    print(lt.nextTimeLightIsLessThan(percent,d))
                elif arg[0]=='--phase':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.phase(d))
                elif arg[0]=='--phaseAngle':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.phaseAngle(d))
                elif arg[0]=='--phaseText':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.phaseText(d))
                elif arg[0]=='--phaseText':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.previousFullMoon(d))
                elif arg[0]=='--previousNewMoon':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(lt.previousNewMoon(d))
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  solar.py [options]')
        print('Options:')
        print('   --brightness[=date] ........ %brightness of the moon')
        print('   --fullness[=date] .......... %fullness of the moon')
        print('   --nextFullMoon[=date] ...... when is the next full moon')
        print('   --nextNewMoon[=date] ....... when is the next full moon')
        print('   --nextTimeLightIsGreaterThan[=percent,date]')
        print('   ............................ get the next bright night')
        print('   --nextTimeLightIsLessThan[=percent,date]')
        print('   ............................ get the next dark night')
        print('   --phaseAngle[=date] ........ lunar phase in degrees (new=0 180=full)')
        print('   --phaseText[=date] ......... lunar phase text description')
        print('   --previousFullMoon[=date] .. when was the previous full moon')
        print('   --previousNewMoon[=date] ... when was the previous new moon')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
