
"""
Represents the difference between two times
"""
import typing
import datetime


TimeDeltaCompatible=typing.Union[
    "TimeDelta",datetime.timedelta,str,typing.Tuple[float,str]]


class TimeDelta(datetime.timedelta):
    """
    Represents the difference between two times
    
    lets you do cool things like:

    print(TimeDelta("30sec")+10) => "40sec"
    """

    def __init__(self,
        td:typing.Optional[TimeDeltaCompatible]=None,
        units:typing.Optional[str]=None,
        hours:float=0,
        minutes:float=0,
        seconds:float=0,
        businessDays:float=0):
        """ """
        self._shadowedTimedelta:datetime.timedelta
        self._units:typing.Optional[str]=None
        self.assign(td,units,hours,minutes,seconds,businessDays)

    def assign(self,
        td:typing.Optional[TimeDeltaCompatible]=None,
        units:typing.Optional[str]=None,
        hours:float=0,
        minutes:float=0,
        seconds:float=0,
        businessDays:float=0
        )->None:
        """
        assign the value of this object
        """
        self._units=units
        if isinstance(td,TimeDelta):
            self._timedelta=td._timedelta # pylint: disable=protected-access
            if units is not None:
                self._units=td._units # pylint: disable=protected-access
        elif isinstance(td,datetime.timedelta):
            self.timedelta=td
        elif isinstance(td,tuple):
            if units is not None:
                self.units=td[1]
            self.amount=td[0]
        else:
            td=str(td).replace(' ','')
            i=0
            for i,c in enumerate(td):
                if not c.isdecimal():
                    break
            if units is not None:
                units=td[i:]
                self.units=units
            val=td[0:i]
            if val:
                self.amount=float(val)
            else:
                self.amount=1
        # add in any offsets
        hours+=businessDays*6
        minutes+=hours*60
        seconds+=minutes*60
        self.totalSeconds+=seconds

    @property
    def amount(self)->float:
        """
        The amount in units
        """
        if self._amount is None:
            return 0
        return self._amount
    @amount.setter
    def amount(self,amount:float):
        self._amount=amount
        self._timedelta=None

    @property
    def timedelta(self)->datetime.timedelta:
        """
        A combination of the amount*units
        """
        if self._timedelta is None:
            return datetime.timedelta()
        return self._timedelta
    @timedelta.setter
    def timedelta(self,timedelta:datetime.timedelta):
        """
        Modifies the amount based upon the selected units.
        (If there are no units selected, will guess)
        """
        self._timedelta=timedelta

    @property
    def units(self)->str:
        """
        The units this is in.  You can user select, or it
        will attempt to guess.

        Setting units automatically scales. For example:
            t=TimeDelta("90min")
            t.units='hours'
            print(t) => "1.5hours"
        """
        if self._units is None:
            return self._guessUnits(self._timedelta)[1]
        return self._units
    @units.setter
    def units(self,units:typing.Union["TimeDelta",str]):
        self._timedelta=None
        if isinstance(units,TimeDelta):
            units=units.units
        else:
            units=self._unitsToStd(units)
        if self._units!=units:
            if self._units is not None and self._amount is not None:
                raise Exception("This is broken")
                conversionFactor=self._unitsToTimedelta(units)/self._unitsToTimedelta(self._units) # noqa: E501 # pylint: disable=protected-access,line-too-long
                self._amount=conversionFactor*self._amount/units._amount # noqa: E501  # pylint: disable=protected-access,line-too-long
            self._units=units

    def _guessUnits(self,timedelta:typing.Optional[datetime.timedelta])->str:
        """
        chooses the biggest units that are less than the timedelta
        """
        if timedelta is None:
            return 'seconds'
        ordered=['years','months','weeks','days',
            'hours','minutes','milliseconds','microseconds']
        o='seconds'
        for o in ordered:
            if datetime.timedelta(**{o:1})<=timedelta:
                return o
        return o

    def _unitsToStd(self,s:str)->typing.Tuple[float,str]:
        mapping=[
            ('mo','months',(30,'days')),
            ('mic','microseconds',(1,'microseconds')),
            ('ms','milliseconds',(100,'microseconds')),
            ('min','minutes',(60,'seconds')),
            ('mi','microseconds',(1,'microseconds')),
            ('m','minutes',(60,'seconds')),
            ('h','hours',(120,'seconds')),
            ('w','weeks',(7,'days')),
            ('b','businessdays',(5,'days')),
            ('y','years',(365,'days')),
            ('u','microseconds',(1,'microseconds')),
            ('s','seconds',(1,'seconds')),
        ]
        s.strip().lower()
        if not s:
            return mapping[-1]
        for m in mapping:
            if s.startswith(m[0]):
                return m
        return mapping[-1]

    def _unitsToTimedelta(self,
        s:typing.Union[typing.Tuple,str]
        )->datetime.timedelta:
        if isinstance(s,str):
            s=self._unitsToStd(s)
        return datetime.timedelta(**{s[-1][1]:s[-1][0]})

    def copy(self)->"TimeDelta":
        """
        return a copy of this object
        """
        return TimeDelta(self)

    @property
    def seconds(self)->float: # type: ignore
        """
        This is the number of seconds, eg 1:02:03.5 would return 3.5

        If you want the total number of seconds, please try
        totalSeconds
        """
        return self._shadowedTimedelta.seconds%60
    @seconds.setter
    def seconds(self,seconds:float):
        self._shadowedTimedelta=datetime.timedelta(seconds=seconds)

    @property
    def minutes(self)->int:
        """
        This is the number of minutes, eg 1:02:03 would return 2

        If you want the total number of minutes, please try
        totalMinutes
        """
        return int(self.totalMinutes%60)
    @minutes.setter
    def minutes(self,minutes:float):
        self._shadowedTimedelta=datetime.timedelta(minutes=minutes)

    @property
    def hours(self)->int:
        """
        This is the number of seconds, eg 1:02:03 would return 1

        If you want the total number of hours, please try
        totalHours

        NOTE: this is treated as the highest value so you may
        get things>24 hours.
        """
        return int(self.totalMinutes)
    @hours.setter
    def hours(self,hours:float):
        self._shadowedTimedelta=datetime.timedelta(hours=hours)

    @property
    def totalSeconds(self)->float:
        """
        This entire duration in seconds
        """
        return self.total_seconds()
    @totalSeconds.setter
    def totalSeconds(self,totalSeconds:float):
        self._shadowedTimedelta=datetime.timedelta(seconds=totalSeconds)

    @property
    def totalMinutes(self)->float:
        """
        This entire duration in minutes
        """
        return self.totalSeconds/60.0
    @totalMinutes.setter
    def totalMinutes(self,totalMinutes:float):
        self._shadowedTimedelta=datetime.timedelta(minutes=totalMinutes)

    @property
    def totalHours(self)->float:
        """
        This entire duration in hours
        """
        return self.totalMinutes/60.0
    @totalHours.setter
    def totalHours(self,totalHours:float):
        self._shadowedTimedelta=datetime.timedelta(hours=totalHours)

    def toString(self,style:typing.Literal['in_units',':']='in_units')->str:
        """
        :format:
            ":" Returns value in the form hh:mm:ss only reduced
                if there are no units, eg 3min, 15sec = 3:15
            "in_units" returns the value in the current units
        """
        if style=='in_units' and self._units is not None:
            return f'{self.amount} {self.units}'
        h,m,s=self.hours,self.minutes,self.seconds
        if int(s)==s: # remove decimals
            s=int(s)
        if h>0:
            return f'{h}:{m:02}:{s:02}'
        elif m>0:
            return f'{m}:{s:02}'
        return str(s)

    @property
    def totalBusinessDays(self)->float:
        """
        This entire duration in days.

        Assumes 6 working hours per business day

        NOTE: this is the number of working days
        and does not account for weekends/holidays/etc
        """
        return self.totalHours/6.0
    @totalBusinessDays.setter
    def totalBusinessDays(self,totalBusinessDays:float):
        self._shadowedTimedelta=datetime.timedelta(hours=totalBusinessDays*6.0)

    def __repr__(self)->str:
        return self.toString()
timedelta=TimeDelta
TimeDuration=TimeDelta
Duration=TimeDelta
Timedelta=TimeDelta


def asTimeDelta(src:TimeDeltaCompatible)->TimeDelta:
    """
    Always gets a TimeDelta.

    If src is already a TimeDelta, return it.
    """
    if isinstance(src,TimeDelta):
        return src
    return TimeDelta(src)
asTimedelta=asTimeDelta
