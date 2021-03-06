import types
import logging
from functools import wraps

if 'logger' not in globals():
    logger = logging.getLogger('Main')
    logger.setLevel(logging.DEBUG)

    logger.propagate = False

    if not logger.handlers:
        hdlr = logging.StreamHandler()
        hdlr.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            # '%(asctime)s - '
            '%(name)s - '
            '%(levelname)s '
            '%(filename)s:%(lineno)d: '
            '%(message)s')
        hdlr.setFormatter(formatter)

        logger.addHandler(hdlr)


def flatten(obj, can_return_single: bool=False):
    """
    Flattens nested lists, like so;

    >>> from tyrian.utils import flatten
    >>> flatten([[[[[[['value']]]]]]], can_return_single=True)
    'value'

    >>> flatten([[[[[[['value']]]]]]], can_return_single=False)
    ['value']

    :param obj: nested list of lists, depth uncertain
    :param can_return_single: see above
    """

    if type(obj) == list and len(obj) == 1 and type(obj[0]) == list:
        return flatten(obj[0], can_return_single)
    elif type(obj) == list and len(obj) == 1 and can_return_single:
        return obj[0]
    else:
        return obj


def check_type(name, *args):
    param, value, assert_type = args
    if not (isinstance(value, assert_type) or
            issubclass(type(value), assert_type) or
            type(value) == assert_type):
        raise AssertionError(
            'Check failed for {0} - parameter {1} = {2} not {3}.'
            .format(name, *args))
    return value


def enforce_types(func: types.FunctionType):
    """
    checks supplied argument types against the annotations

    :param func: function to enforce argument types for
    """
    @wraps(func)
    def newf(*args, **kwargs):
        name = func.__name__
        for k, v in kwargs.items():
            check_type(name, k, v, ann[k])
        if 'return' in ann:
            return check_type(name, '<return_value>', func(*args, **kwargs), ann['return'])
        else:
            return func(*args, **kwargs)

    ann = func.__annotations__
    newf.__type_checked = True

    return newf
