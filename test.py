from tyrian import cli

import sys
sys.argv = ['examples\\simple_test.lisp', 'compiled.pyc'] + sys.argv[1:]

cli.main()
