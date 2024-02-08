"""
Units for time values, eg Day, Month, Year, etc
"""
import typing
from abc import abstractmethod
import datetime
from dateTools import UnixTime,UnixTimeCompatible
if typing.TYPE_CHECKING:
    from dateTools import When


TimeUnitValueTypes=typing.Union[
    float,int,"TimeUnit",datetime.datetime,UnixTime]

class TimeUnit:
    """
    Base class for time units

    These can be concrete or conceptual, eg:
        Month(15) # the 15th of a month
        Month(datetime.now()) # this month
        Month(datetime.now(),15) # the 15th of this month
        Month(datetime.now(),Week(3)) # the 3rd week of this month
        Month(datetime.now(),15)->next() # the 15th of next month
        Month(datetime.now())+1 # next month
        Month(datetime.now(),15)->next(12) # the 15th of this month next year
    And if concrete, can do things like iterate
        for day in Month(datetime.now()):
        for week in Month(datetime.now()).weeks:

    NOTE: whenever the value is out-of-bounds, will clamp
        Year("Feb 29")+1
        is not going to be a leap year, so will return Feb 28
    """

    def __init__(self,
        subUnits:type,
        value:TimeUnitValueTypes,
        conceptualValue:typing.Union[None,float,int]=None):
        """
        :param value: value auto-decides whether it is an concrete
            or conceptual value
        :type value: typing.Union[
            float,int,&quot;TimeUnit&quot;,datetime.datetime]
        :param conceptualValue: _description_, defaults to None
        :type conceptualValue: typing.Union[None,float,int], optional
        """
        self.subUnits:type=subUnits
        self.concreteValue:typing.Optional[datetime.datetime]=None
        self.conceptualValue:typing.Union[float,int,None]=None
        self.value:typing.Optional[UnixTime]=None
        self.assign(value,conceptualValue)

    def __iter__(self)->typing.Iterable["TimeUnit"]:
        return self.subUnits(self,self.concreteValue,self.conceptualValue)

    def __add__(self,value:typing.Union[int,float])->"When":
        return self.next(int(value))
    def __sub__(self,value:typing.Union[int,float])->"When":
        return self.previous(int(value))

    def __gt__(self,other:TimeUnitValueTypes)->bool:
        if self.value is None:
            return False
        if isinstance(other,TimeUnit):
            if other.value is None:
                return False
            return self.value>other.value
        return self.value>other

    def current(self)->"When":
        """
        Time(s) of the current unit we are in

        NOTE: if this is concrete, returns an exact datetime,
            but if abstract, return a range

        :return: _description_
        :rtype: When
        """
        return self.next(0)

    @abstractmethod
    def next(self,count:int=1)->"When":
        """
        Time(s) of the next unit increment

        NOTE: since there is a count index, this is the only one
            that derived classes must implement.

        :return: _description_
        :rtype: When
        """

    def previous(self,count:int=1)->"When":
        """
        Time(s) of the previous unit increment

        :return: _description_
        :rtype: When
        """
        return self.next(-1*count)

    def assign(self,
        value:TimeUnitValueTypes,
        conceptualValue:typing.Union[None,float,int]=None
        )->None:
        """
        :param value: value auto-decides whether it is an concrete
            or conceptual value
        :type value: typing.Union[
            float,int,&quot;TimeUnit&quot;,datetime.datetime]
        :param conceptualValue: _description_, defaults to None
        :type conceptualValue: typing.Union[None,float,int], optional
        """
        self.concreteValue=None
        if isinstance(value,(int,float)):
            if conceptualValue is None:
                self.conceptualValue=value
        elif isinstance(value,TimeUnit):
            self.conceptualValue=value.conceptualValue
            self.concreteValue=value.concreteValue
        elif isinstance(value,datetime.datetime):
            self.conceptualValue=conceptualValue
            self.datetime=value # will set the concrete value
        elif isinstance(value,UnixTime):
            self.conceptualValue=conceptualValue
            self.unixTime=value # will set the concrete value

    @property
    def isConceptual(self)->bool:
        """
        Is this a conceptual time vs a concrete time,
        eg "Tuesday" vs "Tuesday, May25 2021"
        """
        return self.conceptualValue is not None
    @property
    def isConcrete(self)->bool:
        """
        Is this a concrete time vs a conceptual time,
        eg "Tuesday, May25 2021" vs "Tuesday"
        """
        return self.concreteValue is not None

    @property
    def dateTime(self)->typing.Optional[datetime.datetime]:
        """
        get the unit as a datetime
        """
        if self.value is None:
            return None
        return self.value.datetime
    @dateTime.setter
    def dateTime(self,dtime=datetime.datetime):
        """
        assign the datetime
        """
        self.value=dtime

    @property
    def unixTime(self)->UnixTime:
        """
        Representation in unix time value
        """
        return UnixTime(self.datetime)
    @unixTime.setter
    def unixTime(self,unixTime:UnixTimeCompatible):
        if not isinstance(unixTime,UnixTime):
            unixTime=UnixTime(unixTime)
        self.datetime=unixTime.datetime

class Day(TimeUnit):
    """
    Time unit representing days
    """

class Week(TimeUnit):
    """
    Time unit representing weeks
    """

class Month(TimeUnit):
    """
    Time unit representing months
    """
    def __init__(self,
        value:TimeUnitValueTypes,
        conceptualValue:typing.Union[None,float,int]=None):
        """ """
        TimeUnit.__init__(self,Day,value,conceptualValue)
    @property
    def dateTime(self)->datetime.datetime:
        if self.concreteValue is None:
            return datetime.datetime.now()
        return self.concreteValue
    @dateTime.setter
    def dateTime(self,dtime:datetime.datetime):
        self.concreteValue=dtime

    def next(self,count:int=1)->"When":
        """
        Time(s) of the next unit increment

        NOTE: since there is a count index, this is the only one
            that derived classes must implement.

        :return: _description_
        :rtype: When
        """
        dt=self.datetime+datetime.timedelta(months=count)
        return Month(dt,self.conceptualValue)

class Year(TimeUnit):
    """
    Time unit representing years
    """
