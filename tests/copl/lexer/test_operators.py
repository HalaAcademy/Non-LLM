"""Tests cho Lexer — Operators, Delimiters, Comments."""

from copl.lexer import Lexer, TokenType


def lex_types(source: str) -> list[TokenType]:
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    return [t.type for t in tokens if t.type != TokenType.EOF]


def lex_values(source: str) -> list[str]:
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    return [t.value for t in tokens if t.type != TokenType.EOF]


class TestTwoCharOperators:
    def test_arrow(self):
        assert lex_types("->") == [TokenType.ARROW]

    def test_fat_arrow(self):
        assert lex_types("=>") == [TokenType.FAT_ARROW]

    def test_double_colon(self):
        assert lex_types("::") == [TokenType.DOUBLE_COLON]

    def test_eq(self):
        assert lex_types("==") == [TokenType.EQ]

    def test_neq(self):
        assert lex_types("!=") == [TokenType.NEQ]

    def test_lte(self):
        assert lex_types("<=") == [TokenType.LTE]

    def test_gte(self):
        assert lex_types(">=") == [TokenType.GTE]

    def test_and(self):
        assert lex_types("&&") == [TokenType.AND]

    def test_or(self):
        assert lex_types("||") == [TokenType.OR]

    def test_shl(self):
        assert lex_types("<<") == [TokenType.SHL]

    def test_shr(self):
        assert lex_types(">>") == [TokenType.SHR]

    def test_plus_assign(self):
        assert lex_types("+=") == [TokenType.PLUS_ASSIGN]

    def test_minus_assign(self):
        assert lex_types("-=") == [TokenType.MINUS_ASSIGN]

    def test_dotdot(self):
        assert lex_types("..") == [TokenType.DOTDOT]


class TestOneCharOperators:
    def test_plus(self): assert lex_types("+") == [TokenType.PLUS]
    def test_minus(self): assert lex_types("-") == [TokenType.MINUS]
    def test_star(self): assert lex_types("*") == [TokenType.STAR]
    def test_slash(self): assert lex_types("/") == [TokenType.SLASH]
    def test_percent(self): assert lex_types("%") == [TokenType.PERCENT]
    def test_lt(self): assert lex_types("<") == [TokenType.LT]
    def test_gt(self): assert lex_types(">") == [TokenType.GT]
    def test_not(self): assert lex_types("!") == [TokenType.NOT]
    def test_bitand(self): assert lex_types("&") == [TokenType.BITAND]
    def test_bitor(self): assert lex_types("|") == [TokenType.BITOR]
    def test_bitxor(self): assert lex_types("^") == [TokenType.BITXOR]
    def test_assign(self): assert lex_types("=") == [TokenType.ASSIGN]
    def test_question(self): assert lex_types("?") == [TokenType.QUESTION]
    def test_dot(self): assert lex_types(".") == [TokenType.DOT]


class TestDelimiters:
    def test_parens(self):
        assert lex_types("()") == [TokenType.LPAREN, TokenType.RPAREN]

    def test_braces(self):
        assert lex_types("{}") == [TokenType.LBRACE, TokenType.RBRACE]

    def test_brackets(self):
        assert lex_types("[]") == [TokenType.LBRACKET, TokenType.RBRACKET]

    def test_semicolon(self): assert lex_types(";") == [TokenType.SEMICOLON]
    def test_colon(self): assert lex_types(":") == [TokenType.COLON]
    def test_comma(self): assert lex_types(",") == [TokenType.COMMA]
    def test_pipe(self): assert lex_types("|") == [TokenType.BITOR]


class TestComments:
    def test_line_comment_skipped(self):
        """// comment không xuất hiện trong token stream."""
        result = lex_types("x // this is a comment\ny")
        assert TokenType.COMMENT not in result
        assert result == [TokenType.IDENT, TokenType.IDENT]

    def test_block_comment_skipped(self):
        """/* block comment */ không xuất hiện."""
        result = lex_types("a /* comment */ b")
        assert TokenType.BLOCK_COMMENT not in result
        assert result == [TokenType.IDENT, TokenType.IDENT]

    def test_block_comment_multiline(self):
        result = lex_types("a /* line1\nline2 */ b")
        assert result == [TokenType.IDENT, TokenType.IDENT]

    def test_code_after_comment(self):
        lexer = Lexer()
        tokens, _ = lexer.tokenize("// comment\nfn foo() {}")
        types = [t.type for t in tokens if t.type != TokenType.EOF]
        assert TokenType.FN in types


class TestOperatorsInContext:
    def test_function_signature(self):
        """fn foo(x: U32) -> CanStatus"""
        result = lex_types("fn foo(x: U32) -> CanStatus")
        assert TokenType.ARROW in result
        assert TokenType.DOUBLE_COLON not in result

    def test_qualified_name(self):
        """mcal::can::init → IDENT :: IDENT :: IDENT."""
        result = lex_types("mcal::can::init")
        assert result == [
            TokenType.IDENT,
            TokenType.DOUBLE_COLON,
            TokenType.IDENT,
            TokenType.DOUBLE_COLON,
            TokenType.IDENT,
        ]

    def test_contract_expression(self):
        """baudrate > 0 && baudrate <= 1_000_000"""
        result = lex_types("baudrate > 0 && baudrate <= 1_000_000")
        assert TokenType.AND in result
        assert TokenType.LTE in result
        assert TokenType.GT in result

    def test_match_arm(self):
        """pattern => expr"""
        result = lex_types("Ok => true")
        assert TokenType.FAT_ARROW in result

    def test_array_type(self):
        """[U8; 8]"""
        result = lex_types("[U8; 8]")
        assert result == [
            TokenType.LBRACKET,
            TokenType.U8,
            TokenType.SEMICOLON,
            TokenType.INTEGER_LIT,
            TokenType.RBRACKET,
        ]

    def test_try_operator(self):
        """expr? — try operator."""
        result = lex_types("do_thing()?")
        assert TokenType.QUESTION in result


class TestLineColTracking:
    def test_newline_increments_line(self):
        lexer = Lexer()
        tokens, _ = lexer.tokenize("a\nb\nc")
        idents = [t for t in tokens if t.type == TokenType.IDENT]
        assert idents[0].line == 1
        assert idents[1].line == 2
        assert idents[2].line == 3

    def test_col_tracking(self):
        lexer = Lexer()
        tokens, _ = lexer.tokenize("   foo")
        ident = next(t for t in tokens if t.type == TokenType.IDENT)
        assert ident.col == 4  # 3 spaces + 1

    def test_eof_position(self):
        lexer = Lexer()
        tokens, _ = lexer.tokenize("fn")
        eof = tokens[-1]
        assert eof.type == TokenType.EOF
