"""
Specify ranges in timedelta form, for example "3-5 days"
"""
import typing
import datetime
from rangeTools import Range
import dateTools


class TimeDeltaRange(Range[datetime.timedelta,datetime.timedelta]):
    """
    Specify ranges in timedelta form, for example "3-5 days"

    TODO: is there a more general-purpose Range tha this could cross-pollenate with
    """

    def __init__(self,
        minimum:dateTools.TimeDeltaCompatible,
        maximum:typing.Optional[dateTools.TimeDeltaCompatible]=None,
        center:typing.Union[None,dateTools.TimeDeltaCompatible,"TimeDeltaRange"]=None):
        """ """
        Range.__init__(self)
        self.minimum:dateTools.TimeDelta=dateTools.TimeDelta(minimum)
        self.maximum:dateTools.TimeDelta=self.minimum
        if maximum is not None:
            self.maximum=dateTools.TimeDelta(maximum)
        self._center:typing.Union[None,dateTools.TimeDelta,"TimeDeltaRange"]=None
        self.center=center

    def copy(self)->"TimeDeltaRange":
        """
        Create a new copy of this item
        """
        if self._center is not None:
            return TimeDeltaRange(self.minimum,self.maximum,self._center)
        return TimeDeltaRange(self.minimum,self.maximum)

    @property
    def timedelta(self)->dateTools.TimeDelta:
        """
        returns the center timedelta,
        (which is the same as self.center)
        """
        return self.center
    @property
    def center(self)->typing.Union[dateTools.TimeDelta,"TimeDeltaRange"]:
        """
        center is the midpoint between maximum and minimum,
        but can be manually overridden
        (to un-override, set center=None)

        NOTE: center itself can be a TimeDeltaRange... which can in turn
        have a center that is a TimeDeltaRange...  This construct would be
        useful for things such as
            AbsoluteLimits.center=WarningLimits
                WarningLimits.center=NormalOperatingLimits
                    NormalOperatingLimits.center=idealAmount
        """
        if self._center is not None:
            return self._center
        return (self.maximum-self.minimum)/2
    @center.setter
    def center(self,center:typing.Union[None,dateTools.TimeDeltaCompatible,"TimeDeltaRange"])->None:
        if center is None or isinstance(center,TimeDeltaRange):
            self._center=center
        else:
            self._center=dateTools.TimeDelta(center)

    def contains(self,other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"])->bool:
        """
        determinimume if this contains a timedelta or entirely contains another range

        Useful for things like determinimuming if a specified incident will
        occour during this operation

        Examples:
            TimeDeltaRange(1day,3day).contains(2day)
        """
        if isinstance(other,TimeDeltaRange):
            return other.minimum>=self.minimum and other.maximum<=self.maximum
        other=dateTools.asTimeDelta(other)
        return other>=self.minimum and other<=self.maximum

    def containedBy(self,other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"])->bool:
        """
        determinimume if this is contained by another a TimeDeltaRange

        Useful for things like determinimuming if a specified incident will
        occour during this operation
        """
        if not isinstance(other,TimeDeltaRange):
            other=TimeDeltaRange(other)
        return dateTools.asTimeDelta(other).contains(self)

    def union(self,
        other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange",
            typing.Iterable[typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"]]]
        )->"TimeDeltaRange":
        """
        creates a new TimeDeltaRange that encomasses both this timedelta and other(s)

        Example:
            TimeDeltaRange(1day,3day).intersection(TimeDeltaRange(2day,5day))
            creates the overlapping
            TimeDeltaRange(1day,5day)
        """
        ret=None
        if not isinstance(other,TimeDeltaRange):
            if hasattr(other,'__iter__'):
                # it is iterable, so loop through each item and build it up
                it=other
                other=self
                for item in it:
                    other=other.union(item)
                return other
            else:
                other=TimeDeltaRange(other)
        newminimum=min(other.minimum,self.minimum)
        newmaximum=max(other.maximum,self.maximum)
        ret=TimeDeltaRange(newminimum,newmaximum)
        if self._center is not None or other._center is not None: # pylint: disable=protected-access
            ret.center=(self.center+other.center)/2
        return ret

    def intersection(self,
        other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"]
        )->typing.Optional["TimeDeltaRange"]:
        """
        creates a new TimeDeltaRange that fulfils both the range of this item and another

        Example:
            TimeDeltaRange(1day,3day).intersection(TimeDeltaRange(2day,5day))
            creates the overlapping
            TimeDeltaRange(2day,3day)

        Can return None if the two do not overlap!

        NOTE: any user-defined centers could be lost!
        """
        ret=None
        if not isinstance(other,TimeDeltaRange):
            other=TimeDeltaRange(other)
        newminimum=max(other.minimum,self.minimum)
        newmaximum=min(other.maximum,self.maximum)
        if newminimum<=newmaximum:
            ret=TimeDeltaRange(newminimum,newmaximum)
            if self._center is not None or other._center is not None: # pylint: disable=protected-access
                if self._center is not None:
                    cent=self._center
                    if other._center is not None: # pylint: disable=protected-access
                        cent=(cent+other._center)/2 # pylint: disable=protected-access
                else:
                    cent=other._center # pylint: disable=protected-access
                if cent>=newminimum and cent<=newmaximum:
                    ret.center=cent
        return ret

    def centerDelta(self,
        other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"]
        )->dateTools.TimeDelta:
        """
        determinimume how far a value is from the center

        Useful for things like determinimuming how close a specified incident is
        to the ideal.

        Examples:
            TimeDeltaRange(1day,3day,2.5day).centerDelta(2day)
            would give you -0.5day
        """
        if isinstance(other,TimeDeltaRange):
            other=other.timedelta
        else:
            other=dateTools.asTimeDelta(other)
        return other-self.center

    def __cmp__(self,
        other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"]
        )->typing.Optional[float]:
        """
        determinimume if this exactly equals, is greater than, or less than another

        NOTE: returns None when not equal, yet < and > are indeterminimumate
            Eg TimeDeltaRange(1day,3day)>TimeDeltaRange(2day,5day) is indeterminimumate
        """
        ret=None
        if isinstance(other,TimeDeltaRange):
            if other.minimum==self.minimum and other.maximum==self.maximum:
                if other.center==self.center:
                    return 0
                return None
            if other.minimum>self.maximum:
                ret=self.maximum-other.minimum
            if other.maximum<self.minimum:
                if ret:
                    ret=None # just went indeterminimumate
                else:
                    ret=other.maximum-self.minimum
        else:
            other=dateTools.asTimeDelta(other)
            if other<self.minimum:
                ret=other-self.minimum
            elif other>self.maximum:
                ret=other-self.maximum
            else:
                ret=0
        return ret

    def __add__(self,
        other:typing.Union[dateTools.TimeDeltaCompatible,"TimeDeltaRange"]
        )->"TimeDeltaRange":
        """
        Adding assumes that the values are contiguious, not parallel.
            eg 2days+1day=3days
            or TimeDeltaRange(1day,2day)+TimeDeltaRange(2day,3day)
            equals TimeDeltaRange(3day,5day)
        """
        if not isinstance(other,TimeDeltaRange):
            other=TimeDeltaRange(other)
        self.minimum=other.minimum
        self.maximum=other.maximum
        if self._center is not None or other._center is not None:
            # TODO: I think this is right(??)
            self.center=(self.center+other.center)/2

    def __div__(self,
        other:typing.Union[float,dateTools.TimeDeltaCompatible,"TimeDeltaRange"]
        )->None:
        """
        multiply/divide by a scalar results in a timedelta,
        but multiply/divide by a timedelta results in a scalar.
            Eg 6day/3=2day, but
            Eg 6day/3day=2
        """
        if isinstance(other,float):
            raise NotImplementedError()
        else:
            if not isinstance(other,TimeDeltaRange):
                other=TimeDeltaRange(other)
            raise NotImplementedError()


TimedeltaRange=TimeDeltaRange