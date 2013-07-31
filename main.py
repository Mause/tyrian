import os
import json
# from pprint import pprint

from simlang.utils import logger
from simlang.sl_lexer import Lexer
from simlang.sl_parser import Parser


class Simlang(object):
    """
    Primary interface

    """
    def __init__(self,
                 token_defs_filename=None,
                 grammar_filename=None,
                 grammar_mapping_filename=None):
        self.resources = os.path.join(os.path.dirname(__file__), 'simlang/resources')

        token_defs_filename = self.resource(
            token_defs_filename, 'tokens.json')

        grammar_filename = self.resource(
            grammar_filename, 'Grammar_old')

        grammar_mapping_filename = self.resource(
            grammar_mapping_filename, 'GrammarMapping.json')

        with open(token_defs_filename) as fh:
            token_defs = json.load(fh)

        self.lexer = Lexer(token_defs)

        import simlang.nodes as nodes

        with open(grammar_mapping_filename) as fh:
            grammar_mapping = json.load(fh)

        with open(grammar_filename) as fh:
            raw_grammar = fh.read()

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
        with open(filename) as fh:
            lexed = self.lexer.lex(fh.read(), filename)

        # lexed = self.lexer.lex(input('> '))
        # lexed = self.lexer.lex('(print "world")')
        # with open('lexed.json', 'w') as fh:
            # json.dump(lexed, fh)

        # import pdb
        # pdb.set_trace()

        from pprint import pprint
        logger.debug(self.parser.grammar_parser.grammar_mapping)

        logger.info('### kettle of fish ###')

        start_token = self.parser.grammar_parser.settings['start_token']

        logger.debug('Start token: {}'.format(start_token.upper()))

        base_grammar = self.parser.grammar[start_token.upper()]

        index = 0
        results = []
        while index < len(lexed):
            result = base_grammar.check(lexed[index:], '<list>')

            assert result['result'], (result, ' '.join([x['token'] for x in lexed[index:]]))
            del result['tokens']

            # what_was_consumed = ' '.join([x['token'] for x in lexed[index:index+result['consumed']]])
            results.append((result))
            # , what_was_consumed))

            index += result['consumed']

        pprint(results)

        # parse_tree = self.parser.parse(lexed)

        # print(parse_tree.pprint())


def main():
    s = Simlang()
    # s.run('simlang/resources/lisp/lambda.lisp')
    # s.run('simlang/resources/lisp/wizards_game.lisp')
    s.run('simlang/resources/lisp/test.lisp')

if __name__ == '__main__':
    main()
    # import sys
    # import trace

    # coverdir = os.path.join(os.path.dirname(__file__), 'out')

    # tracer = trace.Trace(
    #     ignoredirs=[sys.prefix, sys.exec_prefix],
    #     trace=0,
    #     count=1)
    # try:
    #     tracer.run('main()')
    # finally:
    #     r = tracer.results()
    #     r.write_results(show_missing=True, coverdir=coverdir)
