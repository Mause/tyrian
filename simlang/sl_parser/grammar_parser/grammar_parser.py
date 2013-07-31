"""
Defines the GrammarParser
"""

from copy import copy

from ...utils import logger
from .grammar_nodes import (
    SubGrammarWrapper,
    ContainerNode,
    LiteralNode,
    MultiNode,
    RENode,
    ORNode
)
# import logging
logger = logger.getChild('GrammarParser')
# logger.setLevel(logging.INFO)


class GrammarParser(object):
    """
    Does the grunt work of parsing the Grammar into a usable object;
    see grammar_nodes.py for more
    """
    def __init__(self):
        self.grammar = {}
        self.settings = {}
        self.token_defs = {}
        self.grammar_mapping = {}

        self.tokens_loaded = False
        self.grammar_loaded = False
        self.grammar_mapping_loaded = False

        self.VALUE_CLEANUP_TRANSFORM = str.maketrans({
            '(': ' ( ',
            ')': ' ) ',
            '+': ' + '
        })

    def load_grammar(self, content: str):
        """
        Load grammars from a string.
        All grammars need not be necessarily be loaded at once,
        but all must be loaded before parse_grammars is called.

        a grammar can be defined like so:

            name: <content>;

        whereby within the following constructs are permissible;

        OR, which can be nested, is denoted by a pipe character:
            <token> | <token>

        many of a particular token:
            <token>+

        a subgrammar is simply specified by name
        """

        logger.debug('Loading grammar')
        rules = content.split(';')
        rules = map(str.strip, rules)
        rules = filter(bool, rules)

        for line in rules:
            print(line)
            if line.startswith('%'):
                line = line[1:]

                assert '=' in line, 'Invalid setting'
                key, value = line.split('=')
                key, value = key.strip(), value.strip()

                self.settings[key] = value
                continue
            elif line.startswith('//'):
                continue

            key, *value = line.split(':')
            key = key.upper()
            value = ':'.join(value)

            # clean up the value a bit
            value = (value.translate(self.VALUE_CLEANUP_TRANSFORM)
                          .replace('/*', ' /* ')
                          .replace('*/', ' */ ')
                          .replace('\n', ' ')
                          .strip()
                          .split(' '))
            # strip each segment, filters for empty fragments
            value = map(str.strip, value)
            value = list(filter(bool, value))

            self.grammar[key] = value

        logger.debug('Grammars: {}'.format(self.grammar.keys()))
        logger.debug('Grammar loaded, rules: {}'.format(len(self.grammar)))

        self.grammar_loaded = True

    def load_token_definitions(self, defs):
        """
        Loads token definitions.

        expected to be formatted as follows;
        {
            'literal': {
                '<content>': '<name>'
            },
            'regex': {
                '<regex_expr>': '<name>'
            }
        }
        """

        logger.info('Loading token definitions')
        self.token_defs['literal'] = {}
        for k, v in defs['literal'].items():
            self.token_defs['literal'][v.upper()] = k

        self.token_defs['regex'] = {}
        for k, v in defs['regex'].items():
            self.token_defs['regex'][v.upper()] = k

        logger.info('Loaded token definitions, {} tokens'.format(
            len(self.token_defs['literal']) + len(self.token_defs['regex'])))

        self.tokens_loaded = True

    def load_grammar_mapping(self, grammar_mapping, nodes):
        """
        Load in a mapping between grammars and Nodes
        """
        logger.info('Loading grammar mappings')

        def get(obj, key):
            if type(obj) == dict and key in obj:
                return obj[key]
            elif hasattr(obj, key):
                return getattr(obj, key)

        for k, v in grammar_mapping.items():
            self.grammar_mapping[k] = get(nodes, v)
            logger.debug('{}: {}'.format(k, self.grammar_mapping[k]))

        self.grammar_mapping_loaded = True

    def parse_grammars(self):
        """
        Parses loaded grammars into "check trees"
        Simply iterates over grammars and calls parse_grammar on them.
        """
        assert self.grammar_loaded, 'Please load a grammar before calling this'

        logger.info('Parsing grammars into grammar trees')
        logger.debug('Grammars: {}'.format(list(self.grammar.keys())))

        settings = {
            'grammar_mapping': self.grammar_mapping
        }

        parsed_grammars = {}

        for grammar_key in self.grammar:
            logger.debug('Parsing {}'.format(grammar_key))
            cur, _ = self.parse_grammar(
                self.grammar[grammar_key],
                grammar_key,
                settings=settings)

            assert len(cur.subs) >= 1, cur.subs

            parsed_grammars[grammar_key] = cur
            logger.debug('End product: {}'.format(cur))

        logger.info('Grammar trees loaded')

        return parsed_grammars

    def parse_grammar(self, grammar, grammar_key, settings):
        """
        Called by parse_grammars, 'tis recommended that you simply use that.

        Returns a ContainerNode, where a list of tokens can be
        passed into the root Node.check(<args>) function and validated
        according to the grammar
        """

        assert self.grammar_loaded, 'Please load a grammar before calling this'

        out_tokens = []
        grammar = copy(grammar)
        comment = False

        while grammar:
            token = grammar.pop(0)

            logger.debug('token: {}'.format(token))
            if token.upper() in self.token_defs['literal']:
                literal = self.token_defs['literal'][token]
                out_tokens.append(LiteralNode(
                    settings=settings, content=literal))

            elif token.upper() in self.token_defs['regex']:
                regex = self.token_defs['regex'][token.upper()]
                out_tokens.append(RENode(
                    settings=settings,
                    regex=regex))

            elif token.upper() in self.grammar:
                # we give the sub grammar wrapper a reference to this
                # GrammarParser instance so that it can look up the
                # grammar when its check function is called
                out_tokens.append(SubGrammarWrapper(
                    settings=settings,
                    key=token,
                    grammar_parser_inst=self))

            elif token == '(':
                logger.debug('Step down')
                sub_nodes, grammar = self.parse_grammar(
                    grammar, grammar_key, settings)
                if sub_nodes:
                    out_tokens.append(sub_nodes)

            elif token == ')':
                logger.debug('Step up')
                if out_tokens:
                    return (
                        ContainerNode(settings=settings, subs=out_tokens),
                        grammar)

            elif token == '|':
                first_half = ContainerNode(settings=settings, subs=out_tokens)
                out_tokens = []
                second_half, grammar = self.parse_grammar(
                    grammar, grammar_key, settings)
                if first_half or second_half:
                    out_tokens.append(ORNode(
                        settings=settings, left=first_half, right=second_half))

            elif token == '+':
                token = out_tokens.pop(-1)
                if token:
                    out_tokens.append(MultiNode(settings=settings, sub=token))

            elif token == '/*':
                while token != '*/' and grammar:
                    token = grammar.pop(0)
                comment = True

            else:
                raise Exception('In "{}" token "{}"'.format(
                    grammar_key, token))

            if not comment:
                logger.debug(out_tokens[-1])
            else:
                comment = False

        return ContainerNode(settings=settings, subs=out_tokens), grammar
