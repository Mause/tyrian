import logging


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


def reduce(obj, can_return_single=False):
    """
    Flattens nested lists, like so;

    >>> reduce([[[[[[[None]]]]]]])
    None

    """

    if type(obj) == list and len(obj) == 1 and type(obj[0]) == list:
        return reduce(obj[0])
    elif type(obj) == list and len(obj) == 1 and can_return_single:
        return obj[0]
    else:
        return obj
