#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
This represents a window of opporotunity
"""
import typing
import datetime
from dateTools import inMinutes


class TimeWindow:
    """
    This represents a window of opporotunity
    """

    def __init__(self):
        pass

    def available(self)->bool:
        """
        window is open/available now
        """

    def closes(self)->datetime.datetime:
        """
        return when the current window closes

        (if the window is closed, returns now())
        """

    def closesIn(self)->datetime.timedelta:
        """
        a timedelta representing how long until
        the window closes

        (same as self.closes-now())
        """
        return self.closes()-datetime.datetime.now()

    def closesInMinutes(self)->float:
        """
        returns how many minutes until the window closes
        """
        return inMinutes(self.closesIn)

    def nextWindow(self)->typing.Optional[datetime.datetime]:
        """
        Gets the next occourance of this window
        (Can be None if this is the last)
        """
        return None


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
        print('  timeWindow.py [options]')
        print('Options:')
        print('   NONE')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
