"""
Define the seasons based upon agricultural calendar.

This particular model is specific to Northern temperate climates.

To select the preferred name to call "fall", define 
   PREFER_SEASON_NAME='fall'
or
   PREFER_SEASON_NAME='autumn'
before importing (fall is the default)
"""
import typing
from enum import Enum
from ._seasonsBase import *
from dateTools import DateRange


class FuzzyTemperture(Enum):
    """
    NOTE: this value is always one of FREEZING,WARM,etc
    therefore, FuzzyTemperture('41') < FuzzyTemperture('42') is FALSE!  They are both COOL!
    """

    FREEZING=32
    COLD=40
    COOL=50
    ROOM=60
    WARM=70
    HOT=85

    def __init__(self,value:typing.Union[float,str],units:str='f'):
        """
        value can be:
            a temperture 60.1
            a temperture string "60.1f"
            a descriptive string "slightly warm"
        """
        self.comparisonValue:float=0
        self.assign(value,units)

    def assign(self,value:typing.Union[float,str],units:str='f'):
        units=units.lower()
        if isinstance(value,str):
            value=float(value) # TODO: decode freeform strings
        if units=='c':
            self.comparisonValue=value*(9.0/5.0)+32.0
        elif units=='k':
            self.comparisonValue=value*(9.0/5000.0)+32.0
        else:
            self.comparisonValue=value

    def __int__(self)->int:
        """
        Always returns FREEZING,WARM,etc
        """
        if self.comparisonValue<=self.COOL:
            if self.comparisonValue<=self.COLD:
                if self.comparisonValue<=self.FREEZING:
                    return self.FREEZING
                return self.COLD
            return self.COOL
        if self.comparisonValue>=self.WARM:
            if self.comparisonValue>=self.HOT:
                return self.HOT
            return self.WARM
        return self.ROOM

    def __cmp__(self,other:'FuzzyTemperture')->float:
        return int(self)-int(other)

    def toText(self,caps='Aa')->str:
        """
        """
        ret=str(self) # lower case
        if caps[0].isupper():
            if caps[1].iupper():
                return ret.upper()
            return ret[0].upper()+ret[1:]
        return ret

    def __str__(self)->str:
        """
        gives lower case
        """
        return self.__repr__().lower()
    def __repr__(self)->str:
        """
        Always gives the enum name
        If you want more control, try toText()
        """
        if self.comparisonValue<=self.COOL:
            if self.comparisonValue<=self.COLD:
                if self.comparisonValue<=self.FREEZING:
                    return 'FREEZING'
                return 'COLD'
            return 'COOL'
        if self.comparisonValue>=self.WARM:
            if self.comparisonValue>=self.HOT:
                return 'HOT'
            return 'WARM'
        return 'ROOM'


class AgriculturalSeasons(SeasonsBase):
    """
    Agricultural seasons based upon climate rather than astronomy.
    """

    def __init__(self,tempertureByDayOfYear:typing.SupportsIndex[int],tempertureUnits='f',hemisphere='n'):
        self.tempertureByDayOfYear:typing.SupportsIndex[int]=tempertureByDayOfYear
        self.tempertureUnits=tempertureUnits
        self.hemisphere=hemisphere

    @property
    def spring(self)->DateRange:
        """ as defined by non-freezing weather"""
        return
    @property
    def summer(self)->DateRange:
        """ as defined by warm or hot weather"""
        return
    @property
    def winter(self)->DateRange:
        """ as defined by cold/freezing weather"""
        return
    @property
    def fall(self)->DateRange:
        """ as defined by cool weather"""
        return

    def fuzzyTempertureForDayOfYear(self,dayOfYear:int)->FuzzyTemperture:
        return FuzzyTemperture(self.tempertureByDayOfYear[dayOfYear],self.tempertureUnits)

    def getNextFrostDay(self,fromDay:int,maxDay:typing.Optional[int]=None,reverse=False)->typing.Optional[int]:
        """
        Gets the next expected frost day from a given day
        """
        def freezing(i):
            t=self.tempertureByDayOfYear[i]
            return t<=32
        return self.findDay(freezing,fromDay,maxDay,reverse)

    def findDay(self,comparison:typing.Callable[[int],bool],
        fromDay:int,maxDay:typing.Optional[int]=None,reverse=False
        )->typing.Optional[int]:
        """
        Generic matcher that gets the next day number that matches a given comparison
        If no days are found, returns None

        :comparison: fn(dayNumber)->matched
        """
        if maxDay is None:
            maxDay=fromDay
        i=fromDay
        maxdays=len(self.tempertureByDayOfYear)
        while True:
            if comparison(i):
                return i
            if reverse:
                i-=1
                if i<0:
                    i=maxdays-1
            else:
                i+=1
                if i>maxdays:
                    i=0
            if i==maxDay:
                break
        return None

    @property
    def dayOfFirstFrost(self)->typing.Optional[int]:
        """
        """
        ndays=len(self.tempertureByDayOfYear)
        if self.hemisphere.lower()=='s':
            s=0
            e=int(ndays/2)
        else:
            s=int(ndays/2)
            e=ndays
        return self.getNextFrostDay(s,e)
    @property
    def dayOfLastFrost(self)->typing.Optional[int]:
        ndays=len(self.tempertureByDayOfYear)
        if self.hemisphere.lower()=='s':
            s=int(ndays/2)
            e=0
        else:
            s=ndays
            e=int(ndays/2)
        return self.getNextFrostDay(s,e,reverse=True)

    
