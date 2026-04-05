"""
Test suite for COPL Semantic Analyzer.
Covers Name Resolution, Scoping, Type Systems, and Flow Control semantic rules.
"""

import pytest

from copl.lexer.lexer import Lexer
from copl.parser import parse
from copl.semantics.analyzer import SemanticAnalyzer

def parse_code(code_str: str):
    """Giả lập quy trình đọc Lexer -> Parser -> Trả về AST Module."""
    full_code = f"module my_mod {{ {code_str} }}"
    lexer = Lexer()
    tokens, lex_diags = lexer.tokenize(full_code)
    
    ast, diags = parse(tokens)
    if diags.has_errors():
        for d in diags.errors():
            print(f"Parser error: {d.message}")
    assert ast is not None, "Failed to parse code into AST!"
    return ast

def check_no_errors(analyzer):
    if analyzer.diags.has_errors():
        for d in analyzer.diags.errors():
            print(f"Unexpected Semantic Error: {d.message}")
        assert False, "Expected no errors but found some!"

def test_scope_resolving_success():
    """Nhóm 1: Biến cục bộ tham chiếu thành công."""
    code = """
        fn do_math() -> U32 {
            let x: U32 = 10;
            return x;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    check_no_errors(analyzer)

def test_scope_resolving_undefined_identifier():
    """Nhóm 1: Sử dụng biến chưa khai báo."""
    code = """
        fn do_math() -> Void {
            let y = x;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    # E202: Lỗi undefined identifier
    assert analyzer.diags.has_errors()
    errors = analyzer.diags.errors()
    assert any("Undefined identifier 'x'" in err.message for err in errors)

def test_type_inference_int_ok():
    """Nhóm 2: Tự động truyền ngược LiteralInt lên kiểu I32."""
    code = """
        fn do_math() -> I32 {
            let x = 123;
            return x;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    check_no_errors(analyzer)

def test_type_mismatch_assignment():
    """Nhóm 2: Lỗi gán type rác cho biến U32."""
    code = """
        fn do_math() -> Void {
            let x: U32 = "Hacked String";
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    assert analyzer.diags.has_errors()
    assert any("Type mismatch" in err.message for err in analyzer.diags.errors())

def test_type_mismatch_const():
    """Nhóm 2: Lỗi gán type tĩnh."""
    code = """
        const MY_CONST: Bool = 123;
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    assert analyzer.diags.has_errors()
    assert any("Type mismatch" in err.message for err in analyzer.diags.errors())

def test_immutability_violation():
    """Nhóm 3: Cố tình gán lại giá trị cho biến không có mut."""
    code = """
        fn change_world() -> Void {
            let val: I32 = 5;
            val = 10;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    if not analyzer.diags.has_errors():
        print("Expected immutability violation error but got no errors!")
    assert analyzer.diags.has_errors()
    assert any("Cannot assign to immutable variable 'val'" in err.message for err in analyzer.diags.errors())

def test_mutability_ok():
    """Nhóm 3: Phép gán cho biến 'mut' hợp lệ."""
    code = """
        fn change_world() -> Void {
            let mut val: I32 = 5;
            val = 10;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    check_no_errors(analyzer)

def test_function_return_mismatch():
    """Nhóm 4: Lỗi Return Type Mismatch."""
    code = """
        fn math() -> Bool {
            return 100;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    assert analyzer.diags.has_errors()
    assert any("Function expects return type Bool" in err.message for err in analyzer.diags.errors())

def test_binary_op_validity():
    """Nhóm 5: Phép cộng hai số Int."""
    code = """
        fn ops() -> Void {
            let mut x = 10;
            let y = 5;
            x += y;
            x = x + y;
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    check_no_errors(analyzer)

def test_generics_result_ok():
    """Nhóm 4: Result Generic type Ok/Err resolving without error."""
    code = """
        fn is_valid() -> Result<I32, String> {
            return Ok(10);
        }
    """
    ast = parse_code(code)
    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast)
    check_no_errors(analyzer)
