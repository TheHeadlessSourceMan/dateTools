#!/usr/bin/env
# -*- coding: utf-8 -*-
"""
Run unit tests

See:
    http://pyunit.sourceforge.net/pyunit.html
"""
import unittest
import os
from dateTools import *


__HERE__=os.path.abspath(__file__).rsplit(os.sep,1)[0]+os.sep


class Test(unittest.TestCase):
    """
    Run unit test
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testDecoder(self):
        decodings=[
            (r"5 days ago",r"'Anywhere from '+str(self.startTime)+' to '+str(self.endTime)"),
            (r"within the last 48 hours",r"'Anywhere from '+str(self.startTime)+' to '+str(self.endTime)"),
            (r"the third saturday of october",r"'Anywhere from '+str(self.startTime)+' to '+str(self.endTime)"),
            (r"the week before thanksgiving",r"'Anywhere from '+str(self.startTime)+' to '+str(self.endTime)"),
            ]
        for d in decodings:
            print("testing: "+d[0])
            print("  "+d[1])
            FuzzyTime(d[0])
            result=d.__repr__()
            print("  "+result)
            assert d[1]==result
            
    def testCommandLineHelp(self):
        filenames=('miscFunctions','fuzzytime','dateRanges')
        for f in filenames:
            import importutils
            f=importutils.import(f)
            f.cmdline(['--help'])


def testSuite():
    """
    Combine unit tests into an entire suite
    """
    testSuite = unittest.TestSuite()
    testSuite.addTest(Test("testDecoder"))
    testSuite.addTest(Test("testCommandLineHelp"))
    return testSuite


def cmdline(args):
    """
    Run the command line

    :param args: command line arguments (WITHOUT the filename)
    """
    """
    Run all the test suites in the standard way.
    """
    unittest.main()


if __name__=='__main__':
    import sys
    cmdline(sys.argv[1:])
