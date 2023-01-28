class DateFormatException(Exception):
    def __init__(self,badFormat:str):
        self.__init__(self,f'Bad date format: "{badFormat}"')