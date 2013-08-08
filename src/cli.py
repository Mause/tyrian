"""
Simple command line interface to Tyrian.
call like so;

python -m src.cmd <options>
"""

# standard library
import sys
# sys.setrecursionlimit(115)
# sys.setrecursionlimit(1000000)
import logging

# application specific
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
        s.compile(
            'resources/lisp/simple_test.lisp',
            'compiled.pyc')

if __name__ == '__main__':
    main()
