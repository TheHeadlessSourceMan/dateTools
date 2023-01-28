
import typing
import bisect
import datetime
import threading

AlarmTimeoutCompatible=typing.Union[datetime.datetime,datetime.timedelta]


class FunctionCall:
    """
    bind a function and its parameters for calling later
    """
    def __init__(self,
        fn:typing.Callable,
        args:typing.Optional[typing.Iterable[typing.Any]]=None,
        kwargs:typing.Optional[typing.Dict[str,typing.Any]]=None):
        self._fn:typing.Callable=fn
        if args is None:
            args=[]
        if kwargs is None:
            kwargs={}
        self._args:typing.Iterable[typing.Any]=args
        self._kwargs:typing.Dict[str,typing.Any]=kwargs

    def __call__(self,*args,**kwargs)->typing.Any:
        """
        Call this just like calling fn() passed in!

        any args will be appended to the original args,
        any kwargs will be added into the original kwargs
        """
        callargs=list(self._args)
        callkwargs=dict(self._kwargs)
        if args:
            callargs.extend(callargs)
        if kwargs:
            callkwargs.update(kwargs)
        return self._fn(*callargs,**callkwargs)

    def __repr__(self):
        params=[]
        for p in self._args:
            if isinstance(p,str):
                params.append(f'"{p}"')
            else:
                params.append(str(p))
        for k,v in self._kwargs.items():
            if isinstance(v,str):
                params.append(f'{k}="{v}"')
            else:
                params.append(f'{k}={v}')
        return self._fn.__name__+'('+(', '.join(params))+')'


class Alarm(FunctionCall):
    """
    A single alarm in an AlarmSet
    """

    def __init__(self,
        time:AlarmTimeoutCompatible,
        fn:typing.Callable,
        args:typing.Optional[typing.Iterable[typing.Any]]=None,
        kwargs:typing.Optional[typing.Dict[str,typing.Any]]=None):
        """
        :time: if the time is an absolute time, use it as-is. relative time
            if it is a relative time, use the offset from now for the alarm
        """
        FunctionCall.__init__(self,fn,args,kwargs)
        if isinstance(time,datetime.timedelta):
            time=datetime.datetime.now()+time
        self._time:datetime.datetime=time

    @property
    def time(self)->typing.Optional[datetime.datetime]:
        return self._time

    def __float__(self)->float:
        """
        The comparable value for this is simply the unix timestamp
        """
        if self.time is None:
            return 0.0
        return self.time.timestamp()

    def __int__(self)->int:
        """
        The comparable value for this is simply the unix timestamp
        """
        if self.time is None:
            return 0
        return int(self.time.timestamp())

    def __le__(self,other)->bool:
        """
        Implement comparison
        """
        if not isinstance(other,(int,float)):
            if isinstance(other,datetime.datetime):
                other=other.timestamp()
            else:
                other=float(other)
        return float(self)<=other

    def __lt__(self,other)->bool:
        """
        Implement comparison
        """
        if not isinstance(other,(int,float)):
            if isinstance(other,datetime.datetime):
                other=other.timestamp()
            else:
                other=float(other)
        return float(self)<other

    def __gt__(self,other)->bool:
        """
        Implement comparison
        """
        if not isinstance(other,(int,float)):
            if isinstance(other,datetime.datetime):
                other=other.timestamp()
            else:
                other=float(other)
        return float(self)>other

    def __ge__(self,other)->bool:
        """
        Implement comparison
        """
        if not isinstance(other,(int,float)):
            if isinstance(other,datetime.datetime):
                other=other.timestamp()
            else:
                other=float(other)
        return float(self)>=other

    def __eq__(self,other)->bool:
        """
        Implement comparison
        """
        if not isinstance(other,(int,float)):
            if isinstance(other,datetime.datetime):
                other=other.timestamp()
            else:
                other=float(other)
        return float(self)==other

    def start(self,stopWhenNoAlarmsActive:bool=True)->"AlarmSet":
        """
        Exactly the same as AlarmSet(alarm).start()
        except it also returns the AlarmSet created
        (and stopWhenNoAlarmsActive defaults to True)
        """
        alarmSet=AlarmSet(self)
        alarmSet.start(stopWhenNoAlarmsActive)
        return alarmSet
    def end(self):
        """
        Exactly the same as AlarmSet(alarm).end()
        """
        AlarmSet(self).end()
    def run(self,stopWhenNoAlarmsActive:bool=True)->None:
        """
        Exactly the same as AlarmSet(alarm).start()
        """
        AlarmSet(self).run(stopWhenNoAlarmsActive)

    def __repr__(self)->str:
        return f"{self.time} "+FunctionCall.__repr__(self)


