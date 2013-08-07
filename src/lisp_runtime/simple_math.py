# standard library
from functools import reduce
from operator import mul, truediv, sub

# application specific
from .registry import lisp_function


@lisp_function(name="+")
def symbol_simple_add(*args):
    return sum(args)


@lisp_function(name="*")
def symbol_simple_mul(*args):
    return reduce(mul, args)


@lisp_function(name="/")
def symbol_simple_div(*args):
    return reduce(truediv, args)


@lisp_function(name="-")
def symbol_simple_sub(*args):
    return reduce(sub, args)
