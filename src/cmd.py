from . import Tyrian


def main():
    s = Tyrian()
    s.run('resources/lisp/lambda.lisp')
    # s.run('resources/lisp/wizards_game.lisp')
    # s.run('resources/lisp/test.lisp')

if __name__ == '__main__':
    main()