class PeriodicAlarm(Alarm):
    """
    an alarm that fires periodically.
    
    can have a start and end bound, which will limit
    the alarm to a certian active period
    """

    def __init__(self,
        timeout:datetime.timedelta,
        fn:typing.Callable,
        args:typing.Optional[typing.Iterable[typing.Any]]=None,
        kwargs:typing.Optional[typing.Dict[str,typing.Any]]=None,
        starting:typing.Optional[datetime.datetime]=None,
        ending:typing.Optional[datetime.datetime]=None):
        """
        :time: alarm will occour every this much time
        :starting: timeout periods will always be based on this (default is now)
        :ending: any alarms past this will not be called and the alarm itself will
             be considered expired
        """
        Alarm.__init__(self,typing.cast(datetime.datetime,None),fn,args,kwargs)
        if starting is None:
            starting=datetime.datetime.now()
        self._timeout:datetime.timedelta=timeout
        self._starting:datetime.datetime=starting
        self._ending:typing.Optional[datetime.datetime]=ending
        self._current:typing.Optional[Alarm]=None

    @property
    def starting(self)->datetime.datetime:
        return self._starting
    @property
    def ending(self)->typing.Optional[datetime.datetime]:
        return self._ending

    @property
    def time(self)->typing.Optional[datetime.datetime]:
        if self.current is None:
            return None
        return self.current.time

    @property
    def current(self)->typing.Optional[Alarm]:
        """
        The current next Alarm that will fire
        """
        if self._current is None:
            now=datetime.datetime.now()
            if self._ending is None or now+self._timeout<self._ending:
                nextTime=self._starting+self._timeout
                while nextTime<now:
                    nextTime+=self._timeout
                self._current=Alarm(nextTime,self._fn,self._args,self._kwargs)
        return self._current

    @property
    def nextAlarm(self)->typing.Optional[Alarm]:
        self._current=None
        return self.current

    def __call__(self,*args,**kwargs)->typing.Any:
        """
        Call this just like calling fn() passed in!

        any args will be appended to the original args,
        any kwargs will be added into the original kwargs
        """
        if self._current:
            return self._current(*args,**kwargs)

    def start(self,stopWhenNoAlarmsActive:bool=False)->"AlarmSet":
        """
        Exactly the same as AlarmSet(alarm).start()
        except it also returns the AlarmSet created.
        """
        alarmSet=AlarmSet(self)
        alarmSet.start(stopWhenNoAlarmsActive)
        return alarmSet

    def __repr__(self):
        if self.ending is None:
            end="Forever"
        else:
            end=str(self.ending)
        if self.current is None:
            next="Never"
        else:
            next=str(self.current.time)
        return f"every {self._timeout} between {self.starting}-{end} (next={next}) "+FunctionCall.__repr__(self)


