"""Compatibility surface: the production document lives in reaper_parser."""
from reaper_parser.parser import Document, Element, Line, RPPParseError, parse, emit, tokenize, quote_value
__all__ = ['Document','Element','Line','RPPParseError','parse','emit','tokenize','quote_value']
