import re

#http://fragmentsofcode.wordpress.com/2010/03/10/escape-special-characters-for-solrlucene-query/
ESCAPE_CHARS_RE = re.compile(r'(?<!\\)(?P<char>[&|+\-!(){}[\]^"~*?:])')

def escape(value):
    return ESCAPE_CHARS_RE.sub(r'\\\g<char>', value)