from .registry import lisp_function


@lisp_function(name="+")
def simple_add(*args, **kwargs):
    raise NotImplementedError()
