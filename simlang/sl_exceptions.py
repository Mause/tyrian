

class SimlangException(Exception):
    pass


class SimlangSyntaxError(SimlangException):
    pass


class InvalidToken(SimlangException):
    pass
