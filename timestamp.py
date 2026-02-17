"""
Type information for unix timestamps
"""
import typing


class HasTimestamp(typing.Protocol):
    """
    Duck typing for a class with a unix timestamp member
    """
    timestamp:typing.Union[float,int]

TimestampCompatible=typing.Union[float,int,HasTimestamp]
Timestamp=float
def asTimestamp(timestamp:typing.Union[TimestampCompatible,str])->Timestamp:
    """
    Always return a float timestamp
    """
    if hasattr(timestamp,'timestamp'):
        timestamp=typing.cast(HasTimestamp,timestamp)
        timestamp=timestamp.timestamp
    return float(timestamp) # type: ignore
