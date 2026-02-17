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


class Date(
    datetime.date): # pylint: disable=no-member
    """
    Extended version of the datetime object
    """
    def __new__(cls,*args,**kwargs)->"Date":
        """
        Need to override this so datetime.date.__new__() is not called
        """
        return super().__new__(cls,*args,**kwargs)

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
            date=datetime.datetime.fromtimestamp(date) # pylint: disable=no-member
        if isinstance(date,datetime.date): # pylint: disable=no-member
            self._date=datetime.date(date.day,date.month,date.year) # pylint: disable=no-member
        elif isinstance(date,str):
            from .megaParse import Parser,ParserResult
            parseResult:ParserResult=Parser().parse(date)
            if parseResult is None:
                raise TypeError(f'"{date}" is not a Date')
            if not isinstance(parseResult,(datetime.date,datetime.datetime)): # pylint: disable=isinstance-second-argument-not-valid-type,no-member
                raise TypeError(f'"{date}" parses to a {parseResult.__class__.__name__}, not a Date') # noqa: E501 # pylint: disable=line-too-long
            self.assign(parseResult)
        elif hasattr(date,'date'):
            self.assign(date.date) # type: ignore
        elif hasattr(date,'dateTime'):
            self.assign(asDateTime(date.dateTime)) # type: ignore
        elif hasattr(date,'timestamp'):
            self.assign(asTimestamp(date.timestamp)) # type: ignore
        else:
            raise TypeError(f'Unable to parse date type "{date.__class__.__name__}"')
date=Date
