"""Tests cho Lexer — Number và String literals.

Spec reference: docs/copl/01_grammar_spec.md Section 2.2 (Literals)
"""

import pytest
from copl.lexer import Lexer, TokenType


def lex_one(source: str) -> tuple[TokenType, str]:
    """Lex source và trả về token đầu tiên (bỏ EOF)."""
    lexer = Lexer()
    tokens, diags = lexer.tokenize(source)
    non_eof = [t for t in tokens if t.type != TokenType.EOF]
    assert not diags.has_errors(), f"Errors: {[str(d) for d in diags.errors()]}"
    assert len(non_eof) == 1, f"Expected 1 token, got {non_eof}"
    return non_eof[0].type, non_eof[0].value


def lex_all(source: str) -> list[tuple[TokenType, str]]:
    lexer = Lexer()
    tokens, diags = lexer.tokenize(source)
    return [(t.type, t.value) for t in tokens if t.type != TokenType.EOF]


# ================================================================
# Integer Literals
# ================================================================

class TestIntegerLiterals:
    def test_zero(self):
        t, v = lex_one("0")
        assert t == TokenType.INTEGER_LIT
        assert v == "0"

    def test_decimal(self):
        t, v = lex_one("42")
        assert t == TokenType.INTEGER_LIT and v == "42"

    def test_decimal_large(self):
        t, v = lex_one("1000000")
        assert t == TokenType.INTEGER_LIT

    def test_underscore_separator(self):
        """1_000_000 → value "1000000" (underscores stripped)."""
        t, v = lex_one("1_000_000")
        assert t == TokenType.INTEGER_LIT
        assert v == "1000000"  # underscores removed

    def test_hex_lower(self):
        t, v = lex_one("0xff")
        assert t == TokenType.INTEGER_LIT and v == "0xff"

    def test_hex_upper(self):
        t, v = lex_one("0xFF")
        assert t == TokenType.INTEGER_LIT and v == "0xFF"

    def test_hex_with_underscore(self):
        t, v = lex_one("0xFF_FF")
        assert t == TokenType.INTEGER_LIT
        assert v == "0xFFFF"  # underscore removed

    def test_hex_full_register(self):
        """Hardware register address."""
        t, v = lex_one("0x40006400")
        assert t == TokenType.INTEGER_LIT

    def test_binary(self):
        t, v = lex_one("0b1010")
        assert t == TokenType.INTEGER_LIT and v == "0b1010"

    def test_binary_with_underscore(self):
        t, v = lex_one("0b1010_1010")
        assert t == TokenType.INTEGER_LIT
        assert v == "0b10101010"

    def test_octal(self):
        t, v = lex_one("0o77")
        assert t == TokenType.INTEGER_LIT and v == "0o77"


# ================================================================
# Float Literals
# ================================================================

class TestFloatLiterals:
    def test_basic_float(self):
        t, v = lex_one("3.14")
        assert t == TokenType.FLOAT_LIT

    def test_float_zero(self):
        t, v = lex_one("0.0")
        assert t == TokenType.FLOAT_LIT

    def test_float_exponent_lower(self):
        t, v = lex_one("1.0e5")
        assert t == TokenType.FLOAT_LIT

    def test_float_exponent_upper(self):
        t, v = lex_one("1.0E5")
        assert t == TokenType.FLOAT_LIT

    def test_float_negative_exponent(self):
        t, v = lex_one("1.0e-5")
        assert t == TokenType.FLOAT_LIT

    def test_float_positive_exponent(self):
        t, v = lex_one("2.5E+3")
        assert t == TokenType.FLOAT_LIT

    def test_int_is_not_float(self):
        t, v = lex_one("42")
        assert t == TokenType.INTEGER_LIT  # không phải float


# ================================================================
# String Literals
# ================================================================

class TestStringLiterals:

    def test_empty_string(self):
        t, v = lex_one('""')
        assert t == TokenType.STRING_LIT and v == ""

    def test_simple_string(self):
        t, v = lex_one('"hello"')
        assert t == TokenType.STRING_LIT and v == "hello"

    def test_string_with_space(self):
        t, v = lex_one('"hello world"')
        assert t == TokenType.STRING_LIT and v == "hello world"

    def test_escape_newline(self):
        t, v = lex_one(r'"line1\nline2"')
        assert t == TokenType.STRING_LIT and "\n" in v

    def test_escape_tab(self):
        t, v = lex_one(r'"col1\tcol2"')
        assert t == TokenType.STRING_LIT and "\t" in v

    def test_escape_backslash(self):
        t, v = lex_one(r'"path\\to\\file"')
        assert t == TokenType.STRING_LIT

    def test_escape_quote(self):
        t, v = lex_one(r'"say \"hello\""')
        assert t == TokenType.STRING_LIT and '"' in v

    def test_escape_null(self):
        t, v = lex_one(r'"\0"')
        assert t == TokenType.STRING_LIT

    def test_string_with_numbers(self):
        t, v = lex_one('"id_123"')
        assert t == TokenType.STRING_LIT and v == "id_123"

    def test_unterminated_string_produces_error(self):
        """Unterminated string → error E002."""
        lexer = Lexer()
        tokens, diags = lexer.tokenize('"hello')
        assert diags.has_errors()
        errors = diags.errors()
        assert errors[0].code == "E002"

    def test_string_line_col(self):
        """String token phải có line/col chính xác."""
        lexer = Lexer()
        tokens, _ = lexer.tokenize('  "hello"')
        string_tok = next(t for t in tokens if t.type == TokenType.STRING_LIT)
        assert string_tok.line == 1
        assert string_tok.col == 3  # 2 spaces + opening "


# ================================================================
# Char Literals
# ================================================================

class TestCharLiterals:
    def test_simple_char(self):
        t, v = lex_one("'a'")
        assert t == TokenType.CHAR_LIT and v == "a"

    def test_escape_newline_char(self):
        t, v = lex_one(r"'\n'")
        assert t == TokenType.CHAR_LIT and v == "\n"

    def test_escape_tab_char(self):
        t, v = lex_one(r"'\t'")
        assert t == TokenType.CHAR_LIT and v == "\t"

    def test_digit_char(self):
        t, v = lex_one("'5'")
        assert t == TokenType.CHAR_LIT and v == "5"


# ================================================================
# Mixed: numbers trong context
# ================================================================

class TestNumbersInContext:
    def test_assignment_with_int(self):
        result = lex_all("let x = 42;")
        types = [t for t, _ in result]
        assert TokenType.INTEGER_LIT in types

    def test_hex_in_lower_const(self):
        """lower_const với hardware address 0x40006400."""
        result = lex_all("lower_const CAN1 = 0x40006400")
        types = [t for t, _ in result]
        assert TokenType.LOWER_CONST in types
        assert TokenType.INTEGER_LIT in types

    def test_array_size(self):
        """[U8; 8] — array size là integer."""
        result = lex_all("[U8; 8]")
        types = [t for t, _ in result]
        assert TokenType.INTEGER_LIT in types
        int_vals = [v for t, v in result if t == TokenType.INTEGER_LIT]
        assert int_vals == ["8"]

    def test_baudrate_check(self):
        """baudrate <= 1_000_000 trong contract."""
        result = lex_all("baudrate <= 1_000_000")
        vals = {v for t, v in result if t == TokenType.INTEGER_LIT}
        assert "1000000" in vals  # underscore stripped
