"""
Extended version of the datetime object
"""
import typing
import datetime
if typing.TYPE_CHECKING:
    from .dateTime import DateTimeCompatible,asDateTime,asTimestamp


class HasDate(typing.Protocol):
    """
    Duck typing for a class that has a date member
    """
    date:"DateCompatible"


DateCompatible=typing.Union["DateTimeCompatible"]

def asDate(date:DateCompatible)->"Date":
    """
    Always return a date object.  Create one on the fly if necessary
    """
    if isinstance(date,Date):
        return date
    return Date(date)
class DateMeta(type):
    """
    Metaclass for declaring that Date is a datetime.date
    """
    def __instancecheck__(cls,instance)->bool:
        return instance in (datetime.date,Date) # pylint: disable=no-member

class Date(metaclass=DateMeta):
    """
    Extended version of the datetime object
    """
    def __init__(self,date:typing.Optional[DateCompatible]=None):
        self._date:datetime.date # pylint: disable=no-member
        self.assign(date)

    def assign(self,date:typing.Optional[DateCompatible]=None):
        """
        Assign the value of this object
        """
        if date is None:
            date=datetime.datetime.now() # pylint: disable=no-member
        elif isinstance(date,(int,float)):
            date=datetime.datetime.fromtimestamp(
                date,
            ) # pylint: disable=no-member
        if isinstance(date,datetime.date): # pylint: disable=no-member
            self._date=datetime.date(
                date.year,
                date.month,
                date.day,
            ) # pylint: disable=no-member
        elif isinstance(date,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(date)
            if parseResult is None:
                raise TypeError(f'"{date}" is not a Date')
            self.assign(parseResult)
        elif hasattr(date,'date'):
            self.assign(date.date) # type: ignore
        elif hasattr(date,'dateTime'):
            self.assign(asDateTime(date.dateTime)) # type: ignore
        elif hasattr(date,'timestamp'):
            self.assign(asTimestamp(date.timestamp)) # type: ignore
        else:
            raise TypeError(
                f'Unable to parse date type "{date.__class__.__name__}"',
            )

    @property
    def date(self)->datetime.date:
        """
        Identity as a builtin date.
        """
        return self._date

    def __add__(self,other:typing.Any)->"Date":
        """
        Add a timedelta to this date
        """
        if isinstance(other,datetime.timedelta):
            return Date(self._date+other)
        raise TypeError(
            f'Unable to add {other.__class__.__name__} to Date')

    def __sub__(self,other:typing.Any)->"Date":
        """
        Subtract a timedelta from this date
        """
        if isinstance(other,datetime.timedelta):
            return Date(self._date-other)
        raise TypeError(
            f'Unable to subtract {other.__class__.__name__} from Date')

    def __cmp__(self,other:typing.Any)->int:
        """
        Compare this date to another date
        """
        if isinstance(other,Date):
            return (self._date>other._date)-(self._date<other._date)
        raise TypeError(
            f'Unable to compare Date to {other.__class__.__name__}')
date=Date
