"""
Turn a list of DataRanges into a a very simple html gantt chart.
"""
import typing

from .dateRanges import (
    DateRange,asDateRange,DateRangeCompatible)


GanttEntryCompatible=typing.Union[
    "GanttEntry",typing.Tuple[str,DateRangeCompatible]]


def asGanttEntry(entry:GanttEntryCompatible)->GanttEntry:
    """
    Convert a GanttEntryCompatible to a GanttEntry
    """
    if isinstance(entry,GanttEntry):
        return entry
    if isinstance(entry,tuple): # type: ignore
        name,range=entry
        return GanttEntry(name,asDateRange(range))
    raise TypeError(
        f'Unable to convert {entry} to a GanttEntry')

class GanttEntry:
    """
    A single entry in a Gantt chart
    """
    def __init__(
        self,
        name:str,
        range:DateRangeCompatible, # pylint: disable=redefined-builtin
        color:str='blue',
        ):
        self.name:str=name
        self.range:DateRange=asDateRange(range)
        self.color:str=color


class GanttChart:
    """
    A simple Gantt chart
    """
    def __init__(
        self,
        entries:typing.Iterable[GanttEntryCompatible]=(),
        ):
        self.entries:typing.List[GanttEntry]=[]
        self.append(entries)

    def asHtml(self):
        """
        Get the chart as an html string

        TODO: does not include date headers.
        that is currently beyond the scope of a first draft.
        """
        entries=self.entries
        minDate=min(entry.range.fromTime for entry in entries)
        html=['<table class="gantt-chart">']
        for entry in self.entries:
            html.append(f'<tr><td>{entry.name}</td>')
            startOffset=entry.range.start-minDate
            spaceBefore=float(startOffset.totalDays) # type: ignore
            size=entry.range.totalDays
            html.append(f'<td colspan={int(spaceBefore)}></td>')
            html.append(f'<td colspan={int(size)} style="background-color:{entry.color}"></td>') # noqa: E501 # pylint: disable=line-too-long
            html.append('</tr>')
        html.append('</table>')
        return '\n'.join(html)

    def append(self, entries:typing.Iterable[GanttEntryCompatible]):
        """
        Add more entries to the chart
        """
        self.entries.extend(asGanttEntry(entry) for entry in entries)
    add=append
    extend=append

    def __str__(self):
        return self.asHtml()
