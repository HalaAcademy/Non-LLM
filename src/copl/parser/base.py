"""COPL Parser Base — Khung cơ sở (Base Framework) cho Parser.

Nguồn token từ Lexer. Quản lý con trỏ token, báo lỗi và tính năng Error Recovery.
"""

from typing import Iterable

from copl.errors import (
    Diagnostic,
    DiagnosticBag,
    Severity,
    SourceLocation,
    err_unexpected_token,
)
from copl.lexer.tokens import Token, TokenType


class ParseError(Exception):
    """Exception dùng để unwind parser back ra recovery point."""
    pass


class ParserBase:
    """Class nền tảng xử lý con trỏ Tokens và báo lỗi cho bộ LL(1) Parser."""

    # Tập các token có thể bấu víu (Sync Point) khi xảy ra lỗi để tránh văng crash.
    SYNC_TOKENS = frozenset([
        TokenType.FN,
        TokenType.STRUCT,
        TokenType.ENUM,
        TokenType.MODULE,
        TokenType.RBRACE,
        TokenType.SEMICOLON,
        TokenType.EOF,
    ])

    def __init__(self, tokens: Iterable[Token], filename: str = "<input>") -> None:
        self.tokens: list[Token] = list(tokens)
        self.pos: int = 0
        self.filename: str = filename
        self.diagnostics: DiagnosticBag = DiagnosticBag()

    @property
    def current(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # luôn rơi vào EOF nếu cạn

    def peek(self, n: int = 1) -> Token:
        idx = self.pos + n
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]

    def advance(self) -> Token:
        tok = self.current
        if tok.type != TokenType.EOF:
            self.pos += 1
        return tok

    def loc(self) -> SourceLocation:
        tok = self.current
        return SourceLocation(self.filename, tok.line, tok.col)

    def match(self, ttype: TokenType) -> bool:
        if self.current.type == ttype:
            self.advance()
            return True
        return False

    def expect(self, ttype: TokenType) -> Token:
        if self.current.type == ttype:
            return self.advance()
        
        # Bắn lỗi
        tok = self.current
        loc = SourceLocation(self.filename, tok.line, tok.col)
        err = err_unexpected_token(tok.value or tok.type.name, ttype.name, loc)
        self.diagnostics.add(err)
        raise ParseError()

    def error_recovery(self) -> None:
        """Skip parsing until hitting a synchronization token (Panic Mode)."""
        self.advance()
        while self.current.type not in self.SYNC_TOKENS:
            if self.current.type == TokenType.EOF:
                break
            self.advance()
