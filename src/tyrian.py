# standard library
import os
import json

# application specific
from .lexer import Lexer
from .utils import logger
from .typarser import Parser
from .compiler import Compiler


class Tyrian(object):
    """
    Primary interface to tyrian
    """

    def __init__(self,
                 token_defs_filename=None,
                 grammar_filename=None,
                 settings=None):
        self.resources = os.path.join(
            os.path.dirname(__file__), 'resources\\Grammar')

        # read in the tokens
        token_defs_filename = self.resource(token_defs_filename, 'tokens.json')
        with open(token_defs_filename) as fh:
            token_defs = json.load(fh)

        # read in the Grammar
        grammar_filename = self.resource(grammar_filename, 'Grammar')
        with open(grammar_filename) as fh:
            raw_grammar = fh.read()

        # load up the appropriate Nodes for the parser
        from . import nodes

        self.lexer = Lexer(token_defs)
        self.parser = Parser(
            token_defs=token_defs,
            raw_grammar=raw_grammar,
            nodes=nodes,
            settings=settings
        )
        self.compiler = Compiler()

    def resource(self, default, supplied):
        return (
            os.path.join(self.resources, supplied) if supplied
            else default
        )

    def compile(self, input_filename: str):
        """
        Compile a file into python bytecode
        """

        with open(input_filename) as fh:
            input_filename_content = fh.read()
            lexed = self.lexer.lex(
                input_filename_content, input_filename)

        logger.info('### kettle of fish ###')

        parse_tree = self.parser.parse(lexed)

        print(parse_tree.pprint())

        bytecode = self.compiler.compile(input_filename, parse_tree)

        return bytecode


def main():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    main()
