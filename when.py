"""
A datatype for answering "when" something occours
"""
import typing
import datetime
from dateTools import DatetimeRange

When=typing.Union[datetime.datetime,DatetimeRange]
