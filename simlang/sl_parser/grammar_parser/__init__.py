from .grammar_parser import GrammarParser
GrammarParser
# from main import logger


# def main():
#     tokens = {
#         'regex': {
#             r'\d+': 'NUM'
#         },
#         'literal': {
#             'WORD': 'WORD'
#         }
#     }
#     grammar = '''\
#     SENTENCE: (SUB_GRAM | NUM);
#     SUB_GRAM: WORD WORD NUM+;
#     '''

#     gp = GrammarParser()
#     gp.load_token_definitions(tokens)
#     gp.load_grammar(grammar)
#     gp.parse_grammars()

#     logger.debug('### Running ###')

#     # assert gp.check('WORT')['SENTENCE']['result'] is False, gp.check('WORT')
#     # assert gp.check('WORD')['SENTENCE']['result'] is True, gp.check('WORD')
#     def check(x):
#         return all(q['result'] for q in gp.check(x).values())

#     assert check('WORD WORD 69 69 69 ')

# if __name__ == '__main__':
#     main()
