"""
Exception to throw when something is wrong with the date format
"""

class DateFormatException(Exception):
    """
    Exception to throw when something is wrong with the date format
    """
    def __init__(self,badFormat:str):
        Exception.__init__(self,f'Bad date format: "{badFormat}"')
