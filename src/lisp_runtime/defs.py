from .registry import lisp_function


@lisp_function(name="defparameter")
def defparameter(*args, **kwargs):
    """
    allows you to define a parameter...
    i presume this is essentially a variable
    """
    raise NotImplementedError()
