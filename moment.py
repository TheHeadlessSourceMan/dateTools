from datetime import datetime, timedelta

class Moment:
    def __init__(self):
        self.datetime = datetime.now()

    def format(self, format_string):
        return self.datetime.strftime(format_string)

    def add(self, duration):
        self.datetime += timedelta(duration)

    def subtract(self, duration):
        self.datetime -= timedelta(duration)

    def is_before(self, moment):
        return self.datetime < moment.datetime
    isBefore=is_before

    def is_after(self, moment):
        return self.datetime > moment.datetime
    isAfter=is_after

    def start_of(self, unit_of_time):
        if unit_of_time == "year":
            self.datetime = self.datetime.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "month":
            self.datetime = self.datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "day":
            self.datetime = self.datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "hour":
            self.datetime = self.datetime.replace(minute=0, second=0, microsecond=0)
        elif unit_of_time == "minute":
            self.datetime = self.datetime.replace(second=0, microsecond=0)
        elif unit_of_time == "second":
            self.datetime = self.datetime.replace(microsecond=0)

    def end_of(self, unit_of_time):
        if unit_of_time == "year":
            self.datetime = self.datetime.replace(month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
        elif unit_of_time == "month":
            next_month = self.datetime.replace(day=28) + timedelta(days=4)  # this will never fail
            self.datetime = next_month - timedelta(days=next_month.day)
        elif unit_of_time == "day":
            self.datetime = self.datetime.replace(hour=23, minute=59, second=59, microsecond=999999)
        elif unit_of_time == "hour":
            self.datetime = self.datetime.replace(minute=59, second=59, microsecond=999999)

    def is_same(self, moment, unit_of_time):
        if unit_of_time == "year":
            return self.datetime.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0) == moment.datetime.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "month":
            return self.datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0) == moment.datetime.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "day":
            return self.datetime.replace(hour=0, minute=0, second=0, microsecond=0) == moment.datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        elif unit_of_time == "hour":
            return self.datetime.replace(minute=0, second=0, microsecond=0) == moment.datetime.replace(minute=0, second=0, microsecond=0)
        elif unit_of_time == "minute":
            return self.datetime.replace(second=0, microsecond=0) == moment.datetime.replace(second=0, microsecond=0)
        elif unit_of_time == "second":
            return self.datetime.replace(microsecond=0) == moment.datetime.replace(microsecond=0)
        else:
            return self.datetime == moment.datetime
