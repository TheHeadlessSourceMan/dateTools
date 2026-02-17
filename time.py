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


class Time(
    datetime.time): # pylint: disable=no-member
    """
    Extended version of the datetime.time object
    """
    def __new__(cls,*args,**kwargs)->"Time":
        """
        Need to override this so datetime.time.__new__() is not called
        """
        return super().__new__(cls,*args,**kwargs)

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
            time=datetime.datetime.fromtimestamp(time) # pylint: disable=no-member
        if isinstance(time,datetime.time): # pylint: disable=no-member
            self._time=datetime.time( # pylint: disable=no-member
                time.hour,time.minute,time.second,time.microsecond,
                time.tzinfo,fold=time.fold)
        elif isinstance(time,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(time)
            if parseResult is None:
                raise TypeError(f'"{time}" is not a Time')
            if not isinstance(parseResult,(datetime.time,datetime.datetime)): # pylint: disable=isinstance-second-argument-not-valid-type,no-member
                raise TypeError(f'"{time}" parses to a {parseResult.__class__.__name__}, not a Time') # noqa: E501 # pylint: disable=line-too-long
            self.assign(parseResult)
        elif hasattr(time,'time'):
            self.assign(time.time) # type: ignore
        elif hasattr(time,'timestamp'):
            self.assign(asTimestamp(time.timestamp)) # type: ignore
        else:
            raise TypeError(f'Unable to parse time type "{time.__class__.__name__}"')

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
time=Time
AbsoluteTime=Time
