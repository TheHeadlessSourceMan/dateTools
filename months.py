import typing

MonthAbbrs=('',
    'JAN','FEB','MAR','APR','MAY','JUN','JUL',
    'AUG','SEP','OCT','NOV','DEC')
Months=('',
    'January','February','March','April',
    'May','June','July','August','September',
    'October','November','December')
lowercaseMonthStrToNumber:typing.Dict[str,int]={
    'january':1,'jan':1,
    'february':2,'feb':2,
    'march':3,'mar':3,
    'april':4,'apr':4,
    'may':5,
    'june':6,'jun':6,
    'july':7,'jul':7,
    'august':8,'aug':8,
    'september':9,'sept':9,'sep':9,
    'october':10,'oct':10,
    'november':11,'nov':11,
    'december':12,'dec':12}


class HasMonth(typing.Protocol):
    """
    class with a month member
    """
    @property
    def month(self)->'MonthCompatible':
        ...


MonthCompatible=typing.Union[str,int,'Month',HasMonth]
def asMonth(month:MonthCompatible)->'Month':
    """
    Convert a string, int, or Month object to a Month object.
    """
    while hasattr(month,'month'):
        month=typing.cast(HasMonth,month)
        month=Month(month.month)
    if isinstance(month,Month):
        return month
    return Month(month)


class Month:
    """
    Class representing a month.
    """

    def __init__(self,month:MonthCompatible):
        self.monthNumber:int=getMonthNumber(month)

    @property
    def number(self)->int:
        return self.monthNumber
    def __int__(self)->int:
        return self.monthNumber

    @property
    def name(self)->str:
        return Months[self.monthNumber]

    @property
    def abbr(self)->str:
        return MonthAbbrs[self.monthNumber]

    def __str__(self):
        return self.name


def getMonthNumber(month:MonthCompatible)->int:
    """
    Get the month number from a string, int, or Month object.
    """
    if isinstance(month,Month):
        return month.monthNumber
    if isinstance(month,int):
        if month<1 or month>12:
            raise ValueError(f"Invalid month number {month}")
        return month
    if isinstance(month,str):
        month=month.lower()
        if month not in lowercaseMonthStrToNumber:
            raise ValueError(f'Invalid month "{month}"')
        return lowercaseMonthStrToNumber[month]
    return asMonth(month).monthNumber
