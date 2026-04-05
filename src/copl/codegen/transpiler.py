"""
COPL Transpiler. Chuyển đổi AST thành C Code thông qua CBuilder.
"""

from copl.parser import ast
from copl.semantics.analyzer import SemanticAnalyzer
from copl.codegen.c_builder import CBuilder

class CTranspiler:
    def __init__(self, filename: str):
        self.builder = CBuilder(filename)
        
    def transpile(self, module_node: ast.ASTModule) -> tuple[str, str]:
        """Entry point: Xử lý toàn bộ Module và trả về cặp (Header, Source)."""
        self.visit(module_node)
        return self.builder.render_header(), self.builder.render_source()
        
    def visit(self, node: ast.ASTNode):
        if node is None:
            return
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
        
    def generic_visit(self, node: ast.ASTNode):
        pass
        
    def _get_type_name(self, type_ann) -> str:
        if type_ann is None:
            return "void"
        if type(type_ann).__name__ == "ArrayType":
            # For C generation, a basic approach is mapping array parameter to pointer: U8 -> uint8_t*
            elem_name = self._get_type_name(getattr(type_ann, 'elem_type', None))
            return f"{elem_name}*"
        if type(type_ann).__name__ == "PointerType":
            elem_name = self._get_type_name(getattr(type_ann, 'elem_type', None))
            return f"{elem_name}*"
        if hasattr(type_ann, 'names'):
            return type_ann.names[-1]
        if hasattr(type_ann, 'name'):
            return type_ann.name
        return "void"

    def map_type(self, type_str: str) -> str:
        """Map kiểu COPL về kiểu C."""
        if not type_str: return "void"
        
        is_pointer = False
        if type_str.endswith("*"):
            is_pointer = True
            type_str = type_str[:-1]
            
        mappings = {
            "I32": "int32_t",
            "U32": "uint32_t",
            "I16": "int16_t",
            "U16": "uint16_t",
            "I8": "int8_t",
            "U8": "uint8_t",
            "F32": "float",
            "Bool": "bool",
            "Void": "void",
            "String": "char*"
        }
        mapped = mappings.get(type_str, type_str)
        return mapped + "*" if is_pointer else mapped

    def resolve_type(self, ast_node) -> str:
        return self.map_type(self._get_type_name(getattr(ast_node, 'type_ann', None)))

    # --- Declarations ---
    
    def visit_ASTModule(self, node: ast.ASTModule):
        for item in node.items:
            self.visit(item)

    def visit_LowerBlock(self, node: ast.LowerBlock):
        """Forward Raw C code."""
        if node.target == "c":
            self.builder.emit_raw("/* --- Raw Block Lowering --- */")
            self.builder.emit_raw(node.code)
            self.builder.emit_raw("\n")

    def visit_LowerConstDecl(self, node: ast.LowerConstDecl):
        ctype = self.resolve_type(node)
        # Sinh macro C ép kiểu con trỏ: #define CAN1 ((CAN_TypeDef*)0x40006400)
        address_str = hex(node.address) if isinstance(node.address, int) else str(node.address)
        val = f"(({ctype}){address_str})"
        self.builder.add_macro(node.name, val)

    def visit_LowerStructDecl(self, node: ast.LowerStructDecl):
        # Hạ cấp struct C y hệt typedef struct 
        lines = []
        lines.append(f"typedef struct {{")
        for field in node.fields:
            ftype = self.resolve_type(field)
            volatile_str = "volatile " if getattr(field, 'is_volatile', False) else ""
            lines.append(f"    {volatile_str}{ftype} {field.name};")
        lines.append(f"}} {node.name};")
        self.builder.add_typedef("\n".join(lines))

    def visit_ConstDecl(self, node: ast.ConstDecl):
        # type_ann of node
        ctype = self.resolve_type(node)
        expr_str = self.visit(node.value)
        self.builder.add_macro(node.name, str(expr_str))

    def visit_UseDecl(self, node: ast.UseDecl):
        # Transpiler cấp độ 1 chưa cần Gen file Header tương ứng Use
        pass

    def visit_StaticDecl(self, node: ast.StaticDecl):
        ctype = self.resolve_type(node)
        expr_str = self.visit(node.value)
        
        if getattr(node.type_ann, '__class__', None).__name__ == 'ArrayType':
            elem_name = self.map_type(self._get_type_name(node.type_ann.elem_type))
            size = node.type_ann.size
            self.builder.emit(f"static {elem_name} {node.name}[{size}] = {expr_str};")
        else:
            self.builder.emit(f"static {ctype} {node.name} = {expr_str};")

    def visit_StructDecl(self, node: ast.StructDecl):
        lines = []
        lines.append(f"typedef struct {{")
        for field in node.fields:
            ftype = self.resolve_type(field)
            lines.append(f"    {ftype} {field.name};")
        lines.append(f"}} {node.name};")
        self.builder.add_typedef("\n".join(lines))
        
    def visit_EnumDecl(self, node: ast.EnumDecl):
        lines = []
        lines.append(f"typedef enum {{")
        for variant in node.variants:
            lines.append(f"    {node.name}_{variant.name},")
        lines.append(f"}} {node.name};")
        self.builder.add_typedef("\n".join(lines))

    def visit_FunctionDecl(self, node: ast.FunctionDecl):
        ret_type = self.map_type(self._get_type_name(node.sig.ret_type)) if node.sig.ret_type else "void"
            
        params = []
        for p in node.sig.params:
            ptype = self.resolve_type(p)
            params.append(f"{ptype} {p.name}")
            
        param_str = ", ".join(params) if params else "void"
        sig_str = f"{ret_type} {node.sig.name}({param_str})"
        
        # Thêm Header Protocol nếu hàm là public (tương lai COPL có thể gắn cờ pub)
        self.builder.add_prototype(sig_str)
        
        # Mở body
        self.builder.emit(sig_str + " {")
        self.builder.indent()
        
        if node.body:
            self.visit(node.body)
            
        self.builder.dedent()
        self.builder.emit("}\n")

    # --- Statements ---
    def visit_BlockExpr(self, node: ast.BlockExpr):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_LetStmt(self, node: ast.LetStmt):
        ctype = "auto"
        if node.type_ann:
             ctype = self.resolve_type(node)
        
        expr_str = self.visit(node.value)
        self.builder.emit(f"{ctype} {node.name} = {expr_str};")
        
    def visit_ReturnStmt(self, node: ast.ReturnStmt):
        val = self.visit(node.value) if node.value else ""
        if val:
            self.builder.emit(f"return {val};")
        else:
            self.builder.emit("return;")

    def visit_ExprStmt(self, node: ast.ExprStmt):
        expr_str = self.visit(node.expr)
        if expr_str:
            self.builder.emit(f"{expr_str};")

    # --- Control Flow (Phase 6) ---

    def visit_IfStmt(self, node: ast.IfStmt):
        cond = self.visit(node.condition)
        self.builder.emit(f"if ({cond}) {{")
        self.builder.indent()
        self.visit(node.then_block)
        self.builder.dedent()
        
        if node.else_block:
            if isinstance(node.else_block, ast.IfStmt):
                # else if chain
                self.builder.emit("} else")
                self.visit_IfStmt(node.else_block)
            else:
                self.builder.emit("} else {")
                self.builder.indent()
                self.visit(node.else_block)
                self.builder.dedent()
                self.builder.emit("}")
        else:
            self.builder.emit("}")

    def visit_IfExpr(self, node: ast.IfExpr):
        """If expression — sinh dạng ternary nếu đơn giản, otherwise inline block."""
        cond = self.visit(node.condition)
        self.builder.emit(f"if ({cond}) {{")
        self.builder.indent()
        self.visit(node.then_block)
        self.builder.dedent()
        
        if node.else_block:
            if isinstance(node.else_block, ast.IfExpr):
                self.builder.emit("} else")
                self.visit_IfExpr(node.else_block)
            else:
                self.builder.emit("} else {")
                self.builder.indent()
                self.visit(node.else_block)
                self.builder.dedent()
                self.builder.emit("}")
        else:
            self.builder.emit("}")

    def visit_WhileStmt(self, node: ast.WhileStmt):
        cond = self.visit(node.condition)
        self.builder.emit(f"while ({cond}) {{")
        self.builder.indent()
        self.visit(node.body)
        self.builder.dedent()
        self.builder.emit("}")

    def visit_BreakStmt(self, node: ast.BreakStmt):
        self.builder.emit("break;")

    def visit_ContinueStmt(self, node: ast.ContinueStmt):
        self.builder.emit("continue;")

    def visit_AssignStmt(self, node: ast.AssignStmt):
        lvalue = self.visit(node.lvalue)
        rvalue = self.visit(node.value)
        op = node.op if node.op else "="
        self.builder.emit(f"{lvalue} {op} {rvalue};")

    def visit_MatchExpr(self, node: ast.MatchExpr):
        """Match expression → switch/case (cho enum) hoặc if-else chain."""
        scrutinee = self.visit(node.expr)
        self.builder.emit(f"switch ({scrutinee}) {{")
        self.builder.indent()
        
        for arm in node.arms:
            pattern_str = self._visit_pattern(arm.pattern)
            if pattern_str == "_":
                self.builder.emit(f"default: {{")
            else:
                self.builder.emit(f"case {pattern_str}: {{")
            self.builder.indent()
            self.visit(arm.body)
            self.builder.emit("break;")
            self.builder.dedent()
            self.builder.emit("}")
        
        self.builder.dedent()
        self.builder.emit("}")
    
    def _visit_pattern(self, pattern) -> str:
        """Chuyển pattern → C case label."""
        ptype = type(pattern).__name__
        if ptype == 'WildcardPattern':
            return "_"
        elif ptype == 'IdentifierPattern':
            return pattern.name
        elif ptype == 'LiteralPattern':
            return self.visit(pattern.value)
        elif ptype == 'QualifiedNameExpr':
            return "_".join(pattern.names)
        return "_"

    def visit_CriticalSectionStmt(self, node: ast.CriticalSectionStmt):
        """critical_section { ... } → __disable_irq(); ... __enable_irq();"""
        self.builder.emit("__disable_irq();")
        self.builder.emit("{")
        self.builder.indent()
        self.visit(node.body)
        self.builder.dedent()
        self.builder.emit("}")
        self.builder.emit("__enable_irq();")

    # --- Expressions ---
    
    def visit_LiteralExpr(self, node: ast.LiteralExpr):
        if node.kind == "bool":
            return "true" if node.value else "false"
        if node.kind == "string":
            return f'"{node.value}"'
        return str(node.value)

    def visit_IdentifierExpr(self, node: ast.IdentifierExpr):
        return node.name

    def visit_QualifiedNameExpr(self, node: ast.QualifiedNameExpr):
        # Result::Ok -> Result_Ok
        return "_".join(node.names)

    def visit_BinaryExpr(self, node: ast.BinaryExpr):
        l = self.visit(node.left)
        r = self.visit(node.right)
        return f"{l} {node.op} {r}"

    def visit_UnaryExpr(self, node: ast.UnaryExpr):
        operand = self.visit(node.operand)
        return f"{node.op}{operand}"

    def visit_IndexExpr(self, node: ast.IndexExpr):
        obj = self.visit(node.obj)
        idx = self.visit(node.index)
        return f"{obj}[{idx}]"

    def visit_CallExpr(self, node: ast.CallExpr):
        callee = self.visit(node.callee)
        args = [self.visit(arg) for arg in node.args]
        args_str = ", ".join(args)
        return f"{callee}({args_str})"

    def visit_MemberAccessExpr(self, node: ast.MemberAccessExpr):
        obj = self.visit(node.obj)
        # Nếu obj in HOA (ví dụ CAN1, CAN2) → Pointer Constant trong khối nhúng
        if isinstance(node.obj, ast.IdentifierExpr) and node.obj.name.isupper():
            return f"{obj}->{node.member}"
        return f"{obj}.{node.member}"

    def visit_MethodCallExpr(self, node: ast.MethodCallExpr):
        obj = self.visit(node.obj)
        args = [self.visit(arg) for arg in node.args]
        args.insert(0, f"&{obj}") # Pass by address for methods
        args_str = ", ".join(args)
        return f"{node.method}({args_str})"

    def visit_StructLiteralExpr(self, node: ast.StructLiteralExpr):
        """StructName { a: 1, b: 2 } → (StructName){ .a = 1, .b = 2 }"""
        name = node.struct_name
        inits = []
        for f in node.fields:
            val = self.visit(f.value)
            inits.append(f".{f.name} = {val}")
        return f"({name}){{ {', '.join(inits)} }}"

    def visit_ArrayLiteralExpr(self, node: ast.ArrayLiteralExpr):
        """[1, 2, 3] → { 1, 2, 3 }"""
        elems = [self.visit(e) for e in node.elements]
        return f"{{ {', '.join(elems)} }}"

