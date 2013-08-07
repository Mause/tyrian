from ..utils import logger

logger = logger.getChild('LispRegistry')


if 'lisp_registry' not in globals():
    lisp_registry = {}


def lisp_function(name):
    """
    Registers decorated function in the lisp_registry
    """
    assert name

    def decorator(func):
        # logger.debug('Registering function with name: {}'.format(name))
        func.lisp_name = name
        lisp_registry[name] = func
        return func
    return decorator


def main():
    from pprint import pprint
    pprint(lisp_registry)


if __name__ == '__main__':
    main()
