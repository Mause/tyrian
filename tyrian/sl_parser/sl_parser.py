
# from ..nodes import ParseTree
# from ..sl_exceptions import SimlangSyntaxError
from .grammar_parser import GrammarParser


class Parser(object):
    """
    At the moment simply a wrapper for GrammarParser,
    though in the future will perform parsing duties
    """
    def __init__(self, token_defs, raw_grammar, grammar_mapping, nodes):
        self.grammar_parser = GrammarParser(
            raw_grammar=raw_grammar,
            token_defs=token_defs,
            grammar_mapping=grammar_mapping,
            nodes=nodes
        )

    # def parse(self, lexed):
    #     return ParseTree(self._parse(lexed))

    # def _parse(self, tokens):
    #     nodes = []

    #     tokens = list(filter(bool, tokens))

    #     while tokens:
    #         token = tokens.pop(0)

    #     raise Exception()

    # def _parse(self, tokens):
    #     nodes = []

    #     tokens = list(filter(bool, tokens))

    #     while tokens:
    #         token = tokens.pop(0)

    #         possible = self.determine_possible(tokens)
    #         if possible:
    #             logger.debug('possible: {}'.format(possible))
    #         raise Exception()

    #         if token[0] == 'OPEN_BRACKET':
    #             logger.debug("LISTNODE START")
    #             nodes.append(self._parse(tokens))
    #         elif token[0] == 'CLOSE_BRACKET':
    #             logger.debug('LISTNODE END')
    #             return ListNode(nodes)

    #         elif token[0] == 'ID':
    #             logger.debug('IDNODE')
    #             nodes.append(IDNode(token[1]))

    #         elif token[0] == 'NUMBER':
    #             logger.debug("NUMBER")
    #             nodes.append(NumberNode(token[1]))
    #         else:
    #             raise SimlangSyntaxError(token)

    #     return ListNode(nodes)
