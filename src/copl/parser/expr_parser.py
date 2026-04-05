"""COPL Expression Parser — Pratt Parsing framework.

Xử lý độ ưu tiên luân chuyển toán tử (Operator precedence).
"""

from enum import IntEnum
from typing import Callable, Optional

from copl.errors import Diagnostic, err_unexpected_token
from copl.lexer.tokens import Token, TokenType
from copl.parser.ast import (
    ArrayLiteralExpr,
    BinaryExpr,
    BlockExpr,
    CallExpr,
    Expr,
    IdentifierExpr,
    IndexExpr,
    LiteralExpr,
    MatchArm,
    MatchExpr,
    MemberAccessExpr,
    MethodCallExpr,
    QualifiedNameExpr,
    StructFieldInit,
    StructLiteralExpr,
    TryExpr,
    UnaryExpr,
)
from copl.parser.base import ParseError, ParserBase


class Precedence(IntEnum):
    NONE = 0
    ASSIGN = 1      # = += -= *= /= %= |= &= ^= <<= >>=
    OR = 2          # ||
    AND = 3         # &&
    CMP = 4         # == != < > <= >=
    BIT_OR = 5      # |
    BIT_XOR = 6     # ^
    BIT_AND = 7     # &
    SHIFT = 8       # << >>
    ADD = 9         # + -
    MUL = 10        # * / %
    PREFIX = 11     # ! - ~
    POSTFIX = 12    # . [] () ?
    HIGHEST = 13


