from tyrian import cli

import sys
sys.argv = sys.argv[:1] + ['examples\\simple_test.lisp', 'compiled.pyc'] + sys.argv[1:]

cli.main()
