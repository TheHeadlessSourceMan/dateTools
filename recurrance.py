"""
A general-purpose time recurrance (consider something like a standing meeting in a calendar)
"""
import typing
import datetime
from dateTools import TimeUnitValueTypes,TimeUnit,Month


class Recurrance:
    """
    A general-purpose time recurrance (consider something like a standing meeting in a calendar)

    TODO: be able to export to ical
    """
    if typing.TYPE_CHECKING:
        from dateTools import When

    def __init__(self,timeUnit:TimeUnit=Month,
        indices:typing.Union[None,int,float,typing.Iterable[float]]=None,
        starting:typing.Optional[datetime.datetime]=None,
        ending:typing.Optional[datetime.datetime]=None):
        """

        :param timeUnit: _description_, defaults to Month
        :type timeUnit: TimeUnit, optional
        :param indices: one or more indices of the next lesser time unit
            eg Recurrance(Month,15,30) would be the 15th and 30th of the month
            defaults to None
        :type indices: typing.optional[float], optional
        :param starting: a date which this recurrance starts, defaults to Month
        :param ending: a date which this recurrance ends, defaults to Month
        """
        self.starting:typing.Optional[datetime.datetime]=starting
        self.ending:typing.Optional[datetime.datetime]=ending
        self.timeUnit:typing.Optional[TimeUnitValueTypes]=timeUnit
        if indices is None:
            indices=[-1]
        elif isinstance(indices,(int,float)):
            indices=[indices]
        else:
            indices=list(indices)
        self.indices:typing.List[float]=indices

    def between(self,
        start:typing.Optional[datetime.datetime]=None,
        end:typing.Optional[datetime.datetime]=None)->typing.Generator["When",None,None]:
        """
        Return all occourances between the given dates

        TODO: move to Recurrance

        :param start: _description_
        :type start: datetime.datetime
        :param end: _description_
        :type end: datetime.datetime
        """
        if start is None:
            start=datetime.datetime.now()
        if end is None:
            end=datetime.datetime.now()
        instance:typing.Optional[datetime.datetime]=self.next(start)
        while instance is not None and instance<end:
            yield instance
            instance=self.next(instance)

    def instances(self,
        start:typing.Optional[datetime.datetime]=None,
        end:typing.Optional[datetime.datetime]=None)->int:
        """
        Count how many instances are between the given dates

        TODO: move to Recurrance

        :param start: _description_
        :type start: datetime.datetime
        :param end: _description_
        :type end: datetime.datetime
        """
        return len(list(self.between(start,end)))

    def value(self,fromTime:typing.Optional[datetime.datetime]=None)->typing.Union[float,int]:
        """
        Get the next recurrance value from a specific time

        :param fromTime: the time to get the value at, defaults to Now
        :type fromTime: typing.Optional[datetime.datetime], optional
        :return: the floating point value
        :rtype: typing.Union[float,int]
        """
        if fromTime is None:
            fromTime=datetime.datetime.now()
        return float(self.next().value)

    def next(self,
        fromTime:typing.Optional[datetime.datetime]=None
        )->typing.Optional[datetime.datetime]:
        """
        Get the next instance from a certain time(or from now)

        Can return None if there is no more available

        :param fromTime: time to start with, defaults to now
        :type fromTime: typing.Optional[datetime.datetime], optional
        :return: The instance found or None
        :rtype: TimeUnit
        """
        if fromTime is None:
            fromTime=datetime.datetime.now()
        # TODO: Next is not written
        return None

    def previous(self,fromTime:typing.Optional[datetime.datetime])->TimeUnit:
        """
        Get the previous instance from a certain time(or from now)

        Can return None if there is no more available

        :param fromTime: time to start with, defaults to now
        :type fromTime: typing.Optional[datetime.datetime], optional
        :return: The instance found or None
        :rtype: TimeUnit
        """
        if fromTime is None:
            fromTime=datetime.datetime.now()
        # TODO: Previous is not written