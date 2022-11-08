#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Smartly parse ant date, time, or date range

The idea is to separate out numbers(N), text words (Z), and tokens (T)
    "Wednesday, May 23rd 1945 7:30AM"
     Z        T Z   N    N    NTN Z
and then use the ordering of the elements to determine what is meant

TODO: unfinished and experimental
"""
import typing
import datetime
import re
import dateTools


class Parser:
    """
    Smartly parse ant date, time, or date range

    The idea is to separate out numbers(N), text words (Z), and tokens (T)
        "Wednesday, May 23rd 1945 7:30AM"
         Z        T Z   N    N    NTN Z
    and then use the ordering of the elements to determine what is meant

    TODO: unfinished and experimental
    """

    HOLIDAYS=['easter','christmas']
    WEEKDAYS=['sunday']
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

    def findTextCase(self,s):
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

    def parse(self,s:str="tuesday,may 3",
        referenceDate:typing.Optional[datetime.date]=None
        )->typing.Union[dateTools.Date, dateTools.Time, dateTools.dateToolsDateTime,
            dateTools.DateRange,dateTools.TimeRange,dateTools.DateTimeRange,
            dateTools.SparseDate,dateTools.SparseTime,dateTools.SparseDateTime,
            None]:
        """

        :param referenceDate: used, for example if an email says "meet me next tuesday",
            then the referenceDate would be the send date of that email.
            (default value is now)

        retuns a (custom) Date, Time, DateTime,
            DateRange,TimeRange,DateTimeRange,
            SparseDate,SparseTime,SparseDateTime
            or None
        """
        if isinstance(referenceDate,(str,bytes)):
            referenceDate=self.parse(referenceDate)
        if s is None:
            return None
        if isinstance(s,bytes):
            s=s.decode('utf-8','ignore')
        tokre=r"""(?P<alpha>[a-z]+)|(?P<numeric>(?P<number>[0-9]+)(?P<th>st|nd|rd|th)?)|(\s*?(?P<tok>[,.-/\s\\:|])\s*)""" # pylint: disable=line-too-long
        tokre=re.compile(tokre,re.IGNORECASE|re.DOTALL)
        tokenized=[] # the actual value of the entry
        identities=[] # identity codes for each entry
        refinements=[] # refinemets to the entry's format [(string location,(textCase|th))]
        # first pass is used to glean what types of values we are looking at
        for m in tokre.finditer(s):
            ident=None
            if m.group('alpha') is not None:
                val=m.group('alpha')
                textCase=self.findTextCase(val)
                refinements.append((m.pos,textCase))
                identities.append('Z')
                tokenized.append(val)
            elif m.group('nummeric') is not None:
                val=m.group('nummeric')
                self.append(val.group('number'))
                refinements.append((m.pos,val.group('th') is not None))
                identities.append('N')
                tokenized.append(val)
            elif m.group('tok') is not None:
                val=m.group('tok')
                identities.append('T')
                tokenized.append(val)
                refinements.append((m.pos))
            else:
                raise Exception()
        # second pass determines what those values mean
        for i,entry in enumerate(tokenized):
            ident=identities[i]
            iMax=len(tokenized)
            if ident=='Z':
                if entry=='and':
                    if i>0 and identities[-1]=='T' and identities[-1]==',':
                        # unnecessary
                        del entries[i]
                        del identities[i]
                        del refinements[i]
                    else:
                        entries[i]=','
                        identities[i]='T'
                        refinements[i]=(refinements[i][0])
            elif ident=='N':
                if identeties[i+1]=='T':
                    if entries[i+1]=='.':
                        if identeties[i+2]=='N' and entries[i+3]=='.' and identities[i+4]=='N':
                            # date like yyyy.mm.dd
                            pass # TODO
                        else:
                            # decimal number
                            pass # TODO
                    elif entries[i+1] in ('\\/-'):
                        # traditional date separators
                        n1=entries[i-1]
                        n2=entries[i+1]
                        if entries[i+2] in  ('\\/-'):
                            n3=entries[i+3]
                        else:
                            # a yearless date like 7/25
                            # therefore use referenceDate
                            pass # TODO:
                        # now that we have 3 numbers, determine which is year, month, and day
                        pass # TODO
                    elif entries[i+1]==':':
                        n1=entries[i-1]
                        n2=entries[i+1]
                        if entries[i+2]==':':
                            # Time is hh:mm:ss
                            n3=entries[i+3]
                            # TODO
                        else:
                            # time is hh:mm
                            pass # TODO


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
