# standard library
import os
import json
import pkg_resources

# application specific
from .lexer import Lexer
from .utils import logger
from .typarser import Parser
from .compiler import Compiler

# third party
from peak.util.assembler import Code


class Tyrian(object):
    """
    Primary interface to tyrian

    :param settings: dictionary containing settings
    """

    def __init__(self, settings=None):
        self.resources = os.path.join(
            os.path.dirname(__file__), 'Grammar')

        # read in the tokens
        token_defs_filename = pkg_resources.resource_filename(
            __name__, 'Grammar\\tokens.json')
        with open(token_defs_filename) as fh:
            token_defs = json.load(fh)

        # read in the Grammar
        grammar_filename = pkg_resources.resource_filename(
            __name__, 'Grammar\\Grammar')
        with open(grammar_filename) as fh:
            raw_grammar = fh.read()

        # load up the appropriate Nodes for the parser
        from . import nodes

        self.lexer = Lexer(token_defs)
        self.parser = Parser(
            token_defs=token_defs,
            raw_grammar=raw_grammar,
            grammar_mapping=nodes.grammar_mapping,
            settings=settings
        )
        self.compiler = Compiler()

    def compile(self, input_filename: str) -> Code:
        """
        Compile a file into python bytecode

        :param input_filename: path to file containing lisp code
        """

        with open(input_filename) as fh:
            input_filename_content = fh.read()
            lexed = self.lexer.lex(
                input_filename_content, input_filename)

        logger.info('### kettle of fish ###')

        parse_tree = self.parser.parse(lexed)

        logger.info('### kettle of fish ###')

        bytecode = self.compiler.compile(input_filename, parse_tree)

        return bytecode


def main():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    main()
