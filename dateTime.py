"""
Extended version of datetime.datetime object
"""
import typing
import datetime
from .date import Date
from .time import Time
from .timestamp import (
    Timestamp,TimestampCompatible,asTimestamp)


DateTimeCompatible=typing.Union[
    datetime.date,datetime.time,datetime.datetime, # pylint: disable=no-member
    "DateTime",Date,Time,
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
    def __instancecheck__(cls,instance:typing.Any)->bool:
        return instance in (DateTime,
            datetime.datetime,datetime.time,datetime.date, # noqa: E501 # pylint: disable=no-member
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
        return Date(self._datetime.date())

    @property
    def time(self)->Time:
        """
        Get this as a Date
        (so, essentially just the time without day)
        """
        return Time(self._datetime.time())

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

    def __cmp__(self,other:typing.Any)->int:
        """
        Compare two DateTime objects
        """
        if isinstance(other,DateTime):
            return (self._datetime>other._datetime)-(self._datetime<other._datetime)
        if isinstance(other,datetime.datetime): # noqa: E501 # pylint: disable=no-member
            return (self._datetime>other)-(self._datetime<other)
        if isinstance(other,datetime.date): # noqa: E501 # pylint: disable=no-member
            return (self._datetime>datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                other,
                datetime.time(),
            ))-(self._datetime<datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                other,
                datetime.time(),
            ))
        if isinstance(other,datetime.time): # noqa: E501 # pylint: disable=no-member
            return (self._datetime>datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                datetime.date.today(),
                other,
            ))-(self._datetime<datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                datetime.date.today(),
                other,
            ))
        raise TypeError(
            f'Unable to compare {other.__class__.__name__} to DateTime')

    def __sub__(self,other:typing.Any)->datetime.timedelta:
        """
        Subtract two DateTime objects
        """
        if isinstance(other,DateTime):
            return self._datetime-other._datetime
        if isinstance(other,datetime.datetime): # noqa: E501 # pylint: disable=no-member
            return self._datetime-other
        if isinstance(other,datetime.date): # noqa: E501 # pylint: disable=no-member
            return self._datetime-datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                other,
                datetime.time(),
            )
        if isinstance(other,datetime.time): # noqa: E501 # pylint: disable=no-member
            return self._datetime-datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                datetime.date.today(),
                other,
            )
        raise TypeError(
            f'Unable to subtract {other.__class__.__name__} from DateTime')

    def __rsub__(self,other:typing.Any)->datetime.timedelta:
        """
        Subtract two DateTime objects
        """
        if isinstance(other,datetime.datetime): # noqa: E501 # pylint: disable=no-member
            return other-self._datetime
        if isinstance(other,datetime.date): # noqa: E501 # pylint: disable=no-member
            return datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                other,
                datetime.time(),
            )-self._datetime
        if isinstance(other,datetime.time): # noqa: E501 # pylint: disable=no-member
            return datetime.datetime.combine( # noqa: E501 # pylint: disable=no-member
                datetime.date.today(),
                other,
            )-self._datetime
        raise TypeError(
            f'Unable to subtract DateTime from {other.__class__.__name__}')

    def __add__(self,other:typing.Any)->"DateTime":
        """
        Add a timedelta to this DateTime object
        """
        if isinstance(other,datetime.timedelta):
            return DateTime(self._datetime+other)
        raise TypeError(
            f'Unable to add {other.__class__.__name__} to DateTime')

    def __radd__(self,other:typing.Any)->"DateTime":
        """
        Add a timedelta to this DateTime object
        """
        if isinstance(other,datetime.timedelta):
            return DateTime(self._datetime+other)
        raise TypeError(
            f'Unable to add {other.__class__.__name__} to DateTime')

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
            dateTime=datetime.datetime.fromtimestamp(dateTime) # noqa: E501 # pylint: disable=no-member
        if isinstance(dateTime,datetime.datetime): # noqa: E501 # pylint: disable=isinstance-second-argument-not-valid-type,no-member
            if hasattr(dateTime,'datetime'):
                self.assign(typing.cast(DateTime,dateTime).datetime)
            else:
                self._datetime=dateTime
        elif isinstance(dateTime,datetime.date):
            self._datetime=datetime.datetime.combine(
                dateTime,
                datetime.time(),
            )
        elif isinstance(dateTime,datetime.time):
            self._datetime=datetime.datetime.combine(
                datetime.date.today(),
                dateTime,
            )
        elif isinstance(dateTime,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(dateTime)
            if parseResult is None:
                raise TypeError(f'"{dateTime}" is not a DateTime')
            if hasattr(parseResult,'fromTime') \
                or hasattr(parseResult,'currentDate'):
                raise TypeError(
                    f'"{dateTime}" parses to a '
                    f'{parseResult.__class__.__name__}, not a DateTime',
                )
            self.assign(typing.cast(DateTimeCompatible,parseResult))
        elif hasattr(dateTime,'datetime'):
            self.assign(typing.cast(HasDatetime,dateTime).datetime)
        elif hasattr(dateTime,'dateTime'):
            self.assign(asDateTime(dateTime.dateTime)) # type: ignore
        elif hasattr(dateTime,'date'):
            self.assign(dateTime.date) # type: ignore
        elif hasattr(dateTime,'time'):
            self.assign(dateTime.time) # type: ignore
        elif hasattr(dateTime,'timestamp'):
            self.assign(asTimestamp(dateTime.timestamp)) # type: ignore
        else:
            raise TypeError(f'Unable to parse date type "{dateTime.__class__.__name__}"') # noqa: E501 # pylint: disable=line-too-long
