# standard library
import os
import json

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

    :param token_defs_filename: name of file containing token_defs, see \
    :py:meth:`GrammarParser.load_token_definitions <tyrian.typarser.grammar_parser.GrammarParser.load_token_definitions>` \
    for definition

    :param grammar_filename: name of file containing the grammar, see \
    :py:meth:`GrammarParser.load_grammar <tyrian.typarser.grammar_parser.GrammarParser.load_grammar>` \
    for definition

    :param settings: dictionary containing settings
    """

    def __init__(self,
                 token_defs_filename=None,
                 grammar_filename=None,
                 settings=None):
        self.resources = os.path.join(
            os.path.dirname(__file__), 'Grammar')

        # read in the tokens
        token_defs_filename = self._resource(token_defs_filename, 'tokens.json')
        with open(token_defs_filename) as fh:
            token_defs = json.load(fh)

        # read in the Grammar
        grammar_filename = self._resource(grammar_filename, 'Grammar')
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

    def _resource(self, default, supplied):
        return (
            os.path.join(self.resources, supplied) if supplied
            else default
        )

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