class ExprParser(ParserBase):
    """Pratt Parser để parse Expression COPL."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prefix_parse_fns: dict[TokenType, Callable[[], Expr]] = {}
        self.infix_parse_fns: dict[TokenType, Callable[[Expr], Expr]] = {}
        self.precedences: dict[TokenType, Precedence] = {}

        self._register_rules()

    def _register_rules(self):
        # --- Literals ---
        for tt in (TokenType.INTEGER_LIT, TokenType.FLOAT_LIT, TokenType.STRING_LIT, TokenType.CHAR_LIT, TokenType.TRUE, TokenType.FALSE):
            self.prefix_parse_fns[tt] = self.parse_literal

        self.prefix_parse_fns[TokenType.IDENT] = self.parse_identifier_or_struct
        self.prefix_parse_fns[TokenType.OK] = self.parse_identifier_or_struct
        self.prefix_parse_fns[TokenType.RESULT] = self.parse_identifier_or_struct
        self.prefix_parse_fns[TokenType.STRING_KW] = self.parse_identifier_or_struct
        self.prefix_parse_fns[TokenType.LPAREN] = self.parse_grouped_expr
        self.prefix_parse_fns[TokenType.LBRACKET] = self.parse_array_literal
        self.prefix_parse_fns[TokenType.RETURN] = self.parse_return_expr
        self.prefix_parse_fns[TokenType.LOWER] = self.parse_lower_expr

        # --- Prefix Operators ---
        for tt in (TokenType.NOT, TokenType.MINUS, TokenType.BITNOT):
            self.prefix_parse_fns[tt] = self.parse_prefix

        # --- Binary Operators ---
        self._infix(TokenType.ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.PLUS_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.MINUS_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.STAR_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.SLASH_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.PERCENT_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.BITOR_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.BITAND_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.BITXOR_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.SHL_ASSIGN, Precedence.ASSIGN)
        self._infix(TokenType.SHR_ASSIGN, Precedence.ASSIGN)

        self._infix(TokenType.OR, Precedence.OR)
        self._infix(TokenType.AND, Precedence.AND)

        self._infix(TokenType.EQ, Precedence.CMP)
        self._infix(TokenType.NEQ, Precedence.CMP)
        self._infix(TokenType.LT, Precedence.CMP)
        self._infix(TokenType.GT, Precedence.CMP)
        self._infix(TokenType.LTE, Precedence.CMP)
        self._infix(TokenType.GTE, Precedence.CMP)

        self._infix(TokenType.BITOR, Precedence.BIT_OR)
        self._infix(TokenType.BITXOR, Precedence.BIT_XOR)
        self._infix(TokenType.BITAND, Precedence.BIT_AND)

        self._infix(TokenType.SHL, Precedence.SHIFT)
        self._infix(TokenType.SHR, Precedence.SHIFT)

        self._infix(TokenType.PLUS, Precedence.ADD)
        self._infix(TokenType.MINUS, Precedence.ADD)

        self._infix(TokenType.STAR, Precedence.MUL)
        self._infix(TokenType.SLASH, Precedence.MUL)
        self._infix(TokenType.PERCENT, Precedence.MUL)

        # --- Postfix / Call Operators ---
        self.infix_parse_fns[TokenType.LPAREN] = self.parse_call
        self.precedences[TokenType.LPAREN] = Precedence.POSTFIX

        self.infix_parse_fns[TokenType.LBRACKET] = self.parse_index
        self.precedences[TokenType.LBRACKET] = Precedence.POSTFIX

        self.infix_parse_fns[TokenType.DOT] = self.parse_member_access
        self.precedences[TokenType.DOT] = Precedence.POSTFIX

        self.infix_parse_fns[TokenType.ARROW] = self.parse_member_access
        self.precedences[TokenType.ARROW] = Precedence.POSTFIX

        self.infix_parse_fns[TokenType.QUESTION] = self.parse_try
        self.precedences[TokenType.QUESTION] = Precedence.POSTFIX

    def _infix(self, tt: TokenType, p: Precedence):
        self.infix_parse_fns[tt] = self.parse_infix
        self.precedences[tt] = p

    def get_precedence(self, tt: TokenType) -> Precedence:
        return self.precedences.get(tt, Precedence.NONE)

    # =========================================================================
    # CORE PRATT PARSING
    # =========================================================================

    def parse_expr(self, precedence: Precedence = Precedence.NONE, allow_struct: bool = True) -> Optional[Expr]:
        start_tok = self.current
        prefix_fn = self.prefix_parse_fns.get(start_tok.type)

        if not prefix_fn:
            loc = self.loc()
            err = err_unexpected_token(start_tok.value, "expression", loc)
            self.diagnostics.add(err)
            raise ParseError()

        # Try to pass allow_struct if it's the identifier/struct one
        if prefix_fn == self.parse_identifier_or_struct:
            left_expr = prefix_fn(allow_struct)
        else:
            left_expr = prefix_fn()

        while precedence < self.get_precedence(self.current.type):
            infix_tok = self.current
            infix_fn = self.infix_parse_fns.get(infix_tok.type)
            if not infix_fn:
                break
            # Struct parsing in right side of binary op should respect allow_struct? Yes
            left_expr = infix_fn(left_expr, allow_struct=allow_struct)

        return left_expr

    # =========================================================================
    # PREFIX / LITERALS
    # =========================================================================

    def parse_literal(self) -> Expr:
        tok = self.advance()
        val = tok.value
        kind = "string"
        if tok.type == TokenType.INTEGER_LIT:
            kind = "int"
        elif tok.type == TokenType.FLOAT_LIT:
            kind = "float"
        elif tok.type == TokenType.CHAR_LIT:
            kind = "char"
        elif tok.type in (TokenType.TRUE, TokenType.FALSE):
            kind = "bool"
            val = tok.type == TokenType.TRUE

        return LiteralExpr(tok.line, tok.col, kind=kind, value=val)

    def parse_identifier_or_struct(self, allow_struct: bool = True) -> Expr:
        # Xử lý Identifier hoặc QualifiedName và StructLiteral
        tok = self.advance()
        line, col = tok.line, tok.col

        names = [tok.value]
        # Xử lý qualified name: std::vec::Vec
        while self.current.type == TokenType.DOUBLE_COLON:
            self.advance() # Tiêu thụ ::
            if self.current.type in (TokenType.IDENT, TokenType.OK):
                names.append(self.advance().value)
            else:
                self.diagnostics.add(err_unexpected_token(self.current.value, "identifier", self.loc()))

        # Khả năng đây là Struct Literal: Path { field: expr, ... }
        # hoặc Enum Literal
        if allow_struct and self.current.type == TokenType.LBRACE:
            return self.parse_struct_literal(names, line, col)

        if len(names) == 1:
            return IdentifierExpr(line, col, name=names[0])
        return QualifiedNameExpr(line, col, names=names)

    def parse_struct_literal(self, names: list[str], line: int, col: int) -> Expr:
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                break
                
            fname_tok = self.expect(TokenType.IDENT)
            self.expect(TokenType.COLON)
            val = self.parse_expr()
            fields.append(StructFieldInit(fname_tok.value, val))

            if not self.match(TokenType.COMMA):
                self.expect(TokenType.RBRACE)
                break

        return StructLiteralExpr(line, col, name=QualifiedNameExpr(line, col, names), fields=fields)

    def parse_grouped_expr(self) -> Expr:
        self.expect(TokenType.LPAREN)
        expr = self.parse_expr()
        self.expect(TokenType.RPAREN)
        return expr

    def parse_array_literal(self) -> Expr:
        tok = self.expect(TokenType.LBRACKET)
        elems = []
        if not self.match(TokenType.RBRACKET):
            while True:
                elems.append(self.parse_expr())
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RBRACKET)
        return ArrayLiteralExpr(tok.line, tok.col, elements=elems)

    def parse_return_expr(self, allow_struct: bool = True) -> Expr:
        tok = self.advance()
        val = None
        if self.current.type not in (TokenType.SEMICOLON, TokenType.COMMA, TokenType.RBRACE):
            val = self.parse_expr(allow_struct=allow_struct)
        from copl.parser.ast import ReturnStmt
        return ReturnStmt(tok.line, tok.col, value=val)

    def parse_lower_expr(self, allow_struct: bool = True) -> Expr:
        loc = self.loc()
        self.expect(TokenType.LOWER)
        self.expect(TokenType.AT_TARGET)
        target = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LBRACE)
        
        content = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF: break
            expr_stmt = self.parse_stmt_or_expr()
            content.append(expr_stmt)
            
        from copl.parser.ast import BlockExpr
        return BlockExpr(loc.line, loc.col, statements=content, final_expr=None)

    def parse_prefix(self) -> Expr:
        tok = self.advance()
        operand = self.parse_expr(Precedence.PREFIX)
        return UnaryExpr(tok.line, tok.col, op=tok.value, operand=operand)

    # =========================================================================
    # INFIX / POSTFIX
    # =========================================================================

    def parse_infix(self, left: Expr, allow_struct: bool = True) -> Expr:
        tok = self.advance()
        precedence = self.get_precedence(tok.type)
        right = self.parse_expr(precedence, allow_struct=allow_struct)
        return BinaryExpr(left.line, left.col, left=left, op=tok.value, right=right)

    def parse_call(self, left: Expr, allow_struct: bool = True) -> Expr:
        tok = self.expect(TokenType.LPAREN)
        args = []
        if not self.match(TokenType.RPAREN):
            while True:
                args.append(self.parse_expr())
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
        return CallExpr(tok.line, tok.col, callee=left, args=args)

    def parse_index(self, left: Expr, allow_struct: bool = True) -> Expr:
        tok = self.expect(TokenType.LBRACKET)
        index_expr = self.parse_expr()
        self.expect(TokenType.RBRACKET)
        return IndexExpr(tok.line, tok.col, obj=left, index=index_expr)

    def parse_member_access(self, left: Expr, allow_struct: bool = True) -> Expr:
        tok = self.advance()
        member_tok = self.expect(TokenType.IDENT)
        
        # Nếu có LPAREN tiếp theo -> MethodCall
        if self.current.type == TokenType.LPAREN:
            self.advance() # consume (
            args = []
            if not self.match(TokenType.RPAREN):
                while True:
                    args.append(self.parse_expr())
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
            return MethodCallExpr(tok.line, tok.col, obj=left, method=member_tok.value, args=args)
            
        return MemberAccessExpr(tok.line, tok.col, obj=left, member=member_tok.value)

    def parse_try(self, left: Expr, allow_struct: bool = True) -> Expr:
        tok = self.expect(TokenType.QUESTION)
        return TryExpr(tok.line, tok.col, expr=left)
