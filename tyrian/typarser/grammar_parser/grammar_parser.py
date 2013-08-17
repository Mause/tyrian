"""
Defines the GrammarParser
"""
# standard library
import inspect
from copy import copy

# application specific
from .grammar_nodes import (
    SubGrammarWrapper,
    ContainerNode,
    LiteralNode,
    MultiNode,
    RENode,
    ORNode
)
from ...utils import logger
from ...exceptions import GrammarDefinitionError

logger = logger.getChild('GrammarParser')


class GrammarParser(object):
    """
    Does the grunt work of parsing the Grammar into a usable object;
    see grammar_nodes.py for more
    """

    def __init__(self,
                 raw_grammar: dict=None,
                 token_defs: dict=None,
                 nodes=None,
                 settings: dict=None):

        self.settings = {}
        self.loaded_grammars = {}
        self.tokens_loaded = False
        self.grammar_loaded = False
        self.grammar_mapping_loaded = False

        self.VALUE_CLEANUP_TRANSFORM = str.maketrans({
            '(': ' ( ',
            ')': ' ) ',
            '+': ' + ',
            '\n': ' '
        })

        if nodes:
            self.load_grammar_mapping(nodes)

        if token_defs:
            self.load_token_definitions(token_defs)

        if raw_grammar:
            self.load_grammar(raw_grammar)
            self.parse_grammars()

    def load_grammar(self, content: str) -> None:
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

        logger.info('Loading grammar')
        rules = content.split(';')
        rules = map(str.strip, rules)
        rules = filter(bool, rules)

        loaded_grammars = {}

        for line in rules:
            if line.startswith('%'):
                # handle settings
                line = line[1:]

                assert '=' in line, 'Invalid setting'
                key, value = line.split('=')
                key, value = key.strip(), value.strip()

                self.settings[key] = value
                continue
            elif line.startswith('//'):
                # ignore comments
                continue

            key, *value = line.split(':')
            key = key.upper()

            assert key not in self.token_defs, (
                'Do not name grammars the same as tokens')

            value = ':'.join(value)

            # clean up the value a bit
            value = (value.translate(self.VALUE_CLEANUP_TRANSFORM)
                          .replace('/*', ' /* ')
                          .replace('*/', ' */ ')
                          .strip()
                          .split(' '))
            # strip each segment, filters for empty fragments
            value = map(str.strip, value)
            value = list(filter(bool, value))

            loaded_grammars[key] = value

        self.grammar_loaded = True
        self.loaded_grammars = loaded_grammars

        logger.info('Grammars: {}'.format(', '.join(loaded_grammars.keys())))
        logger.info('Grammar loaded, rules: {}'.format(len(loaded_grammars)))

    def load_token_definitions(self, defs: dict) -> None:
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

        token_defs = {}

        logger.info('Loading token definitions')
        token_defs['literal'] = {}
        for k, v in defs['literal'].items():
            assert v.upper() not in self.loaded_grammars, (
                'Do not name tokens the same as grammars')
            token_defs['literal'][v.upper()] = k

        token_defs['regex'] = {}
        for k, v in defs['regex'].items():
            assert v.upper() not in self.loaded_grammars, (
                'Do not name tokens the same as grammars')
            token_defs['regex'][v.upper()] = k

        logger.info('Loaded token definitions, {} tokens'.format(
            len(token_defs['literal']) + len(token_defs['regex'])))

        self.tokens_loaded = True
        self.token_defs = token_defs

    def load_grammar_mapping(self, nodes):
        """
        Load in a mapping between grammars and Nodes
        """
        logger.info('Loading grammar mappings')

        grammar_mapping = {}
        raw_grammar_mapping = nodes.grammar_mapping

        for k, v in raw_grammar_mapping.items():
            k = k.upper()

            if not inspect.isclass(v):
                if type(nodes) == dict and v in nodes:
                    v = nodes[v]
                elif hasattr(nodes, v):
                    v = getattr(nodes, v)

            grammar_mapping[k] = v

            logger.debug('{}: {}'.format(k, grammar_mapping[k]))

        self.grammar_mapping_loaded = True
        self.grammar_mapping = grammar_mapping

        logger.info('{} grammar mappings loaded'.format(len(grammar_mapping)))

    def parse_grammars(self) -> dict:
        """
        Parses loaded grammars into "check trees"

        These check trees consist of a root ContainerNode, where a list
        of tokens can be passed into the root GrammarNode.check(<args>) function
        and validated according to the loaded grammars.
        """
        assert self.grammar_loaded, 'Please load a grammar before calling this'
        assert self.tokens_loaded, 'Please load some tokens before calling this'

        logger.info('Parsing grammars into grammar trees')

        settings = {
            'grammar_mapping': self.grammar_mapping
        }

        assert self.grammar_mapping, self.grammar_mapping

        parsed_grammars = {}

        for grammar_key in self.loaded_grammars:
            grammar_definition = self.loaded_grammars[grammar_key]
            settings.update({
                'grammar_key': grammar_key,
                'grammar_definition': grammar_definition
            })

            logger.info('Parsing {}'.format(grammar_key))
            cur, _ = self.parse_grammar(
                grammar=grammar_definition,
                grammar_key=grammar_key,
                settings=settings)

            assert len(cur.subs) >= 1, cur.subs

            parsed_grammars[grammar_key] = cur

        logger.info('Grammar trees loaded')

        self.grammars = parsed_grammars
        return parsed_grammars

    def parse_grammar(self,
                      grammar: str,
                      grammar_key: str,
                      settings: dict) -> ContainerNode:
        """
        See self.parse_grammars
        """
        assert self.grammar_loaded, 'Please load a grammar before calling this'
        assert self.tokens_loaded, 'Please load some tokens before calling this'

        out_tokens = []
        grammar = copy(grammar)
        comment = False
        node = None

        while grammar:
            # grab the first token, tell the Nodes
            token = grammar.pop(0)
            settings['token'] = token
            logger.debug('token: {}'.format(token))

            if token.upper() in self.token_defs['literal']:
                # if its a literal token
                literal = self.token_defs['literal'][token]
                node = LiteralNode(settings=settings, content=literal)

            elif token.upper() in self.token_defs['regex']:
                regex = self.token_defs['regex'][token.upper()]
                node = RENode(settings=settings, regex=regex, name=token)

            elif token.upper() in self.loaded_grammars:
                # we give the sub grammar wrapper a reference to this
                # GrammarParser instance so that it can look up the
                # grammar when its check function is called
                node = SubGrammarWrapper(
                    settings=settings,
                    key=token,
                    grammar_parser_inst=self)

            elif token == '(':
                logger.debug('Step down')
                sub_nodes, grammar = self.parse_grammar(
                    grammar, grammar_key, settings)
                if sub_nodes:
                    node = sub_nodes

            elif token == ')':
                logger.debug('Step up')
                if out_tokens:
                    node = ContainerNode(settings=settings, subs=out_tokens)
                    return node, grammar
                else:
                    raise GrammarDefinitionError('Empty brackets in Grammar')

            elif token == '|':
                first_half = ContainerNode(settings=settings, subs=out_tokens)
                out_tokens = []
                second_half, grammar = self.parse_grammar(
                    grammar, grammar_key, settings)
                if first_half or second_half:
                    node = ORNode(settings=settings,
                                  left=first_half,
                                  right=second_half)
                else:
                    raise GrammarDefinitionError('Invalid ORNode in Grammar')

            elif token == '+':
                token = out_tokens.pop(-1)
                if token:
                    node = MultiNode(settings=settings, sub=token)

            elif token == '/*':
                while token != '*/' and grammar:
                    token = grammar.pop(0)
                comment = True

            else:
                raise Exception('In "{}" token "{}"'.format(
                    grammar_key, token))

            out_tokens.append(node)

            if not comment:
                logger.debug(out_tokens[-1])
            else:
                comment = False

        return ContainerNode(settings=settings, subs=out_tokens), grammar