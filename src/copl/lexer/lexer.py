"""COPL Lexer — Biến source text thành Token stream.

Spec reference: docs/copl/01_grammar_spec.md Section 2 (Lexical Grammar)
Error codes: E001 (unexpected token), E002 (unterminated string)

Đặc điểm:
  - Single-pass streaming (O(1) memory)
  - Hỗ trợ: integer (decimal/hex/binary/octal) với _ separator
  - Hỗ trợ: float với exponent
  - Hỗ trợ: string escape sequences
  - Hỗ trợ: @annotation keywords
  - Error recovery: ngay cả khi gặp invalid char, lexer tiếp tục
"""

from __future__ import annotations
from typing import Iterator

from copl.errors import (
    DiagnosticBag,
    SourceLocation,
    err_unexpected_token,
    err_unterminated_string,
)
from copl.lexer.tokens import (
    ANNOTATION_KEYWORDS,
    KEYWORDS,
    Token,
    TokenType,
)


class Lexer:
    """
    COPL Lexer — LL(1) single-pass scanner.

    Sử dụng:
        lexer = Lexer()
        tokens, diagnostics = lexer.tokenize(source, "myfile.copl")
        if diagnostics.has_errors():
            diagnostics.print_all()
        else:
            # proceed with parsing
            pass
    """

    def __init__(self) -> None:
        self._source: str = ""
        self._filename: str = "<input>"
        self._pos: int = 0
        self._line: int = 1
        self._col: int = 1
        self._diagnostics: DiagnosticBag = DiagnosticBag()

    # ================================================================
    # Public API
    # ================================================================

    def tokenize(
        self, source: str, filename: str = "<input>"
    ) -> tuple[list[Token], DiagnosticBag]:
        """
        Tokenize toàn bộ source string.

        Returns:
            (tokens, diagnostics) — tokens luôn kết thúc bằng EOF token.
            Ngay cả khi có lỗi, vẫn trả về tokens đã scan được + EOF.
        """
        self._source = source
        self._filename = filename
        self._pos = 0
        self._line = 1
        self._col = 1
        self._diagnostics = DiagnosticBag()

        tokens: list[Token] = []
        for tok in self._scan_all():
            tokens.append(tok)

        return tokens, self._diagnostics

    # ================================================================
    # Core scanner
    # ================================================================

    def _scan_all(self) -> Iterator[Token]:
        """Generator: yield tokens một cách tuần tự."""
        while self._pos < len(self._source):
            tok = self._next_token()
            if tok is None:
                continue
            # Skip comments
            if tok.type in (TokenType.COMMENT, TokenType.BLOCK_COMMENT):
                continue
            yield tok

        yield self._make_token(TokenType.EOF, "")

    def _next_token(self) -> Token | None:
        """Scan và trả về token tiếp theo. None nếu whitespace."""
        self._skip_whitespace()
        if self._pos >= len(self._source):
            return None

        c = self._current()

        # Comments
        if c == "/" and self._peek() == "/":
            return self._scan_line_comment()
        if c == "/" and self._peek() == "*":
            return self._scan_block_comment()

        # Annotations: @context, @platform, etc.
        if c == "@":
            return self._scan_annotation()

        # String literal
        if c == '"':
            return self._scan_string()

        # Char literal
        if c == "'":
            return self._scan_char()

        # Numbers
        if c.isdigit():
            return self._scan_number()
        if c == "." and self._peek().isdigit():
            return self._scan_number()

        # Identifiers and keywords (including lower_struct, lower_const)
        if c.isalpha() or c == "_":
            return self._scan_identifier_or_keyword()

        # Operators and delimiters
        return self._scan_operator_or_delimiter()

    # ================================================================
    # Whitespace
    # ================================================================

    def _skip_whitespace(self) -> None:
        while self._pos < len(self._source) and self._source[self._pos] in " \t\r\n":
            if self._source[self._pos] == "\n":
                self._line += 1
                self._col = 1
            else:
                self._col += 1
            self._pos += 1

    # ================================================================
    # Comments
    # ================================================================

    def _scan_line_comment(self) -> Token:
        start_col = self._col
        start_line = self._line
        # Consume //
        self._advance(); self._advance()
        text = "//"
        while self._pos < len(self._source) and self._current() != "\n":
            text += self._current()
            self._advance()
        return Token(TokenType.COMMENT, text, start_line, start_col, self._filename)

    def _scan_block_comment(self) -> Token:
        start_col = self._col
        start_line = self._line
        self._advance(); self._advance()  # /*
        text = "/*"
        while self._pos < len(self._source):
            if self._current() == "*" and self._peek() == "/":
                self._advance(); self._advance()
                text += "*/"
                break
            if self._current() == "\n":
                self._line += 1
                self._col = 1
                self._pos += 1
            else:
                text += self._current()
                self._advance()
        return Token(TokenType.BLOCK_COMMENT, text, start_line, start_col, self._filename)

    # ================================================================
    # Annotations: @context, @platform, @trace, @contract, @effects, @target, @offset
    # ================================================================

    def _scan_annotation(self) -> Token:
        start_line, start_col = self._line, self._col
        self._advance()  # consume @

        # Đọc tên sau @
        word = ""
        while self._pos < len(self._source) and (
            self._current().isalnum() or self._current() == "_"
        ):
            word += self._current()
            self._advance()

        if word in ANNOTATION_KEYWORDS:
            ttype = ANNOTATION_KEYWORDS[word]
        else:
            ttype = TokenType.AT  # unknown annotation → generic @

        return Token(ttype, "@" + word, start_line, start_col, self._filename)

    # ================================================================
    # String literals
    # ================================================================

    def _scan_string(self) -> Token:
        start_line, start_col = self._line, self._col
        self._advance()  # consume opening "
        value = ""

        while self._pos < len(self._source):
            c = self._current()
            if c == '"':
                self._advance()  # consume closing "
                return Token(TokenType.STRING_LIT, value, start_line, start_col, self._filename)
            if c == "\n":
                # Unterminated string
                break
            if c == "\\":
                value += self._scan_escape()
            else:
                value += c
                self._advance()

        # Unterminated string
        loc = SourceLocation(self._filename, start_line, start_col)
        self._diagnostics.add(err_unterminated_string(loc))
        return Token(TokenType.INVALID, value, start_line, start_col, self._filename)

    def _scan_escape(self) -> str:
        """Scan escape sequence sau \\."""
        self._advance()  # consume backslash
        if self._pos >= len(self._source):
            return "\\"
        c = self._current()
        self._advance()
        escapes = {
            "n": "\n", "t": "\t", "r": "\r",
            "\\": "\\", '"': '"', "'": "'",
            "0": "\0",
        }
        if c in escapes:
            return escapes[c]
        if c == "x":
            # \xFF hex escape
            hex_str = ""
            for _ in range(2):
                if self._pos < len(self._source) and self._current() in "0123456789abcdefABCDEF":
                    hex_str += self._current()
                    self._advance()
            if hex_str:
                return chr(int(hex_str, 16))
        return "\\" + c  # Unknown escape — keep as-is

    # ================================================================
    # Char literals
    # ================================================================

    def _scan_char(self) -> Token:
        start_line, start_col = self._line, self._col
        self._advance()  # consume opening '
        value = ""

        if self._pos < len(self._source):
            c = self._current()
            if c == "\\":
                value = self._scan_escape()
            elif c != "'":
                value = c
                self._advance()

        if self._pos < len(self._source) and self._current() == "'":
            self._advance()  # consume closing '

        return Token(TokenType.CHAR_LIT, value, start_line, start_col, self._filename)

    # ================================================================
    # Number literals: integer và float
    # ================================================================

    def _scan_number(self) -> Token:
        start_line, start_col = self._line, self._col
        text = ""
        is_float = False

        # Prefix: 0x, 0b, 0o
        if self._current() == "0" and self._pos + 1 < len(self._source):
            next_c = self._source[self._pos + 1].lower()
            if next_c == "x":
                return self._scan_hex(start_line, start_col)
            elif next_c == "b":
                return self._scan_binary(start_line, start_col)
            elif next_c == "o":
                return self._scan_octal(start_line, start_col)

        # Decimal integer or float
        while self._pos < len(self._source) and (
            self._current().isdigit() or self._current() == "_"
        ):
            if self._current() != "_":
                text += self._current()
            self._advance()

        # Float part: .digits
        if (
            self._pos < len(self._source)
            and self._current() == "."
            and self._pos + 1 < len(self._source)
            and self._source[self._pos + 1].isdigit()
        ):
            is_float = True
            text += "."
            self._advance()
            while self._pos < len(self._source) and (
                self._current().isdigit() or self._current() == "_"
            ):
                if self._current() != "_":
                    text += self._current()
                self._advance()

        # Exponent: e±digits
        if self._pos < len(self._source) and self._current().lower() == "e":
            is_float = True
            text += self._current()
            self._advance()
            if self._pos < len(self._source) and self._current() in "+-":
                text += self._current()
                self._advance()
            while self._pos < len(self._source) and self._current().isdigit():
                text += self._current()
                self._advance()

        ttype = TokenType.FLOAT_LIT if is_float else TokenType.INTEGER_LIT
        return Token(ttype, text, start_line, start_col, self._filename)

    def _scan_hex(self, line: int, col: int) -> Token:
        self._advance(); self._advance()  # 0x
        text = "0x"
        while self._pos < len(self._source) and (
            self._current() in "0123456789abcdefABCDEF_"
        ):
            if self._current() != "_":
                text += self._current()
            self._advance()
        return Token(TokenType.INTEGER_LIT, text, line, col, self._filename)

    def _scan_binary(self, line: int, col: int) -> Token:
        self._advance(); self._advance()  # 0b
        text = "0b"
        while self._pos < len(self._source) and self._current() in "01_":
            if self._current() != "_":
                text += self._current()
            self._advance()
        return Token(TokenType.INTEGER_LIT, text, line, col, self._filename)

    def _scan_octal(self, line: int, col: int) -> Token:
        self._advance(); self._advance()  # 0o
        text = "0o"
        while self._pos < len(self._source) and self._current() in "01234567_":
            if self._current() != "_":
                text += self._current()
            self._advance()
        return Token(TokenType.INTEGER_LIT, text, line, col, self._filename)

    # ================================================================
    # Identifiers và Keywords
    # QUAN TRỌNG: lower_struct và lower_const là keyword COMPOUND
    # Phải check chúng trước khi check "lower" đơn lẻ
    # ================================================================

    def _scan_identifier_or_keyword(self) -> Token:
        start_line, start_col = self._line, self._col
        text = ""

        while self._pos < len(self._source) and (
            self._current().isalnum() or self._current() == "_"
        ):
            text += self._current()
            self._advance()

        # Keyword lookup (bao gồm lower_struct, lower_const, test_suite...)
        ttype = KEYWORDS.get(text, TokenType.IDENT)
        return Token(ttype, text, start_line, start_col, self._filename)

    # ================================================================
    # Operators và Delimiters
    # ================================================================

    def _scan_operator_or_delimiter(self) -> Token:
        start_line, start_col = self._line, self._col
        c = self._current()
        self._advance()
        n = self._current() if self._pos < len(self._source) else ""
        # Three-character operators
        third = self._source[self._pos + 1] if self._pos + 1 < len(self._source) else ""
        three = c + n + third
        three_char_map: dict[str, TokenType] = {
            "<<=": TokenType.SHL_ASSIGN,
            ">>=": TokenType.SHR_ASSIGN,
        }
        if three in three_char_map:
            self._advance()
            self._advance()
            return Token(three_char_map[three], three, start_line, start_col, self._filename)

        # Two-character operators
        two = c + n
        two_char_map: dict[str, TokenType] = {
            "->": TokenType.ARROW,
            "=>": TokenType.FAT_ARROW,
            "::": TokenType.DOUBLE_COLON,
            "==": TokenType.EQ,
            "!=": TokenType.NEQ,
            "<=": TokenType.LTE,
            ">=": TokenType.GTE,
            "&&": TokenType.AND,
            "||": TokenType.OR,
            "<<": TokenType.SHL,
            ">>": TokenType.SHR,
            "+=": TokenType.PLUS_ASSIGN,
            "-=": TokenType.MINUS_ASSIGN,
            "*=": TokenType.STAR_ASSIGN,
            "/=": TokenType.SLASH_ASSIGN,
            "%=": TokenType.PERCENT_ASSIGN,
            "|=": TokenType.BITOR_ASSIGN,
            "&=": TokenType.BITAND_ASSIGN,
            "^=": TokenType.BITXOR_ASSIGN,
            "..": TokenType.DOTDOT,
        }
        if two in two_char_map:
            self._advance()  # consume second char
            return Token(two_char_map[two], two, start_line, start_col, self._filename)

        # One-character operators
        one_char_map: dict[str, TokenType] = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.STAR,
            "/": TokenType.SLASH,
            "%": TokenType.PERCENT,
            "<": TokenType.LT,
            ">": TokenType.GT,
            "!": TokenType.NOT,
            "&": TokenType.BITAND,
            "|": TokenType.BITOR,
            "^": TokenType.BITXOR,
            "~": TokenType.BITNOT,
            "=": TokenType.ASSIGN,
            "?": TokenType.QUESTION,
            ".": TokenType.DOT,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ";": TokenType.SEMICOLON,
            ":": TokenType.COLON,
            ",": TokenType.COMMA,
            "#": TokenType.HASH,
        }
        if c in one_char_map:
            return Token(one_char_map[c], c, start_line, start_col, self._filename)

        # Ký tự không hợp lệ
        loc = SourceLocation(self._filename, start_line, start_col)
        self._diagnostics.add(
            err_unexpected_token(repr(c), "valid token", loc)
        )
        return Token(TokenType.INVALID, c, start_line, start_col, self._filename)

    # ================================================================
    # Helpers
    # ================================================================

    def _current(self) -> str:
        return self._source[self._pos] if self._pos < len(self._source) else ""

    def _peek(self) -> str:
        return self._source[self._pos + 1] if self._pos + 1 < len(self._source) else ""

    def _advance(self) -> str:
        c = self._current()
        if c == "\n":
            self._line += 1
            self._col = 1
        else:
            self._col += 1
        self._pos += 1
        return c

    def _make_token(self, ttype: TokenType, value: str) -> Token:
        return Token(ttype, value, self._line, self._col, self._filename)
