import sys
from pkg_resources import load_entry_point, DistributionNotFound

if __name__ == '__main__':
    try:
        sys.exit(
            load_entry_point('tyrian', 'console_scripts', 'tyrian')()
        )
    except DistributionNotFound:
        from tyrian import cli
        sys.exit(cli.main())
