# application specific
from ..utils import logger

logger = logger.getChild('LispRegistry')


if 'lisp_registry' not in globals():
    lisp_registry = {}


def lisp_function(**kwargs):
    """
    Registers decorated function in the lisp_registry

    if the decorator is being used like so;

    .. code-block:: python

        @lisp_registry
        def func():
            pass

    then we assume the __name__ attribute of the function is to be used

    if the decorator is used like so;

    .. code-block:: python

        @lisp_registry(name="blardy")
        def randy():
            pass

    then we use the supplied name :)
    """

    def decorator(func):
        logger.debug('Registering function with name: {}'.format(kwargs['name']))
        name = kwargs['name']

        assert name not in lisp_registry, (
            'Function "{}" already exists'.format(name))

        lisp_registry[name] = func
        return func

    if 'name' not in kwargs and not kwargs['name']:
        return decorator(kwargs['func'])
    else:
        return decorator


def main():
    from pprint import pprint
    pprint(lisp_registry)


if __name__ == '__main__':
    main()
