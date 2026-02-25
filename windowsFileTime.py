"""
Type information for windows file time timestamps
"""
import typing
from timestamp import Timestamp,TimestampCompatible,asTimestamp
if typing.TYPE_CHECKING:
    from .dateTime import DateTime,DateTimeCompatible


WindowsFileTimestampCompatible=typing.Union[float,int,"WindowsFileTimestamp",TimestampCompatible]
WindowsFileTimeCompatible=WindowsFileTimestampCompatible
WindowsTimestampCompatible=WindowsFileTimestampCompatible
def asWindowsFileTimestamp(
    timestamp:typing.Union[None,WindowsFileTimestampCompatible,str]
    )->"WindowsFileTimestamp":
    """
    Always return a float timestamp
    """
    if isinstance(timestamp,WindowsFileTimestamp):
        return timestamp
    if isinstance(timestamp,str):
        timestamp=float(timestamp)
    return WindowsFileTimestamp(timestamp)
asWindowsFileTime=asWindowsFileTimestamp
asWindowsTimestamp=asWindowsFileTimestamp


class WindowsFileTimestamp:
    """
    Track a windows timestamp with convenient
    conversion to/from posix timestamp and datetime
    """
    WINDOWS_EPOCH=116444736000000000  # Windows FILETIME epoch in 100-nanosecond intervals
    HUNDRED_NANOSECONDS=10000000  # Number of 100-nanosecond intervals in one second

    def __init__(self,value:typing.Optional[WindowsFileTimestampCompatible]=None):
        self._value:float=0
        self.assign(value)

    @property
    def value(self)->int:
        """
        Numeric value of this timestamp
        """
        return int(self._value)
    @value.setter
    def value(self,value:typing.Optional[WindowsFileTimestampCompatible]):
        self.assign(value)

    def assign(self,value:typing.Optional[WindowsFileTimestampCompatible]=None):
        """
        Assign the value of this timestamp
        """
        if value is None:
            import datetime
            value=datetime.datetime.now().timestamp()
        if isinstance(value,WindowsFileTimestamp):
            self._value=int(value)
        else:
            self.posixtime=asTimestamp(value)

    @property
    def posixtime(self)->Timestamp:
        """
        This time converted to a posix/UNIX timestamp
        """
        if self._value<self.WINDOWS_EPOCH:
            raise ValueError("FILETIME value is out of range.")
        return asTimestamp((self._value-self.WINDOWS_EPOCH)//self.HUNDRED_NANOSECONDS)
    @posixtime.setter
    def posixtime(self,value:TimestampCompatible):
        value=asTimestamp(value)
        if value<0:
            raise ValueError("POSIX timestamp cannot be negative.")
        self._value=(value*self.HUNDRED_NANOSECONDS)+self.WINDOWS_EPOCH

    @property
    def timestamp(self)->Timestamp:
        """
        This time converted to a posix/UNIX timestamp
        """
        return self.posixtime
    @timestamp.setter
    def timestamp(self,value:TimestampCompatible):
        self.posixtime=value

    @property
    def datetime(self)->"DateTime":
        """
        Get/set this as a datetime object
        """
        from .dateTime import DateTime
        return DateTime(self.posixtime)
    @datetime.setter
    def datetime(self,datetime:"DateTimeCompatible"):
        from .dateTime import asDateTime
        self.posixtime=asDateTime(datetime).timestamp()

    def __int__(self)->int:
        return self.value
WindowsFileTime=WindowsFileTimestamp
WindowsTimestamp=WindowsFileTimestamp
