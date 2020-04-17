"""This module implements the built-in data types of the Scheme language, along
with a parser for Scheme expressions.

In addition to the types defined in this file, some data types in Scheme are
represented by their corresponding type in Python:
    number:       int or float
    symbol:       string
    boolean:      bool
    unspecified:  None

The __repr__ method of a Scheme value will return a Python expression that
would be evaluated to the value, where possible.

The __str__ method of a Scheme value will return a Scheme expression that
would be read to the value, where possible.
"""

from __future__ import print_function  # Python 2 compatibility

import numbers

from ucb import main, trace, interact
from scheme_tokens import tokenize_lines, DELIMITERS
from buffer import Buffer, InputReader, LineReader


# Pairs and Scheme lists

class Pair(object):
    """A pair has two instance attributes: first and rest. rest must be a Pair or nil

    >>> s = Pair(1, Pair(2, nil))
    >>> s
    Pair(1, Pair(2, nil))
    >>> print(s)
    (1 2)
    >>> print(s.map(lambda x: x+4))
    (5 6)
    """
    def __init__(self, first, rest):
        from scheme_builtins import scheme_valid_cdrp, SchemeError
        if not scheme_valid_cdrp(rest):
            raise SchemeError("cdr can only be a pair, nil, or a promise but was {}".format(rest))
        self.first = first
        self.rest = rest

    def __repr__(self):
        return 'Pair({0}, {1})'.format(repr(self.first), repr(self.rest))

    def __str__(self):
        s = '(' + repl_str(self.first)
        rest = self.rest
        while isinstance(rest, Pair):
            s += ' ' + repl_str(rest.first)
            rest = rest.rest
        if rest is not nil:
            s += ' . ' + repl_str(rest)
        return s + ')'
    def __len__(self):
        n, rest = 1, self.rest
        while isinstance(rest, Pair):
            n += 1
            rest = rest.rest
        if rest is not nil:

            src.pop_first()
            raise TypeError('length attempted on improper list')
        return n

    def __eq__(self, p):
        if not isinstance(p, Pair):
            return False
        return self.first == p.first and self.rest == p.rest

    def map(self, fn):
        """Return a Scheme list after mapping Python function FN to SELF."""
        mapped = fn(self.first)
        if self.rest is nil or isinstance(self.rest, Pair):
            return Pair(mapped, self.rest.map(fn))
        else:
            raise TypeError('ill-formed list (cdr is a promise)')

class nil(object):
    """The empty list"""

    def __repr__(self):
        return 'nil'

    def __str__(self):
        return '()'

    def __len__(self):
        return 0

    def map(self, fn):
        return self

nil = nil() # Assignment hides the nil class; there is only one instance

# Scheme list parser

# Quotation markers
quotes = {"'":  'quote',
          '`':  'quasiquote',
          ',':  'unquote'}

characters = ['!', '$', '%', '&', '*', '/', ':', '<', '=', '>', '?', '@', '^', '_', '~', '-', '+', '.']

def scheme_read(src):
    """Read the next expression from SRC, a Buffer of tokens.

    >>> scheme_read(Buffer(tokenize_lines(['nil'])))
    nil
    >>> scheme_read(Buffer(tokenize_lines(['1'])))
    1
    >>> scheme_read(Buffer(tokenize_lines(['true'])))
    True
    >>> scheme_read(Buffer(tokenize_lines(['(+ 1 2)'])))
    Pair('+', Pair(1, Pair(2, nil)))
    """
    if src.current() is None:
        raise EOFError

    if (type(src.current()) is int) or (type(src.current()) is float):
        return src.pop_first()
    elif src.current() == "nil":
        src.pop_first()
        return nil
    elif type(src.current()) is bool and src.current():
        src.pop_first()
        return True
    elif type(src.current()) is bool and not src.current():
        src.pop_first()
        return False
    elif src.current() == "(":
        src.pop_first()
        return read_tail(src)
    else:
        if type(src.current()) is str and check_valid(src.current()):
            return src.pop_first().lower()
        elif type(src.current()) is str and src.current() in quotes:
            quote = quotes[src.current()]
            src.pop_first()
            return Pair(quote, Pair(scheme_read(src), nil))
        else:
             raise SyntaxError("unexpected tokens")
    # BEGIN PROBLEM 1/2
    "*** YOUR CODE HERE ***"

    # END PROBLEM 1/2

def check_valid(s):
    for c in s.lower():
        if (not 0 <= ord(c) - ord('a') <= 25) and (not 0 <= ord(c) - ord('0') <= 9) and (c not in characters):
            return False
    return True
        

def read_tail(src):
    """Return the remainder of a list in SRC, starting before an element or ).
    >>> read_tail(Buffer(tokenize_lines([')'])))
    nil
    >>> read_tail(Buffer(tokenize_lines(['2 3)'])))
    Pair(2, Pair(3, nil))
    """
    try:
        if src.current() is None:
            raise SyntaxError('unexpected end of file')
        # BEGIN PROBLEM 1
        "*** YOUR CODE HERE ***"
        if src.current() == ")":
            src.pop_first()
            return nil
        elif src.current() == "(":
            return Pair(scheme_read(src), read_tail(src))
        elif type(src.current()) is int or type(src.current()) is float:
            return Pair(src.pop_first(), read_tail(src))
        elif type(src.current()) is bool and src.current():
            src.pop_first()
            return Pair(True, read_tail(src))
        elif type(src.current()) is bool and not src.current():
            src.pop_first()
            return Pair(False, read_tail(src))
        elif type(src.current()) is str and check_valid(src.current()):
            return Pair(src.pop_first().lower(), read_tail(src))
        elif type(src.current()) is str and src.current() in quotes:
            quote = quotes[src.current()]
            src.pop_first()
            return Pair(Pair(quote, Pair(scheme_read(src), nil)), read_tail(src))
        else:
            raise SyntaxError('unexpected tokens')
        # END PROBLEM 1
    except EOFError:
        raise SyntaxError('unexpected end of file')

# Convenience methods

def buffer_input(prompt='scm> '):
    """Return a Buffer instance containing interactive input."""
    return Buffer(tokenize_lines(InputReader(prompt)))

def buffer_lines(lines, prompt='scm> ', show_prompt=False):
    """Return a Buffer instance iterating through LINES."""
    if show_prompt:
        input_lines = lines
    else:
        input_lines = LineReader(lines, prompt)
    return Buffer(tokenize_lines(input_lines))

def read_line(line):
    """Read a single string LINE as a Scheme expression."""
    return scheme_read(Buffer(tokenize_lines([line])))

def repl_str(val):
    """Should largely match str(val), except for booleans and undefined."""
    if val is True:
        return "#t"
    if val is False:
        return "#f"
    if val is None:
        return "undefined"
    if isinstance(val, numbers.Number) and not isinstance(val, numbers.Integral):
        return repr(val)  # Python 2 compatibility
    return str(val)

# Interactive loop
def read_print_loop():
    """Run a read-print loop for Scheme expressions."""
    while True:
        try:
            src = buffer_input('read> ')
            while src.more_on_line:
                expression = scheme_read(src)
                print('str :', expression)
                print('repr:', repr(expression))
        except (SyntaxError, ValueError) as err:
            print(type(err).__name__ + ':', err)
        except (KeyboardInterrupt, EOFError):  # <Control>-D, etc.
            print()
            return

@main
def main(*args):
    if len(args) and '--repl' in args:
        read_print_loop()
