# application specific
from .registry import lisp_function


@lisp_function(name="defparameter")
def defparameter(key, val):
    """
    allows you to define a global parameter/variable
    """
    globals()[key] = val
    assert key in globals()


@lisp_function(name='defvar')
def defvar(*args):
    """
    functionally identical to defparameter
    """
    defparameter(*args)
