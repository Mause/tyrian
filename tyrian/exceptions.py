

class TyrianException(Exception):
    """
    Base exception to allow for easy catching of all exceptions raised by
    tyrian
    """
    pass


class TyrianSyntaxError(TyrianException):
    """
    Raised when a syntax is found
    """
    pass


class InvalidToken(TyrianException):
    """
    Raised when an invalid token is found
    """
    pass


class GrammarDefinitionError(TyrianException):
    """
    Raised when the grammar definition file is found to have an error
    """
    pass


class NoSuchGrammar(TyrianException):
    """
    Raised when a reference grammar does not exist
    """
    pass
