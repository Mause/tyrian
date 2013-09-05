"""
Simple command line interface to Tyrian.
call like so;

python cli.py <options>
"""

# standard library
import sys
import logging
from dis import dis

# application specific
from .utils import logger
from .tyrian import Tyrian

_verbosity_map = [
    (logging.NOTSET, 'NOTSET'),
    (logging.DEBUG, 'DEBUG'),
    (logging.INFO, 'INFO'),
    (logging.WARNING, 'WARNING'),
    (logging.ERROR, 'ERROR'),
    (logging.FATAL, 'FATAL')
]


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Tyrian is a lisp to python bytecode compiler')

    parser.add_argument(
        'input_filename', type=str, help="input filename containing LISP")
    parser.add_argument(
        'output_filename', type=str, help="file to write bytecode to")

    parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="controls verbosity. Must be used a few times to lower the \
              barrier to the interesting stuff")

    args = parser.parse_args()
    verbosity = 5 - args.verbose

    assert verbosity in range(0, 6), 'Bad verbosity'

    logger.setLevel(_verbosity_map[verbosity][0])

    inst = Tyrian()
    bytecode = inst.compile(args.input_filename)

    if _verbosity_map[verbosity][0] <= logging.INFO:
        dis(bytecode.code())

    logger.info('Writing to file...')
    with open(args.output_filename, 'wb') as fh:
        inst.compiler.write_code_to_file(
            bytecode.code(),
            fh, args.input_filename)


if __name__ == '__main__':
    main(sys.argv)
