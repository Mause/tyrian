# application specific
from ..utils import logger

logger = logger.getChild('LispRegistry')


if 'lisp_registry' not in globals():
    lisp_registry = {}


def lisp_function(**kwargs):
    """
    Registers decorated function in the lisp_registry
    """

    def decorator(func):
        # logger.debug('Registering function with name: {}'.format(name))
        name = kwargs['name']

        assert name not in lisp_registry, (
            'Function "{}" already exists'.format(name))

        lisp_registry[name] = func
        return func

    if 'name' not in kwargs and not kwargs['name']:
        # if the decorator is being used like so;
        # @lisp_registry
        # def func(): pass
        # then we assume the name of the function is to be used
        return decorator(kwargs['func'])
    else:
        # if the decorator is used like so;
        # @lisp_registry(name="blardy")
        # def randy(): pass
        # then we use the supplied name :)
        return decorator


def main():
    from pprint import pprint
    pprint(lisp_registry)


if __name__ == '__main__':
    main()
