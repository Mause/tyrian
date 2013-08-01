import os
import json
from .lexer import Lexer
from .utils import logger
from .typarser import Parser


class Tyrian(object):
    """
    Primary interface
    """

    def __init__(self,
                 token_defs_filename=None,
                 grammar_filename=None,
                 grammar_mapping_filename=None):
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
            nodes=nodes
        )

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

        # lexed = self.lexer.lex(input('> '))
        # lexed = self.lexer.lex('(print "world")')
        # with open('lexed.json', 'w') as fh:
            # json.dump(lexed, fh)

        from pprint import pprint

        logger.info('### kettle of fish ###')

        start_token = self.parser.grammar_parser.settings['start_token']

        base_grammar = self.parser.grammar_parser.grammars[start_token.upper()]
        print(base_grammar)

        index = 0
        results = []
        while index < len(lexed):
            result = base_grammar.check(lexed[index:], '<list>')

            assert result['result'], (result, ' '.join([x['token'] for x in lexed[index:]]))
            del result['tokens']

            what_was_consumed = ' '.join([x['token'] for x in lexed[index:index+result['consumed']]])
            results.append((result, what_was_consumed))

            index += result['consumed']

        pprint(results[0][0]['parse_tree'])

        # parse_tree = self.parser.parse(lexed)

        # print(parse_tree.pprint())
