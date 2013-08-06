from .registry import lisp_function


@lisp_function(name="+")
def symbol_simple_add(*args, **kwargs):
    print(args)
    # raise NotImplementedError()


@lisp_function(name="simple_add")
def simple_add(*args):
    return sum(args)
    # raise NotImplementedError()
