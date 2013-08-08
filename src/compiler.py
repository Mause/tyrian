# standard libary
import os
import types
import marshal
from types import CodeType
from py_compile import wr_long, MAGIC

# application specific
from .nodes import (
    Node,
    IDNode,
    SymbolNode,
    ListNode,
    NumberNode,
    StringNode,
    ParseTree
)
from .utils import logger, enforce_types

# third party
from peak.util.assembler import (
    Code,
    Global,
    Call,
    Const,
    # Function,
    # Suite
)

logger = logger.getChild('Compiler')


class Compiler(object):
    def __init__(self):
        self.called = False

    @enforce_types
    def inject_function(self,
                        codeobject: Code,
                        function: types.FunctionType,
                        name: str=None) -> Code:
        name = name if name else function.__name__
        # logger.debug('injecting function: "{}" -> {}'.format(name, function))
        codeobject = self.inject_function_code(
            codeobject=codeobject,
            function_codeobj=function.__code__,
            name=name)

        return codeobject

    @enforce_types
    def inject_function_code(self,
                             codeobject: Code,
                             function_codeobj: CodeType,
                             name: str=None) -> Code:
        codeobject.LOAD_CONST(function_codeobj)
        codeobject.LOAD_CONST(name)
        codeobject.MAKE_FUNCTION(0)
        codeobject.STORE_GLOBAL(name)

        return codeobject

    @enforce_types
    def write_code_to_file(self, codeobject: Code, fh):

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

    @enforce_types
    def bootstrap_obj(self, codeobject: Code) -> Code:
        from .lisp_runtime.registry import lisp_registry
        assert lisp_registry

        for name, function in lisp_registry.items():
            obj = self.inject_function(codeobject, function, name)

        return obj

    @enforce_types
    def compile(self, filename: str, parse_tree) -> Code:
        assert not self.called
        self.called = True
        filename = os.path.abspath(filename)

        lineno = -1

        code = Code()
        code.set_lineno(lineno)
        code = self.bootstrap_obj(code)
        lineno += 1

        code.co_filename = filename
        lineno, code = self._compile(
            codeobject=code,
            element=parse_tree,
            lineno=lineno,
            filename=filename)

        lineno += 1
        code.set_lineno(lineno)

        code.return_(None)
        return code

    @enforce_types
    def _compile(self,
                 codeobject: Code,
                 element: (Node, object),
                 lineno: int,
                 filename: str) -> tuple:
        if isinstance(element, ParseTree):
            for element in element.content:
                print('element:', element, element.content)
                lineno += 1
                codeobject.set_lineno(lineno)

                codeobject = self._compile_single(
                    codeobject=codeobject,
                    filename=filename,
                    element=element,
                    lineno=lineno,
                    result_required=False)

        else:
            codeobject = self._compile_single(
                codeobject=codeobject,
                filename=filename,
                element=element,
                lineno=lineno,
                result_required=True)

        return lineno, codeobject

    @enforce_types
    def _compile_single(self,
                        codeobject: Code,
                        filename: str,
                        element: Node,
                        lineno: int,
                        result_required: bool):
        if isinstance(element.content[0], (IDNode, SymbolNode)):
            if element.content[0].content == 'defun':
                # wahey! creating a function!
                codeobject = self.compile_function(
                    codeobject,
                    filename,
                    element,
                    lineno)
            else:
                # whahey! calling a function!
                codeobject = self.call_function(codeobject, filename, element, lineno)
                if not result_required:
                    codeobject.POP_TOP()
        else:
            raise Exception('{} -> {}'.format(element, element.content))

        return codeobject

    @enforce_types
    def call_function(self,
                      codeobject: Code,
                      filename: str,
                      element: Node,
                      lineno: int) -> Code:
        name, *args = element.content

        name = name.content
        codeobject(Global(name))

        for arg in args:
            if isinstance(arg, (IDNode, SymbolNode)):
                # proper_args.append(Local(arg.content))
                codeobject(Global(arg.content))
            elif isinstance(arg, ListNode):
                logger.debug('subcall: {} -> {}'.format(arg, arg.content))
                _, codeobject = self._compile(
                    codeobject,
                    arg,
                    lineno,
                    filename)
            elif isinstance(arg, (NumberNode, StringNode)):
                codeobject(Const(arg.content))
            else:
                raise Exception(arg)

        # if name == 'pprint':
        #     raise Exception(args)
        codeobject.CALL_FUNCTION(len(args))

        return codeobject

    @enforce_types
    def compile_function(self,
                         codeobject: Code,
                         filename: str,
                         element: Node,
                         lineno: int) -> Code:
        _, name, args, *body = element.content

        name = name.content
        args = args.content

        func_code = codeobject.nested(name)
        func_code.co_filename = filename
        print('func_code:', func_code)

        if body:
            *body, return_func = body

            # compile all but the last statement
            for body_frag in body:
                print('compiling: {}:{} -> {}'.format(
                    body_frag,
                    id(body_frag),
                    body_frag.content))
                func_code = self._compile_single(
                    codeobject=func_code,
                    filename=filename,
                    element=body_frag,
                    lineno=lineno,
                    result_required=False)

            func_code = self._compile_single(
                codeobject=func_code,
                filename=filename,
                element=return_func,
                lineno=lineno,
                result_required=True)
            func_code.RETURN_VALUE()
        else:
            func_code.return_()

        codeobject = self.inject_function_code(
            codeobject=codeobject,
            function_codeobj=func_code.code(codeobject),
            name=name)

        return codeobject
