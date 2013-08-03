from .nodes import (
    IDNode
)
from peak.util.assembler import *
from .utils import logger

logger = logger.getChild('Compiler')


class Compiler(object):
    def __init__(self):
        pass

    def compile(self, filename, parse_tree):
        c = Code()
        c.co_filename = filename
        for element in parse_tree.expressions:
            op = self._compile(filename, element)
            c(op)
        return c

    def _compile(self, filename, element):
        if type(element.content[0]) == IDNode:
            if element.content[0].content == 'defun':
                # wahey! creating a function!
                op = self.compile_function(filename, element)
                # c.Function()
            else:
                # whahey! calling a function!
                op = self.call_function(filename, element)

        return op

    def call_function(self, filename, element):
        name, *args = element.content

        import pdb
        pdb.set_trace()

        proper_args = []
        for arg in args:
            if type(arg) == IDNode:
                proper_args.append(Local(arg.content))
            else:
                proper_args.append(Const(arg.content))
            print(proper_args[-1])

        name = name.content

        c = Call(Global(name), proper_args, (), (), ())

        logger.debug('Call: {}({}) -> {}'.format(name, args, c))

        return c

    def compile_function(self, filename, element):
        _, name, args, *body = element.content

        if type(args) == list:
            raise Exception(args)

        logger.debug('Definition: {}({})'.format(name.content, args.content))

        return name.content, None

        c = Code()
        c.co_filename = filename

        # func = Function()

        # func = Code()
        print(name, args, body)
        # func.
        raise Exception(element.content)