class AlarmSet:
    """
    A set of alarms, which will track which are active,
    which are expired, and sleep until the next alarm is ready.

    This does allow for sending in expired times, whic
    can be useful for scheduling, etc.
    """

    def __init__(self,
        alarms:typing.Union[None,Alarm,typing.Iterable[Alarm]]=None):
        """ """
        self._active:typing.List[Alarm]=[]
        self._expired:typing.List[Alarm]=[]
        self._thread:typing.Optional[threading.Thread]=None
        self._threadInterruptEvent:typing.Optional[threading.Event]=None
        self._keepGoing:bool=True
        self._stopWhenNoAlarmsActive:bool=False
        self.add(alarms)

    @property
    def expired(self)->typing.Iterable[Alarm]:
        """
        expired alarms, in time-order
        """
        return self._expired

    @property
    def active(self)->typing.Iterable[Alarm]:
        """
        active alarms, in time-order
        """
        return self._active

    @property
    def all(self)->typing.Iterable[Alarm]:
        """
        all alarms, in time-order, whether expired or active
        """
        yield from self._expired
        yield from self._active

    def __iter__(self)->typing.Iterable[Alarm]:
        return self.all

    def nextAlarm(self,fromTime:typing.Optional[datetime.datetime]=None)->typing.Optional[Alarm]:
        """
        get the next alarm (optionally, on or after a given time)
        """
        if fromTime is not None:
            raise NotImplementedError()
        if not self._active:
            return None
        return self._active[0]

    def previousAlarm(self,fromTime:typing.Optional[datetime.datetime]=None)->typing.Optional[Alarm]:
        """
        get the last/previous alarm (optionally, on or after a given time)
        """
        if fromTime is not None:
            raise NotImplementedError()
        if not self._expired:
            return None
        return self._expired[-1]

    @typing.overload
    def add(self,
        timeOrAlarm:AlarmTimeoutCompatible,
        fn:typing.Callable,
        args:typing.Optional[typing.Iterable[typing.Any]]=None,
        kwargs:typing.Optional[typing.Dict[str,typing.Any]]=None)->None: ...
    @typing.overload
    def add(self,
        timeOrAlarm:typing.Union[None,Alarm,typing.Iterable[Alarm]],
        fn:None=None,
        args:None=None,
        kwargs:None=None)->None: ...
    def add(self,
        timeOrAlarm:typing.Union[None,Alarm,typing.Iterable[Alarm],AlarmTimeoutCompatible],
        fn:typing.Optional[typing.Callable]=None,
        args:typing.Optional[typing.Iterable[typing.Any]]=None,
        kwargs:typing.Optional[typing.Dict[str,typing.Any]]=None)->None:
        """
        :timeOrAlarm:
            if it's one or more Alarm(s), simply add it/them
            if the time is an absolute time, create an alarm to use it as-is
            if it is a relative time, create an alarm with that offset from now
        :fn: if timeOrAlarm is a time, this is the function that the created alarm will call
        :args: if timeOrAlarm is a time, these are the parameters to be passed to fn()
        :kwargs: if timeOrAlarm is a time, these are the keyword parameters to be passed to fn()

        Attempting to add an alarm whose time has already elapsed will simply add it
        to the appropriate time in the expired list.
        """
        if timeOrAlarm is None:
            return 
        if isinstance(timeOrAlarm,Alarm):
            alarms:typing.Iterable[Alarm]=(timeOrAlarm,)
        elif isinstance(timeOrAlarm,(datetime.datetime,datetime.timedelta)):
            alarms=(Alarm(timeOrAlarm,typing.cast(typing.Callable,fn),args,kwargs),)
        else:
            alarms=timeOrAlarm
        for alarm in alarms:
            if alarm<datetime.datetime.now():
                bisect.insort(self._expired,alarm)
            else:
                newFirstAlarm:bool = not self._active or alarm<self._active[0]
                bisect.insort(self._active,alarm)
                if newFirstAlarm:
                    self._interrupt() # interrupt waiting on the current _current and wait on the one that it changed to instead
    append=add
    extend=add

    def __repr__(self)->str:
        ret=[str(alarm) for alarm in self.__iter__()]
        ret.insert(0,"alarms:")
        return "\n   ".join(ret)

    def start(self,stopWhenNoAlarmsActive:bool=False)->None:
        """
        start the thread running if it is not already
        """
        self._stopWhenNoAlarmsActive=stopWhenNoAlarmsActive
        if self._thread is None:
            self._thread=threading.Thread(target=self.run,args=[stopWhenNoAlarmsActive])
    def _interrupt(self):
        """
        cause the thread to interrupt any waits
        and re-calculate what should be going on
        """
        if self._threadInterruptEvent is not None:
            self._threadInterruptEvent.set()
    def end(self):
        """
        stop any running thread
        """
        if self._thread is not None:
            t=self._thread # keep a copy since member will be cleared
            self._keepGoing=False
            self._interrupt()
            t.join()
    def run(self,stopWhenNoAlarmsActive:bool=True)->None:
        """
        Main thread loop

        (Usually you don't want to call this, but rather call start() 
        to run it in another thread instead)
        """
        #print('started')
        self._keepGoing=True
        self._stopWhenNoAlarmsActive=stopWhenNoAlarmsActive
        if self._threadInterruptEvent is None:
            self._threadInterruptEvent=threading.Event()
        else:
            self._threadInterruptEvent.clear()
        while self._keepGoing:
            if not self._active:
                if self._stopWhenNoAlarmsActive:
                    #print("all alarms finished")
                    break
                self._threadInterruptEvent.wait(1)
                continue
            if self._active[0].time:
                t:float=(self._active[0].time-datetime.datetime.now()).total_seconds()
            else:
                t=0.05
            #print('sleeping for',t)
            if t<0:
                raise Exception(f"Unexpected sleep time {t}")
            if self._threadInterruptEvent.wait(t):
                self._threadInterruptEvent.clear()
            else:
                self._fireCurrentAlarms()
        self._thread=None
        #print('ended',self._keepGoing)

    def _fireCurrentAlarms(self,lookahead:float=0.05):
        """
        For each active alarm that has expired, we
            Will call it as a function then move it
            to expired as necessary.
        :lookahead: if the alarm will expiew in this many seconds, just
            call it expired now
        """
        for alarm in self._active:
            # reset now in every loop in case the alarm's fn takes some time
            now=datetime.datetime.now().timestamp()+lookahead
            if alarm>now:
                break
            alarm() # call it!
            del self._active[0]
            if hasattr(alarm,'nextAlarm'):
                next=alarm.nextAlarm
                if next:
                    # we already removed and so now re-add periodic 
                    # alarm to keep it in sorted order
                    self._active.append(alarm)
                else:
                    # periodic alarm is done
                    self._expired.append(alarm)
            else:
                self._expired.append(alarm)


