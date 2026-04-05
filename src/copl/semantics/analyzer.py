"""Semantic Analyzer - Trình phân tích ngữ nghĩa đi duyệt qua AST.

6-Pass analysis theo Spec 09_compiler_architecture.md:
  Pass 1: Name resolution (hoisting)
  Pass 2: Type checking (bidirectional)
  Pass 3: Effect inference
  Pass 4: Profile checking
  Pass 5: Contract checking
  Pass 6: Trace linking (future)
"""

from typing import Any, Optional, List
from copl.parser import ast
from copl.semantics.scope import SymbolTable, Symbol, SymbolKind
from copl.semantics import types
from copl.errors import DiagnosticBag, Diagnostic, Severity, SourceLocation
from copl.semantics.effect_checker import EffectChecker, Profile as EffectProfile
from copl.semantics.profile_checker import ProfileChecker, Profile
from copl.semantics.contract_checker import ContractChecker

class SemanticError(Exception):
    pass

class SemanticAnalyzer:
    """Tree-Walker đi qua các mấu Node để bind Type và check Context."""
    
    def __init__(self, diags: Optional[DiagnosticBag] = None, profile: str = "embedded"):
        self.symtab = SymbolTable()
        self.diags = diags or DiagnosticBag()
        
        # Để hỗ trợ return checking, ta lưu lại kiểu trả về của hàm đang phân tích hiện tại
        self.current_function_return_type: Optional[types.BaseType] = None
        
        # Phase 5: Advanced checkers
        self.profile = Profile(profile) if isinstance(profile, str) else profile
        self.effect_checker = EffectChecker(profile=EffectProfile(self.profile.value))
        self.profile_checker = ProfileChecker(profile=self.profile)
        self.contract_checker = ContractChecker()
        
    def error(self, msg: str, line: int, col: int):
        self.diags.add(Diagnostic(
            code="E101",
            severity=Severity.ERROR,
            message=msg,
            location=SourceLocation("unknown_file", line, col)
        ))
        
    def analyze(self, node: ast.ASTNode):
        """Entry point cho việc phân giải — 6-pass pipeline."""
        # Pass 1: Thu thập Declaration (Hoisting / Name resolution)
        self.hoist_declarations(node)
        # Pass 2: Phân giải (Type checking)
        self.visit(node)
        
        # Pass 3: Effect inference
        effect_diags = self.effect_checker.check_module(node)
        for ed in effect_diags:
            severity = Severity.ERROR if ed.code.startswith('E') else Severity.WARNING
            self.diags.add(Diagnostic(
                code=ed.code,
                severity=severity,
                message=ed.message,
                location=SourceLocation("unknown_file", ed.line, ed.col)
            ))
        
        # Pass 4: Profile checking
        profile_diags = self.profile_checker.check_module(node)
        for pd in profile_diags:
            self.diags.add(Diagnostic(
                code=pd.code,
                severity=Severity.ERROR,
                message=pd.message,
                location=SourceLocation("unknown_file", pd.line, pd.col)
            ))
        
        # Pass 5: Contract checking
        contract_diags = self.contract_checker.check_module(node)
        for cd in contract_diags:
            self.diags.add(Diagnostic(
                code=cd.code,
                severity=Severity.ERROR,
                message=cd.message,
                location=SourceLocation("unknown_file", cd.line, cd.col)
            ))
        
        # Pass 6: Trace linking (future)
        # TODO: self.trace_linker.link(node)
        
        return node
        
    def hoist_declarations(self, node: ast.ASTNode):
        """Pass 1: Quét Module để nạp tất cả Struct/Function vào Global Scope."""
        if isinstance(node, ast.ASTModule):
            for item in node.items:
                if isinstance(item, ast.FunctionDecl):
                    sym = Symbol(item.sig.name, SymbolKind.FUNCTION, node=item)
                    self.symtab.global_scope.define(sym)
                elif isinstance(item, ast.StructDecl):
                    sym = Symbol(item.name, SymbolKind.STRUCT, type_info=types.StructType(item.name), node=item)
                    self.symtab.global_scope.define(sym)
                elif isinstance(item, ast.EnumDecl):
                    sym = Symbol(item.name, SymbolKind.ENUM, type_info=types.EnumType(item.name), node=item)
                    self.symtab.global_scope.define(sym)

    def visit(self, node: ast.ASTNode) -> Any:
        """Dynamic dispatch dạng Visitor Pattern."""
        if node is None:
            return None
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node: ast.ASTNode) -> Any:
        """Duyệt fallback."""
        pass

    # ==========================================
    # VISITING DECLARATIONS (Khai Báo)
    # ==========================================
    def visit_ASTModule(self, node: ast.ASTModule):
        for item in node.items:
            self.visit(item)

    def visit_FunctionDecl(self, node: ast.FunctionDecl):
        # Resolve return type
        ret_type = self.resolve_type(node.sig.ret_type) if node.sig.ret_type else types.VoidType()
        self.current_function_return_type = ret_type
        
        # Cập nhật type_info cho Symbol trong Global Scope
        sym = self.symtab.resolve(node.sig.name, current_only=False)
        if sym:
            sym.type_info = ret_type
            
        self.symtab.enter_scope(name=f"fn_{node.sig.name}")
        
        # Đưa param vào parameters scope
        for param in node.sig.params:
            param_type = self.resolve_type(param.type_ann)
            p_sym = Symbol(param.name, SymbolKind.VARIABLE, type_info=param_type)
            self.symtab.define(p_sym)
            
        # Duyệt body
        if node.body:
            self.visit(node.body)
            
        self.symtab.exit_scope()
        self.current_function_return_type = None

    def visit_LowerConstDecl(self, node: ast.LowerConstDecl):
        ctype = self.resolve_type(node.type_ann)
        sym = Symbol(node.name, SymbolKind.CONSTANT, type_info=ctype, is_mut=False)
        if not self.symtab.define(sym):
            self.error(f"Constant '{node.name}' already defined", node.line, node.col)

    def visit_LowerStructDecl(self, node: ast.LowerStructDecl):
        pass

    def visit_StructDecl(self, node: ast.StructDecl):
        pass

    def visit_ConstDecl(self, node: ast.ConstDecl):
        val_type = self.visit(node.value)
        decl_type = self.resolve_type(node.type_ann) if node.type_ann else val_type
        
        if val_type and decl_type and not val_type.is_assignable_to(decl_type):
            if hasattr(val_type, 'name') and val_type.name == "LiteralInt" and hasattr(decl_type, 'name') and decl_type.name in ["I32", "U32", "I8", "U8"]:
                pass
            else:
                self.error(f"Type mismatch: cannot assign {val_type} to const of type {decl_type}", node.line, node.col)
            
        sym = Symbol(node.name, SymbolKind.CONSTANT, type_info=decl_type)
        self.symtab.define(sym)

    # ==========================================
    # VISITING STATEMENTS
    # ==========================================
    def visit_BlockExpr(self, node: ast.BlockExpr) -> types.BaseType:
        self.symtab.enter_scope("block")
        last_type = types.VoidType()
        
        stmt_list = node.statements if hasattr(node, 'statements') else getattr(node, 'items', [])

        for stmt in stmt_list:
            t = self.visit(stmt)
            if t: last_type = t
            
        final_expr = getattr(node, 'final_expr', None)
        if final_expr is not None:
            last_type = self.visit(final_expr)
            
        self.symtab.exit_scope()
        return last_type

    def visit_LetStmt(self, node: ast.LetStmt):
        val_type = self.visit(node.value)
        decl_type = self.resolve_type(node.type_ann) if node.type_ann else val_type
        
        if decl_type is None:
            decl_type = types.PrimitiveType("InferError")
            
        if val_type and decl_type:
            if hasattr(val_type, 'name') and val_type.name == "LiteralInt":
                if not hasattr(decl_type, 'name') or decl_type.name not in ("I32", "U32", "U8", "I8", "U16", "I16"):
                    val_type = types.PrimitiveType("I32")
                    if hasattr(decl_type, 'name') and decl_type.name == "LiteralInt":
                        decl_type = types.PrimitiveType("I32")
                else:
                    val_type = decl_type

            if not val_type.is_assignable_to(decl_type):
                self.error(f"Type mismatch in let statement. Expected {decl_type}, got {val_type}", node.line, node.col)

        sym = Symbol(node.name, SymbolKind.VARIABLE, type_info=decl_type, is_mut=node.is_mut)
        if not self.symtab.define(sym):
            self.error(f"Variable '{node.name}' already defined in this scope", node.line, node.col)

    def visit_ExprStmt(self, node: ast.ExprStmt):
        return self.visit(node.expr)
        
    def visit_ReturnStmt(self, node: ast.ReturnStmt):
        val_type = self.visit(node.value) if node.value else types.VoidType()
        if self.current_function_return_type and not val_type.is_assignable_to(self.current_function_return_type):
            if hasattr(val_type, 'name') and val_type.name == "LiteralInt" and hasattr(self.current_function_return_type, 'name') and self.current_function_return_type.name in ["I32", "U32", "U8"]:
                pass
            # Cho phép GenericType Result match ngầm với generic OK.
            elif isinstance(val_type, types.GenericType) and val_type.base == "Result" and isinstance(self.current_function_return_type, types.GenericType) and self.current_function_return_type.base == "Result":
                pass
            elif type(val_type).__name__ == "VoidType" and getattr(self.current_function_return_type, 'name', None) in ["Unit", "Void"]:
                pass
            else:
                self.error(f"Function expects return type {self.current_function_return_type}, but returned {val_type}", node.line, node.col)
        return types.BottomType()

    def visit_AssignStmt(self, node: ast.AssignStmt):
        ltype = self.visit(node.lvalue)
        rtype = self.visit(node.value)
        
        if isinstance(node.lvalue, ast.IdentifierExpr):
            sym = self.symtab.resolve(node.lvalue.name)
            if sym and not sym.is_mut:
                self.error(f"Cannot assign to immutable variable '{sym.name}'", node.line, node.col)
                
        if ltype and rtype and not rtype.is_assignable_to(ltype):
            if hasattr(rtype, 'name') and rtype.name == "LiteralInt" and hasattr(ltype, 'name') and ltype.name in ["U8", "I32", "U32", "I8"]:
                pass
            else:
                self.error(f"Cannot assign {rtype} to {ltype}", node.line, node.col)
        return types.VoidType()

    # ==========================================
    # VISITING EXPRESSIONS
    # ==========================================
    def visit_LiteralExpr(self, node: ast.LiteralExpr) -> types.BaseType:
        if node.kind == "int":
            return types.PrimitiveType("LiteralInt")
        elif node.kind == "float":
            return types.PrimitiveType("F32")
        elif node.kind == "bool":
            return types.PrimitiveType("Bool")
        elif node.kind == "string":
            return types.PrimitiveType("String")
        return types.PrimitiveType("Unknown")

    def visit_IdentifierExpr(self, node: ast.IdentifierExpr) -> types.BaseType:
        if node.name in ("Ok", "Err"):
            return types.GenericType("Result", [types.PrimitiveType("Unknown"), types.PrimitiveType("Unknown")])
            
        sym = self.symtab.resolve(node.name)
        if not sym:
            self.error(f"Undefined identifier '{node.name}'", node.line, node.col)
            return types.PrimitiveType("Error")
        return sym.type_info or types.PrimitiveType("Unknown")

    def visit_BinaryExpr(self, node: ast.BinaryExpr) -> types.BaseType:
        l = self.visit(node.left)
        r = self.visit(node.right)
        
        if node.op in ("==", "!=", "<", "<=", ">", ">="):
            return types.PrimitiveType("Bool")
            
        if node.op in ("=", "+=", "-=", "*=", "/=", "%=", "|=", "&=", "^=", "<<=", ">>="):
            if isinstance(node.left, ast.IdentifierExpr):
                sym = self.symtab.resolve(node.left.name)
                if sym and not sym.is_mut:
                    self.error(f"Cannot assign to immutable variable '{sym.name}'", node.line, node.col)
            return l
            
        if l and l.name == "LiteralInt" and r and r.name != "LiteralInt":
            return r
        return l

    def visit_CallExpr(self, node: ast.CallExpr) -> types.BaseType:
        callee_type = self.visit(node.callee)
        for arg in node.args:
            self.visit(arg)
            
        # Hardcode return type for Result::Ok / Err
        if isinstance(node.callee, ast.IdentifierExpr) and node.callee.name in ("Ok", "Err"):
            return types.GenericType("Result", [types.PrimitiveType("Unknown"), types.PrimitiveType("Unknown")])
            
        if hasattr(callee_type, 'ret_type'):
            return callee_type.ret_type
        return types.PrimitiveType("Unknown")

    def visit_MemberAccessExpr(self, node: ast.MemberAccessExpr) -> types.BaseType:
        self.visit(node.obj)
        return types.PrimitiveType("Unknown")

    def visit_MethodCallExpr(self, node: ast.MethodCallExpr) -> types.BaseType:
        self.visit(node.obj)
        for arg in node.args:
            self.visit(arg)
        return types.PrimitiveType("Unknown")
        
    def visit_QualifiedNameExpr(self, node: ast.QualifiedNameExpr) -> types.BaseType:
        if node.names[0] == "Ok":
            return types.GenericType("Result", [types.PrimitiveType("Unknown"), types.PrimitiveType("Unknown")])
        sym = self.symtab.resolve(node.names[0])
        if sym and sym.type_info:
            return sym.type_info
        return types.PrimitiveType("Unknown")

    # ==========================================
    # UTILS
    # ==========================================
    def resolve_type(self, ast_type: ast.ASTType) -> types.BaseType:
        """Convert biến ASTType văn bản thành BaseType thật."""
        if isinstance(ast_type, ast.PrimitiveType):
            return types.PrimitiveType(ast_type.name)
        elif isinstance(ast_type, ast.NamedType):
            base_name = ast_type.names[-1]
            
            # Support cho GenericType
            if hasattr(ast_type, 'generic_args') and ast_type.generic_args:
                args = [self.resolve_type(arg) for arg in ast_type.generic_args]
                return types.GenericType(base_name, args)
                
            if base_name in ("I32", "U32", "U16", "I16", "U8", "I8", "F32", "Bool", "String"):
                return types.PrimitiveType(base_name)
            sym = self.symtab.resolve(base_name)
            if sym and sym.type_info:
                return sym.type_info
            
            # Fallback nếu tên là Result nhưng ko có generic args
            if base_name == "Result":
                return types.GenericType("Result", [types.PrimitiveType("Unknown"), types.PrimitiveType("Unknown")])
                
            return types.PrimitiveType(base_name)
        elif isinstance(ast_type, ast.ResultType):
            ok_type = self.resolve_type(ast_type.ok_type)
            err_type = self.resolve_type(ast_type.err_type)
            return types.GenericType("Result", [ok_type, err_type])
            
        elif ast_type is None:
            return types.VoidType()
            
        return types.PrimitiveType("Unknown")
