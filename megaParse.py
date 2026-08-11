#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Smartly parse a date, time, datetime, or date range.
"""
import calendar
import datetime
from email.utils import parsedate_to_datetime
import importlib
import re
import typing

from .ordinalIndicators import ordinalIndicators

try:
    dateutil_easter=importlib.import_module('dateutil.easter')
    dateutil_parser=importlib.import_module('dateutil.parser')
except ImportError:
    dateutil_easter=None
    dateutil_parser=None

if typing.TYPE_CHECKING:
    from .date import Date
    from .dateTime import DateTime
    from .time import Time
    from dateTools import DateRange, SparseDate


ParserResult=typing.Union[
    "Date",
    "Time",
    "DateTime",
    "DateRange",
    "SparseDate",
    None,
]

class Parser:
    """
    Smartly parse any date, time, or date range

    The idea is to separate out numbers(N), text words (Z), and tokens (T)
        "Wednesday, May 23rd 1945 7:30AM"
         Z        T Z   N    N    NTN Z
    and then use the ordering of the elements to determine what is meant

    TODO: unfinished and experimental
    """

    HOLIDAYS=['easter','christmas']
    WEEKDAYS=[day.lower() for day in calendar.day_name]
    IDENTS=[
        ('Z','unknown string'),
        ('N','unknown nummeric'),
        ('M','month'),
        ('W','weekday'),
        ('D','day'),
        ('T','token'),
        ]
    TEXTCASE=[
        'llll',#adamwest
        'llul',#adamWest
        'ulul',#AdamWest
        'ulll',#Adamwest
        'uuuu',#ADAMWEST
        ]
    RANGE_PATTERN=re.compile(
        r'^\s*(?:from\s+)?(?P<start>.+?)\s+'
        r'(?:to|until|through|thru|till)\s+(?P<end>.+?)\s*$',
        re.IGNORECASE,
    )
    SPACED_DASH_RANGE_PATTERN=re.compile(
        r'^\s*(?P<start>.+?)\s+[-–—]+\s+(?P<end>.+?)\s*$',
        re.IGNORECASE,
    )
    COMPACT_TIME_RANGE_PATTERN=re.compile(
        r'^\s*(?P<start>[0-9]{1,2}(?::[0-9]{2}(?::[0-9]{2})?)?'
        r'\s*(?:[ap]\.?m\.?)?)\s*[-–—]+\s*'
        r'(?P<end>[0-9]{1,2}(?::[0-9]{2}(?::[0-9]{2})?)?'
        r'\s*(?:[ap]\.?m\.?)?)\s*$',
        re.IGNORECASE,
    )
    RELATIVE_WEEKDAY_PATTERN=re.compile(
        r'^\s*(?:(?P<modifier>next|last|this|coming)\s+)?'
        r'(?P<weekday>[a-z]+)'
        r'(?:\s*(?:,|at)?\s+(?P<tail>.+))?\s*$',
        re.IGNORECASE,
    )
    ORDINAL_SUFFIX_PATTERN=re.compile(
        r'(?<=\d)(?:' + '|'.join(ordinalIndicators[1:]) + r')\b',
        re.IGNORECASE,
    )
    TIME_ONLY_PATTERN=re.compile(
        r'^\s*(?:[0-9]{1,2}(?::[0-9]{2}(?::[0-9]{2})?)?'
        r'\s*(?:[ap]\.?m\.?)?|noon|midnight)\s*$',
        re.IGNORECASE,
    )
    HAS_TIME_PATTERN=re.compile(
        r'(?<!\d)[0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?(?!\d)|'
        r'(?<!\d)[0-9]{1,2}\s*(?:[ap]\.?m\.?)(?![a-z])|'
        r'\b(?:noon|midnight|now)\b',
        re.IGNORECASE,
    )
    HAS_DATE_PATTERN=re.compile(
        r'\b(?:today|tomorrow|yesterday|christmas|xmas|easter|'
        r'mon(?:day)?|tue(?:s|sday)?|wed(?:nesday)?|'
        r'thu(?:r|rs|rsday)?|fri(?:day)?|sat(?:urday)?|sun(?:day)?|'
        r'jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|'
        r'jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t|tember)?|'
        r'oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)\b|'
        r'\b[0-9]{4}[-/\.][0-9]{1,2}(?:[-/\.][0-9]{1,4})?\b|'
        r'\b[0-9]{1,2}[-/\.][0-9]{1,2}(?:[-/\.][0-9]{2,4})?\b',
        re.IGNORECASE,
    )
    MERIDIEM_PATTERN=re.compile(r'([ap])\.?m\.?$', re.IGNORECASE)
    WEEKDAY_LOOKUP={
        'mon':0,
        'monday':0,
        'tue':1,
        'tues':1,
        'tuesday':1,
        'wed':2,
        'wednesday':2,
        'thu':3,
        'thur':3,
        'thurs':3,
        'thursday':3,
        'fri':4,
        'friday':4,
        'sat':5,
        'saturday':5,
        'sun':6,
        'sunday':6,
    }

    def findTextCase(self,s:str)->str:
        """
        given a word pair, determine text case

        IMPORTANT it only works if "s" has two words in it
        """
        if s[0].isupper():
            first='u'
        else:
            first='l'
        middle='u'
        second='l'
        hasLower=False
        hasUpper=False
        for c in s[1:]:
            if c.isupper():
                if not hasUpper:
                    hasUpper=True
                    second='h'
                    if hasLower: # failfast
                        break
            else:
                if not hasLower:
                    hasLower=True
                    middle='l'
                    if hasUpper: # failfast
                        break
        return ''.join((first,middle,second,middle))

    def parse(self,
        s:typing.Union[None,str,bytes]="tuesday,may 3",
        referenceDate:typing.Union[
            datetime.date,
            datetime.datetime,
            None,
            str,
            bytes,
        ]=None,
        )->ParserResult:
        """
        Parse a date string

        :param referenceDate: used, for example if an email says
            "meet me next tuesday",
            then the referenceDate would be the send date of that email.
            (default value is now)

        returns a Date, Time, DateTime, DateRange, SparseDate, or None
        """
        if s is None:
            return None
        if isinstance(s,bytes):
            s=s.decode('utf-8','ignore')
        s=self._normalize_text(s)
        if not s:
            return None
        reference_dt=self._coerce_reference_datetime(referenceDate)
        sparse_result=self._parse_sparse(s,reference_dt)
        if sparse_result is not None:
            return sparse_result
        if self._looks_like_range_text(s):
            return self._parse_range(s,reference_dt)
        direct_result=self._parse_direct_value(s,reference_dt)
        if direct_result is not None:
            return direct_result
        parsed=self._parse_datetime_text(s,reference_dt)
        if parsed is None:
            return None
        if self._is_time_only_text(s):
            return self._make_time(parsed.timetz().replace(tzinfo=None))
        if self._contains_time_hint(s) and self._contains_date_hint(s):
            return self._make_datetime(parsed)
        return self._make_date(parsed.date())

    def _normalize_text(self,text:str)->str:
        for plain,superscript in enumerate('⁰¹²³⁴⁵⁶⁷⁸⁹'):
            text=text.replace(superscript,str(plain))
        for src,dst in (
            ('ˢᵗ','st'),
            ('ⁿᵈ','nd'),
            ('ʳᵈ','rd'),
            ('ᵗʰ','th'),
            ('ˢᵀ','st'),
            ('ᴺᴰ','nd'),
            ('ᴿᴰ','rd'),
            ('ᵀᴴ','th'),
        ):
            text=text.replace(src,dst)
        text=text.replace('–','-').replace('—','-')
        text=self.ORDINAL_SUFFIX_PATTERN.sub('',text)
        text=re.sub(r'\b([ap])\.?m\.?\b',r'\1m',text,flags=re.IGNORECASE)
        text=re.sub(r'\bsept\b','sep',text,flags=re.IGNORECASE)
        text=re.sub(r'\s+', ' ', text)
        return text.strip()

    def _coerce_reference_datetime(self,
        referenceDate:typing.Union[
            datetime.date,
            datetime.datetime,
            None,
            str,
            bytes,
        ],
        )->datetime.datetime:
        if referenceDate is None:
            return datetime.datetime.now()
        if isinstance(referenceDate,bytes):
            referenceDate=referenceDate.decode('utf-8','ignore')
        if isinstance(referenceDate,str):
            parsed=self.parse(referenceDate)
            coerced=self._coerce_result_datetime(parsed,None)
            if coerced is None:
                raise ValueError(
                    f'referenceDate "{referenceDate}" must be a date/time',
                )
            return coerced
        if isinstance(referenceDate,datetime.datetime):
            return referenceDate
        return datetime.datetime.combine(referenceDate,datetime.time())

    def _parse_range(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->typing.Optional["DateRange"]:
        if self._has_dangling_range_connector(self_text):
            return None
        match=self.RANGE_PATTERN.match(self_text)
        if match is None:
            match=self.SPACED_DASH_RANGE_PATTERN.match(self_text)
        if match is None:
            match=self.COMPACT_TIME_RANGE_PATTERN.match(self_text)
        if match is None:
            return None
        start_text=match.group('start').strip()
        end_text=match.group('end').strip()
        start_text,end_text=self._inherit_meridiem(start_text,end_text)
        start_result=self._parse_single_value(start_text,reference_dt)
        if start_result is None:
            return None
        start_dt=self._coerce_result_datetime(start_result,reference_dt)
        if start_dt is None:
            return None
        end_result=self._parse_single_value(end_text,start_dt)
        if end_result is None:
            return None
        end_dt=self._coerce_result_datetime(end_result,start_dt)
        if end_dt is None:
            return None
        if self._is_time_result(start_result) \
            and self._is_time_result(end_result):
            if end_dt<start_dt:
                end_dt=end_dt+datetime.timedelta(days=1)
        elif self._is_date_result(start_result) \
            and self._is_time_result(end_result):
            end_time=self._coerce_result_time(end_result)
            if end_time is None:
                return None
            end_dt=datetime.datetime.combine(start_dt.date(),end_time)
        if end_dt<start_dt:
            return None
        from .dateRanges import DateRange
        return DateRange((start_dt,end_dt))

    def _looks_like_range_text(self,text:str)->bool:
        if self.COMPACT_TIME_RANGE_PATTERN.match(text):
            return True
        if re.search(r'\s[-–—]+\s',text):
            return True
        return re.search(
            r'\b(?:to|until|through|thru|till)\b',
            text,
            re.IGNORECASE,
        ) is not None

    def _has_dangling_range_connector(self,text:str)->bool:
        if re.match(r'^\s*(?:to|until|through|thru|till)\b',text,re.I):
            return True
        if re.search(r'\b(?:to|until|through|thru|till)\s*$',text,re.I):
            return True
        if re.match(r'^\s*from\b',text,re.I) \
            and self.RANGE_PATTERN.match(text) is None:
            return True
        return False

    def _parse_single_value(self,
        text:str,
        reference_dt:datetime.datetime,
        )->ParserResult:
        sparse_result=self._parse_sparse(text,reference_dt)
        if sparse_result is not None:
            return sparse_result
        direct_result=self._parse_direct_value(text,reference_dt)
        if direct_result is not None:
            return direct_result
        parsed=self._parse_datetime_text(text,reference_dt)
        if parsed is None:
            return None
        if self._is_time_only_text(text):
            return self._make_time(parsed.timetz().replace(tzinfo=None))
        if self._contains_time_hint(text) and self._contains_date_hint(text):
            return self._make_datetime(parsed)
        return self._make_date(parsed.date())

    def _parse_sparse(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->typing.Optional["SparseDate"]:
        lower=self_text.lower()
        from .SparseDate import SparseDate
        if lower in ('daily','every day','each day'):
            return SparseDate(reference_dt.date(),skipWeekdays=[],holidays=[])
        if lower in (
            'weekday',
            'weekdays',
            'every weekday',
            'every weekdays',
            'business day',
            'business days',
            'workday',
            'workdays',
        ):
            return SparseDate(
                reference_dt.date(),
                skipWeekdays=(5,6),
                holidays=[],
            )
        if lower in ('weekend','weekends','every weekend','every weekends'):
            return SparseDate(
                reference_dt.date(),
                skipWeekdays=(0,1,2,3,4),
                holidays=[],
            )
        match=re.match(
            r'^(?:every|each)\s+(?P<start>[a-z]+)'
            r'(?:\s+(?:to|through|thru)\s+(?P<end>[a-z]+))?s?$',
            lower,
        )
        if match is None:
            return None
        start_name=match.group('start')
        if start_name not in self.WEEKDAY_LOOKUP:
            return None
        end_name=match.group('end')
        allowed=self._weekday_span(start_name,end_name)
        start_date=self._advance_to_allowed(reference_dt.date(),allowed)
        skip=[day for day in range(7) if day not in allowed]
        return SparseDate(start_date,skipWeekdays=skip,holidays=[])

    def _parse_direct_value(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->ParserResult:
        lower=self_text.lower()
        if lower=='now':
            return self._make_datetime(reference_dt)
        if lower=='today':
            return self._make_date(reference_dt.date())
        if lower=='tomorrow':
            return self._make_date(
                reference_dt.date()+datetime.timedelta(days=1),
            )
        if lower=='yesterday':
            return self._make_date(
                reference_dt.date()-datetime.timedelta(days=1),
            )
        if lower=='noon':
            return self._make_time(datetime.time(12,0))
        if lower=='midnight':
            return self._make_time(datetime.time(0,0))
        holiday=self._parse_holiday(lower,reference_dt)
        if holiday is not None:
            return holiday
        weekday=self._parse_relative_weekday(self_text,reference_dt)
        if weekday is not None:
            return weekday
        return None

    def _parse_holiday(self,
        lower:str,
        reference_dt:datetime.datetime,
        )->typing.Optional[ParserResult]:
        if lower not in ('christmas','xmas','easter'):
            return None
        year=reference_dt.year
        if lower in ('christmas','xmas'):
            holiday=datetime.date(year,12,25)
        else:
            if dateutil_easter is None:
                return None
            holiday=dateutil_easter.easter(year)
        if holiday<reference_dt.date():
            if lower in ('christmas','xmas'):
                holiday=datetime.date(year+1,12,25)
            elif dateutil_easter is not None:
                holiday=dateutil_easter.easter(year+1)
        return self._make_date(holiday)

    def _parse_relative_weekday(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->ParserResult:
        match=self.RELATIVE_WEEKDAY_PATTERN.match(self_text)
        if match is None:
            return None
        weekday_name=match.group('weekday').lower()
        if weekday_name not in self.WEEKDAY_LOOKUP:
            return None
        modifier=(match.group('modifier') or '').lower()
        target=self.WEEKDAY_LOOKUP[weekday_name]
        current=reference_dt.weekday()
        if modifier=='last':
            delta=(current-target) % 7
            delta=7 if delta==0 else delta
            base_date=reference_dt.date()-datetime.timedelta(days=delta)
        else:
            delta=(target-current) % 7
            if modifier in ('next','coming') and delta==0:
                delta=7
            base_date=reference_dt.date()+datetime.timedelta(days=delta)
        tail=match.group('tail')
        if tail is None:
            return self._make_date(base_date)
        time_result=self._parse_single_value(
            tail,
            datetime.datetime.combine(base_date,reference_dt.time()),
        )
        if time_result is None:
            return self._make_date(base_date)
        parsed_time=self._coerce_result_time(time_result)
        if parsed_time is None:
            parsed_dt=self._coerce_result_datetime(
                time_result,
                datetime.datetime.combine(base_date,reference_dt.time()),
            )
            if parsed_dt is None:
                return self._make_date(base_date)
            return self._make_datetime(parsed_dt)
        return self._make_datetime(
            datetime.datetime.combine(base_date,parsed_time),
        )

    def _parse_datetime_text(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->typing.Optional[datetime.datetime]:
        default=self._default_datetime_for_text(self_text,reference_dt)
        iso_text=self_text.replace('Z','+00:00')
        try:
            return datetime.datetime.fromisoformat(iso_text)
        except ValueError:
            pass
        if dateutil_parser is not None:
            dayfirst_options=[self._should_use_day_first(self_text),False,True]
            for dayfirst in dict.fromkeys(dayfirst_options):
                try:
                    return dateutil_parser.parse(
                        self_text,
                        default=default,
                        dayfirst=dayfirst,
                        fuzzy=True,
                    )
                except (OverflowError,TypeError,ValueError):
                    continue
        try:
            return parsedate_to_datetime(self_text)
        except (TypeError,ValueError,IndexError,OverflowError):
            pass
        for pattern in self._strptime_patterns(self_text):
            parse_text=self_text
            parse_pattern=pattern
            has_year=('%Y' in pattern) or ('%y' in pattern)
            has_month_or_day=any(
                token in pattern for token in ('%d','%m','%b','%B')
            )
            if not has_year and has_month_or_day:
                parse_text=f'{self_text} {default.year}'
                parse_pattern=f'{pattern} %Y'
            try:
                parsed=datetime.datetime.strptime(parse_text,parse_pattern)
            except ValueError:
                continue
            if '%Y' not in pattern and '%y' not in pattern:
                parsed=parsed.replace(year=default.year)
            if '%m' not in pattern and '%b' not in pattern \
                and '%B' not in pattern:
                parsed=parsed.replace(month=default.month)
            if '%d' not in pattern:
                parsed=parsed.replace(day=default.day)
            return parsed
        return None

    def _default_datetime_for_text(self,
        self_text:str,
        reference_dt:datetime.datetime,
        )->datetime.datetime:
        if self._is_time_only_text(self_text):
            return reference_dt.replace(minute=0,second=0,microsecond=0)
        default=reference_dt.replace(
            month=1,
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        if re.search(r'\b[0-9]{1,2}[-/\.][0-9]{1,2}\b',self_text):
            default=default.replace(month=reference_dt.month,day=1)
        return default

    def _strptime_patterns(self,self_text:str)->typing.Iterable[str]:
        lower=self_text.lower()
        if self._is_time_only_text(lower):
            return (
                '%H:%M:%S',
                '%H:%M',
                '%I:%M%p',
                '%I%p',
                '%H%M',
            )
        if self._contains_time_hint(lower):
            return (
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%Y/%m/%d %H:%M:%S',
                '%Y/%m/%d %H:%M',
                '%m/%d/%Y %H:%M',
                '%m/%d/%Y %I:%M%p',
                '%d/%m/%Y %H:%M',
                '%d/%m/%Y %I:%M%p',
                '%b %d %Y %H:%M',
                '%b %d %Y %I:%M%p',
                '%B %d %Y %H:%M',
                '%B %d %Y %I:%M%p',
            )
        return (
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y.%m.%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%m/%d/%y',
            '%d/%m/%y',
            '%Y%m%d',
            '%b %d %Y',
            '%b %d, %Y',
            '%B %d %Y',
            '%B %d, %Y',
            '%b %d',
            '%B %d',
            '%d %b',
            '%d %B',
            '%d %b %Y',
            '%d %B %Y',
            '%b %Y',
            '%B %Y',
            '%Y',
        )

    def _should_use_day_first(self,self_text:str)->bool:
        match=re.search(
            r'\b(?P<left>[0-9]{1,2})[-/\.](?P<right>[0-9]{1,2})'
            r'(?:[-/\.](?P<year>[0-9]{2,4}))?\b',
            self_text,
        )
        if match is None:
            return False
        left=int(match.group('left'))
        right=int(match.group('right'))
        if left>12 and right<=12:
            return True
        if right>12 and left<=12:
            return False
        return False

    def _inherit_meridiem(self,
        start_text:str,
        end_text:str,
        )->typing.Tuple[str,str]:
        start_meridiem=self.MERIDIEM_PATTERN.search(start_text)
        end_meridiem=self.MERIDIEM_PATTERN.search(end_text)
        if start_meridiem is None and end_meridiem is not None \
            and self.TIME_ONLY_PATTERN.match(start_text):
            start_text=f'{start_text}{end_meridiem.group(0)}'
        elif end_meridiem is None and start_meridiem is not None \
            and self.TIME_ONLY_PATTERN.match(end_text):
            end_text=f'{end_text}{start_meridiem.group(0)}'
        return start_text,end_text

    def _contains_time_hint(self,text:str)->bool:
        return self.HAS_TIME_PATTERN.search(text) is not None

    def _contains_date_hint(self,text:str)->bool:
        return self.HAS_DATE_PATTERN.search(text) is not None

    def _is_time_only_text(self,text:str)->bool:
        return self.TIME_ONLY_PATTERN.match(text) is not None

    def _weekday_span(self,
        start_name:str,
        end_name:typing.Optional[str],
        )->typing.Set[int]:
        start=self.WEEKDAY_LOOKUP[start_name]
        if end_name is None:
            return {start}
        end=self.WEEKDAY_LOOKUP[end_name]
        allowed:set[int]=set()
        day=start
        while True:
            allowed.add(day)
            if day==end:
                break
            day=(day+1) % 7
        return allowed

    def _advance_to_allowed(self,
        start_date:datetime.date,
        allowed:typing.Set[int],
        )->datetime.date:
        date_value=start_date
        for _ in range(7):
            if date_value.weekday() in allowed:
                return date_value
            date_value=date_value+datetime.timedelta(days=1)
        return start_date

    def _coerce_result_datetime(self,
        result:ParserResult,
        reference_dt:typing.Optional[datetime.datetime],
        )->typing.Optional[datetime.datetime]:
        if result is None:
            return None
        if isinstance(result,datetime.datetime):
            return result
        if isinstance(result,datetime.date):
            return datetime.datetime.combine(result,datetime.time())
        if isinstance(result,datetime.time):
            base_date=datetime.date.today()
            if reference_dt is not None:
                base_date=reference_dt.date()
            return datetime.datetime.combine(base_date,result)
        if hasattr(result,'datetime'):
            value=typing.cast(typing.Any,result).datetime
            if isinstance(value,datetime.datetime):
                return value
        if hasattr(result,'currentDate'):
            current=typing.cast(typing.Any,result).currentDate
            if isinstance(current,datetime.date):
                return datetime.datetime.combine(current,datetime.time())
        date_value=self._coerce_result_date(result)
        if date_value is not None:
            return datetime.datetime.combine(date_value,datetime.time())
        time_value=self._coerce_result_time(result)
        if time_value is not None:
            base_date=datetime.date.today()
            if reference_dt is not None:
                base_date=reference_dt.date()
            return datetime.datetime.combine(base_date,time_value)
        return None

    def _coerce_result_date(self,
        result:ParserResult,
        )->typing.Optional[datetime.date]:
        if result is None:
            return None
        if isinstance(result,datetime.datetime):
            return typing.cast(datetime.datetime,result).date()
        if isinstance(result,datetime.date):
            return result
        if hasattr(result,'date'):
            value=typing.cast(typing.Any,result).date
            if isinstance(value,datetime.date):
                return value
            if hasattr(value,'date'):
                nested=value.date
                if isinstance(nested,datetime.date):
                    return nested
        if hasattr(result,'currentDate'):
            current=typing.cast(typing.Any,result).currentDate
            if isinstance(current,datetime.date):
                return current
        return None

    def _coerce_result_time(self,
        result:ParserResult,
        )->typing.Optional[datetime.time]:
        if result is None:
            return None
        if isinstance(result,datetime.datetime):
            return result.timetz().replace(tzinfo=None)
        if isinstance(result,datetime.time):
            return result
        if hasattr(result,'time'):
            value=typing.cast(typing.Any,result).time
            if isinstance(value,datetime.time):
                return value
            if hasattr(value,'time'):
                nested=value.time
                if isinstance(nested,datetime.time):
                    return nested
        return None

    def _is_time_result(self,result:ParserResult)->bool:
        return self._coerce_result_time(result) is not None \
            and self._coerce_result_date(result) is None

    def _is_date_result(self,result:ParserResult)->bool:
        return self._coerce_result_date(result) is not None \
            and self._coerce_result_time(result) is None

    def _make_date(self,value:datetime.date)->"Date":
        from .date import Date
        return Date(value)

    def _make_time(self,value:datetime.time)->"Time":
        from .time import Time
        return Time(value)

    def _make_datetime(self,value:datetime.datetime)->"DateTime":
        from .dateTime import DateTime
        return DateTime(value)


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  megaParse.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
