"""COPL Parser — Bộ phân tích cú pháp tạo Cây AST.

LL(1)/LL(2) Recursive Descent Parser với Pratt Parsing cho Expressions.
Spec reference: docs/copl/01_grammar_spec.md
"""

from typing import Iterable

from copl.errors import DiagnosticBag
from copl.lexer.tokens import Token, TokenType
from copl.parser.ast import ASTModule, QualifiedNameExpr
from copl.parser.base import ParseError

from copl.parser.expr_parser import ExprParser
from copl.parser.type_parser import TypeParser
from copl.parser.stmt_parser import StmtParser
from copl.parser.decl_parser import DeclParser


class Parser(DeclParser, StmtParser, TypeParser, ExprParser):
    """
    Parser chính của bộ biên dịch COPL.
    
    Kế thừa chuỗi Mixins phân tích cú pháp để xây dựng AST hoàn chỉnh.
    """

    def parse_module(self) -> ASTModule:
        """Entry point để parse một source file thành ASTModule."""
        tok = self.expect(TokenType.MODULE)
        
        # Parse qualified name
        name_toks = [self.expect(TokenType.IDENT).value]
        while self.match(TokenType.DOT):
            name_toks.append(self.expect(TokenType.IDENT).value)
        
        name_expr = QualifiedNameExpr(tok.line, tok.col, names=name_toks)
        
        self.expect(TokenType.LBRACE)
        items = self.parse_module_items()
        self.expect(TokenType.RBRACE)
        
        return ASTModule(tok.line, tok.col, name=name_expr, items=items)

    def parse_module_items(self) -> list:
        items = []
        while self.current.type != TokenType.RBRACE and self.current.type != TokenType.EOF:
            try:
                item = self.parse_item()
                if item:
                    items.append(item)
            except ParseError:
                # Phục hồi lỗi: Bỏ qua token rác cho đến khi gặp token Sync (như fn, struct, })
                self.error_recovery()
        return items

    def parse_item(self):
        """Parse từng thực thể mức Module dựa trên thẻ lệnh lookahead."""
        tt = self.current.type
        
        if tt == TokenType.EOF:
            return None
        
        # Trỏ luồng parse module item vô bảng định tuyến của DeclParser Mixin
        return self.parse_decl()


def parse(tokens: Iterable[Token], filename: str = "<input>") -> tuple[ASTModule | None, DiagnosticBag]:
    """Cổng nối tiếp nhanh (Helper function) để Parse list token thành ASTModule."""
    parser = Parser(tokens, filename)
    
    ast_module = None
    if parser.current.type == TokenType.MODULE:
        try:
            ast_module = parser.parse_module()
        except ParseError:
            pass # Lỗi lớn nhất không parse được block module gốc
    else:
        # Nếu COPL file chỉ có declarations mà thiếu `module ... {` thì bọc màng ảo
        # Ở spec, file bét nhất phải có module {...}
        pass

    return ast_module, parser.diagnostics
