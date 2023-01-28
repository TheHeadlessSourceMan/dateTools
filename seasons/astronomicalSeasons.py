"""
These are the standard calendar seasons based
strictly on astronomy (solstaces and equinoxes)

To select the preferred name to call "fall", define 
   PREFER_SEASON_NAME='fall'
or
   PREFER_SEASON_NAME='autumn'
before importing (fall is the default)
"""
from ._seasonsBase import *

    
class AstronimicalSeasons(SeasonsBase):
    """
    These are the standard calendar seasons based
    strictly on astronomy (solstaces and equinoxes)
    """
    @property
    def spring(self)->Season:
        raise NotImplementedError()
    @property
    def summer(self)->Season:
        raise NotImplementedError()
    @property
    def winter(self)->Season:
        raise NotImplementedError()
    @property
    def fall(self)->Season:
        raise NotImplementedError()


Seasons=AstronimicalSeasons