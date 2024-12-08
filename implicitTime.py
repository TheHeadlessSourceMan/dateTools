"""
An implicit time can be:
    An actual, explicit date/time
    A reference to another time
        Later that day
        After
        A week before
    A reference to an event date or time
        Christmas
        Midnight
        The following week
        After the party
    A reference to an overlapping time
    at a different location/perspective
        Simultaneously
        Meanwhile
"""

class ImplicitTime:
    """
    An implicit time can be:
        An actual, explicit date/time
        A reference to another time
            Later that day
            After
            A week before
        A reference to an event date or time
            Christmas
            Midnight
            The following week
            After the party
        A reference to an overlapping time
        at a different location/perspective
            Simultaneously
            Meanwhile
    """
    def __init__(self,indicator:str,inReferenceTo:'ImplicitTime'):
        self.indicator=indicator
        self.inReferenceTo=inReferenceTo

    def __cmp__(self,other:'ImplicitTime'):
        """
        Compare two implicit times to see whether
        the other even occoured before, after, or simultaneous
        to the current time.
        """
