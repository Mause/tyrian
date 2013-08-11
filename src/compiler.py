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
    Const,
    Local
)

logger = logger.getChild('Compiler')


class Compiler(object):
    """
    Handles compilation of ParseTree's
    """

    def __init__(self):
        self.locals = set()

    @enforce_types
    def compile(self, filename: str, parse_tree) -> Code:
        """
        Takes a filename and a parse_tree and returns a BytecodeAssembler
        Code object

        'Compiles' the parse tree

        If you want to compile something
        """

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
        """
        Compiles a single Node
        """

        if isinstance(element, ParseTree):
            for element in element.content:
                lineno += 1

                codeobject.set_lineno(lineno)

                lineno, codeobject = self._compile_single(
                    codeobject=codeobject,
                    filename=filename,
                    element=element,
                    lineno=lineno,
                    result_required=False,
                    scope=[])

        else:
            lineno, codeobject = self._compile_single(
                codeobject=codeobject,
                filename=filename,
                element=element,
                lineno=lineno,
                result_required=True,
                scope=[])

        return lineno, codeobject

    @enforce_types
    def _compile_single(self,
                        codeobject: Code,
                        filename: str,
                        element: Node,
                        lineno: int,
                        result_required: bool,
                        scope: list) -> tuple:
        """
        compiles a single Node
        """

        if isinstance(element.content[0], (IDNode, SymbolNode)):
            if element.content[0].content == 'defun':
                # wahey! creating a function!
                lineno, codeobject = self.compile_function(
                    codeobject,
                    filename,
                    element,
                    lineno)

            elif element.content[0].content in ('let',
                                                'defparameter',
                                                'defvar'):
                # inline variable assignments
                lineno, codeobject = self.handle_variable_assignment(
                    codeobject,
                    filename,
                    element,
                    lineno)

            else:
                # whahey! calling a function!
                lineno, codeobject = self.call_function(
                    codeobject,
                    filename,
                    element,
                    lineno,
                    scope)

                if not result_required:
                    # if the result aint required, clean up the stack
                    codeobject.POP_TOP()
        else:
            raise Exception('{} -> {}'.format(element, element.content))

        return lineno, codeobject

    @enforce_types
    def handle_variable_assignment(self,
                                   codeobject: Code,
                                   filename: str,
                                   element: Node,
                                   lineno: int) -> tuple:
        """
        Handles an inline variable assignment
        """

        function_name, name, args = element.content
        name = name.content
        if isinstance(args, ListNode):
            # if it has to evaluated first, do so
            logger.debug('subcall: {} -> {}'.format(args, args.content))
            lineno, codeobject = self._compile(
                codeobject,
                args,
                lineno,
                filename)
        elif isinstance(args, (NumberNode, StringNode)):
            # if it is simply a literal, treat it as such
            codeobject.LOAD_CONST(args.content)

        # global or local
        if function_name.content == 'let':
            codeobject.STORE_FAST(name)
            self.locals.add(name)
        elif function_name.content in ('defparameter', 'defvar'):
            codeobject.STORE_GLOBAL(name)
        else:
            raise Exception(function_name)

        return lineno, codeobject

    @enforce_types
    def call_function(self,
                      codeobject: Code,
                      filename: str,
                      element: Node,
                      lineno: int,
                      scope: list) -> tuple:
        """
        Generates code to call a function, with possible nested calls
        """

        name, *args = element.content

        name = name.content
        codeobject(Global(name))

        for arg in args:
            if isinstance(arg, (IDNode, SymbolNode)):
                if arg.content in scope:
                    codeobject.LOAD_FAST(arg.content)
                elif arg.content in self.locals:
                    codeobject(Local(arg.content))
                else:
                    codeobject.LOAD_GLOBAL(arg.content)
            elif isinstance(arg, ListNode):
                logger.debug('subcall -> {}'.format(arg.content))
                lineno, codeobject = self._compile(
                    codeobject,
                    arg,
                    lineno,
                    filename)
            elif isinstance(arg, (NumberNode, StringNode)):
                codeobject(Const(arg.content))
            else:
                raise Exception(arg)

        codeobject.CALL_FUNCTION(len(args))

        return lineno, codeobject

    @enforce_types
    def compile_function(self,
                         codeobject: Code,
                         filename: str,
                         element: Node,
                         lineno: int) -> tuple:
        """
        'Compiles' function, using the last functions return value
        in the function body as the return value for the function proper
        """
        _, name, args, *body = element.content

        name = name.content
        args = args.content

        args = [arg.content for arg in args]

        func_code = codeobject.nested(name, args)
        func_code.co_filename = filename

        if body:
            *body, return_func = body

            # compile all but the last statement
            for body_frag in body:
                lineno, func_code = self._compile_single(
                    codeobject=func_code,
                    filename=filename,
                    element=body_frag,
                    lineno=lineno,
                    result_required=False,
                    scope=args)

            lineno, func_code = self._compile_single(
                codeobject=func_code,
                filename=filename,
                element=return_func,
                lineno=lineno,
                result_required=True,
                scope=args)
            func_code.RETURN_VALUE()

        else:
            func_code.return_()

        codeobject = self.inject_function_code(
            codeobject=codeobject,
            function_codeobj=func_code.code(codeobject),
            name=name)

        return lineno, codeobject

    @enforce_types
    def inject_function(self,
                        codeobject: Code,
                        function: types.FunctionType,
                        name: str=None) -> Code:
        """
        Injects a python land function via inject_function_code
        """
        name = name if name else function.__name__

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
        """
        Injects a code object as a function
        """

        codeobject.LOAD_CONST(function_codeobj)
        codeobject.LOAD_CONST(name)
        codeobject.MAKE_FUNCTION(0)
        codeobject.STORE_GLOBAL(name)

        return codeobject

    def write_code_to_file(self,
                           codeobject: types.CodeType,
                           filehandler=None,
                           filename: str=None):
        """
        Write a code object to the specified filehandler
        """

        st = os.stat(filename or __file__)
        size = st.st_size & 0xFFFFFFFF
        timestamp = int(st.st_mtime)

        # write a placeholder for the MAGIC
        filehandler.write(b'\0\0\0\0')

        wr_long(filehandler, timestamp)
        wr_long(filehandler, size)
        marshal.dump(codeobject, filehandler)
        filehandler.flush()

        # write the magic to the start
        filehandler.seek(0, 0)
        filehandler.write(MAGIC)

    @enforce_types
    def bootstrap_obj(self, codeobject: Code) -> Code:
        """
        Injects all the library functions
        """

        from .lisp_runtime.registry import lisp_registry
        assert lisp_registry

        for name, function in lisp_registry.items():
            codeobject = self.inject_function(codeobject, function, name)

        return codeobject
