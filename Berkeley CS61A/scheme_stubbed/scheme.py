"""A Scheme interpreter and its read-eval-print loop."""
from __future__ import print_function  # Python 2 compatibility

from scheme_builtins import *
from scheme_reader import *
from ucb import main, trace

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, tail = False): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in environment ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Pair('+', Pair(2, Pair(2, nil)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    if expr == 'nil' or expr is nil:
        return nil
    elif type(expr) is int or type(expr) is float or type(expr) is bool:
        return expr
    elif type(expr) is str:
        cur = env.look_up(expr)
        if cur is None:
            raise SchemeError("Cannot find symbol in the current environment!")
        else:
            return cur
    elif expr is None:
        return None

    if tail:
        return Thunk(expr, env)

    result = Thunk(expr, env)
    while isinstance(result, Thunk):
        expr, env = result.expr, result.env
        if isinstance(expr, Pair):
            first, rest = expr.first, expr.rest
            if type(first) is str and first in SPECIAL_FORMS:
                result = SPECIAL_FORMS[first](rest, env)
            else:
                eval_first = scheme_eval(first, env)
                if scheme_procedurep(eval_first):
                    if isinstance(eval_first, MacroProcedure):
                        result = eval_first.apply(rest, env)
                    else:
                        rest = rest.map(lambda x: scheme_eval(x, env))
                        result = scheme_apply(eval_first, rest, env)
                else:
                    raise SchemeError("Invalid call expression {}".format(str(eval_first)))
        else:
            result = scheme_eval(expr, env)
    return result

def self_evaluating(expr):
    return scheme_atomp(expr) or scheme_stringp(expr) or expr is None

def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    environment ENV."""
    check_procedure(procedure)
    return procedure.apply(args, env)

################
# Environments #
################

class Frame(object):
    """An environment frame binds Scheme symbols to Scheme values."""

    def __init__(self, parent):
        """An empty frame with parent frame PARENT (which may be None)."""
        "Your Code Here"
        self.parent = parent
        self.bindings = {}

    def __repr__(self):
        if self.parent is None:
            return '<Global Frame>'
        s = sorted(['{0}: {1}'.format(k, v) for k, v in self.bindings.items()])
        return '<{{{0}}} -> {1}>'.format(', '.join(s), repr(self.parent))

    def define(self, symbol, value):
        """Define Scheme SYMBOL to have VALUE."""
        self.bindings[symbol] = value

    def look_up(self, symbol):
        cur_frame = self
        while(cur_frame is not None and symbol not in cur_frame.bindings):
            cur_frame = cur_frame.parent

        if cur_frame is None:
            return None
        else:
            return cur_frame.bindings[symbol]

    # BEGIN PROBLEM 2/3
    "*** YOUR CODE HERE ***"
    # END PROBLEM 2/3

##############
# Procedures #
##############

class Procedure(object):
    """The supertype of all Scheme procedures."""

def scheme_procedurep(x):
    return isinstance(x, Procedure)

class BuiltinProcedure(Procedure):
    """A Scheme procedure defined as a Python function."""

    def __init__(self, fn, use_env=False, name='builtin'):
        self.name = name
        self.fn = fn
        self.use_env = use_env

    def __str__(self):
        return '#[{0}]'.format(self.name)

    def apply(self, args, env):
        """Apply SELF to ARGS in ENV, where ARGS is a Scheme list.

        >>> env = create_global_frame()
        >>> plus = env.bindings['+']
        >>> twos = Pair(2, Pair(2, nil))
        >>> plus.apply(twos, env)
        4
        """
        # BEGIN PROBLEM 2
        "*** YOUR CODE HERE ***"
        python_args = []
        cur = args
        while(cur != nil):
            python_args.append(cur.first)  
            cur = cur.rest
        if self.use_env:
            python_args.append(env)

        try:
            return self.fn(*python_args)
        except:
            raise SchemeError("The function is not well-defined")
        
        # END PROBLEM 2

class LambdaProcedure(Procedure):
    """A procedure defined by a lambda expression or a define form."""

    def __init__(self, formals, body, env):
        """A procedure with formal parameter list FORMALS (a Scheme list),
        whose body is the Scheme list BODY, and whose parent environment
        starts with Frame ENV."""
        self.formals = formals
        self.body = body
        self.env = env

    def __str__(self):
        return str(Pair('lambda', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'LambdaProcedure({0}, {1}, {2})'.format(
            repr(self.formals), repr(self.body), repr(self.env))

    def apply(self, args, env):
        cur_param, cur_arg = self.formals, args
        new_env = Frame(self.env)
        while(cur_param is not nil):
            if cur_arg is nil:
                raise SchemeError
            else:
                new_env.define(cur_param.first, cur_arg.first)
                cur_param, cur_arg = cur_param.rest, cur_arg.rest
        return do_begin_form(self.body, new_env)

def add_builtins(frame, funcs_and_names):
    """Enter bindings in FUNCS_AND_NAMES into FRAME, an environment frame,
    as built-in procedures. Each item in FUNCS_AND_NAMES has the form
    (NAME, PYTHON-FUNCTION, INTERNAL-NAME)."""
    for name, fn, proc_name in funcs_and_names:
        frame.define(name, BuiltinProcedure(fn, name=proc_name))

#################
# Special Forms #
#################

"""
How you implement special forms is up to you. We recommend you encapsulate the
logic for each special form separately somehow, which you can do here.
"""

def do_define_form(rest, env):
    if scheme_symbolp(rest.first):
        env.define(rest.first, scheme_eval(rest.rest.first, env))
        return rest.first
    else:
        if isinstance(rest.first, Pair) and scheme_symbolp(rest.first.first):
            #Create a lambda procedure that contains list of formal parameters, the current environment, and a body of expressions. 
            if rest.rest is not nil:
                env.define(rest.first.first, LambdaProcedure(rest.first.rest, rest.rest, env))
                return rest.first.first
            else:
                raise SchemeError
        else:
            raise SchemeError

def do_quote_form(rest, env):
    return rest.first

def do_quasiquote_form(rest, env):
    return do_quasiquote_form2(rest.first, env)
    #if rest == nil or type(rest) is int or (type(rest) is str and scheme_reader.check_valid(rest)):
     #   return rest
    #elif isinstance(rest, Pair) and rest.first == 'unquote':
     #   return scheme_eval(rest.rest, env)
    #elif isinstance(rest, Pair):
     #   return Pair(do_quasiquote_for(let ((y (+ x 2)) (x (+ y 3))) (cons x (cons y nil)))m(rest.first, env), do_quasiquote_form(rest.rest, env))
    #else:
     #   raise SchemeError

def do_quasiquote_form2(rest, env):
    if rest == nil or type(rest) is int or (type(rest) is str and check_valid(rest)):
        return rest
    elif isinstance(rest, Pair) and rest.first == 'unquote':
        return scheme_eval(rest.rest.first, env)
    elif isinstance(rest, Pair):
        return Pair(do_quasiquote_form2(rest.first, env), do_quasiquote_form2(rest.rest, env))
    else:
        raise SchemeError


def do_unquote_form(rest, env):
    raise SchemeError("Invalid unquote form.")

def do_lambda_form(rest, env):
    new_env = Frame(env)
    if rest.rest is not nil:
        return LambdaProcedure(rest.first, rest.rest, new_env)
    else:
        raise SchemeError

def do_begin_form(rest, env):
    if rest is nil:
        return None

    while rest is not nil:
        if rest.rest is nil:
            return scheme_eval(rest.first, env, tail = True)
        else:
            scheme_eval(rest.first, env)
            rest = rest.rest


def do_if_form(rest, env):
    cond = scheme_eval(rest.first, env)
    if type(cond) is bool and (not cond):
        return scheme_eval(rest.rest.rest.first, env, tail = True)
    else:
        return scheme_eval(rest.rest.first, env, tail = True)

def do_and_form(rest, env):
    #Have to rewrite this function to support tail recursion in scheme
    cur = rest
    if cur is nil:
        return True

    while(cur is not nil):
        expr = cur.first
        if cur.rest is nil:
            return scheme_eval(expr, env, tail = True)
        else:
            this = scheme_eval(expr, env)
            if type(this) is bool and (not this):
                return False
            else:
                cur = cur.rest

def do_or_form(rest, env):
    #Have to rewrite this function to support tail recursion in scheme
    cur = rest
    if cur is nil:
        return False

    while(cur is not nil):
        expr = cur.first
        if cur.rest is nil:
            return scheme_eval(expr, env, tail = True)
        else:
            this = scheme_eval(expr, env)
            if not (type(this) is bool and (not this)):
                return this
            else:
                cur = cur.rest


def do_cond_form(rest, env):
    #Have to rewrite this function to support tail recursion in scheme
    if rest is nil:
        return None
    cur_clause = rest
    cur_cond = rest.first.first
    while(cur_clause is not nil):
        if cur_cond == 'else':
            return do_begin_form(cur_clause.first.rest, env)
        else:
            pred = scheme_eval(cur_cond, env)
            if type(pred) is bool and (not pred):
                cur_clause = cur_clause.rest
                if cur_clause is nil:
                    break
                cur_cond = cur_clause.first.first
            else:
                if cur_clause.first.rest is nil:
                    return pred
                else:
                    return do_begin_form(cur_clause.first.rest, env)
    return None

def do_let_form(rest, env):
    new_env = Frame(env)
    cur = rest.first
    while(cur is not nil):
        try:
            if(len(cur.first.rest) > 1 or len(cur.first.rest) <= 0):
                raise SchemeError
            else:
                expr = scheme_eval(cur.first.rest.first, env)
        except:
            raise SchemeError("Error in bindings!")

        if scheme_symbolp(cur.first.first):
            new_env.define(cur.first.first, expr)
        else:
            raise SchemeError
        cur = cur.rest
    return do_begin_form(rest.rest, new_env)

def do_mu_form(rest, env):
    if rest.rest is not nil:
        return MuProcedure(rest.first, rest.rest)
    else:
        raise SchemeError

def do_macro_form(rest, env):
    if isinstance(rest.first, Pair) and rest.rest is not nil and scheme_symbolp(rest.first.first):
        env.define(rest.first.first, MacroProcedure(rest.first.rest, rest.rest.first))
    else:
        raise SchemeError("Invalid call to define-macro.")
    return rest.first.first

SPECIAL_FORMS = {
        'define': do_define_form,
        'quote': do_quote_form,
        'quasiquote': do_quasiquote_form,
        'unquote': do_unquote_form,
        'lambda': do_lambda_form,
        'begin': do_begin_form,
        'if': do_if_form,
        'and': do_and_form,
        'or': do_or_form,
        'cond': do_cond_form,
        'let': do_let_form,
        'mu': do_mu_form,
        'define-macro': do_macro_form,
        }

# Utility methods for checking the structure of Scheme programs

def check_form(expr, min, max=float('inf')):
    """Check EXPR is a proper list whose length is at least MIN and no more
    than MAX (default: no maximum). Raises a SchemeError if this is not the
    case.

    >>> check_form(read_line('(a b)'), 2)
    """
    if not scheme_listp(expr):
        raise SchemeError('badly formed expression: ' + repl_str(expr))
    length = len(expr)
    if length < min:
        raise SchemeError('too few operands in form')
    elif length > max:
        raise SchemeError('too many operands in form')
def check_formals(formals):
    """Check that FORMALS is a valid parameter list, a Scheme list of symbols
    in which each symbol is distinct. Raise a SchemeError if the list of
    formals is not a list of symbols or if any symbol is repeated.

    >>> check_formals(read_line('(a b c)'))
    """
    symbols = set()
    def check_and_add(symbol, is_last):
        if not scheme_symbolp(symbol):
            raise SchemeError('non-symbol: {0}'.format(symbol))
        if symbol in symbols:
            raise SchemeError('duplicate symbol: {0}'.format(symbol))
        symbols.add(symbol)

    while isinstance(formals, Pair):
        check_and_add(formals.first, formals.rest is nil)
        formals = formals.rest

    # here for compatibility with DOTS_ARE_CONS
    if formals != nil:
        check_and_add(formals, True)

def check_procedure(procedure):
    """Check that PROCEDURE is a valid Scheme procedure."""
    if not scheme_procedurep(procedure):
        raise SchemeError('{0} is not callable: {1}'.format(
            type(procedure).__name__.lower(), repl_str(procedure)))

#################
# Dynamic Scope #
#################

class MuProcedure(Procedure):
    """A procedure defined by a mu expression, which has dynamic scope.
     _________________
    < Scheme is cool! >
     -----------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    """

    def __init__(self, formals, body):
        """A procedure with formal parameter list FORMALS (a Scheme list) and
        Scheme list BODY as its definition."""
        self.formals = formals
        self.body = body


    def __str__(self):
        return str(Pair('mu', Pair(self.formals, self.body)))

    def __repr__(self):
        return 'MuProcedure({0}, {1})'.format(
            repr(self.formals), repr(self.body))

    def apply(self, args, env):
        cur_param, cur_arg = self.formals, args
        new_env = Frame(env)
        while(cur_param is not nil):
            if cur_arg is nil:
                raise SchemeError
            else:
                new_env.define(cur_param.first, cur_arg.first)
                cur_param, cur_arg = cur_param.rest, cur_arg.rest
        return do_begin_form(self.body, new_env)


##################
# Tail Recursion #
##################

# Make classes/functions for creating tail recursive programs here?

def complete_apply(procedure, args, env):
    """Apply procedure to args in env; ensure the result is not a Thunk.
    Right now it just calls scheme_apply, but you will need to change this
    if you attempt the extra credit."""
    val = scheme_apply(procedure, args, env) 
    while isinstance(val, Thunk):
        expr, env = val.expr, val.env
        val = scheme_eval(expr, env)
    return val

class Thunk:
    def __init__(self, expr, env):
        self.expr = expr
        self.env = env

####################
# Extra Procedures #
####################

def scheme_map(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'map')
    check_type(s, scheme_listp, 1, 'map')
    return s.map(lambda x: complete_apply(fn, Pair(x, nil), env))

def scheme_filter(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'filter')
    check_type(s, scheme_listp, 1, 'filter')
    head, current = nil, nil
    while s is not nil:
        item, s = s.first, s.rest
        if complete_apply(fn, Pair(item, nil), env):
            if head is nil:
                head = Pair(item, nil)
                current = head
            else:
                current.rest = Pair(item, nil)
                current = current.rest
    return head

def scheme_reduce(fn, s, env):
    check_type(fn, scheme_procedurep, 0, 'reduce')
    check_type(s, lambda x: x is not nil, 1, 'reduce')
    check_type(s, scheme_listp, 1, 'reduce')
    value, s = s.first, s.rest
    while s is not nil:
        value = complete_apply(fn, scheme_list(value, s.first), env)
        s = s.rest
    return value

class MacroProcedure(Procedure):
    def __init__(self, formals, body):
        self.formals = formals
        self.body = body

    def apply(self, args, env):
        new_env = Frame(env)
        cur_param = self.formals
        cur_arg = args
        while(cur_param is not nil):
            if cur_arg is nil:
                raise SchemeError("Unmatched number of arguments in macro procedure")
            else:
                firstp, firsta = cur_param.first, cur_arg.first
                new_env.define(firstp, firsta)
                cur_param, cur_arg = cur_param.rest, cur_arg.rest

        body = scheme_eval(self.body, new_env)
        return scheme_eval(body, env)
################
#iInput/Output #
################

def read_eval_print_loop(next_line, env, interactive=False, quiet=False,
                         startup=False, load_files=()):
    """Read and evaluate input until an end of file or keyboard interrupt."""
    if startup:
        for filename in load_files:
            scheme_load(filename, True, env)
    while True:
        try:
            src = next_line()
            while src.more_on_line:
                expression = scheme_read(src)
                result = scheme_eval(expression, env)
                if not quiet and result is not None:
                    print(repl_str(result))
        except (SchemeError, SyntaxError, ValueError, RuntimeError) as err:
            if (isinstance(err, RuntimeError) and
                'maximum recursion depth exceeded' not in getattr(err, 'args')[0]):
                raise
            elif isinstance(err, RuntimeError):
                print('Error: maximum recursion depth exceeded')
            else:
                print('Error:', err)
        except KeyboardInterrupt:  # <Control>-C
            if not startup:
                raise
            print()
            print('KeyboardInterrupt')
            if not interactive:
                return
        except EOFError:  # <Control>-D, etc.
            print()
            return

def scheme_load(*args):
    """Load a Scheme source file. ARGS should be of the form (SYM, ENV) or
    (SYM, QUIET, ENV). The file named SYM is loaded into environment ENV,
    with verbosity determined by QUIET (default true)."""
    if not (2 <= len(args) <= 3):
        expressions = args[:-1]
        raise SchemeError('"load" given incorrect number of arguments: '
                          '{0}'.format(len(expressions)))
    sym = args[0]
    quiet = args[1] if len(args) > 2 else True
    env = args[-1]
    if (scheme_stringp(sym)):
        sym = eval(sym)
    check_type(sym, scheme_symbolp, 0, 'load')
    with scheme_open(sym) as infile:
        lines = infile.readlines()
    args = (lines, None) if quiet else (lines,)
    def next_line():
        return buffer_lines(*args)

    read_eval_print_loop(next_line, env, quiet=quiet)

def scheme_open(filename):
    """If either FILENAME or FILENAME.scm is the name of a valid file,
    return a Python file opened to it. Otherwise, raise an error."""
    try:
        return open(filename)
    except IOError as exc:
        if filename.endswith('.scm'):
            raise SchemeError(str(exc))
    try:
        return open(filename + '.scm')
    except IOError as exc:
        raise SchemeError(str(exc))

def create_global_frame():
    """Initialize and return a single-frame environment with built-in names."""
    env = Frame(None)
    env.define('eval',
               BuiltinProcedure(scheme_eval, True, 'eval'))
    env.define('apply',
               BuiltinProcedure(complete_apply, True, 'apply'))
    env.define('load',
               BuiltinProcedure(scheme_load, True, 'load'))
    env.define('procedure?',
               BuiltinProcedure(scheme_procedurep, False, 'procedure?'))
    env.define('map',
               BuiltinProcedure(scheme_map, True, 'map'))
    env.define('filter',
               BuiltinProcedure(scheme_filter, True, 'filter'))
    env.define('reduce',
               BuiltinProcedure(scheme_reduce, True, 'reduce'))
    env.define('undefined', None)
    add_builtins(env, BUILTINS)
    return env

@main
def run(*argv):
    import argparse
    parser = argparse.ArgumentParser(description='CS 61A Scheme Interpreter')
    parser.add_argument('-load', '-i', action='store_true',
                       help='run file interactively')
    parser.add_argument('file', nargs='?',
                        type=argparse.FileType('r'), default=None,
                        help='Scheme file to run')
    args = parser.parse_args()

    next_line = buffer_input
    interactive = True
    load_files = []

    if args.file is not None:
        if args.load:
            load_files.append(getattr(args.file, 'name'))
        else:
            lines = args.file.readlines()
            def next_line():
                return buffer_lines(lines)
            interactive = False

    read_eval_print_loop(next_line, create_global_frame(), startup=True,
                         interactive=interactive, load_files=load_files)
    tscheme_exitonclick()
