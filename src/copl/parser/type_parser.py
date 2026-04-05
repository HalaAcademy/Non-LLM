"""COPL Type Parser — Phân tích Type Expression.

Spec reference: docs/copl/01_grammar_spec.md (Type Expressions)
"""

from typing import Optional

from copl.errors import err_unexpected_token
from copl.lexer.tokens import TokenType
from copl.parser.ast import (
    ArrayType,
    ASTType,
    NamedType,
    OptionalType,
    PointerType,
    PrimitiveType,
    TupleType,
)
from copl.parser.base import ParseError, ParserBase


class TypeParser(ParserBase):
    """Mixin xử lý các Type Declarations."""

    def parse_type(self) -> ASTType:
        """Parse 1 type expression tổng quát."""
        loc = self.loc()
        tt = self.current.type

        # 1. Array Type: [ Type ; size ]
        if self.match(TokenType.LBRACKET):
            elem_type = self.parse_type()
            self.expect(TokenType.SEMICOLON)
            
            # Khúc này size thường là expression integer. Do TypeParser là mixin của tổng thể
            # ta sẽ mượn parse_expr ở ParserBase con (lúc run time nó sẽ có do kế thừa đa hình)
            size_expr = self.parse_expr() 
            
            self.expect(TokenType.RBRACKET)
            # Tạm ép size_expr lấy token value nguyên thuỷ nếu nó là LiteralExpr
            size_val = size_expr.value if hasattr(size_expr, 'value') else 0 
            return ArrayType(loc.line, loc.col, elem_type=elem_type, size=int(size_val))

        # 2. Pointer Type: * Type
        if self.match(TokenType.STAR):
            elem_type = self.parse_type()
            return PointerType(loc.line, loc.col, elem_type=elem_type)

        # 3. Optional Type: ? Type
        if self.match(TokenType.QUESTION):
            inner = self.parse_type()
            return OptionalType(loc.line, loc.col, inner=inner)

        # 4. Tuple Type: ( Type, Type )
        if self.match(TokenType.LPAREN):
            elements = []
            if not self.match(TokenType.RPAREN):
                while True:
                    elements.append(self.parse_type())
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.RPAREN)
            # Mẹo: Dù có 1 element thì (Type) vẫn là Tuple 1 phần tử (hoặc coi như group). Tại COPL spec, ta bọc TupleType.
            return TupleType(loc.line, loc.col, elements=elements)

        primitives = {
            TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64, TokenType.USIZE,
            TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64, TokenType.ISIZE,
            TokenType.F32, TokenType.F64,
            TokenType.BOOL, TokenType.CHAR, TokenType.STRING_KW, TokenType.UNIT
        }
        if tt in primitives:
            tok = self.advance()
            return PrimitiveType(loc.line, loc.col, name=tok.value or tok.type.name.capitalize())

        # 6. Named Type / Generic Type (vd: Result<T, E>, string_name)
        if tt in (TokenType.IDENT, TokenType.RESULT, TokenType.STRING_KW):
            if tt in (TokenType.RESULT, TokenType.STRING_KW):
                names = [tt.name.lower().capitalize()] # or just use token value
                if tt == TokenType.STRING_KW:
                    names = ["String"]
                elif tt == TokenType.RESULT:
                    names = ["Result"]
                self.advance()
            else:
                names = [self.advance().value]
                
            while self.match(TokenType.DOT) or self.match(TokenType.DOUBLE_COLON):
                if self.current.type == TokenType.IDENT:
                    names.append(self.advance().value)
                
            generic_args = []
            if self.match(TokenType.LT):
                while True:
                    generic_args.append(self.parse_type())
                    if not self.match(TokenType.COMMA):
                        break
                self.expect(TokenType.GT)
                
            return NamedType(loc.line, loc.col, names=names, generic_args=generic_args)

        # Hết Fallback
        self.diagnostics.add(err_unexpected_token(self.current.value or self.current.type.name, "type definition", loc))
        raise ParseError()
