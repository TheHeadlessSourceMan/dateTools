#!/usr/bin/env
# -*- coding: utf-8 -*-
"""Parser-focused unit tests for dateTools.megaParse."""

# pylint: disable=wrong-import-position

import datetime
import os
import sys
from typing import Any, Optional
import unittest
from dateTools.dateRanges import DateRange
from dateTools.megaParse import Parser
from dateTools.SparseDate import SparseDate


HERE=os.path.abspath(__file__).rsplit(os.sep,1)[0]
PARENT=os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0,PARENT)


class ParserTests(unittest.TestCase):
    """Stress tests for parser behavior, including edge cases."""

    def setUp(self)->None:
        self.parser=Parser()
        self.ref=datetime.datetime(2025,1,15,10,30,0)

    def parse(self,
        text:Optional[Any],
        reference:Optional[datetime.datetime]=None,
        )->Any:
        # Keep one deterministic reference instant for reproducible assertions.
        if reference is None:
            reference=self.ref
        return self.parser.parse(text,reference)

    def assertDate(self,
        result:Any,
        year:int,
        month:int,
        day:int,
        )->None:
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result,'date'))
        date_value=result.date
        # dateTools wrappers may expose nested date/date-like members.
        if hasattr(date_value,'date'):
            date_value=date_value.date
        self.assertEqual(datetime.date(year,month,day),date_value)

    def assertTime(self,
        result:Any,
        hour:int,
        minute:int,
        second:int=0,
        )->None:
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result,'time'))
        time_value=result.time
        # dateTools wrappers may expose nested time/time-like members.
        if hasattr(time_value,'time'):
            time_value=time_value.time
        self.assertEqual(hour,time_value.hour)
        self.assertEqual(minute,time_value.minute)
        self.assertEqual(second,time_value.second)

    def assertDateTime(self,
        result:Any,
        year:int,
        month:int,
        day:int,
        hour:int,
        minute:int,
        second:int=0,
        )->None:
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result,'datetime'))
        dt_value=result.datetime
        self.assertEqual(
            datetime.datetime(year,month,day,hour,minute,second),
            dt_value,
        )

    def asDatetime(self,value:Any)->datetime.datetime:
        # Normalize dateTools wrapper objects to builtin datetime.
        if isinstance(value,datetime.datetime):
            return value
        if hasattr(value,'datetime'):
            return value.datetime
        if hasattr(value,'date') and hasattr(value,'time'):
            date_value=value.date
            time_value=value.time
            if hasattr(date_value,'date'):
                date_value=date_value.date
            if hasattr(time_value,'time'):
                time_value=time_value.time
            return datetime.datetime.combine(date_value,time_value)
        raise AssertionError(f'Cannot coerce value to datetime: {value!r}')

    def asTime(self,value:Any)->datetime.time:
        # Normalize dateTools wrapper objects to builtin time.
        if isinstance(value,datetime.time):
            return value
        if hasattr(value,'time'):
            time_value=value.time
            if hasattr(time_value,'time'):
                time_value=time_value.time
            return time_value
        raise AssertionError(f'Cannot coerce value to time: {value!r}')

    def test_none_and_empty_inputs(self)->None:
        self.assertIsNone(self.parse(None))
        self.assertIsNone(self.parse(''))
        self.assertIsNone(self.parse('   \t  \n'))

    def test_bytes_and_unicode_ordinal_normalization(self)->None:
        result=self.parse(b'  MAY 5\xe1\xb5\x97\xca\xb0   2024  ')
        self.assertDate(result,2024,5,5)

    def test_direct_keywords(self)->None:
        self.assertDate(self.parse('today'),2025,1,15)
        self.assertDate(self.parse('tomorrow'),2025,1,16)
        self.assertDate(self.parse('yesterday'),2025,1,14)
        self.assertTime(self.parse('noon'),12,0)
        self.assertTime(self.parse('midnight'),0,0)

        now_result=self.parse('now')
        self.assertDateTime(now_result,2025,1,15,10,30,0)

    def test_holidays_and_rollover(self)->None:
        self.assertDate(
            self.parse('christmas',datetime.datetime(2025,12,1,9,0,0)),
            2025,
            12,
            25,
        )
        self.assertDate(
            self.parse('christmas',datetime.datetime(2025,12,26,9,0,0)),
            2026,
            12,
            25,
        )

    def test_relative_weekday_modifiers(self)->None:
        # Reference date is Wednesday 2025-01-15.
        self.assertDate(self.parse('wednesday'),2025,1,15)
        self.assertDate(self.parse('next wednesday'),2025,1,22)
        self.assertDate(self.parse('coming wednesday'),2025,1,22)
        self.assertDate(self.parse('last wednesday'),2025,1,8)
        self.assertDate(self.parse('this monday'),2025,1,20)

    def test_relative_weekday_with_time_tail(self)->None:
        result=self.parse('monday, 8:15pm')
        self.assertDateTime(result,2025,1,20,20,15,0)

    def test_simple_time_only(self)->None:
        self.assertTime(self.parse('9:05'),9,5)
        self.assertTime(self.parse('09:05:30'),9,5,30)
        self.assertTime(self.parse('11pm'),23,0)

    def test_date_only_and_ambiguous_numeric_dates(self)->None:
        self.assertDate(self.parse('2024-02-29'),2024,2,29)
        self.assertDate(self.parse('13/02/2025'),2025,2,13)
        self.assertDate(self.parse('02/13/2025'),2025,2,13)

    def test_datetime_with_timezone_z(self)->None:
        result=self.parse('2025-01-02T03:04:05Z')
        self.assertIsNotNone(result)
        self.assertTrue(hasattr(result,'datetime'))
        self.assertEqual(
            datetime.datetime(
                2025,1,2,3,4,5,tzinfo=datetime.timezone.utc,
            ),
            result.datetime,
        )

    def test_textual_dates_with_varied_spacing_and_case(self)->None:
        self.assertDate(self.parse('   FeBrUaRy   7,   2026  '),2026,2,7)
        self.assertDate(self.parse('7 feb 2026'),2026,2,7)

    def test_simple_month_day_without_year(self)->None:
        # For month-day inputs without an explicit year, parser should use
        # the reference year.
        self.assertDate(self.parse('Oct 20'),2025,10,20)

    def test_date_ranges_by_keywords_and_dashes(self)->None:
        checks=[
            (
                'from 2025-01-02 to 2025-01-05',
                datetime.datetime(2025,1,2,0,0,0),
                datetime.datetime(2025,1,5,0,0,0),
            ),
            (
                '2025-01-02 through 2025-01-05',
                datetime.datetime(2025,1,2,0,0,0),
                datetime.datetime(2025,1,5,0,0,0),
            ),
            (
                '2025-01-02 - 2025-01-05',
                datetime.datetime(2025,1,2,0,0,0),
                datetime.datetime(2025,1,5,0,0,0),
            ),
        ]
        for text,start,end in checks:
            with self.subTest(text=text):
                result=self.parse(text)
                self.assertIsInstance(result,DateRange)
                self.assertEqual(start,self.asDatetime(result.fromTime))
                self.assertEqual(end,self.asDatetime(result.toTime))

    def test_simple_month_name_date_range(self)->None:
        result=self.parse('June 20 - July 1')
        self.assertIsInstance(result,DateRange)
        self.assertEqual(
            datetime.datetime(2025,6,20,0,0,0),
            self.asDatetime(result.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,7,1,0,0,0),
            self.asDatetime(result.toTime),
        )

    def test_fall_month_name_date_range(self)->None:
        result=self.parse('Oct 20 - Nov 15')
        self.assertIsInstance(result,DateRange)
        self.assertTrue(
            isinstance(result.fromTime,datetime.datetime) \
            or hasattr(result.fromTime,'datetime'),
            f'Expected datetime-like fromTime, got {result.fromTime!r}',
        )
        self.assertTrue(
            isinstance(result.toTime,datetime.datetime) \
            or hasattr(result.toTime,'datetime'),
            f'Expected datetime-like toTime, got {result.toTime!r}',
        )
        self.assertEqual(
            datetime.datetime(2025,10,20,0,0,0),
            self.asDatetime(result.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,11,15,0,0,0),
            self.asDatetime(result.toTime),
        )

    def test_august_to_sept_date_range(self)->None:
        result=self.parse('Aug 22 - Sept 7')
        self.assertIsInstance(result,DateRange)
        self.assertEqual(
            datetime.datetime(2025,8,22,0,0,0),
            self.asDatetime(result.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,9,7,0,0,0),
            self.asDatetime(result.toTime),
        )

    def test_compact_time_ranges_and_meridiem_inheritance(self)->None:
        result=self.parse('9-11pm')
        self.assertIsInstance(result,DateRange)
        self.assertEqual(
            datetime.datetime(2025,1,15,21,0,0),
            self.asDatetime(result.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,1,15,23,0,0),
            self.asDatetime(result.toTime),
        )

        overnight=self.parse('11pm-1am')
        self.assertIsInstance(overnight,DateRange)
        self.assertEqual(
            datetime.datetime(2025,1,15,23,0,0),
            self.asDatetime(overnight.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,1,16,1,0,0),
            self.asDatetime(overnight.toTime),
        )

    def test_mixed_date_time_range(self)->None:
        result=self.parse('2025-03-10 to 4pm')
        self.assertIsInstance(result,DateRange)
        self.assertEqual(
            datetime.datetime(2025,3,10,0,0,0),
            self.asDatetime(result.fromTime),
        )
        self.assertEqual(
            datetime.datetime(2025,3,10,16,0,0),
            self.asDatetime(result.toTime),
        )

    def test_reject_reverse_date_range(self)->None:
        # Date/datetime ranges that reverse in time should be rejected.
        self.assertIsNone(self.parse('2025-03-10 18:00 to 2025-03-10 09:00'))
        self.assertIsNone(self.parse('2025-01-05 - 2025-01-02'))

    def test_sparse_schedule_keywords(self)->None:
        daily=self.parse('daily')
        self.assertIsInstance(daily,SparseDate)
        self.assertEqual([],daily.skipWeekdays)

        weekdays=self.parse('weekdays')
        self.assertIsInstance(weekdays,SparseDate)
        self.assertEqual([5,6],weekdays.skipWeekdays)

        weekends=self.parse('weekend')
        self.assertIsInstance(weekends,SparseDate)
        self.assertEqual([0,1,2,3,4],weekends.skipWeekdays)

        mon_to_wed=self.parse('every monday to wednesday')
        self.assertIsInstance(mon_to_wed,SparseDate)
        self.assertEqual([3,4,5,6],mon_to_wed.skipWeekdays)

    def test_invalid_and_garbage_inputs(self)->None:
        bad_inputs=[
            'not a date',
            '13:90',
            '2023-02-29',
            '32/01/2025',
            '2025-01-02 to',
            'to 2025-01-02',
            'every moonbeam',
        ]
        for text in bad_inputs:
            with self.subTest(text=text):
                self.assertIsNone(self.parse(text))

    def test_reference_date_parsing_and_validation(self)->None:
        result=self.parser.parse('today',referenceDate='2026-06-01 12:00')
        self.assertDate(result,2026,6,1)
        with self.assertRaises(ValueError):
            self.parser.parse('today',referenceDate='not a reference date')


def testSuite()->unittest.TestSuite:
    """Combine unit tests into a suite."""
    return unittest.defaultTestLoader.loadTestsFromTestCase(ParserTests)


def cmdline(args:list[str])->None:
    """Run all test suites."""
    unittest.main(argv=[sys.argv[0]]+list(args))


if __name__=='__main__':
    cmdline(sys.argv[1:])
