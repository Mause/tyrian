import sys
import logging

from . import Tyrian
from .utils import logger

def main():
    if '-v' in sys.argv:
        verbosity = 1
    else:
        verbosity = 0

    if verbosity == 0:
        logger.getChild('GrammarParser').setLevel(logging.INFO)
        logger.getChild('GrammaNodes').setLevel(logging.INFO)


    s = Tyrian()

    if 'dr' not in sys.argv:
        s.run('resources/lisp/lambda.lisp')
    # s.run('resources/lisp/wizards_game.lisp')
    # s.run('resources/lisp/test.lisp')

if __name__ == '__main__':
    main()
