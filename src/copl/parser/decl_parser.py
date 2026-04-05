"""COPL Declaration Parser — Phân tích Cấu trúc hệ thống và Khai báo.

Xử lý function, struct, enum, test, requirements, context.
"""

from typing import Union

from copl.errors import err_unexpected_token
from copl.lexer.tokens import TokenType
from copl.parser.ast import (
    ContractBlock,
    DictionaryBlock,
    EffectAnnotation,
    EnumDecl,
    EnumVariant,
    FieldDecl,
    FunctionDecl,
    FunctionSig,
    ConstDecl,
    LowerConstDecl,
    LowerStructDecl,
    LowerStructField,
    Param,
    QualifiedNameExpr,
    StructDecl,
    Item,
    LiteralExpr,
)
from copl.parser.base import ParseError, ParserBase


class DeclParser(ParserBase):
    """Mixin xử lý các Item/Declaration ở cấp độ Module."""

    def parse_decl(self) -> Union[Item, None]:
        """Tuyến đầu phân nhánh (Routing) các Declaration phổ biến."""
        tt = self.current.type

        # Modifiers
        is_pub = False
        if self.match(TokenType.PUB):
            is_pub = True
            tt = self.current.type

        if tt == TokenType.STRUCT:
            return self.parse_struct_decl(is_pub)
        elif tt == TokenType.ENUM:
            return self.parse_enum_decl(is_pub)
        elif tt == TokenType.FN:
            return self.parse_fn_decl(is_pub)
        elif tt == TokenType.CONST:
            return self.parse_const_decl(is_pub)
        elif tt == TokenType.STATIC:
            return self.parse_static_decl(is_pub)
        elif tt == TokenType.USE:
            return self.parse_use_decl()
        
        # Lower / Hardware
        if tt == TokenType.LOWER_STRUCT:
            return self.parse_lower_struct_decl()
        elif tt == TokenType.LOWER_CONST:
            return self.parse_lower_const_decl()

        # Decorators / System Blocks
        if tt in (TokenType.AT_PLATFORM, TokenType.AT_CONTEXT):
            return self.parse_system_decorator_block()

        # Testing & Spec Linking
        if tt == TokenType.TEST:
            return self.parse_test_entity()
        elif tt == TokenType.REQUIREMENT:
            return self.parse_requirement_entity()

        # Fallback error recovery
        loc = self.loc()
        self.diagnostics.add(err_unexpected_token(self.current.value, "module item (struct, fn, enum, ...)", loc))
        raise ParseError()

    def parse_struct_decl(self, is_pub: bool) -> StructDecl:
        loc = self.loc()
        self.expect(TokenType.STRUCT)
        name = self.expect(TokenType.IDENT).value
        
        # Generic <T>
        generic_params = self._parse_generic_params()
            
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                break
            
            fname = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            ftype = self.parse_type()
            self.match(TokenType.COMMA) # optional trailing comma
            
            fields.append(FieldDecl(fname, ftype))
            
        return StructDecl(loc.line, loc.col, name=name, is_pub=is_pub, fields=fields, generic_params=generic_params)

    def parse_enum_decl(self, is_pub: bool) -> EnumDecl:
        loc = self.loc()
        self.expect(TokenType.ENUM)
        name = self.expect(TokenType.IDENT).value
        generic_params = self._parse_generic_params()
        
        self.expect(TokenType.LBRACE)
        variants = []
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF:
                break
            
            if self.current.type in (TokenType.IDENT, TokenType.OK):
                vname = self.advance().value
            else:
                vname = self.expect(TokenType.IDENT).value
            
            v_tuple = []
            v_struct = []
            if self.match(TokenType.LPAREN):
                # Tuple variant: Ok(Type, Type)
                while not self.match(TokenType.RPAREN):
                    v_tuple.append(self.parse_type())
                    if not self.match(TokenType.COMMA):
                        break
                        
            elif self.match(TokenType.LBRACE):
                # Struct variant: Move { x: i32, y: i32 }
                while not self.match(TokenType.RBRACE):
                    fname = self.expect(TokenType.IDENT).value
                    self.expect(TokenType.COLON)
                    v_struct.append(FieldDecl(fname, self.parse_type()))
                    self.match(TokenType.COMMA)
                    
            self.match(TokenType.COMMA)
            variants.append(EnumVariant(vname, tuple_types=v_tuple, struct_fields=v_struct))
            
        return EnumDecl(loc.line, loc.col, name=name, is_pub=is_pub, variants=variants, generic_params=generic_params)

    def parse_fn_decl(self, is_pub: bool) -> FunctionDecl:
        loc = self.loc()
        self.expect(TokenType.FN)
        name = self.expect(TokenType.IDENT).value
        generic_params = self._parse_generic_params()
        
        self.expect(TokenType.LPAREN)
        params = []
        if not self.match(TokenType.RPAREN):
            while True:
                pname = self.expect(TokenType.IDENT).value
                self.expect(TokenType.COLON)
                ptype = self.parse_type()
                params.append(Param(pname, ptype))
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.RPAREN)
            
        ret_type = None
        if self.match(TokenType.ARROW):
            ret_type = self.parse_type()
            
        # Parse Annotations: @effects [pure], @contract { pre: [], post: [] }
        effects = None
        contract = None
        
        while self.current.type in (TokenType.AT_EFFECTS, TokenType.AT_CONTRACT, TokenType.AT_TRACE):
            tt = self.advance().type
            if tt == TokenType.AT_EFFECTS:
                self.expect(TokenType.LBRACKET)
                eff_list = []
                if not self.match(TokenType.RBRACKET):
                    while True:
                        eff_list.append(self.expect(TokenType.IDENT).value)
                        if not self.match(TokenType.COMMA):
                            break
                    self.expect(TokenType.RBRACKET)
                effects = EffectAnnotation(effects=eff_list)
            elif tt == TokenType.AT_CONTRACT:
                self.expect(TokenType.LBRACE)
                pre_list = []
                post_list = []
                while not self.match(TokenType.RBRACE):
                    if self.current.type == TokenType.EOF: break
                    cat = self.expect(TokenType.IDENT).value # 'pre' or 'post'
                    self.expect(TokenType.COLON)
                    self.expect(TokenType.LBRACKET)
                    
                    if cat == "pre":
                        while not self.match(TokenType.RBRACKET):
                            pre_list.append(self.parse_expr())
                            self.match(TokenType.COMMA)
                    elif cat == "post":
                        while not self.match(TokenType.RBRACKET):
                            post_list.append(self.parse_expr())
                            self.match(TokenType.COMMA)
                    self.match(TokenType.COMMA)
                contract = ContractBlock(pre=pre_list, post=post_list)
            elif tt == TokenType.AT_TRACE:
                self.expect(TokenType.LBRACE)
                while not self.match(TokenType.RBRACE):
                    self.advance() # consume ignore internal items cho @trace function level
                    
        body = self.parse_block()
        sig = FunctionSig(loc.line, loc.col, name, is_pub, params, ret_type, generic_params, contract, effects)
        return FunctionDecl(loc.line, loc.col, sig=sig, body=body)

    def parse_lower_struct_decl(self) -> LowerStructDecl:
        loc = self.loc()
        self.expect(TokenType.LOWER_STRUCT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.AT_TARGET)
        target = self.expect(TokenType.IDENT).value
        
        self.expect(TokenType.LBRACE)
        fields = []
        while not self.match(TokenType.RBRACE):
            fname = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            is_vol = self.match(TokenType.VOLATILE)
            ftype = self.parse_type()
            
            offset = 0
            if self.match(TokenType.AT_OFFSET):
                offset_tok = self.expect(TokenType.INTEGER_LIT)
                val_str = str(offset_tok.value).lower()
                offset = int(val_str, base=16 if 'x' in val_str else 10)
                
            self.match(TokenType.COMMA)
            fields.append(LowerStructField(fname, ftype, offset, is_vol))
            
        return LowerStructDecl(loc.line, loc.col, name=name, target=target, fields=fields)

    def parse_lower_const_decl(self) -> LowerConstDecl:
        loc = self.loc()
        self.expect(TokenType.LOWER_CONST)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        ftype = self.parse_type()
        
        self.expect(TokenType.AT_TARGET)
        target = self.expect(TokenType.IDENT).value
        
        self.expect(TokenType.ASSIGN)
        addr_tok = self.expect(TokenType.INTEGER_LIT)
        val_str = str(addr_tok.value).lower()
        addr = int(val_str, base=16 if 'x' in val_str else 10)
        self.expect(TokenType.SEMICOLON)
        
        return LowerConstDecl(loc.line, loc.col, name=name, type_ann=ftype, target=target, address=addr)

    def parse_const_decl(self, is_pub: bool) -> ConstDecl:
        loc = self.loc()
        self.expect(TokenType.CONST)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type_ann = self.parse_type()
        self.expect(TokenType.ASSIGN)
        val = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        return ConstDecl(loc.line, loc.col, name=name, is_pub=is_pub, type_ann=type_ann, value=val)

    def parse_use_decl(self) -> UseDecl:
        loc = self.loc()
        self.expect(TokenType.USE)
        path_names = []
        path_names.append(self.expect(TokenType.IDENT).value)
        while self.match(TokenType.DOT):
            if self.current.type == TokenType.IDENT:
                path_names.append(self.advance().value)
            else:
                break
        
        use_list = []
        if self.match(TokenType.LBRACE):
            while not self.match(TokenType.RBRACE):
                if self.current.type == TokenType.EOF: break
                if self.current.type == TokenType.IDENT:
                    use_list.append(self.advance().value)
                self.match(TokenType.COMMA)
                
        self.expect(TokenType.SEMICOLON)
        from copl.parser.ast import UseDecl, QualifiedNameExpr
        return UseDecl(loc.line, loc.col, path=QualifiedNameExpr(loc.line, loc.col, names=path_names), alias=None, use_list=use_list)

    def parse_static_decl(self, is_pub: bool) -> StaticDecl:
        loc = self.loc()
        self.expect(TokenType.STATIC)
        is_mut = self.match(TokenType.MUT)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.COLON)
        type_ann = self.parse_type()
        self.expect(TokenType.ASSIGN)
        val = self.parse_expr()
        self.expect(TokenType.SEMICOLON)
        from copl.parser.ast import StaticDecl
        return StaticDecl(loc.line, loc.col, name=name, is_pub=is_pub, is_mut=is_mut, type_ann=type_ann, value=val)

    def parse_system_decorator_block(self):
        """Parse `@platform { ... }` or `@context { ... }`."""
        loc = self.loc()
        tok = self.advance() # AT_PLATFORM or AT_CONTEXT
        kind = "platform" if tok.type == TokenType.AT_PLATFORM else "context"
        
        self.expect(TokenType.LBRACE)
        fields = {}
        while not self.match(TokenType.RBRACE):
            if self.current.type == TokenType.EOF: break
            fname = self.expect(TokenType.IDENT).value
            self.expect(TokenType.COLON)
            
            # Value can be string lit, ident, or array
            val = None
            if self.current.type == TokenType.STRING_LIT:
                val = LiteralExpr(self.current.line, self.current.col, 'string', self.advance().value)
            elif self.current.type == TokenType.IDENT:
                val = QualifiedNameExpr(self.current.line, self.current.col, names=[self.advance().value])
                while self.match(TokenType.MINUS): # hardware arm-cortex-m4 has minus symbol
                    val.names[0] += "-" + self.advance().value
            else:
                self.advance() # fallback consume
                
            fields[fname] = val
            self.match(TokenType.COMMA)
            
        return DictionaryBlock(loc.line, loc.col, kind=kind, fields=fields)

    def parse_test_entity(self):
        loc = self.loc()
        self.expect(TokenType.TEST)
        name = self.expect(TokenType.IDENT).value
        self.expect(TokenType.LBRACE)
        # Bỏ qua logic validation entity ở phase 1
        while not self.match(TokenType.RBRACE):
            # Cào ngoặc `{}` đệm cho an toàn thay vì advance ngây ngô
            if self.match(TokenType.LBRACE):
                while not self.match(TokenType.RBRACE):
                    self.advance()
            else:
                self.advance()
        return DictionaryBlock(loc.line, loc.col, "test", {"name": name})

    def parse_requirement_entity(self):
        loc = self.loc()
        self.expect(TokenType.REQUIREMENT)
        self.expect(TokenType.IDENT)
        self.expect(TokenType.LBRACE)
        while not self.match(TokenType.RBRACE):
            self.advance()
        return DictionaryBlock(loc.line, loc.col, "requirement", {})

    def _parse_generic_params(self) -> list[str]:
        generic_params = []
        if self.match(TokenType.LT):
            while True:
                generic_params.append(self.expect(TokenType.IDENT).value)
                if not self.match(TokenType.COMMA):
                    break
            self.expect(TokenType.GT)
        return generic_params
