"""
Base classes and types for working with seasons

To select the preferred name to call "fall", define
   PREFER_SEASON_NAME='fall'
or
   PREFER_SEASON_NAME='autumn'
before importing (fall is the default)
"""
import typing
import re
from dateTools import Date,DateRange,DateFormatException


SEASON_NAMES_FALL=('spring','summer','winter','fall','fall')
SEASON_NAMES_AUTUMN=('spring','summer','winter','fall','autumn')
if PREFER_SEASON_NAME=='autumn': # type:ignore
    SEASON_NAMES=SEASON_NAMES_AUTUMN
else:
    SEASON_NAMES=SEASON_NAMES_FALL

AreaSubdivReText=r"""(the\s+)?(mid(dle\s+of\s+)|early|late)[\s,-]*"""
SeasonReText=r"""(?P<subdiv>"""+AreaSubdivReText+r""")?(?P<season>spring|summer|winter|fall|autumn)"""
SeasonRangeReText=r"""((?P<subdiv>"""+AreaSubdivReText+r""")(\s*(to|[-])\s*(?P<subdivTo>"""+AreaSubdivReText+r"""))?)?(?P<season>spring|summer|winter|fall|autumn)"""

SeasonRe=re.compile(SeasonReText,re.IGNORECASE|re.DOTALL)
SeasonRangeRe=re.compile(SeasonRangeReText,re.IGNORECASE|re.DOTALL)


class Season(DateRange):
    """
    General-purpose season.

    You usually DO NOT create this directly, but do something like:
        Seasons.summer
        Seasons.get('late spring')
        AgriculturalSeasons.get('late spring')
    """

    def __init__(self,parent:"SeasonsBase",name:str,fromDay:Date,toDay:Date):
        self._isSubSeason=False
        DateRange.__init__(self,fromDay,toDay)

    def subRange(self,s:str)->DateRange:
        """
        Get a sub-season ("early","mid", or "late")
        """
        dr=DateRange(self,subRange(s))
        if not self._isSubSeason:
            dr=SeasonBase(s,dr.fromDay,dr.toDay)
            dr._isSubSeason=True
        return dr

class SeasonsBase:
    """
    Base class for seasons
    """
    def get(self,seasonDesc:str)->SeasonBase:
        """
        :seasonDesc: anything like
        """
        m=SeasonRe.match(seasonDesc)
        if m is None:
            raise DateFormatException(seasonDesc)
        seasonName=m.group('season').lower()
        ret=typing.cast("SeasonBase",getattr(self,seasonName))
        if 'subdiv' in ret.groups.names():
            ret=ret.subRange(m.group('subdiv'))
        return ret
    def getRange(self,seasonDesc:str)->DateRange:
        """
        :seasonDesc: anything like
            "mid-spring to late summer"
            "mid spring-mid summer"
            ...
        """
        m=SeasonRe.match(seasonDesc)
        if m is None:
            raise DateFormatException(seasonDesc)
        seasonName=m.group('season').lower()
        ret=typing.cast(SeasonBase,getattr(self,seasonName))
        if 'subdivTo' in ret.groups.names():
            ret1=ret.subRange(m.group('subdiv'))
            ret2=ret.subRange(m.group('subdivTo'))
            ret=DateRange(ret1,ret2) # new range that covers both
        elif 'subdiv' in ret.groups.names():
            ret=ret.subRange(m.group('subdiv'))
        return ret
    @property
    def spring(self)->"SeasonBase":
        """
        Spring season
        """
        raise NotImplementedError()
    @property
    def summer(self)->"SeasonBase":
        """
        Summer season
        """
        raise NotImplementedError()
    @property
    def winter(self)->"SeasonBase":
        """
        Winter season
        """
        raise NotImplementedError()
    @property
    def fall(self)->"SeasonBase":
        """
        Autumn season
        """
        raise NotImplementedError()
    @property
    def autumn(self)->"SeasonBase":
        """
        Autumn season
        """
        return self.fall
