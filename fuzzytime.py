#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Decode a time from within a freeform string, for example:
    * 5 days ago
    * within the last 48 hours
    * the third saturday of october
    * the week before thanksgiving
"""
import typing
import datetime


class FuzzyTime:
    """
    Decode a time from within a freeform string, for example:
        * 5 days ago
        * within the last 48 hours
        * the third saturday of october
        * the week before thanksgiving
    """

    def __init__(self,
        timestring:typing.Optional[str]=None):
        """
        This is fairly minimal for now, but it
        could be expanded to read things like:
            * 5 days ago
            * within the last 48 hours
            * the third saturday of october
            * the week before thanksgiving
        """
        self.startTime:datetime.datetime=datetime.datetime.now()
        self.endTime:datetime.datetime=datetime.datetime.now()
        if timestring is not None:
            self.assign(timestring)

    @property
    def timedelta(self)->datetime.timedelta:
        """
        the time difference between start and end
        """
        return self.endTime-self.startTime
    @timedelta.setter
    def timedelta(self,delta:datetime.timedelta):
        self.assign(delta)

    def setTime(self,timestring:str)->None:
        """
        set the time from a string
        """
        self.assign(timestring)

    def assign(self,timestring:str)->None:
        """
        set the time from a string
        """
        timestring=timestring.lower().replace(' ago','')
        tokens=self._tokenize(timestring)
        lastNumeric=0
        for token in tokens:
            if token[-1]=='s':
                token=token[0:-1]
            elif (token[0]>='0' and token[0]<='9') or token[0]=='.':
                lastNumeric=float(token)
            elif token in ('sec','second'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()-datetime.timedelta(seconds=lastNumeric)
            elif token in ('min','minute'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()-datetime.timedelta(minutes=lastNumeric)
            elif token in ('hr','hour'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()-datetime.timedelta(hours=lastNumeric)
            elif token in ('dy','day'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()-datetime.timedelta(days=lastNumeric)
            elif token in ('wk','week'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()-datetime.timedelta(weeks=lastNumeric)
            elif token in ('mt','mth','month'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()
                self.endTime=self.endTime.replace(
                    year=int((self.endTime.month+lastNumeric)/12))
                self.endTime=self.endTime.replace(
                    month=(self.endTime.month+lastNumeric)%12)
            elif token in ('yr','year'):
                self.startTime=datetime.datetime.now()
                self.endTime=datetime.datetime.now()
                self.endTime=self.endTime.replace(
                    year=self.endTime.year+lastNumeric)

    def _tokenize(self,timestring:str)->typing.Iterable[str]:
        """
        split a time string into tokens
        """
        tokens=[]
        inNumbers=False
        currentToken=[]
        for c in timestring:
            if c in [' ','\t','\r','\n']:
                inNumbers=False
                if currentToken:
                    tokens.append(''.join(currentToken))
                    currentToken=[]
            elif '0'<=c<='9' or c=='.':
                if not inNumbers:
                    inNumbers=True
                    if currentToken:
                        tokens.append(''.join(currentToken))
                        currentToken=[]
                currentToken.append(c)
            else:
                if inNumbers:
                    inNumbers=False
                    if currentToken:
                        tokens.append(''.join(currentToken))
                        currentToken=[]
                currentToken.append(c)
        if currentToken:
            tokens.append(''.join(currentToken))
        return tokens

    def __ne__(self,other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime!=other.startTime \
                or self.endTime!=other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime!=other or self.endTime!=other

    def __eq__(self, # type: ignore
        other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime==other.startTime \
                and self.endTime==other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime<=other<=self.endTime

    def __lt__(self,other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime<other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime<other

    def __le__(self,other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime<=other.startTime \
                or self.endTime<=other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime<=other

    def __gt__(self,other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime>other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime>other

    def __ge__(self,other:"FuzzyTime")->bool:
        """
        comparison operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime>=other.startTime \
                or self.endTime>=other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime>=other

    def __contains__(self,other:"FuzzyTime")->bool:
        """
        the "in" operator
        """
        if isinstance(other,str):
            other=FuzzyTime(other)
        if isinstance(other,FuzzyTime):
            return self.startTime>=other.startTime \
                or self.endTime>=other.endTime
        if not isinstance(other,datetime.datetime):
            other=datetime.datetime(other)
        return self.startTime>=other>=self.endTime

    def __repr__(self)->str:
        """
        string representation of this object
        """
        return 'Anywhere from '+str(self.startTime)+' to '+str(self.endTime)


def cmdline(args:typing.Iterable[str])->int:
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    fuzzy=FuzzyTime()
    printhelp=False
    if not args:
        printhelp=True
    else:
        for arg in args:
            if arg[0]=='-':
                if arg[1]=='-':
                    arg=arg[2:].split('=',1)
                    if arg[0]=='help':
                        printhelp=True
                        break
                    else:
                        print('ERR: Unknown arg "--'+arg[0]+'"')
                        printhelp=True
                        break
                else:
                    print('ERR: Unknown arg "'+arg+'"')
                    printhelp=True
                    break
            else:
                fuzzy.setTime(arg)
                print(str(fuzzy))
                break
    if printhelp:
        print('USAGE:\n\tfuzzytime.py [options] text_to_decipher [...]')
        print('OPTIONS:')
        print('\t--help ................ print this help')
        return -1
    return 0


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
