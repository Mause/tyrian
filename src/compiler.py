# standard libary
import os
import marshal
from py_compile import wr_long, MAGIC

# application specific
from .nodes import (
    IDNode,
    SymbolNode
)

from peak.util.assembler import *
from .utils import logger

logger = logger.getChild('Compiler')


# def function_from_python_land(code, func, name):
#     c = func.__code__
#     if c.co_freevars:
#         frees = c.co_freevars
#         for name in frees:
#             code.LOAD_CLOSURE(name)
#         if sys.version >= '2.5':
#             code.BUILD_TUPLE(len(frees))
#         code.LOAD_CONST(c)
#         return code.MAKE_CLOSURE(len(defaults), len(frees))
#     else:
#         code.LOAD_CONST(c)
#         return code.MAKE_FUNCTION(0)


class Compiler(object):
    def __init__(self):
        self.called = False

    def inject_function(self, obj, function, name=None):
        name = name if name else function.__name__
        print('injecting function:', name, function)
        obj.LOAD_CONST(function.__code__)
        obj.LOAD_CONST(name)
        obj.MAKE_FUNCTION(0)
        obj.STORE_FAST(name)

        return obj

    def bootstrap_obj(self, obj):
        # from .lisp_runtime.bootstrap import run_bootstrap
        # obj = self.inject_function(obj, run_bootstrap)
        # obj.CALL_FUNCTION()

        from .lisp_runtime.registry import lisp_registry
        assert lisp_registry

        for name, function in lisp_registry.items():
            obj = self.inject_function(obj, function, name)

        return obj

    def compile(self, filename, parse_tree):
        assert not self.called
        self.called = True
        lineno = -1

        code = Code()
        code.set_lineno(lineno)
        code = self.bootstrap_obj(code)

        lineno += 1

        print('base_code:', code)
        filename = os.path.abspath(filename)
        code.co_filename = filename

        for element in parse_tree.expressions:
            lineno += 1
            code.set_lineno(lineno)

            op = self._compile(filename, element)
            code(op)

        lineno += 1
        code.set_lineno(lineno)

        code.return_(None)

        return code

    def write_code_to_file(self, codeobject, fh):

        st = os.stat(__file__)
        size = st.st_size & 0xFFFFFFFF
        timestamp = int(st.st_mtime)

        fh.write(b'\0\0\0\0')
        wr_long(fh, timestamp)
        wr_long(fh, size)
        marshal.dump(codeobject, fh)
        fh.flush()
        fh.seek(0, 0)
        fh.write(MAGIC)

        return

    def _compile(self, filename, element):
        if type(element.content[0]) in (IDNode, SymbolNode):
            if element.content[0].content == 'defun':
                # wahey! creating a function!
                op = self.compile_function(filename, element)
            else:
                # whahey! calling a function!
                op = self.call_function(filename, element)
        else:
            raise Exception(element)

        return op

    def call_function(self, filename, element):
        name, *args = element.content

        proper_args = []
        for arg in args:
            if isinstance(arg, (IDNode, SymbolNode)):
                # proper_args.append(Local(arg.content))
                proper_args.append(Global(arg.content))
            else:
                proper_args.append(Const(arg.content))

        name = name.content

        c = Call(Global(name), proper_args, (), (), ())

        # logger.debug('Call: {}({}) -> {}'.format(name, args, c))

        return c

    def compile_function(self, filename, element):
        _, name, args, *body = element.content

        name = name.content
        args = args.content

        # print('args:', type(args), args)
        # for arg in args.content:
        #     print('args:', arg)

        func_code = Code()
        func_code.co_filename = filename
        print('func_code:', func_code)
        for body_frag in body:
            body_frag = self._compile(filename, body_frag)
            func_code(body_frag)

        func = Function(
            body=func_code,
            name=name,
            args=args)

        return func
