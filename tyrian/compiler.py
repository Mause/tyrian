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
    AST
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
    Handles compilation of :py:class:`AST <tyrian.nodes.AST>`'s
    """

    def __init__(self):
        self.locals = set()

    @enforce_types
    def compile_parse_tree(self, filename: str, parse_tree) -> Code:
        """
        Takes a filename and a parse_tree and returns a BytecodeAssembler
        Code object

        :param filename: filename of file to compile
        :param parse_tree: parse_tree to compile
        :rtype: Code
        """

        filename = os.path.abspath(filename)

        line_no = -1

        code = Code()
        code.set_lineno(line_no)
        code = self.bootstrap_obj(code)
        line_no += 1

        code.co_filename = filename
        line_no, code = self.compile_parse_tree_internal(
            codeobject=code,
            parse_tree=parse_tree,
            line_no=line_no,
            filename=filename
        )

        line_no += 1
        code.set_lineno(line_no)

        code.return_(None)
        return code

    @enforce_types
    def compile_parse_tree_internal(self,
                                    codeobject: Code,
                                    parse_tree: AST,
                                    line_no: int,
                                    filename: str) -> tuple:
        """
        Compiles a single AST

        :param codeobject: Code instance to output opcodes to
        :param parse_tree: parse_tree to compile
        :param line_no: current line number
        :rtype: tuple
        """
        assert isinstance(parse_tree, AST)

        for element in parse_tree.content:
            line_no += 1

            codeobject.set_lineno(line_no)

            line_no, codeobject = self.compile_single(
                codeobject=codeobject,
                filename=filename,
                element=element,
                line_no=line_no,
                result_required=False,
                scope=[]
            )

        return line_no, codeobject

    @enforce_types
    def compile_single(self,
                       codeobject: Code,
                       filename: str,
                       element: Node,
                       line_no: int,
                       result_required: bool,
                       scope: list) -> tuple:
        """
        compiles a single Node
        """

        # if not element.content:
        #     return line_no, codeobject

        if isinstance(element.content[0], (IDNode, SymbolNode)):
            if element.content[0].content == 'defun':
                # wahey! creating a function!
                line_no, codeobject = self.compile_function(
                    codeobject,
                    filename,
                    element,
                    line_no
                )

            elif element.content[0].content == 'lambda':
                raise Exception((element, element.content))

            elif element.content[0].content in ('let',
                                                'defparameter',
                                                'defvar'):
                # inline variable assignments
                line_no, codeobject = self.handle_variable_assignment(
                    codeobject,
                    filename,
                    element,
                    line_no,
                    scope
                )

            else:
                # whahey! calling a function!
                line_no, codeobject = self.call_function(
                    codeobject,
                    filename,
                    element,
                    line_no,
                    scope
                )

                if not result_required:
                    # if the result aint required, clean up the stack
                    codeobject.POP_TOP()
        else:
            raise Exception('{} -> {}'.format(element, element.content))

        return line_no, codeobject

    @enforce_types
    def handle_variable_assignment(self,
                                   codeobject: Code,
                                   filename: str,
                                   element: Node,
                                   line_no: int,
                                   scope: list) -> tuple:
        """
        Handles an inline variable assignment
        """

        function_name, name, args = element.content
        name = name.content

        if isinstance(args, ListNode):
            # if it has to evaluated first, do so
            logger.debug('subcall: {} -> {}, with scope {}'.format(
                args, args.content, scope))
            line_no, codeobject = self.compile_single(
                codeobject=codeobject,
                filename=filename,
                element=args,
                line_no=line_no,
                result_required=True,
                scope=scope
            )

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

        return line_no, codeobject

    @enforce_types
    def call_function(self,
                      codeobject: Code,
                      filename: str,
                      element: Node,
                      line_no: int,
                      scope: list) -> tuple:
        """
        Generates code to call a function, with possible nested calls as
        function arguments
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
                logger.debug('subcall -> {}, with scope {}'.format(
                    arg.content, scope)
                )

                line_no, codeobject = self.compile_single(
                    codeobject=codeobject,
                    filename=filename,
                    element=arg,
                    line_no=line_no,
                    result_required=True,
                    scope=scope
                )

            elif isinstance(arg, (NumberNode, StringNode)):
                codeobject(Const(arg.content))

            else:
                raise Exception(arg)

        codeobject.CALL_FUNCTION(len(args))

        return line_no, codeobject

    @enforce_types
    def compile_function(self,
                         codeobject: Code,
                         filename: str,
                         element: Node,
                         line_no: int) -> tuple:
        """
        'Compiles' function, using the last functions return value
        in the function body as the return value for the function proper
        """
        _, name, args, *body = element.content

        name = name.content
        args = args.content

        args = [arg.content for arg in args]

        func_code = codeobject.nested(name, args)

        if body and any(el.content for el in body):
            *body, return_func = [el for el in body if el.content]

            # compile all bar the last statement
            for body_frag in body:
                line_no, func_code = self.compile_single(
                    codeobject=func_code,
                    filename=filename,
                    element=body_frag,
                    line_no=line_no,
                    result_required=False,
                    scope=args
                )

            # compile the last statement, and ask for the result value
            line_no, func_code = self.compile_single(
                codeobject=func_code,
                filename=filename,
                element=return_func,
                line_no=line_no,
                result_required=True,
                scope=args
            )
            func_code.RETURN_VALUE()

        else:
            func_code.return_()

        # inject the function into the codeobject
        codeobject = self.inject_function_code(
            codeobject=codeobject,
            function_codeobj=func_code.code(codeobject),
            name=name
        )

        return line_no, codeobject

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
            name=name
        )

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
