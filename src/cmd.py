import sys
import logging

from .utils import logger
from .tyrian import Tyrian


def main():
    if '-v' in sys.argv:
        verbosity = 1
    else:
        verbosity = 0

    if verbosity == 0:
        logger.getChild('GrammarParser').setLevel(logging.INFO)
        logger.getChild('GrammerNodes').setLevel(logging.INFO)
        logger.getChild('Lexer').setLevel(logging.INFO)

    s = Tyrian()

    if 'dr' not in sys.argv:
        # s.run('resources/lisp/lambda.lisp')
        # s.run('resources/lisp/wizards_game.lisp')
        # s.run('resources/lisp/test.lisp')
        s.run('resources/lisp/simple_test.lisp')

if __name__ == '__main__':
    main()
