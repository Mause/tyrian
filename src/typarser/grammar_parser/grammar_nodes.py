import re
# import sys
# import pdb
# import time
from ...utils import logger
from collections import namedtuple

import logging
logger = logger.getChild('GrammerNodes')
logger.setLevel(logging.INFO)
# time.sleep = lambda x: None  # time.sleep(0.5 * x)
# logger.debug = lambda *a, **kw: sys.stdout.write('DEBUG: {}\n'.format(a[0]))


class Node(object):
    """
    Base Node
    """

    def __repr__(self):
        raise NotImplementedError()

    def build_parse_tree(self, token):
        # if hasattr()
        raise Exception((self, token))

        raise Exception(self.settings['grammar_mapping'])

        return token

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


class SubGrammarWrapper(Node):
    """
    Acts as proxy for subgrammar.

    Serves to ensure that we need not copy the subgrammar,
    and that we need not parse the grammars in any particular order.
    """
    def __init__(self, settings, key, grammar_parser_inst):
        # these setting are for the grammar mappings and such
        self.settings = settings

        self.key = key
        self.grammar_parser_inst = grammar_parser_inst

    def __repr__(self):
        return '<SubGrammarWrapper key="{}">'.format(self.key)

    def _check(self, tokens, path):
        path += '.' + '<' + self.key + '>'
        # self.__qualname__ +
        logger.debug(path)

        key = self.key.upper()
        grammar = self.grammar_parser_inst.grammars[key]

        return grammar.check(tokens, path)


class ContainerNode(Node):
    """
    Serves as a container for one or more sub Nodes
    """
    def __init__(self, settings, subs):
        # these setting are for the grammar mappings and such
        self.settings = settings

        if len(subs) == 1 and type(subs[0]) == ContainerNode:
            subs = subs[0].subs
        elif len(subs) == 1 and type(subs[0]) == ContainerNode and len(subs[0]) == 0:
            subs = []

        my_subs = []
        for sub in subs:
            sub.parent = self
            my_subs.append(sub)
        self.subs = subs

    def __repr__(self):
        return '<ContainerNode len(subs)=={}>'.format(len(self.subs))

    def _check(self, tokens, path):
        # we dont log the ContainerNode, it just creates spam
        logger.debug(path + '.CN')

        response = {
            'tokens': [],
            'parse_tree': []
        }

        result = True
        consumed = 0
        for node in self.subs:
            # time.sleep(2)
            cur = node.check(tokens[consumed:], path)

            result = result and cur['result']
            if result:
                consumed += cur['consumed']
                response['tokens'] += cur['tokens']
                assert (cur['parse_tree'])
                response['parse_tree'].append(cur['parse_tree'])
            else:
                logger.debug(path + ' failed')
                break

        response['result'] = result
        response['consumed'] = consumed if result else 0
        response['parse_tree'] = self.build_parse_tree(
            response['parse_tree'] if response['parse_tree'] else [])
        return response


class LiteralNode(Node):
    """
    Compares a token directly against a string
    """
    def __init__(self, settings, content):
        # these setting are for the grammar mappings and such
        self.settings = settings

        self.content = content

        self.LiteralNode = namedtuple('LiteralNode', 'content')

    def __repr__(self):
        return '<LiteralNode content={}>'.format(repr(self.content))

    def _check(self, tokens, path):
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


class RENode(Node):
    def __init__(self, settings, regex):
        # these setting are for the grammar mappings and such
        self.settings = settings

        self.raw_re = regex
        self.RE = re.compile(regex)

        self.RENode = namedtuple('RENode', 'content')

    def __repr__(self):
        return '<RENode regex="{}">'.format(self.raw_re)

    def _check(self, tokens, path):

        token = tokens[0]['token']

        logger.debug(path + '.REN<' + self.raw_re + '><' + token + '>')
        match = self.RE.match(token)
        result = bool(match)
        return {
            'result': result,
            'consumed': 1 if result else 0,
            'tokens': [token] if result else [],
            'parse_tree': self.RENode(token)
        }


class ORNode(Node):
    def __init__(self, settings, left, right):
        # these setting are for the grammar mappings and such
        self.settings = settings

        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

    def __repr__(self):
        return '<ORNode left="{}" right="{}">'.format(
            self.left, self.right)

    def _check(self, tokens, path):
        path += '.ORN'
        logger.debug(path)

        f_result = self.left.check(tokens, path)
        logger.debug('Left: {}'.format(f_result))

        if f_result['result']:
            return f_result

        s_result = self.right.check(tokens, path)
        logger.debug('Right: {}'.format(s_result))
        if s_result['result']:
            return s_result

        return {
            'result': False,
            'consumed': 0,
            'tokens': [],
            'parse_tree': False
        }


class MultiNode(Node):
    debugging = False

    def __init__(self, settings, sub):
        # these setting are for the grammar mappings and such
        self.settings = settings

        sub.parent = self
        self.subs = sub

    def __repr__(self):
        return '<MultiNode token={}>'.format(self.subs)

    def _check(self, tokens, path):
        path += '.MN'
        logger.debug(path)

        response = {
            'tokens': [],
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
            response['parse_tree'] = self.build_parse_tree(response['parse_tree'])
        return response
