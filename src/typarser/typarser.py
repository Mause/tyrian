# application specific
from ..utils import flatten
from .grammar_parser import GrammarParser
from ..nodes import ParseTree, ContainerNode, ListNode
from ..exceptions import TyrianSyntaxError, NoSuchGrammar


class Parser(object):
    """
    Simplifies parsing
    """
    def __init__(self, **kwargs):
        self.grammar_parser = GrammarParser(**kwargs)

    def parse(self, lexed: list) -> ParseTree:
        start_token = self.grammar_parser.settings['start_token'].upper()

        if start_token not in self.grammar_parser.grammars:
            raise NoSuchGrammar('No such grammar as "{}"'.format(start_token))

        base_grammar = self.grammar_parser.grammars[start_token]

        index = 0
        results = []

        while index < len(lexed):
            result = base_grammar.check(lexed[index:], '<list>')

            if not result['result']:
                raise TyrianSyntaxError()
                # , (result, ' '.join([x['token'] for x in lexed[index:]]))
            del result['tokens']

            results.append(result)

            index += result['consumed']

        processed = self._process(results)
        return ParseTree(processed)

    def _process(self, parsed: list) -> ContainerNode:
        processed = []
        for result in parsed:
            parse_tree = result['parse_tree']
            parse_tree = flatten(parse_tree, can_return_single=True)

            parse_tree = ListNode(parse_tree)

            processed.append(parse_tree)
        return processed