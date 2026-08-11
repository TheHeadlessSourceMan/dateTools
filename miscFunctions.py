#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
contains misc helpful functions
"""
import typing
import datetime
import dateTools.fuzzytime as fuzzytime


# some handy constants
ONE_DAY=datetime.timedelta(days=1)
ONE_WEEK=ONE_DAY*7


def humanTime(
    time:datetime.time,
    quartersOny:bool=False
    )->str:
    """
    Turns a time like 7:44 into a rounded
    human-spoken time like "Quarter to eight"

    :property quartersOny: if True, don't use
        "five till/after" and "ten till/after"
    """
    sectionNames={5:'Five',10:"Ten",15:"Quarter",30:"Half"}
    numberNames={0:"o'clock",1:'one',2:'two',3:'three',4:'four',5:'five',
        6:'six',7:'seven',8:'eight',9:'nine',10:'ten',11:'eleven',12:'twelve'}
    if not quartersOny:
        answer=roundTime(time,'minutes',5)
        if answer.minute not in (0,5,10,50,55):
            answer=roundTime(time,'minutes',15)
    else:
        answer=roundTime(time,'minutes',15)
    minutesApart=int(abs((answer-time).seconds)/60)%60
    if minutesApart==0:
        ret='%s %s'%(numberNames[answer.hour],numberNames[0])
    elif minutesApart>30:
        hour=answer.hour+1
        while hour>12:
            hour-=12
        ret='%s till %s'%(60-sectionNames[minutesApart],numberNames[hour])
    else:
        ret='%s after %s'%(sectionNames[minutesApart],numberNames[answer.hour])
    return ret


def roundTime(
    time:datetime.time,
    toUnits:str,
    toUnitAmount:int=1
    )->datetime.datetime:
    """
    round the time to whatever is given

    examples:
        roundTime(1:34,'minutes',5) => 1:35

    TODO: handle weeks?
    TODO: works with datetime.datetime, but what if they pass
        another kind of object in?
    """
    def _roundToDecade(n:float,dec:float)->float:
        return int(round(n/dec))*dec
    toUnits=toUnits.lower()
    if toUnits[-1]=='s': # remove plural ("days" => "day")
        toUnits=toUnits[0:-1]
    # now go and do it
    vals:typing.Dict[str,typing.Any]={}
    found=False
    for units in ('year','month','day','hour','minute','second'):
        if found:
            vals[units]=0
        elif units!=toUnits:
            vals[units]=getattr(time,units)
        else:
            vals[units]=_roundToDecade(getattr(time,units),toUnitAmount)
            found=True
    return datetime.datetime(**vals)


def nextDay(
    fromDay:typing.Union[None,datetime.date,datetime.datetime]=None
    )->datetime.date:
    """
    add one day to the given time

    :property fromDay: if not specified, use now()
    """
    if fromDay is None:
        fromDay=datetime.datetime.now()
    if isinstance(fromDay,datetime.datetime):
        fromDay=fromDay.date()
    return fromDay+ONE_DAY


def previousDay(
    fromDay:typing.Union[None,datetime.date,datetime.datetime]=None
    )->datetime.date:
    """
    subtract one day from the given time

    :property fromDay: if not specified, use now()
    """
    if fromDay is None:
        fromDay=datetime.datetime.now()
    if isinstance(fromDay,datetime.datetime):
        fromDay=fromDay.date()
    return fromDay-ONE_DAY


def findDay(
    matchingFn:typing.Callable[[datetime.datetime],bool],
    previous:bool=False,
    fromDay:typing.Union[None,datetime.date,datetime.datetime]=None,
    safetyNet:bool=True
    )->typing.Optional[datetime.date]:
    """
    find the next day matching a condition

    :property matchingFn: user-provided function that takes a datetime
        and returns True if it matches
    :property previous: search going back in time
    :property fromDay: if not specified, use now()
    :property safetyNet: detects if dates are getting too far out of hand

    NOTE: this always tests fromDay first, so if you want to skip that,
        start with nextDay(fromDay)
    """
    if fromDay is None:
        fromDay=datetime.datetime.now()
    if not isinstance(fromDay,datetime.datetime):
        fromDay=datetime.datetime.combine(fromDay,datetime.time())
    n=0
    while True:
        if matchingFn(fromDay):
            break
        if previous:
            fromDay-=ONE_DAY
        else:
            fromDay+=ONE_DAY
        if safetyNet:
            n+=1
            if n>=10000:
                raise Exception('SAFETY_NET: Day appears to never be found!')
    return fromDay


def toTime(
    something:typing.Union[None,str,datetime.datetime,datetime.time]
    )->datetime.time:
    """
    convert something to a time

    can handle:
        time object
        datetime object
        "12:00PM"
        "24:00"
        any object with a time or datetime member

    If it is none of those, throws an exception.
    """
    if something is None:
        raise Exception('Unable to convert "None" to time')
    if isinstance(something,datetime.time):
        return something
    if isinstance(something,str):
        something=something.replace(' ','')
        if something[-1].lower()=='m':
            # decode AM/PM
            something=datetime.datetime.strptime(something,'%I:%M%p').time()
        else:
            # 24 hour clock
            something=datetime.datetime.strptime(something,'%H:%M').time()
    elif hasattr(something,'time'): # also handles datetime objects
        something=something.time
        if callable(something):
            something=something()
    elif hasattr(something,'datetime'):
        something=something.datetime
        if callable(something):
            something=something()
        something=something.time()
    else:
        className=something.__class__.__name__
        raise Exception(f'Unable to convert "{className}" to time.')
    return something

InUnitsValuesFloats=typing.Literal[
    'days','hours','minutes','seconds',
    'd','h','m','s']
InUnitsValues=typing.Literal[InUnitsValuesFloats,'hms']
@typing.overload
def timeDeltaInUnits(
    timeDelta:None,
    inUnits:typing.Optional[InUnitsValues]=None
    )->None:
    ...
@typing.overload
def timeDeltaInUnits(
    timeDelta:typing.Union[datetime.timedelta,str],
    inUnits:None
    )->datetime.timedelta:
    ...
@typing.overload
def timeDeltaInUnits(
    timeDelta:typing.Union[datetime.timedelta,str],
    inUnits:typing.Literal['hms']
    )->str:
    ...
@typing.overload
def timeDeltaInUnits(
    timeDelta:typing.Union[datetime.timedelta,str],
    inUnits:typing.Literal[InUnitsValuesFloats]
    )->float:
    ...
def timeDeltaInUnits(
    timeDelta:typing.Union[None,datetime.timedelta,str],
    inUnits:typing.Optional[InUnitsValues]=None
    )->typing.Union[None,float,datetime.timedelta,str]:
    """
    Convert a datetime.timedelta into the requested units

    :timeDelta: can be anything that toTimeDelta() supports
    :property inUnits: can be 'days', 'hours', 'minutes', 'seconds',
        or 'hms' for string format like "1d 5h 3m 21s"
        (very forgiving - anything that starts with 'd','h','m','s')
        if None, returns a datetime.timedelta
    """
    if timeDelta is None:
        return None
    if not isinstance(timeDelta,datetime.timedelta):
        timeDelta=toTimeDelta(timeDelta)
    if inUnits is None or not inUnits:
        return timeDelta
    formatConversion=str(inUnits).lower()
    if formatConversion=='hms':
        seconds=timeDelta.total_seconds()
        minutes=int(seconds/60) # also does a floor()
        seconds-=minutes*60
        hours=int(minutes/60)
        minutes-=hours*60
        days=int(hours/24)
        hours-=days
        return '%dd %dh %dm %fs'%(days,hours,minutes,seconds)
    c=formatConversion[0]
    denom={'d':(60*60*24),'h':(60*60),'m':(60)}.get(c,1)
    return timeDelta.total_seconds()/denom

@typing.overload
def toTimeDelta(
    something:typing.Union[datetime.timedelta,str]
    )->datetime.timedelta:
    ...
@typing.overload
def toTimeDelta(
    something:None
    )->None:
    ...
def toTimeDelta(
    something:typing.Union[None,datetime.timedelta,str]
    )->typing.Optional[datetime.timedelta]:
    """
    convert something to a timedelta
    """
    if something is None:
        return None
    if isinstance(something,datetime.timedelta):
        return something
    if not isinstance(something,fuzzytime.FuzzyTime):
        something=fuzzytime.FuzzyTime(something)
    return something.timedelta


def unitsInTimdelta(
    units:typing.Union[str,float],
    inUnits:typing.Optional[str]=None
    )->datetime.timedelta:
    """
    Convert a value in the specified units into a datetime.timedelta

    :property units: expects an int or float, but can also be a string -
        possibly with inUnits included (eg. "5h")
    :property inUnits: can be 'days', 'hours', 'minutes', or 'seconds'
        (format is very forgiving - anything that starts with 'd','h','m','s')
        if None, returns a datetime.timedelta
    """
    if isinstance(units,str):
        import re
        units=units.replace(',','')
        regex=r"""\s*[-]?\s*(?P<units>[0-9.]+)\s*(?P<inUnits>[a-z])?"""
        regex=re.compile(regex,re.IGNORECASE)
        td:typing.Optional[datetime.timedelta]=None
        for m in regex.finditer(units):
            iu=m.group('inUnits')
            if iu is None:
                iu=inUnits
            unitTd=unitsInTimdelta(float(m.group('units')),iu)
            if td is None:
                td=unitTd
            else:
                td+=unitTd
        if td is None:
            raise Exception(f'Unable to convert "{units}" to timedelta')
        return td
    if inUnits is None or not inUnits:
        raise Exception('inUnits must be specified')
    c=inUnits[0].lower() # type: ignore
    paramName={'d':'days','h':'hours','m':'minutes'}.get(c,'seconds')
    return datetime.timedelta(**{paramName:units})


def inDays(
    timeDelta:datetime.timedelta
    )->float:
    """
    returns the timedelta in total minutes

    :property timeDelta: can be a datetime.timedelta,
        or anything that toTimeDelta() supports
    """
    return timeDeltaInUnits(timeDelta,'d')


def inHours(
    timeDelta:datetime.timedelta
    )->float:
    """
    returns the timedelta in total minutes

    :property timeDelta: can be a datetime.timedelta,
        or anything that toTimeDelta() supports
    """
    return timeDeltaInUnits(timeDelta,'h')


def inMinutes(
    timeDelta:datetime.timedelta
    )->float:
    """
    returns the timedelta in total minutes

    :property timeDelta: can be a datetime.timedelta,
        or anything that toTimeDelta() supports
    """
    return timeDeltaInUnits(timeDelta,'m')


def inSeconds(
    timeDelta:datetime.timedelta
    )->float:
    """
    returns the timedelta in total seconds

    :property timeDelta: can be a datetime.timedelta,
        or anything that toTimeDelta() supports
    """
    return timeDeltaInUnits(timeDelta,'s')


def secondsToHMS(sec:float)->str:
    """
    Convert total seconds to "5d 3h 5m 28s" format
    """
    result=None
    m=sec/60
    sec=sec%60
    h=m/60
    m=m%60
    d=h/24
    h=h%24
    if d==0:
        if h==0:
            if m==0:
                result=str(sec)+'s'
            else:
                result=str(m)+'m '+str(sec)+'s'
        else:
            result=str(h)+'h '+str(m)+'m '+str(sec)+'s'
    else:
        result=str(d)+'d '+str(h)+'h '+str(m)+'m '+str(sec)+'s'
    return result


def secondsToColonFormat(
    sec:float,
    military:bool=False,
    showSeconds:bool=False):
    """
    Convert total seconds to hh:mm:ss format
    """
    result=None
    m=sec/60
    sec=sec%60
    h=m/60
    m=m%60
    if military:
        ampm=''
    else:
        if h>12:
            h=h-12
            ampm='PM'
        else:
            ampm='AM'
    result=str(h)+':'
    if m<10:
        result=result+'0'
    result=result+str(m)
    if showSeconds:
        result=result+':'
        if sec<10:
            result=result+'0'
        result=result+str(sec)
    return result+ampm


def dayFromString(day:typing.Union[int,str])->int:
    """
    Get a weekday from a string
    """
    if isinstance(day,int):
        return day
    day=day.strip().upper()
    if day[0]=='S':
        if day[1]=='A':
            day=6
        elif day[1]=='U':
            day=0
    elif day[0]=='M':
        day=1
    elif day[0]=='T':
        if day[1]=='U':
            day=2
        elif day[1]=='H':
            day=4
    elif day[0]=='W':
        day=3
    elif day[0]=='F':
        day=5
    if not isinstance(day,int):
        day=0
    return day


numericFamilies=('hundred','thousand','million','billion','trillion')
numericFamConv=(100,1000,1000000,1000000000,1000000000)
numerics=('zero','one','two','three','four','five','six','seven','eight',
    'nine','ten','eleven','twelve','thirteen','fourteen','fifteen',
    'sixteen','seventeen','eighteen','nineteen')
decades:typing.List[typing.Optional[str]]=[
    None,None,'twenty','thirty','fourty','fifty',
    'sixty','seventy','eighty','ninety']
numericPlaces=('none','first','second','third','fourth','fifth','sixth',
    'seventh','eighth','nineth','tenth','eleventh','twelfth')
def numberToText(
    number:int,
    place:bool=False
    )->str:
    """
    convert a number to text, eg
        1,225,819 =>
        "one million, two hundred twenty five thousand, eight hundred nineteen"

    :property place: if True, say "twenty-third" instead of "twenty three"
    """
    raise NotImplementedError()

def reWithoutNames(
    regex:typing.Union[typing.Pattern[str],str]
    )->str:
    """
    strip names form the regex
    """
    import re
    if isinstance(regex,re.Pattern):
        regex=regex.pattern
    regex=re.sub(r'\(\?P\<[^>]*\>',r'(',regex)
    return regex

_numberDetect=None
def numberDetectRe()->typing.Pattern[str]:
    """
    return a regular expression capable of detecting numbers like
        fifteenth
        twenty-third
        23rd
        sixteen
        one thousand
        one point four five million
        eighteen thousand
        1.45 million
        2.25
        one hundred thousand six undred and fifty two

    NOTE: limited to English numbers
    """
    global _numberDetect
    if _numberDetect is None:
        import re
        decadeStrings:str='|'.join(
            typing.cast(typing.List[str],decades[2:]))
        nx:str=r"""\s*
            ((?P<decade>"""+decadeStrings+r""")(-\s)*)?
            ((
                (?P<digits>[0-9][0-9,.]*)|
                (
                    (?P<numeric>"""+('|'.join(numerics))+r""")
                    (\s*point
                        (?P<numericDecimal>(\s*("""+('|'.join(numerics[1:10]))+r"""))+)
                    )?
                )|
                (?P<numericPlace>"""+('|'.join(numericPlaces))+r""")
            )(st|nd|rd|th)?)?"""
        regex:str=r"""("""+nx+r"""\s*
            (?P<fam>"""+('|'.join(numericFamilies))+r""")*
            (\s*and)?
        )"""
        #print(regex)
        regex=regex.replace(' ','').replace('\n','')
        _numberDetect=re.compile(regex,re.IGNORECASE|re.DOTALL)
    return _numberDetect


def numberdecode(number:str)->float:
    """
    decode a number using numberDetectRe

    capable of detecting numbers like
        fifteenth
        twenty-third
        23rd
        sixteen
        one thousand
        one point four five million
        eighteen thousand
        1.45 million
        2.25
        one hundred thousand six undred and fifty two
    """
    acc=0
    for match in numberDetectRe().finditer(number):
        #print('"%s" matched to "%s"'%
        #   (number,number[match.start():match.end()]))
        val=0
        digits=match.group('digits')
        if digits is not None:
            val+=float(digits.replace(',',''))
        numeric=match.group('numeric')
        if numeric is not None:
            val+=numerics.index(numeric)
            numericDecimal=match.group('numericDecimal')
            if numericDecimal is not None:
                numericDecimal=numericDecimal.strip().split()
                divisor=0.1
                for nd in numericDecimal:
                    val+=numerics.index(nd)*divisor
                    divisor*=0.1
        numericPlace=match.group('numericPlace')
        if numericPlace is not None:
            val+=numericPlaces.index(numericPlace)
        decade=match.group('decade')
        if decade is not None:
            val+=decades.index(decade)*10
        fam=match.group('fam')
        if fam is not None:
            val*=numericFamConv[numericFamilies.index(fam)]
        acc+=val
    return acc


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--numberdecode':
                    n=numberdecode(arg[1])
                    print(n)
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  miscFunctions.py [options]')
        print('Options:')
        print('   --numberdecode=number ...... decode a number')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
