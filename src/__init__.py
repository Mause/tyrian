import os
import json
from .lexer import Lexer
from .utils import logger
from .typarser import Parser
from .compiler import Compiler

class Tyrian(object):
    """
    Primary interface
    """

    def __init__(self,
                 token_defs_filename=None,
                 grammar_filename=None,
                 grammar_mapping_filename=None,
                 settings=None):
        self.resources = os.path.join(os.path.dirname(__file__), 'resources')

        token_defs_filename = self.resource(
            token_defs_filename, 'tokens.json')
        with open(token_defs_filename) as fh:
            token_defs = json.load(fh)

        grammar_filename = self.resource(
            grammar_filename, 'Grammar_old')
        with open(grammar_filename) as fh:
            raw_grammar = fh.read()

        grammar_mapping_filename = self.resource(
            grammar_mapping_filename, 'GrammarMapping.json')
        with open(grammar_mapping_filename) as fh:
            grammar_mapping = json.load(fh)

        from . import nodes

        self.lexer = Lexer(token_defs)
        self.parser = Parser(
            token_defs=token_defs,
            raw_grammar=raw_grammar,
            grammar_mapping=grammar_mapping,
            nodes=nodes,
            settings=settings
        )
        self.compiler = Compiler()

    def resource(self, default, supplied):
        return (
            os.path.join(self.resources, supplied) if supplied
            else default
        )

    def run(self, filename):
        filename = os.path.join(
            os.path.dirname(__file__),
            filename)
        with open(filename) as fh:
            lexed = self.lexer.lex(fh.read(), filename)

        from pprint import pprint

        logger.info('### kettle of fish ###')

        results = self.parser.parse(lexed)

        results = results.expressions

        pprint(results[0][0]['parse_tree'])

        # parse_tree = self.parser.parse(lexed)

        # print(parse_tree.pprint())

def main():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    main()
