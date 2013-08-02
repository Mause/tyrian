import re
import logging
from collections import namedtuple

from .utils import logger
from .exceptions import InvalidToken

logger = logger.getChild('Lexer')


class Lexer(object):
    """
    Performs lexing
    """
    def __init__(self, token_defs):
        self.tokens = {}
        self.TRANS = str.maketrans({
            '(': ' ( ',
            ')': ' ) ',
            '"': ' " ',
            "'": " ' ",
        })

        if token_defs:
            self.load_token_definitions(token_defs)
        else:
            self.tokens_loaded = False

    def match_with(self, left):
        """
        Convenience function.

        returns an collections.namedtuple with a match function that compares
        left with the supplied right
        """

        MatchFunction = namedtuple('MatchFunction', 'match')

        def internal(right):
            return left == right
        return MatchFunction(internal)

    def load_token_definitions(self, token_defs):
        """
        Iterates through the supplied token_defs dictionary, creates wrappers
        for literals and compiles regex's

        See tyrian.grammar.GrammarParser.load_token_definitions for format
        """

        for k, v in token_defs['literal'].items():
            k = self.match_with(k)
            self.tokens[k] = v

        for k, v in token_defs['regex'].items():
            k = re.compile(k)
            self.tokens[k] = v

        self.tokens_loaded = True

    def lex(self, content: str, filename: str=None):
        """
        Takes a string to lex accourding to token definition loaded
        via load_token_definitions

        """
        assert self.tokens_loaded, (
            'Please call load_token_definitions before calling this function')

        lines = content.split('\n')

        tokens = []
        for line_no, line in enumerate(lines, start=1):
            for token in self._lex(line, line_no, filename):
                tokens.append(token)

        return tokens

    def _lex(self, line, line_no, filename):
        """
        used internally by lex, does actual lexing
        """

        line = (line.translate(self.TRANS)
                    .strip()
                    .split(' '))

        for current_token in line:
            for definition, name in self.tokens.items():
                logging.debug(definition.match(current_token), current_token)
                if definition.match(current_token):
                    yield {
                        "name": name,
                        "token": current_token,
                        "line_no": line_no,
                        'filename': filename
                    }
                    break
            else:
                if current_token.strip():
                    msg = '"{}" on line {}'.format(current_token, line_no)
                    if filename:
                        msg += ' of file {}'.format(filename)
                    raise InvalidToken(msg)
