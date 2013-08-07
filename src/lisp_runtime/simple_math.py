from .registry import lisp_function


@lisp_function(name="+")
def symbol_simple_add(*args, **kwargs):
    return sum(args)
