"""
Tools for handling English ordinal indicators eg 1st,2nd,3rd,etc

See also:
    https://en.wikipedia.org/wiki/Ordinal_indicator
"""
import typing
import re

ordinals=(None,'first','second','third','fourh','fifth','sixth','seventh','eighth','nineth','tenth','eleventh')
ordinalIndicators=(None,'st','nd','rd','th')

# NOTE: this is techically a misapplication of unicode, but sometimes people do it.
unicodeSuperscriptOrdinalIndicators=(None,'ˢᵗ','ⁿᵈ','ʳᵈ','ᵗʰ')
unicodeSuperscriptOrdinalIndicatorsCaps=(None,'ˢᵀ','ᴺᴰ','ᴿᴰ','ᵀᴴ')
unicodeSuperscriptDigits=('⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹')

ordinalIndicatorsRegexText='()'
ordinalIndicatorsRegex=re.compile(ordinalIndicatorsRegexText)

def removeUnicodeSuperscripts(s:str)->str:
    """
    Remove unicode superscripts for digits and ordinal indicators
    (NOTE: this will not un-superscript all characters, but just 0-9 and st,nd,rd,and th)

    # TODO: a regex may be more efficient
    """
    for lower,upper,actual in zip(unicodeSuperscriptOrdinalIndicators,unicodeSuperscriptOrdinalIndicatorsCaps,ordinalIndicators):
        if lower is not None and actual is not None:
            s=s.replace(lower,actual).replace(upper,actual).replace(upper[0]+lower[1],actual)
    for actual,super in enumerate(unicodeSuperscriptDigits):
        s=s.replace(super,actual)
    return s

def fromOrdinal(fromOrdinal:typing.Union[int,str])->str:
    """
    Convert from ordinals to numbers
    
    NOTE: Converts ALL orinals in the string to numeric digits.
    NOTE: If an unrecognizeable string is passed in, returns it unmodified.

    Always returns a string, which you can then decode to an int

    Examples:
        toOrdinal("1st") => "1"
        toOrdinal("I am 1st, you are 2nd") => "I am 1, you are 2"
        toOrdinal("I like eggs") => "I like eggs"
    """
    if isinstance(fromOrdinal,int):
        return str(fromOrdinal)


def toOrdinal(fromNumber:typing.Union[int,str],mixedText=True,caps='ab')->str:
    """
    Convert numbers into ordinals

    NOTE: If an unrecognizeable string is passed in, returns it unmodified.
    NOTE: Only converts the last number, so toOrdinal(fromOrdinal(x)) may not be the same thing

    :caps: caps example 'ab','Ab',or 'AB'

    Examples:
        toOrdinal(1,mixedText=True) => "1st"
        toOrdinal(1,mixedText=False) => "first"
        toOrdinal(1,mixedText=False,caps='Ab') => "First"
        toOrdinal("I'll see you on the 4") => "I'll see you on the 4th"
        toOrdinal("I'll see you on Easter") => "I'll see you on Easter"
        toOrdinal("I am 1, you are 2") => "I am 1, you are 2nd"
    """
    if not isinstance(fromNumber,str):
        txtnum=str(fromNumber)
    else:
        txtnum=fromNumber.strip()
        if not txtnum or not txtnum[-1].isdigit():
            return fromNumber
    lastDigit=int(txtnum[-1])
    if mixedText:
        if lastDigit>4 or lastDigit<1:
            lastDigit=4 # "th" is for everything else
        indic=typing.cast(str,ordinalIndicators[lastDigit])
        if caps[0].isupper():
            if caps[1].isupper():
                indic=indic.upper()
            else:
                indic[0]=indic[0].upper()
        if isinstance(fromNumber,str) and txtnum!=fromNumber:
            # add back on the trailing whitespace
            return txtnum+indic+fromNumber[len(fromNumber)-len(txtnum):]
        return txtnum+indic
    raise NotImplementedError()