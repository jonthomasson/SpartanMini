'''
Parse one BSDL file at the file level.

Currently only used by parseall.py in the tools directory.

Currently only parses well enough to extract ID Code and instruction
register values.  Should be fairly easy to extend.

There are a lot of crap BSDL files out there, and this parser
attempts to wade through the crap and generate reasonable results
where possible.

Copyright (C) 2011 by Patrick Maupin.  All rights reserved.
License information at: http://playtag.googlecode.com/svn/trunk/LICENSE.txt
'''

import re
import collections
import traceback

class BSDLError(ValueError):
    pass

class TokenRegex(object):
    vhdl_comment = r'\-\-[^\n]*'
    c_comment = r'\/\*.*?\*\/'
    cpp_comment = r'\/\/[^\n]*'
    bad_comment_1 = r'\*{4}[^\n]*'
    bad_comment_2 = r'\n__[^\n]*'

    optional_exponent = '(?:[eE][+-]?[0-9]+)?'
    float1 = r'[0-9]+\.?[0-9]*' + optional_exponent
    float2 = r'\.[0-9]+' + optional_exponent
    string = r'\"(?:[^"]|\"\")*\"?'
    multi_operator = r'\*\*|\/\=|\<\=|\>\=|\:\='
    word = r'\w+'
    single = r'\S'

    comments = vhdl_comment, c_comment, cpp_comment, bad_comment_1, bad_comment_2
    code = float1, float2, string, multi_operator, word, single
    pattern = '(%s)' % '|'.join(comments + code)
    splitter = re.compile(pattern).split

def hack_comments(data):
    ''' Get rid of cruft around the packages and entities.
    '''
    def anycase(what):
        return ''.join('[%s%s]' % (x, x.upper()) for x in what)

    separator = r'((?:\n|^)\s*(?:%s|%s|%s) )' % (anycase('entity'), anycase('package'), anycase('end'))
    splitter = re.compile(separator).split
    result = splitter(data)
    if len(result) < 2:
        return data
    inside = False
    result[0] = result[0].count('\n') * '\n'
    for index in range(1, len(result), 2):
        ending = result[index].strip().lower() == 'end'
        if not inside:
            if ending:
                return data
            inside = True
        elif ending:
            inside = False
            temp = result[index+1]
            suffix = temp.count('\n') * '\n'
            prefix = temp and temp.split('\n')[0] or ''
            result[index+1] = prefix + suffix
        index += 2
    return ''.join(result)

def tokenize(fname, warnings, hack, splitter=TokenRegex.splitter):
    f = open(fname, 'rb')
    data = f.read()
    f.close()

    data = data.replace('\r\n', '\n').replace('\r', '\n')
    data = data.replace('\x1a', '').replace('\x00', '')

    if hack:
        data = hack_comments(data)
    nextlinenum = 1
    for token in splitter(data):
        linenum = nextlinenum
        nextlinenum += token.count('\n')
        if token.startswith(('--', '/*', '//', '****', '\n__')):
            if not token.startswith('--'):
                warnings.append((linenum, 'Bad Comment Type'))
            continue
        elif not token.strip():
            continue
        if token.startswith('"'):
            if len(token) == 1 or not token.endswith('"'):
                warnings.append((linenum, 'Unterminated quoted string'))
            elif token.count('\n'):
                warnings.append((linenum, 'Quoted string spans %s lines' % (token.count('\n') + 1)))
        yield token, linenum

def nestparens(source):
    current = []
    stack = []
    for t in source:
        if t[0] not in ('(', ')'):
            current.append(t)
            continue
        if t[0] == '(':
            new = [t]
            current.append(new)
            stack.append(current)
            current = new
        else:
            if not stack:
                raise BSDLError("Unmatched ')' on line %s" % t[1])
            current.append(t)
            current = stack.pop()
    if stack:
        raise BSDLError("Unmatched '(' on line %s" % current[0][1])
    return current

def group_semi(source):
    splitpoints = []
    for i, x in enumerate(source):
        if isinstance(x, list):
            source[i] = group_semi(x)
        elif x[0] == ';':
            splitpoints.append(i)
    if not splitpoints:
        return source
    splitpoints = zip([-1] + splitpoints, splitpoints + [len(source)])
    return [source[a+1:b] for (a,b) in splitpoints if b-a > 1]

class ChipInfo(object):
    def __init__(self, fname):
        self.bsdl_file_name = fname
        self.use = set()
        self.bsdl_extension = set()

