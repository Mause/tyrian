# application specific
from .registry import lisp_function


@lisp_function(name="defparameter")
def defparameter(*args, **kwargs):
    """
    allows you to define a parameter/variable
    """
    globals()[args[0]] = args[1]
    assert args[0] in globals()
