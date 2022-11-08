"""
A wrapper around a unix time... basically so it doesn't get confused with any old number

Also you can do interesting things like
    UnixTime(datetime.now())+3000
"""
import typing
import datetime


UnixTimeCompatible=typing.Union["UnixTime",int,float,datetime.datetime]
class UnixTime:
    """
    A wrapper around a unix time... basically so it doesn't get confused with any old number

    Also you can do interesting things like
        UnixTime(datetime.now())+3000
    """
    def __init__(self,value:typing.Optional[UnixTimeCompatible]=None):
        if value is None:
            value=datetime.datetime.now()
        if isinstance(value,UnixTime):
            value=value.value
        if isinstance(value,datetime.datetime):
            value=value.timestamp()
        self.value:float=value

    @property
    def datetime(self)->datetime.datetime:
        """
        This unix time as a datetime
        """
        return datetime.datetime.fromtimestamp(self.value)
    @datetime.setter
    def datetime(self,dt:datetime.datetime):
        self.value=dt.timestamp()

    def _toNumericValue(self,value:UnixTimeCompatible)->typing.Union[float,int]:
        if isinstance(value,(int,float)):
            return value
        if isinstance(value,UnixTime):
            return value.value
        return UnixTime(value).value

    def __int__(self):
        return int(self.value)
    def __float__(self):
        return float(self.value)
    def __repr__(self):
        return str(self.value)

    def __gt__(self,value:UnixTimeCompatible)->bool:
        return self.value>self._toNumericValue(value)
    def __lt__(self,value:UnixTimeCompatible)->bool:
        return self.value<self._toNumericValue(value)
    def __eq__(self,value:typing.Any)->bool:
        if not isinstance(value,(UnixTime,int,float,datetime.datetime)):
            return False
        return self.value==self._toNumericValue(value)

    def __add__(self,value:UnixTimeCompatible)->"UnixTime":
        return UnixTime(self.value+self._toNumericValue(value))
    def __sub__(self,value:UnixTimeCompatible)->"UnixTime":
        return UnixTime(self.value-self._toNumericValue(value))
    def __mul__(self,value:UnixTimeCompatible)->"UnixTime":
        return UnixTime(self.value*self._toNumericValue(value))
    def __div__(self,value:UnixTimeCompatible)->"UnixTime":
        return UnixTime(self.value/self._toNumericValue(value))