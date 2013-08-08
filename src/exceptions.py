

class TyrianException(Exception):
    pass


class TyrianSyntaxError(TyrianException):
    pass


class InvalidToken(TyrianException):
    pass


class GrammarDefinitionError(TyrianException):
    pass


class NoSuchGrammar(TyrianException):
    pass
