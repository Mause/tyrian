

class TyrianException(Exception):
    pass


class TyrianSyntaxError(TyrianException):
    pass


class InvalidToken(TyrianException):
    pass
