"""
Extended version of datetime.datetime object
"""
import typing
import datetime
from .date import Date
from .time import Time
from .timestamp import Timestamp,TimestampCompatible,asTimestamp


DateTimeCompatible=typing.Union[
    datetime.date,datetime.time,datetime.datetime, # pylint: disable=no-member
    str,TimestampCompatible]

class HasDateTime(typing.Protocol):
    """
    Duck typing for a class with a dateTime member
    """
    dateTime:"DateTimeCompatible"
class HasDatetime(typing.Protocol):
    """
    Duck typing for a class with a datetime member
    """
    datetime:"DateTimeCompatible"

def asDateTime(dateTime:typing.Optional[DateTimeCompatible])->"DateTime":
    """
    Always return a DateTime object.
    Create one if necessary.
    """
    if isinstance(dateTime,DateTime):
        return dateTime
    return DateTime(dateTime)

class DateTimeMeta(type):
    """
    Metaclass for declaring that DateTime is a datetime.datetime
    """
    def __instancecheck__(cls,instance)->bool:
        return instance in (DateTime,
            datetime.datetime,datetime.time,datetime.date, # pylint: disable=no-member
            Date,Time)
class DateTime( # pylint: disable=inherit-non-class # type: ignore
    metaclass=DateTimeMeta):
    """
    Extended version of datetime.datetime object
    """
    def __init__(self,dateTime:typing.Optional[DateTimeCompatible]=None):
        self._datetime:datetime.datetime
        if dateTime is not None:
            self.assign(dateTime)

    def timestamp(self)->Timestamp:
        """
        Return a timestamp value
        """
        return asTimestamp(self._datetime.timestamp())

    @property
    def datetime(self)->datetime.datetime:
        """
        Identity
        """
        return self._datetime

    @property
    def date(self)->Date:
        """
        Get this as a Date
        (so, essentially just the day without hours/minutes/seconds)
        """
        return Date(self.timestamp())

    @property
    def time(self)->Time:
        """
        Get this as a Date
        (so, essentially just the time without day)
        """
        return Time(self.timestamp())

    def min(self, # type: ignore
        other:DateTimeCompatible
        )->"DateTime":
        """
        Minimum of this and another object
        """
        other=asDateTime(other)
        return DateTime(min(self.timestamp(),other.timestamp()))

    def max(self, # type: ignore
        other:DateTimeCompatible
        )->"DateTime":
        """
        Maximum of this and another object
        """
        other=asDateTime(other)
        return DateTime(max(self.timestamp(),other.timestamp()))

    @classmethod
    def now(cls)->"DateTime": # type: ignore
        """
        current datetime
        """
        return DateTime() # type: ignore

    def assign(self, # type: ignore # pylint: disable=arguments-renamed
        dateTime:typing.Optional[DateTimeCompatible]=None
        )->None:
        """
        Assign the value of this datetime object
        """
        if dateTime is None:
            dateTime=datetime.datetime.now() # pylint: disable=no-member
        elif isinstance(dateTime,(int,float)):
            dateTime=datetime.datetime.fromtimestamp(dateTime) # pylint: disable=no-member
        if isinstance(dateTime,datetime.datetime): # pylint: disable=isinstance-second-argument-not-valid-type,no-member
            if hasattr(dateTime,'datetime'):
                self.assign(typing.cast(DateTime,dateTime).datetime)
            else:
                self._datetime=dateTime
        elif isinstance(dateTime,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(dateTime)
            if parseResult is None:
                raise TypeError(f'"{dateTime}" is not a DateTime')
            if not isinstance(parseResult,(datetime.date,datetime.datetime)): # pylint: disable=isinstance-second-argument-not-valid-type,no-member
                raise TypeError(f'"{dateTime}" parses to a {parseResult.__class__.__name__}, not a DateTime') # noqa: E501 # pylint: disable=line-too-long
            self.assign(parseResult)
        elif hasattr(dateTime,'date'):
            self.assign(dateTime.date) # type: ignore
        elif hasattr(dateTime,'dateTime'):
            self.assign(asDateTime(dateTime.dateTime)) # type: ignore
        elif hasattr(dateTime,'timestamp'):
            self.assign(asTimestamp(dateTime.timestamp)) # type: ignore
        else:
            raise TypeError(f'Unable to parse date type "{dateTime.__class__.__name__}"')
