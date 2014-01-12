# application specific
from .registry import lisp_function


@lisp_function(name="+")
def symbol_simple_add(*args):
    return sum(args)


@lisp_function(name="*")
def symbol_simple_mul(*args):
    from functools import reduce
    from operator import mul

    return reduce(mul, args)


@lisp_function(name="/")
def symbol_simple_div(*args):
    from functools import reduce
    from operator import truediv

    return reduce(truediv, args)


@lisp_function(name="-")
def symbol_simple_sub(*args):
    from functools import reduce
    from operator import sub

    return reduce(sub, args)


@lisp_function(name='sqrt')
def sqrt(arg):
    from math import sqrt as math_sqrt
    return math_sqrt(arg)
