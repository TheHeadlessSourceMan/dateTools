#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Simple program to get the time of day 'morning','afternoon','evening', or 'night'
"""
import typing
import datetime


def timeOfDay(timestamp:typing.Union[None,datetime.datetime,datetime.date]=None,
    leadTimeHours:float=0,closeOfBusiness:datetime.time=None)->str:
    """
    :property timestamp: timestamp to get time of day of. if missing, use now
    :property leadTimeHours: add this many hours - useful for emails and stuff like that
    :property closeOfBusiness: if the time is after closeOfBusiness hour,
        then will assume 'morning' tomorrow
    """
    if timestamp is None:
        timestamp=datetime.datetime.now()
    if leadTimeHours!=0:
        timestamp=timestamp+datetime.timedelta(hours=leadTimeHours)
    if closeOfBusiness is not None and timestamp.hour>closeOfBusiness:
        return 'morning'
    if timestamp.hour<12:
        return 'morning'
    if timestamp.hour<18:
        return 'evening'
    return 'night'


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    printhelp=False
    if not args:
        printhelp=True
    else:
        leadTimeHours=0
        closeOfBusiness=None
        for arg in args:
            if arg.startswith('-'):
                arg=[a.strip() for a in arg.split('=',1)]
                if arg[0] in ['-h','--help']:
                    printhelp=True
                elif arg[0]=='--now':
                    print(timeOfDay(leadTimeHours=leadTimeHours,closeOfBusiness=closeOfBusiness))
                elif arg[0]=='--closeOfBusiness':
                    closeOfBusiness=int(arg[1])
                elif arg[0]=='--leadTimeHours':
                    leadTimeHours=int(arg[1])
                else:
                    print('ERR: unknown argument "'+arg[0]+'"')
            else:
                print('ERR: unknown argument "'+arg+'"')
    if printhelp:
        print('Usage:')
        print('  timeOfDay.py [options]')
        print('Options:')
        print('   --now ................. get the time based on now')
        print('   --closeOfBusiness= .... set a close of business hour (times')
        print('                  later than this will wrap to "morning")')
        print('   --leadTimeHours= ...... add this many hours')
        return -1
    return 0


if __name__=='__main__':
    import sys
    sys.exit(cmdline(sys.argv[1:]))
