# standard library
import re
from copy import copy
from collections import namedtuple

# application specific
from ...utils import logger, flatten
from ...exceptions import NoSuchGrammar

logger = logger.getChild('GrammerNodes')

__all__ = [
    'GrammarNode',
    'SubGrammarWrapper',
    'MultiNode',
    'LiteralNode',
    'ContainerNode',
    'RENode',
    'ORNode'
]


class GrammarNode(object):
    """
    Base GrammarNode
    """

    def __repr__(self) -> str:
        raise NotImplementedError()

    def check(self, tokens: list, path: str) -> dict:
        raise NotImplementedError()


class SubGrammarWrapper(GrammarNode):
    """
    Acts as proxy for subgrammar, ensuring that we need not copy the
    subgrammar, nor that we need parse the grammars in any particular order.

    :param grammar_parser_inst: an instance of the \
    :py:class:`GrammarParser <tyrian.typarser.grammar_parser.GrammarParser>`, \
    used to access subgrammars
    """
    def __init__(self, settings: dict, key: str, grammar_parser_inst) -> None:
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        self.key = key
        self.grammar_parser_inst = grammar_parser_inst

    def __repr__(self) -> str:
        return '<SubGrammarWrapper key="{}">'.format(self.key)

    def build_parse_tree(self, token: str):
        token = flatten(token)

        key = self.key.upper()
        grammar_mapping = self.settings['grammar_mapping']

        if key in grammar_mapping:
            if token:
                try:
                    return grammar_mapping[key](token)
                except TypeError:
                    raise TypeError('{} accepts no arguments'.format(
                        grammar_mapping[key].__qualname__
                    ))
            else:
                logger.debug(
                    'Mapping found for {}, '
                    'but token is empty: "{}"'.format(key, token))
        else:
            logger.debug('No mapping found for {}'.format(key))
            return token

    def check(self, tokens: list, path: str) -> dict:
        path += '.' + '<' + self.key + '>'

        logger.debug(path)

        key = self.key.upper()

        if key not in self.grammar_parser_inst.grammars:
            raise NoSuchGrammar('No such grammar as "{}"'.format(key))

        grammar = self.grammar_parser_inst.grammars[key]

        result = grammar.check(tokens, path)
        if result['result']:
            result['parse_tree'] = self.build_parse_tree(result['parse_tree'])

        return result


class ContainerNode(GrammarNode):
    """
    Serves as a container for one or more sub Nodes

    :param subs: subnodes to contain
    """
    def __init__(self, settings: dict, subs: list) -> None:
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)
        if 'grammar_definition' in settings:
            del settings['grammar_definition']

        if len(subs) == 1 and type(subs[0]) == ContainerNode:
            subs = subs[0].subs
        elif len(subs) == 1 and type(subs[0]) == ContainerNode:
            subs = []

        my_subs = []
        for sub in subs:
            sub.parent = self
            my_subs.append(sub)
        self.subs = subs

    def __repr__(self) -> str:
        return '<ContainerNode len(subs)=={}>'.format(len(self.subs))

    def check(self, tokens: list, path: str) -> dict:
        logger.debug(path + '.CN')

        response = {
            'tokens': [],
            'parse_tree': []
        }

        result = True
        consumed = 0
        for node in self.subs:
            cur = node.check(tokens[consumed:], path)

            result = result and cur['result']
            if result:
                consumed += cur['consumed']
                response['tokens'] += cur['tokens']

                response['parse_tree'].append(cur['parse_tree'])
            else:
                logger.debug(path + ' failed')
                break

        response['result'] = result
        response['consumed'] = consumed if result else 0
        response['parse_tree'] = flatten(
            response['parse_tree'], can_return_single=True)
        return response


class LiteralNode(GrammarNode):
    """
    Compares a token directly against a string

    :param content: content against which to test
    """
    def __init__(self, settings: dict, content):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        self.content = content

        self.LiteralNode = namedtuple('LiteralNode', 'content,line_no')

    def __repr__(self) -> str:
        return '<LiteralNode content={}>'.format(repr(self.content))

    def check(self, tokens: list, path: str) -> dict:
        logger.debug(path + '.LN<' + self.content + '>')

        if tokens:
            token = tokens[0]['token'] if 'token' in tokens[0] else tokens[0]
            result = token == self.content
        else:
            result = False

        return {
            'result': result,
            'consumed': 1 if result else 0,
            'tokens': [token] if result else [],
            'parse_tree': self.LiteralNode(token, tokens[0]['line_no'])
        }


class RENode(GrammarNode):
    """
    Matches a token against a regular expression

    :param regex: regular expression to match against
    :param name: name of what the regular expression tests for
    """
    def __init__(self, settings: dict, regex, name):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)
        self.name = name

        self.raw_re = regex
        self.RE = re.compile(regex)

        self.RENode = namedtuple('RENode', 'content,name,line_no')

    def __repr__(self) -> str:
        return '<RENode regex="{}">'.format(self.raw_re)

    def check(self, tokens: list, path: str) -> dict:

        token = tokens[0]['token']

        logger.debug(path + '.REN<' + self.raw_re + '><' + token + '>')
        match = self.RE.match(token)
        result = bool(match)

        if result:
            try:
                match = match.groups()[0]
                match = float(match)
            except:
                pass
        parse_tree = (
            self.RENode(match, self.name, tokens[0]['line_no'])
            if result else None
        )

        return {
            'result': result,
            'consumed': 1 if result else 0,
            'tokens': [token] if result else [],
            'parse_tree': parse_tree
        }


class ORNode(GrammarNode):
    """
    checks between two possible sets of subnodes

    :param left: node on left side of OR symbol
    :param right: node on right side of OR symbol
    """
    def __init__(self, settings: dict, left, right):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return '<ORNode left={} right={}>'.format(
            self.left, self.right)

    def check(self, tokens: list, path: str) -> dict:
        path += '.ORN'
        logger.debug(path)

        left_result = self.left.check(tokens, path)
        logger.debug('Left: {}'.format(left_result))

        if left_result['result']:
            left_result['parse_tree'] = flatten(
                left_result['parse_tree'], can_return_single=True)
            return left_result

        right_result = self.right.check(tokens, path)
        right_result.__repr__()

        logger.debug('Right: {}'.format(right_result))
        if right_result['result']:
            right_result['parse_tree'] = flatten(
                right_result['parse_tree'], can_return_single=True)
            return right_result

        return {
            'result': False,
            'consumed': 0,
            'tokens': [],
            'parse_tree': False
        }


class MultiNode(GrammarNode):
    """
    Checks for multiple instances of a set of subnode

    :param sub: node to checks for multiple instances of
    """
    def __init__(self, settings: dict, sub):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        sub.parent = self
        self.subs = sub

    def __repr__(self) -> str:
        return '<MultiNode token={}>'.format(self.subs)

    def check(self, tokens: list, path: str) -> dict:
        path += '.MN'
        logger.debug(path)

        response = {
            'tokens': [],
            'result': False,
            'parse_tree': []
        }
        consumed = 0
        while len(tokens) > consumed and tokens[consumed:]:
            r = self.subs.check(tokens[consumed:], path)

            if r['result']:
                response['result'] = True
                response['parse_tree'].append(r['parse_tree'])
            else:
                logger.debug(path + ' failed')
                break

            consumed += r['consumed']
            response['tokens'] += r['tokens']

        response["consumed"] = consumed if response['result'] else 0
        if not response['result']:
            response['tokens'] = []
            response['parse_tree'] = []
        else:
            response['parse_tree'] = flatten(
                response['parse_tree'], can_return_single=True)
        return response
