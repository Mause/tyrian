# application specific
from ..utils import flatten
from .grammar_parser import GrammarParser
from ..nodes import ParseTree, ContainerNode, ListNode
from ..exceptions import TyrianSyntaxError, NoSuchGrammar

__all__ = ['Parser']


class Parser(object):
    """
    Simplifies parsing
    """
    def __init__(self, **kwargs):
        self.grammar_parser = GrammarParser(**kwargs)

    def parse(self, lexed: list) -> ParseTree:
        """
        given a list of tokens, returns a :py:class:`ParseTree <tyrian.nodes.ParseTree>`
        """

        # grab the start token from the settings
        start_token = self.grammar_parser.settings['start_token'].upper()

        if start_token not in self.grammar_parser.grammars:
            raise NoSuchGrammar('No such grammar as "{}"'.format(start_token))

        base_grammar = self.grammar_parser.grammars[start_token]

        index = 0
        results = []

        while index < len(lexed):
            result = base_grammar.check(lexed[index:], '<list>')

            if not result['result']:
                raise TyrianSyntaxError(
                    'error found near line {} in file {}'.format(
                        lexed[index]['line_no'],
                        lexed[index]['filename']))

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
