"""
Code to perform lexing accourding to token definitions
"""

# standard library
import re
import logging
import operator
import functools

# application specific
from .utils import logger, enforce_types
from .exceptions import InvalidToken

logger = logger.getChild('Lexer')


class Lexer(object):
    """
    Code to perform lexing according to token definitions

    :param token_defs: dictionary containing token definitions, see \
    :py:meth:`Lexer.load_token_definitions <tyrian.lexer.Lexer.load_token_definitions>`
    """

    def __init__(self, token_defs: dict):
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

    def match_with(self, left: str) -> tuple:
        """
        Convenience function.

        returns an object with a match attribute partial'ed operator.eq,
        configured to match `left` with the supplied `right`
        """

        match = functools.partial(operator.eq, left)

        return type('obj', (object,), {'match': match})

    @enforce_types
    def load_token_definitions(self, token_defs: dict):
        """
        Iterates through the supplied token_defs dictionary, creates wrappers
        for literals and compiles regex's

        See \
        :py:meth:`GrammarParser.load_token_definitions <tyrian.typarser.grammar_parser.GrammarParser.load_token_definitions>` \
        for format
        """

        for k, v in token_defs['literal'].items():
            k = self.match_with(k)
            self.tokens[k] = v

        for k, v in token_defs['regex'].items():
            k = re.compile(k)
            self.tokens[k] = v

        self.tokens_loaded = True

    @enforce_types
    def lex(self, content: str, filename: str=None) -> list:
        """
        Takes a string to lex according to token definition loaded
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

    @enforce_types
    def _lex(self, line: str, line_no: int, filename: str):
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
