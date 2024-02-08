
"""
Represents the difference between two times
"""
import typing
import datetime


TimeDeltaCompatible=typing.Union[datetime.timedelta,"TimeDelta"]


class TimeDelta(datetime.timedelta):
    """
    Represents the difference between two times
    """

    def __init__(self,
        src:typing.Optional[TimeDeltaCompatible]=None):
        datetime.timedelta.__init__(self)
        if src is not None:
            self.assign(src)

    def assign(self,src:TimeDeltaCompatible)->None:
        """
        assign the value of this object
        """
        raise NotImplementedError()

    def copy(self)->"TimeDelta":
        """
        return a copy of this object
        """
        return TimeDelta(self)
timedelta=TimeDelta
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
