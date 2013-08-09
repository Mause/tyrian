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


def flatten(obj, can_return_single=False):
    """
    Flattens nested lists, like so;

    >>> flatten([[[[[[[None]]]]]]], can_return_single=True)
    None

    >>> flatten([[[[[[[None]]]]]]], can_return_single=False)
    [None]

    """

    if type(obj) == list and len(obj) == 1 and type(obj[0]) == list:
        return flatten(obj[0])
    elif type(obj) == list and len(obj) == 1 and can_return_single:
        return obj[0]
    else:
        return obj


def check_type(*args):
    param, value, assert_type = args
    if not (isinstance(value, assert_type) or
            issubclass(type(value), assert_type) or
            type(value) == assert_type):
        raise AssertionError(
            'Check failed - parameter {0} = {1} not {2}.'
            .format(*args))
    return value


def enforce_types(func):
    @wraps(func)
    def newf(*args, **kwargs):
        for k, v in kwargs.items():
            check_type(k, v, ann[k])
        if 'return' in ann:
            return check_type('<return_value>', func(*args, **kwargs), ann['return'])
        else:
            return func(*args, **kwargs)

    ann = func.__annotations__
    newf.__type_checked = True

    return newf
