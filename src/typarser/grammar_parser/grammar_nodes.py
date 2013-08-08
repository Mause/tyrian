# standard library
import re
from copy import copy
from collections import namedtuple

# application specific
from ...utils import logger, flatten
from ...exceptions import NoSuchGrammar

logger = logger.getChild('GrammerNodes')


class GrammarNode(object):
    """
    Base GrammarNode
    """

    def __repr__(self) -> str:
        raise NotImplementedError()

    def check(self, *args, **kwargs):
        """
        Passthrough function used during testing
        """

        r = self._check(*args, **kwargs)
        assert 'parse_tree' in r

        if r['result']:
            assert r['parse_tree'], (
                self.__qualname__,
                r,
                self.subs if hasattr(self, 'subs') else 'nope')
        return r


class SubGrammarWrapper(GrammarNode):
    """
    Acts as proxy for subgrammar.

    Serves to ensure that we need not copy the subgrammar,
    and that we need not parse the grammars in any particular order.
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
                return grammar_mapping[key](token)
            else:
                logger.debug(
                    'Mapping found for {}, '
                    'but token is empty: "{}"'.format(key, token))
        else:
            logger.debug('No mapping found for {}'.format(key))
            return token

    def _check(self, tokens: list, path: str) -> dict:
        path += '.' + '<' + self.key + '>'

        logger.debug(path)

        key = self.key.upper()

        if key not in self.grammar_parser_inst.grammars:
            raise NoSuchGrammar('No such grammar as "{}"'.format(key))

        grammar = self.grammar_parser_inst.grammars[key]

        result = grammar.check(tokens, path)
        if result['result'] is True:
            result['parse_tree'] = self.build_parse_tree(result['parse_tree'])

        return result


class ContainerNode(GrammarNode):
    """
    Serves as a container for one or more sub Nodes
    """
    def __init__(self, settings: dict, subs: list) -> None:
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)
        if 'grammar_definition' in settings:
            del settings['grammar_definition']

        if len(subs) == 1 and type(subs[0]) == ContainerNode:
            subs = subs[0].subs
        elif len(subs) == 1 and type(subs[0]) == ContainerNode and len(subs[0]) == 0:
            subs = []

        my_subs = []
        for sub in subs:
            sub.parent = self
            my_subs.append(sub)
        self.subs = subs

    def __repr__(self) -> str:
        return '<ContainerNode len(subs)=={}>'.format(len(self.subs))

    def _check(self, tokens: list, path: str) -> dict:
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
    """
    def __init__(self, settings: dict, content):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        self.content = content

        self.LiteralNode = namedtuple('LiteralNode', 'content')

    def __repr__(self) -> str:
        return '<LiteralNode content={}>'.format(repr(self.content))

    def _check(self, tokens: list, path: str) -> dict:
        logger.debug(path + '.LN<' + self.content + '>')

        if tokens:
            token = tokens[0]['token']
            result = token == self.content
        else:
            result = False

        return {
            'result': result,
            'consumed': 1 if result else 0,
            'tokens': [token] if result else [],
            'parse_tree': self.LiteralNode(token)
        }


class RENode(GrammarNode):
    def __init__(self, settings: dict, regex, name):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)
        self.name = name

        self.raw_re = regex
        self.RE = re.compile(regex)

        self.RENode = namedtuple('RENode', 'content,name')

    def __repr__(self) -> str:
        return '<RENode regex="{}">'.format(self.raw_re)

    def _check(self, tokens: list, path: str) -> dict:

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
            self.RENode(match, self.name)
            if result else None
        )

        return {
            'result': result,
            'consumed': 1 if result else 0,
            'tokens': [token] if result else [],
            'parse_tree': parse_tree
        }


class ORNode(GrammarNode):
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

    def _check(self, tokens: list, path: str) -> dict:
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
    debugging = False

    def __init__(self, settings: dict, sub):
        # these setting are for the grammar mappings and such
        self.settings = copy(settings)

        sub.parent = self
        self.subs = sub

    def __repr__(self) -> str:
        return '<MultiNode token={}>'.format(self.subs)

    def _check(self, tokens: list, path: str) -> dict:
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

            if r['result'] is True:
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
