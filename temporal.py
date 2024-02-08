"""
This is a python implementation of the javascript
Temporal date/time handling system
"""
import typing


class Temporal:
    """
    This is a python implementation of the javascript
    Temporal date/time handling system.

    (Temporal is endorsed as the likely secessor to Moment.js
    https://momentjs.com/docs/#/-project-status/future/ )

    See also:
        https://tc39.es/proposal-temporal/docs/index.html
        https://tc39.es/proposal-temporal/docs/cookbook.html
        https://github.com/tc39/proposal-temporal
    """

    class TemporalBase:
        def decode(self,s:str):
            ...
        def encode(self)->str:
            ...

    class ZonedDateTime(TemporalBase):
        ...

    class TimeZone:
        ...

    class Calendar:
        ...

    class Duration:
        ...

    class Instance:
        ...

    class PlainDateTime:
        ...

    class PlainDate:
        ...

    class PlainMonthDay:
        ...

    class PlainYearMonth:
        ...

    class PlainTime:
        ...