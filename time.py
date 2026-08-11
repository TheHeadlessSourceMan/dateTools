"""
Extended version of the datetime.time object
"""
import typing
import datetime
if typing.TYPE_CHECKING:
    from .dateTime import DateTimeCompatible
    from .timestamp import asTimestamp


class HasTime(typing.Protocol):
    """
    Duck typing for a class that has a time member
    """
    time:"TimeCompatible"


TimeCompatible=typing.Union["DateTimeCompatible"]


def asTime(time:"TimeCompatible")->"Time":
    """
    Always return a time object.  Create one on the fly if necessary
    """
    if isinstance(time,Time):
        return time
    return Time(time)


class TimeMeta(type):
    """
    Metaclass for declaring that Time is a datetime.time
    """
    def __instancecheck__(cls,instance)->bool:
        return instance in (datetime.time,Time) # pylint: disable=no-member
class Time(metaclass=TimeMeta):
    """
    Extended version of the datetime.time object
    """
    def __init__(self,time:typing.Optional["TimeCompatible"]=None):
        self._time:datetime.time # pylint: disable=no-member
        if time is not None:
            self.assign(time)

    def assign(self,time:typing.Optional["TimeCompatible"]=None)->None:
        """
        Assign the value of this time object
        """
        if time is None:
            time=datetime.datetime.now() # pylint: disable=no-member
        elif isinstance(time,(int,float)):
            time=datetime.datetime.fromtimestamp(
                time,
            ) # pylint: disable=no-member
        if isinstance(time,datetime.time): # pylint: disable=no-member
            self._time=datetime.time( # pylint: disable=no-member
                time.hour,time.minute,time.second,time.microsecond,
                time.tzinfo,fold=time.fold)
        elif isinstance(time,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(time)
            if parseResult is None:
                raise TypeError(f'"{time}" is not a Time')
            self.assign(parseResult)
        elif hasattr(time,'time'):
            self.assign(time.time) # type: ignore
        elif hasattr(time,'timestamp'):
            self.assign(asTimestamp(time.timestamp)) # type: ignore
        else:
            raise TypeError(
                f'Unable to parse time type "{time.__class__.__name__}"',
            )

    def strftime(self,format:str)->str:
        """
        Return a string representation of this time object
        """
        return self._time.strftime(format)

    @property
    def time(self)->datetime.time:
        """
        Identity as a builtin time.
        """
        return self._time

    @property
    def hour(self)->int:
        """
        hour
        """
        return self._time.hour

    @property
    def minute(self)->int:
        """
        minute
        """
        return self._time.minute

    @property
    def second(self)->int:
        """
        second
        """
        return self._time.second

    @property
    def microsecond(self)->int:
        """
        second
        """
        return self._time.microsecond

    def __cmp__(self,other:typing.Any)->int:
        """
        Compare this time to another time
        """
        if isinstance(other,Time):
            return (self._time>other._time)-(self._time<other._time)
        raise TypeError(
            f'Unable to compare {other.__class__.__name__} to Time')

    def __add__(self,
        other:typing.Any)->"Time":
        """
        Add a timedelta to this time object
        """
        if isinstance(other,datetime.timedelta):
            return Time(self._time+other)
        raise TypeError(
            f'Unable to add {other.__class__.__name__} to Time')

    def __sub__(self,other:typing.Any)->"Time":
        """
        Subtract a timedelta from this time object
        """
        if isinstance(other,datetime.timedelta):
            return Time(self._time-other)
        raise TypeError(
            f'Unable to subtract {other.__class__.__name__} from Time')
time=Time
AbsoluteTime=Time
