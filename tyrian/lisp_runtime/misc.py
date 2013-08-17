from .registry import lisp_function


@lisp_function(name="return")
def return_func(arg):
    """
    when used as the last function call in a function,
    its output is used as the return value for the function
    """
    return arg


@lisp_function(name="callfunc")
def call_function(func, *args):
    """
    helper for calling function, usually lambda functions
    """
    return func(*args)
