"""COPL Statement Parser — Phân tích các khối Câu lệnh (Statements).

Spec reference: docs/copl/01_grammar_spec.md (Statements & Control Flow)
"""

from typing import Union

from copl.errors import err_unexpected_token
from copl.lexer.tokens import TokenType
from copl.parser.ast import (
    AssignStmt,
    BlockExpr,
    BreakStmt,
    ContinueStmt,
    Expr,
    ExprStmt,
    IfStmt,
    LetStmt,
    MatchArm,
    MatchExpr,
    ReturnStmt,
    Stmt,
    WhileStmt,
    CriticalSectionStmt,
    IdentifierPattern,
    LiteralPattern,
    WildcardPattern,
    OrPattern,
)
from copl.parser.base import ParseError, ParserBase


class StmtParser(ParserBase):
    """Mixin xử lý các Câu lệnh thực thi (Statement)."""

    def parse_block(self) -> BlockExpr:
        """Parse khối lệnh { ... }"""
        tok = self.expect(TokenType.LBRACE)
        stmts = []
        final_expr = None

        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                self.expect(TokenType.RBRACE) # Triggers error recovery if missing RBRACE
                break
                
            # Cờ báo hiệu cuối block xem có phải biểu thức trả về không
            curr_pos = self.pos
            parsed_item = self.parse_stmt_or_expr()
            
            if isinstance(parsed_item, Stmt):
                stmts.append(parsed_item)
            elif isinstance(parsed_item, Expr):
                # Nếu là biểu thức mà sau đó là '}' thì đây là final_expr
                if self.current.type == TokenType.RBRACE:
                    final_expr = parsed_item
                else:
                    # Nếu có dấu chấm phẩy thì là ExprStmt, nhưng hàm `parse_stmt_or_expr` 
                    # đã consume SEMICOLON rồi trả về Stmt.
                    # Nếu nó lòi ra Expr mà ko có chấm phẩy thì dính lỗi ngữ pháp, trừ phi block.
                    # Ở COPL, block trả final_expr nếu ko có semicolon.
                    pass
                    
    
        return BlockExpr(tok.line, tok.col, statements=stmts, final_expr=final_expr)

    def parse_stmt_or_expr(self) -> Union[Stmt, Expr]:
        """Quyết định đọc loại Statement nào."""
        tt = self.current.type
        loc = self.loc()

        if tt == TokenType.LET:
            return self.parse_let_stmt()
        elif tt == TokenType.IF:
            return self.parse_if()
        elif tt == TokenType.MATCH:
            return self.parse_match()
        elif tt == TokenType.WHILE:
            return self.parse_while_stmt()
        elif tt == TokenType.RETURN:
            self.advance()
            val = None
            if self.current.type != TokenType.SEMICOLON:
                val = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return ReturnStmt(loc.line, loc.col, value=val)
        elif tt == TokenType.BREAK:
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return BreakStmt(loc.line, loc.col)
        elif tt == TokenType.CONTINUE:
            self.advance()
            self.expect(TokenType.SEMICOLON)
            return ContinueStmt(loc.line, loc.col)
        elif tt == TokenType.CRITICAL_SECTION:
            self.advance()
            body = self.parse_block()
            return CriticalSectionStmt(loc.line, loc.col, body=body)
        elif tt == TokenType.LOWER:
            return self.parse_lower_block_stmt()

        # Nếu không phải các lệnh trên, đây là một Expression (đứng độc lập hoặc Assign).
        expr = self.parse_expr()
        
        # Nếu tiếp theo là dấu bằng `=` hoặc assign ops 
        assign_ops = {
            TokenType.ASSIGN, TokenType.PLUS_ASSIGN, TokenType.MINUS_ASSIGN, 
            TokenType.STAR_ASSIGN, TokenType.SLASH_ASSIGN, TokenType.PERCENT_ASSIGN
        }
        if self.current.type in assign_ops:
            op_tok = self.advance()
            val_expr = self.parse_expr()
            self.expect(TokenType.SEMICOLON)
            return AssignStmt(loc.line, loc.col, lvalue=expr, op=op_tok.value, value=val_expr)

        # Biểu thức bình thường có ';' kết thúc
        if self.match(TokenType.SEMICOLON):
            return ExprStmt(loc.line, loc.col, expr=expr)
            
        # Không có ';' -> Trả về Expr (dùng cho final_expr của block)
        return expr

    def parse_let_stmt(self) -> LetStmt:
        loc = self.loc()
        self.expect(TokenType.LET)
        is_mut = self.match(TokenType.MUT)
        name_tok = self.expect(TokenType.IDENT)
        
        type_ann = None
        if self.match(TokenType.COLON):
            type_ann = self.parse_type()
            
        self.expect(TokenType.ASSIGN)
        value_expr = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        
        return LetStmt(loc.line, loc.col, name=name_tok.value, is_mut=is_mut, type_ann=type_ann, value=value_expr)

    def parse_if(self) -> Union[IfStmt, IfExpr]:
        loc = self.loc()
        self.expect(TokenType.IF)
        
        # If let TODO: support `if let Pattern = Expr`
        
        condition = self.parse_expr(allow_struct=False)
        then_block = self.parse_block()
        else_block = None
        
        if self.match(TokenType.ELSE):
            if self.current.type == TokenType.IF:
                else_block = self.parse_if()
            else:
                else_block = self.parse_block()
                
        # COPL cho phép if return giá trị như một expression
        # Trong context của StmtParser, ta trả về IfStmt. Tuy nhiên AST định nghĩa IfExpr và IfStmt giống lõi
        return IfStmt(loc.line, loc.col, condition=condition, then_block=then_block, else_block=else_block)

    def parse_while_stmt(self) -> WhileStmt:
        loc = self.loc()
        self.expect(TokenType.WHILE)
        condition = self.parse_expr(allow_struct=False)
        body = self.parse_block()
        return WhileStmt(loc.line, loc.col, condition=condition, body=body)

    def parse_match(self) -> Union[MatchExpr, Stmt]:
        loc = self.loc()
        self.expect(TokenType.MATCH)
        expr = self.parse_expr(allow_struct=False)
        self.expect(TokenType.LBRACE)
        
        arms = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                break
            
            # pattern
            pat = self.parse_pattern()
            self.expect(TokenType.FAT_ARROW)
            
            # body
            # body có thể là block { ... } hoặc expr;
            if self.current.type == TokenType.LBRACE:
                body = self.parse_block()
                self.match(TokenType.COMMA) # Tùy chọn comma sau block
            else:
                body = self.parse_expr()
                self.expect(TokenType.COMMA)
                
            arms.append(MatchArm(pat, body))
            
        return MatchExpr(loc.line, loc.col, expr=expr, arms=arms)
        
    def parse_pattern(self):
        # Giản lược đệ quy pattern OR
        pat = self._parse_single_pattern()
        while self.match(TokenType.PIPE):
            right = self._parse_single_pattern()
            pat = OrPattern(pat.line, pat.col, left=pat, right=right)
        return pat
            
    def _parse_single_pattern(self):
        loc = self.loc()
        if self.match(TokenType.UNDERSCORE):
            return WildcardPattern(loc.line, loc.col)
            
        # Literal pattern
        if self.current.type in (TokenType.INTEGER_LIT, TokenType.STRING_LIT):
            lit = self.parse_literal()
            return LiteralPattern(loc.line, loc.col, value=lit)
            
        # Identifier hoặc Enum Variant Pattern
        if self.current.type == TokenType.IDENT:
            # Xử lý Direction::North (Enum variant destructuring)
            names = [self.advance().value]
            while self.match(TokenType.DOUBLE_COLON):
                names.append(self.expect(TokenType.IDENT).value)
                
            return IdentifierPattern(loc.line, loc.col, name="::".join(names))
            
        self.diagnostics.add(err_unexpected_token(self.current.value, "pattern", loc))
        raise ParseError()

    def parse_lower_block_stmt(self) -> ExprStmt:
        """Parse `lower @target c { CAN1->MCR |= 1; }`"""
        loc = self.loc()
        self.expect(TokenType.LOWER)
        self.expect(TokenType.AT_TARGET)
        target = self.expect(TokenType.IDENT).value
        
        self.expect(TokenType.LBRACE)
        
        # Parse expression thô lặp lại trong block
        # Ở đây ta xài ExprParser để cào các expression gán bên trong: `CAN1->MCR |= CAN_MCR_INRQ;`
        # Điều này hoàn toàn xài đc Pratt Parser do -> (DOT postfix) và |= (ASSIGN) đều là token hợp lệ.
        stmts = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                break
            # Dùng lại luồng parse stmt/expr ở trên
            expr_stmt = self.parse_stmt_or_expr()
            stmts.append(expr_stmt)
            
        # Gói vào BlockExpr để trả về
        return ExprStmt(loc.line, loc.col, expr=BlockExpr(loc.line, loc.col, statements=stmts))
