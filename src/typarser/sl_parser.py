
from ..utils import reduce
from ..nodes import ParseTree, ContainerNode
# from ..sl_exceptions import TyrianSyntaxError
from .grammar_parser import GrammarParser


class Parser(object):
    """

    """
    def __init__(self,
                 token_defs=None,
                 raw_grammar=None,
                 nodes=None,
                 settings=None):
        self.grammar_parser = GrammarParser(
            raw_grammar=raw_grammar,
            token_defs=token_defs,
            nodes=nodes,
            settings=settings
        )

    def parse(self, lexed: list) -> ParseTree:
        start_token = self.grammar_parser.settings['start_token']

        base_grammar = self.grammar_parser.grammars[start_token.upper()]

        index = 0
        results = []

        while index < len(lexed):
            result = base_grammar.check(lexed[index:], '<list>')

            assert result['result'], (result, ' '.join([x['token'] for x in lexed[index:]]))
            del result['tokens']

            results.append(result)

            index += result['consumed']

        processed = self._process(results)
        return ParseTree(processed)

    def _process(self, parsed: list) -> ContainerNode:
        processed = []
        for result in parsed:
            parse_tree = result['parse_tree']
            parse_tree = reduce(parse_tree, can_return_single=True)

            parse_tree = ContainerNode(parse_tree)

            processed.append(parse_tree)
        return ContainerNode(processed, strip=False)
