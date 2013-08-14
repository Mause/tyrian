"""
Simple command line interface to Tyrian.
call like so;

python -m src.cmd <options>
"""

# standard library
import logging

# application specific
from .utils import logger
from .tyrian import Tyrian


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Tyrian is lisp to python bytecode compiler')

    parser.add_argument('input_filename', type=str)
    parser.add_argument('output_filename', type=str)

    parser.add_argument('-v', '--verbose', action='count')
    parser.add_argument('-q', '--quiet', action='count')

    args = parser.parse_args()
    print(args)

    verbosity = (
        args.verbose if args.verbose else 0 -
        args.quiet if args.quiet else 0
    )

    verbosity_map = [
        logging.NOTSET,
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.FATAL
    ]

    logger.setLevel(verbosity_map[verbosity])

    inst = Tyrian()

    bytecode = inst.compile(args.input_filename)

    print('end product;')
    from dis import dis
    dis(bytecode.code())

    logger.info('Writing to file...')
    with open(args.output_filename, 'wb') as fh:
        inst.compiler.write_code_to_file(
            bytecode.code(),
            fh, args.input_filename)


if __name__ == '__main__':
    main()
