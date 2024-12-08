#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This program calculates solar times
(requires the skyfield astronomy library)
"""
import typing
import datetime

showedSkyfieldWarning=False
skyfieldError=''
try:
    import skyfield.almanac
    import skyfield.api
    import skyfield.timelib
    def skyfieldCheck():
        """
        Dummied out function
        """
        return True
except ImportError as e:
    skyfieldError=str(e)
    def skyfieldCheck():
        """
        Check for the existance of the skyfield library
        """
        global showedSkyfieldWarning
        if not showedSkyfieldWarning:
            showedSkyfieldWarning=True
            msg='WARN: This requires the skyfield astronomical library\n\
            install via:\n\
                pip install skyfield'
            print(skyfieldError)
            print()
            print(msg)
        return False


class SolarTimes:
    """
    This program calculates solar times

    (requires the skyfield astronomy library)

    See also:
        https://rhodesmill.org/skyfield/api.html
        https://rhodesmill.org/skyfield/planets.html
    """

    def __init__(self,
        latlong:typing.Tuple[float,float],
        timezone:typing.Optional[str]=None):
        """
        if timezone is not specified, use the system timezone
        """
        self._ephemeris:typing.Optional[int]=None
        self.latlong:typing.Tuple[float,float]=latlong
        self.timezone:typing.Optional[str]=timezone

    @property
    def ephemeris(self):
        "the ephemeris table for calculating solar times"
        if self._ephemeris is None:
            self._ephemeris=skyfield.api.load('de440s.bsp')
        return self._ephemeris

    def _datetime(self,
        date:typing.Union[None,datetime.date,skyfield.timelib.Time,str]=None
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
            return datetime.datetime.now()
        if isinstance(date,skyfield.timelib.Time):
            return date.utc_datetime()
        if isinstance(date,str):
            import fuzzytime
            return fuzzytime.FuzzyTime(str).startTime
        return date

    def _skyfieldTime(self,
        date:typing.Union[None,datetime.date,skyfield.timelib.Time,str]=None
        )->skyfield.timelib.Time:
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

    def equinoxes(self,
        date:typing.Optional[datetime.date]=None,
        nextOccourance:bool=False
        )->typing.List[typing.Tuple[datetime.datetime,str]]:
        """
        get all the equinoxes/solstaces for the year of date

        :property nextOccourance: instead of all the events for this year,
            get all the events of the next year, starting with date

        returns [(eventDate,eventName)]
        """
        # get the start and end of the year
        timescale=skyfield.api.load.timescale()
        if nextOccourance:
            date=self._datetime(date)
            firstDay=timescale.utc(date.year,1,1)
            lastDay=timescale.utc(date.year,12,31)
        else:
            firstDay=self._skyfieldTime(date)
            # get one year from that
            lastDay=self._skyfieldTime(
                firstDay.utc_datetime()+datetime.timedelta(days=365))
        # get the events that occour durring that time
        times,events=skyfield.almanac.find_discrete(firstDay,lastDay,
            skyfield.almanac.seasons(self.ephemeris))
        # convert events to names and time to datetime
        ret=[]
        timezone=datetime.datetime.now().astimezone().tzinfo
        for i,time in enumerate(times):
            event=events[i]
            event=skyfield.almanac.SEASON_EVENTS[event]
            time=time.astimezone(timezone)
            ret.append((event,time))
        return ret

    def nextVernalEquinox(self,
        date:typing.Optional[datetime.date]=None
        )->typing.List[typing.Tuple[datetime.datetime,str]]:
        """
        get the date of the next vernal equinox
        """
        return self.equinoxes(date,True)[0][1]

    def nextAutumnalEquinox(self,
        date:typing.Optional[datetime.date]=None
        )->typing.List[typing.Tuple[datetime.datetime,str]]:
        """
        get the date of the next autumnal equinox
        """
        return self.equinoxes(date,True)[2][1]

    def nextWinterSolstice(self,
        date:typing.Optional[datetime.date]=None
        )->typing.List[typing.Tuple[datetime.datetime,str]]:
        """
        get the date of the next winter solstice
        """
        return self.equinoxes(date)[3][1]

    def nextSummerSolstice(self,
        date:typing.Optional[datetime.date]=None
        )->typing.List[typing.Tuple[datetime.datetime,str]]:
        """
        get the date of the next summer solstice
        """
        return self.equinoxes(date)[1][1]

    def allday(self,
        date:typing.Optional[datetime.date]=None
        )->typing.Tuple[datetime.time,datetime.time]:
        """
        convert a datetime to all day range

        TODO: should probably be moved to daterange
        """
        startTime=date-datetime.timedelta(
            hours=date.hour,minutes=date.minute,seconds=date.second)
        endTime=startTime+datetime.timedelta(hours=24)
        return (startTime,endTime)

    def sunriseSunset(self,
        date:typing.Optional[datetime.date]=None
        )->typing.Tuple[datetime.time,datetime.time]:
        """
        get the sunrise time

        :property date: if not specified, use now()
        """
        if not skyfieldCheck():
            return None
        date=self._datetime(date)
        dateRange=self.allday(date)
        location=skyfield.api.wgs84.latlon(self.latlong[0],self.latlong[1])
        startTime=self._skyfieldTime(dateRange[0])
        endTime=self._skyfieldTime(dateRange[1])
        finderFunction=skyfield.almanac.sunrise_sunset(self.ephemeris,location)
        ssTimes,ssTypes=skyfield.almanac.find_discrete(
            startTime,endTime,finderFunction)
        if ssTypes[0]==0:
            return (self._datetime(ssTimes[1]),self._datetime(ssTimes[0]))
        return (self._datetime(ssTimes[0]),self._datetime(ssTimes[1]))

    def sunrise(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.time:
        """
        get the sunrise time

        :property date: if not specified, use now()
        """
        return self.sunriseSunset(date)[0]

    def sunset(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.time:
        """
        get the sunset time

        :property date: if not specified, use now()
        """
        return self.sunriseSunset(date)[1]

    def dayLength(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.timedelta:
        """
        how long the day is

        :property date: if not specified, use now()
        """
        ss=self.sunriseSunset(date)
        return ss[1]-ss[0]

    def nightLength(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.timedelta:
        """
        how long the night is

        :property date: if not specified, use now()
        """
        return datetime.timedelta(hours=24)-self.dayLength(date)

    def solarNoon(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.time:
        """
        the time of solar noon (sun directly overhead)

        this is probably different than 12:00

        :property date: if not specified, use now()
        """
        ss=self.sunriseSunset(date)
        return ss[0]+(ss[1]-ss[0])/2

    def solarMidnight(self,
        date:typing.Optional[datetime.date]=None
        )->datetime.time:
        """
        the time of solar midnight (sun directly below feet)

        this is probably different than 12:00

        :property date: if not specified, use now()
        """
        return self.solarNoon(date)+datetime.timedelta(hours=12)

    def sunPath(self,
        date:typing.Optional[datetime.date]=None
        )->typing.List[datetime.time,float]:
        """
        returns a table of [(time,angle)] for every minute
        of the sun's path throughout the given day
        """
        oneMinute=datetime.timedelta(minutes=1)
        ss=self.sunriseSunset(date)
        t=ss[0]
        ret=[]
        while t<ss[1]:
            ret.append((t,self.angle(t)))
            t+=oneMinute
        return ret

    def sunPathCsv(self,
        date:typing.Optional[datetime.date]=None
        )->str:
        """
        same as sunPath, but returns a csv table
        """
        return self._pathToCsv(self.sunPath(date))

    def _pathToCsv(self,
        path:typing.Iterable[datetime.time,float]
        )->str:
        """
        convert a sun path to a csv file string
        """
        ret=["time,azimuth,elevation"]
        for date,angle in path:
            row=(date.astimezone().isoformat(),angle[0],angle[1])
            ret.append(','.join(row))
        return '\n'.join(ret)

    def getSolarProfile(self
        )->typing.Tuple[
            typing.List[typing.Tuple[datetime.time,float]],
            typing.List[typing.Tuple[datetime.time,float]],
            typing.List[typing.Tuple[datetime.time,float]]]:
        """
        gets a solar profile for this latitude
        returns (min,mid,max) paths
        """
        equinoxes=self.equinoxes()
        return (
            self.sunPath(equinoxes[1][1]),
            self.sunPath(equinoxes[2][1]),
            self.sunPath(equinoxes[3][1]))

    def getSolarProfileCsv(self
        )->typing.Tuple[
            str,
            str,
            str]:
        """
        gets a solar profile for this latitude
        returns (min,mid,max) path csv's
        """
        return [self._pathToCsv(x) for x in self.getSolarProfile()]

    def saveSolarProfile(self,directory:typing.Optional[str]=None)->None:
        """
        saves three path csv files for this latitude
            summer.csv, winter.csv, and middle.csv
        """
        import os
        if directory is None:
            directory=''
        elif directory[-1] not in ('/',os.sep):
            directory=directory+os.sep
        filenames=('summer.csv','middle.csv','winter.csv')
        data=self.getSolarProfileCsv()
        for i,filename in enumerate(filenames):
            f=open(directory+filename,'wb')
            f.write(data[i].encode('utf-8'))
            f.close()

    def angle(self,
        date:typing.Optional[datetime.datetime]=None
        )->float:
        """
        get the sun's angle at a given time

        :property date: if not specified, use now()

        returns (azimuth,elevation,distance)
            where distance is in au, which can be interpreted as a percent
        """
        date=self._skyfieldTime(date)
        # look at the sun (but don't hurt yourself ;) )
        ephem=self.ephemeris['sun']
        location=self.ephemeris['earth'].at(date).observe(ephem)
        # account for our location on earth
        location=location.frame_latlon(
            skyfield.api.wgs84.latlon(self.latlong[0],self.latlong[1]))
        return location[1].degrees,location[0].degrees,location[2].au

    def azimuth(self,
        date:typing.Optional[datetime.datetime]=None
        )->float:
        """
        get the compass angle of the sun (0=North,90=East,180=South,270=West)

        This is true notrh, relative to earth's axis, not magnetic north
        to get that you will need to use a look-up table

        :property date: if not specified, use now()
        """
        return self.angle(date)[0]

    def elevation(self,
        date:typing.Optional[datetime.datetime]=None
        )->float:
        """
        get the elevation angle of the sun (0=level,90=directly overhead)

        :property date: if not specified, use now()
        """
        return self.angle(date)[1]

    def distance(self,
        date:typing.Optional[datetime.datetime]=None
        )->float:
        """
        get the elevation angle of the sun (0=level,90=directly overhead)

        :property date: if not specified, use now()
        """
        return self.angle(date)[2]


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        # NOTE: default coordinates should closely match
        #        https://www.timeanddate.com/sun/usa/salt-lake-city
        st=SolarTimes((40.7607793,-111.8910474))
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--latlong':
                    ll=None
                    if len(arg)>1:
                        ll=arg[1].split(',')
                    st=SolarTimes(ll)
                elif arg[0]=='--angle':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.angle(d))
                elif arg[0]=='--azimuth':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.azimuth(d))
                elif arg[0]=='--elevation':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.elevation(d))
                elif arg[0]=='--equinoxes':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    for equinox in st.equinoxes(d):
                        print('%s - %s'%(equinox[0],equinox[1].isoformat()))
                elif arg[0]=='--nextAutumnalEquinox':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.nextAutumnalEquinox(d))
                elif arg[0]=='--nextSummerSolstice':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.nextSummerSolstice(d))
                elif arg[0]=='--nextVernalEquinox':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.nextVernalEquinox(d))
                elif arg[0]=='--nextWinterSolstice':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.nextWinterSolstice(d))
                elif arg[0]=='--solarMidnight':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.solarMidnight(d).astimezone().isoformat())
                elif arg[0]=='--solarNoon':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.solarNoon(d).astimezone().isoformat())
                elif arg[0]=='--sunPath':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.sunPathCsv(d))
                elif arg[0]=='--sunrise':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.sunrise(d).astimezone().isoformat())
                elif arg[0]=='--sunriseSunset':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    ss=st.sunriseSunset(d)
                    print('sunrise: %s'%ss[0].astimezone().isoformat())
                    print('sunset:  %s'%ss[1].astimezone().isoformat())
                elif arg[0]=='--sunset':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.sunset(d).astimezone().isoformat())
                elif arg[0]=='--dayLength':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.dayLength(d))
                elif arg[0]=='--nightLength':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.nightLength(d))
                elif arg[0]=='--distance':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.distance())
                elif arg[0]=='--saveSolarProfile':
                    d=None
                    if len(arg)>1:
                        d=arg[1]
                    print(st.saveSolarProfile())
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  solar.py [options]')
        print('Options:')
        print('   --latlong=lat,long ..... IMPORTANT! certain calculations')
        print('                            will be incorrect without knowing')
        print('                            the global position we are talking')
        print('                            about FIRST!')
        print('   --angle[=date] ......... both the azimuth and elevation')
        print('   --azimuth[=date] ....... compass direction of the sun')
        print('   --elevation[=date] ..... elevation of the sun in the sky')
        print('   --equinoxes[=date] ..... name and time of all equinoxes')
        print('                            this year')
        print('   --nextAutumnalEquinox[=date]')
        print('     ...................... date of the next autumn equinox')
        print('   --nextSummerSolstice[=date]')
        print('     ...................... date of the next summer solstice')
        print('   --nextVernalEquinox[=date]')
        print('     ...................... date of the next spring equinox')
        print('   --nextWinterSolstice[=date]')
        print('                            date of the next winter solstice')
        print('   --solarMidnight[=date] . get the time the sun is opposite')
        print('                            side of the earth')
        print('   --solarNoon[=date] ..... get the time the sun is directly')
        print('                            overhead.')
        print('   --sunPath[=date] ....... the angle of the sun for every')
        print('                            minute of the day')
        print('   --sunrise[=date] ....... the sunrise time')
        print('   --sunriseSunset[=date] . sunrise and sunset time')
        print('   --sunset[=date] ........ sunset time')
        print('   --dayLength[=date] ..... how long a day is')
        print('   --nightLength[=date] ... how long a night is')
        print('   --saveSolarProfile ..... save solar profile to csv')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
