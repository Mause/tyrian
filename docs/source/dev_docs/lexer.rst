tyrian.lexer
==================

    .. autoclass:: tyrian.lexer.Lexer

        .. currentmodule:: tyrian.lexer
        .. automethod:: match_with(left: str)
        .. automethod:: load_token_definitions(defs: dict)
        .. automethod:: lex(content: str, filename: str) -> list
        .. automethod:: _lex(line: str, line_no: int, filename: str) -> dict