class FileParser(object):

    def raise_error(self, s, linenum=None):
        if linenum is not None:
            s += ' on line %s' % linenum
        warnings = self.warnings
        if warnings:
            warnings = '\n        '.join('Line %s -- %s' % x for x in warnings)
            s = '%s\n     Additional information:\n        %s' % (s, warnings)
        s = '\nError in parsing BSDL file %s:\n    %s\n' % (self.fname, s)
        raise BSDLError(s)

    def nexttok(self, line, linenum=None, expected=None, errmsg='Invalid token', lowercase=True,
                              isinstance=isinstance, tuple=tuple, str=str, token=None):
        if line:
            token = line.pop()
            if isinstance(token, tuple):
                token, linenum = token
                if lowercase:
                    token = token.lower()
            else:
                token = None
        if isinstance(expected, str):
            expected = expected,
        if token is None or (expected is not None and token not in expected):
            if expected is not None:
                errmsg += '(expected %s)' % ' or '.join(repr(x) for x in expected)
            if token is not None:
                errmsg += '(got %s)' % repr(token)
            self.raise_error(errmsg, linenum)
        return token

    def peek(self, line, isinstance=isinstance, tuple=tuple):
        if not line or not isinstance(line[-1], tuple):
            return None
        return line[-1][0].lower()

    def combine_strings(self, line, type=type, tuple=tuple):
        while len(line) > 2:
            c, b, a = line[-3:]
            if type(a) == type(b) == type(c) == tuple:
                if a[0].startswith('"') and b[0] == '&' and c[0].startswith('"'):
                    line[-3:] = [(a[0][:-1] + c[0][1:], a[1])]
                    continue
            break

    def __init__(self, fname):
        try:
            self.run(fname)
            parsed_ok = not self.warnings
        except KeyboardInterrupt:
            raise
        except:
            print "Retrying", fname
            self.run(fname, True)
            self.warnings.append((1, "Invalid comments before entity"))
            parsed_ok = False
        for chip in self.chips:
            chip.parsed_ok = parsed_ok

    def run(self, fname, hack=False):
        self.fname = fname
        self.warnings = warnings = []
        self.chips = []
        self.packages = []
        self.chip = None

        tokens = tokenize(fname, warnings, hack)
        tokens = nestparens(tokens)
        tokens = group_semi(tokens)
        if not tokens:
            self.raise_error("No file data found (all inside comment?)")
        line = tokens[0]
        if not isinstance(line, list):
            self.raise_error("Expected initial entity statement", tokens[0][1])
        tokens.reverse()
        linenum = 1
        while tokens:
            line = tokens.pop()
            line.reverse()
            keyword = self.peek(line)
            if keyword is None:
                self.raise_error("Parse error", linenum)
            linenum = line.pop()[-1]
            starting = keyword in ('entity', 'package')
            chip = self.chip
            if starting != (chip is None):
                if starting:
                    self.raise_error("Unexpected nested entity declaration", linenum)
                else:
                    self.raise_error("Unexpected %s declaration outside entity" % repr(keyword), linenum)
            func = getattr(self, 'handle_' + keyword, None)
            if func is None:
                self.raise_error("Unexpected keyword %s" % repr(keyword), linenum)
            line = func(line, chip, linenum)
            if line is not None:
                line.reverse()
                tokens.append(line)

    def handle_entity(self, line, chip, linenum):
        chip = self.chip = ChipInfo(self.fname)
        self.chips.append(chip)

        name = chip.name = self.nexttok(line, linenum, errmsg = 'Expected chip name after entity')
        self.nexttok(line, linenum, 'is')
        return line

    def handle_package(self, line, chip, linenum):
        chip = self.chip = ChipInfo(self.fname)
        self.packages.append(chip)

        name = chip.name = self.nexttok(line, linenum, errmsg = 'Expected chip name after entity')
        if name == 'body':
            name = chip.name = self.nexttok(line, linenum, errmsg = 'Expected chip name after entity')
        self.nexttok(line, linenum, 'is')

    def handle_port(self, line, chip, linenum):
        pass

    def handle_generic(self, line, chip, linenum):
        pass

    def handle_constant(self, line, chip, linenum):
        pass

    def handle_use(self, line, chip, linenum):
        chip.use.add(self.nexttok(line, linenum, errmsg='Expected library name after use'))
        self.nexttok(line, linenum, '.')
        self.nexttok(line, linenum, 'all')
        if line:
            self.warnings.append((linenum, "Expected ';' after 'use <package>.all'"))

    def handle_attribute(self, line, chip, linenum):
        name = self.nexttok(line, linenum, errmsg='Expected attribute name')
        separator = self.nexttok(line, linenum, (':', 'of'))
        if separator == ':':
            self.nexttok(line, linenum, 'bsdl_extension')
            if line:
                self.raise_error('Unexpected text after "bsdl_extension"')
            chip.bsdl_extension.add(name)
            return
        parent = self.nexttok(line, linenum, errmsg="Expected parent for attribute %s" % name)
        self.nexttok(line, linenum, ':')
        attrtype = self.nexttok(line, linenum, ('signal', 'entity'))
        if attrtype == 'signal':
            return
        self.nexttok(line, linenum, 'is')
        if parent.lower() != chip.name.lower():
            self.warnings.append((linenum, "Entity name mismatch on attribute"))
        self.combine_strings(line)
        if len(line) != 1:
            line = ' '.join(str(x[0]) for x in reversed(line))
            self.raise_error('Expected exactly one value for attribute %s; got %s\n    (Missing &?)' % (name, repr(line)))
        value = line[0][0]
        assert isinstance(value, str)
        setattr(chip, name, value)

    def handle_end(self, line, chip, linenum):
        self.chip = None
        if not line:
            self.warnings.append((linenum, 'Expected entity name after end'))
            return
        entity = self.nexttok(line, linenum, errmsg='Expected entity name after end')
        if entity.lower() != chip.name.lower():
            self.warnings.append((linenum, "Entity name mismatch on end -- %s and %s" % (entity.lower(), chip.name.lower())))
        if line:
            self.warnings.append((linenum, "Unexpected text after entity end -- %s" % repr(line[:80])))

