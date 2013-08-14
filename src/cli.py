"""
Simple command line interface to Tyrian.
call like so;

python cli.py <options>
"""

# standard library
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
        description='Tyrian is lisp to python bytecode compiler')

    parser.add_argument('input_filename', type=str)
    parser.add_argument('output_filename', type=str)

    parser.add_argument('-v', '--verbose', action='count', default=0)

    args = parser.parse_args()

    verbosity = 5 - args.verbose

    if 0 <= verbosity <= 5:
        logger.setLevel(_verbosity_map[verbosity][0])
    else:
        logger.setLevel(logging.FATAL)

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
    main()
