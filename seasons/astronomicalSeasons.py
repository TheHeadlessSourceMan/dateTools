"""
These are the standard calendar seasons based
strictly on astronomy (solstaces and equinoxes)

To select the preferred name to call "fall", define
   PREFER_SEASON_NAME='fall'
or
   PREFER_SEASON_NAME='autumn'
before importing (fall is the default)
"""
from _seasonsBase import SeasonsBase


class AstronimicalSeasons(SeasonsBase):
    """
    These are the standard calendar seasons based
    strictly on astronomy (solstaces and equinoxes)
    """
    @property
    def spring(self)->"Season":
        """
        Spring season
        """
        raise NotImplementedError()
    @property
    def summer(self)->"Season":
        """
        Summer season
        """
        raise NotImplementedError()
    @property
    def winter(self)->"Season":
        """
        Winter season
        """
        raise NotImplementedError()
    @property
    def fall(self)->"Season":
        """
        Autumn season
        """
        raise NotImplementedError()


Seasons=AstronimicalSeasons