Timer=Alarm
PeriodicTimer=PeriodicAlarm
TimerSet=AlarmSet


def test_expired():
    """
    Test that alarms are correctly separated into expired and active
    """
    aset=AlarmSet()
    aset.add(datetime.timedelta(seconds=-1),print,("Alarm 1 expired.",))
    aset.add(datetime.timedelta(seconds=3),print,("Alarm 2 ative.",))
    aset.add(PeriodicAlarm(datetime.timedelta(seconds=4),print,("Alarm 3 expired.",),end=datetime.datetime.fromtimestamp(100)))
    aset.add(PeriodicAlarm(datetime.timedelta(seconds=4),print,("Alarm 4 active.",)))
    print('Expired:')
    print('\n'.join([str(x) for x in aset.expired]))
    print('Active:')
    print('\n'.join([str(x) for x in aset.active]))

def test_ordering():
    """
    Test that the alarms are ranked in the correct order
    """
    aset=AlarmSet()
    aset.add(datetime.timedelta(seconds=5),print,("Alarm 1 fired.",))
    aset.add(datetime.timedelta(seconds=3),print,("Alarm 2 fired.",))
    aset.add(Alarm(datetime.timedelta(seconds=4),print,("Alarm 3 fired.",)))
    aset.add(PeriodicAlarm(datetime.timedelta(seconds=4),print,("Alarm 4 fired.",)))
    print(aset)

def test_running():
    """
    Test that the alarms run at the correct times
    """
    aset=AlarmSet()
    def fn(s):
        now=datetime.datetime.now()
        print(f'{now} -- {s}')
    now=datetime.datetime.now()
    print(f'{now} -- START')
    aset.add(datetime.timedelta(seconds=5),fn,("Alarm 1 fired.",))
    aset.add(datetime.timedelta(seconds=3),fn,("Alarm 2 fired.",))
    aset.add(Alarm(datetime.timedelta(seconds=4),fn,("Alarm 3 fired.",)))
    aset.add(PeriodicAlarm(datetime.timedelta(seconds=1),fn,("Alarm 4 fired.",)))
    aset.run()

def test():
    test_ordering()
    test_expired()
    test_running()