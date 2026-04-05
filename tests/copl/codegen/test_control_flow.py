"""TDD Tests cho Phase 6: Advanced Code Generation.

Kiểm tra control flow lowering COPL → C.
Lưu ý: Parser hiện tại không hỗ trợ `mut` trong function params,
nên dùng `let mut` inside body.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from copl.lexer import Lexer
from copl.parser import parse
from copl.codegen.transpiler import CTranspiler


def _transpile(source: str) -> tuple[str, str]:
    """Helper: COPL source → (header, source) C code."""
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename="<test>")
    assert ast_node is not None, "Parser returned None — check COPL syntax"
    transpiler = CTranspiler("<test>")
    return transpiler.transpile(ast_node)


# ============================================
# 1. If/Else Lowering
# ============================================

def test_if_stmt_simple():
    source = '''module examples.ctrl {
        fn check(x: U32) -> Bool {
            if x > 100 {
                return true;
            }
            return false;
        }
    }'''
    _, c_src = _transpile(source)
    assert "if (" in c_src
    assert "x > 100" in c_src
    assert "return true;" in c_src

def test_if_else_stmt():
    source = '''module examples.ctrl {
        fn classify(x: U32) -> U32 {
            if x > 100 {
                return 1;
            } else {
                return 0;
            }
        }
    }'''
    _, c_src = _transpile(source)
    assert "if (" in c_src
    assert "} else {" in c_src
    assert "return 1;" in c_src
    assert "return 0;" in c_src


# ============================================
# 2. While Loop
# ============================================

def test_while_loop():
    source = '''module examples.ctrl {
        fn countdown(n: U32) -> U32 {
            let mut i: U32 = n;
            while i > 0 {
                i = i - 1;
            }
            return i;
        }
    }'''
    _, c_src = _transpile(source)
    assert "while (" in c_src
    assert "i > 0" in c_src


# ============================================
# 3. Break
# ============================================

def test_break_stmt():
    source = '''module examples.ctrl {
        fn search(n: U32) -> U32 {
            let mut i: U32 = 0;
            while i < n {
                if i == 5 {
                    break;
                }
                i = i + 1;
            }
            return i;
        }
    }'''
    _, c_src = _transpile(source)
    assert "break;" in c_src
    assert "while (" in c_src


# ============================================
# 4. Assignment
# ============================================

def test_assignment():
    source = '''module examples.ctrl {
        fn inc(x: U32) -> U32 {
            let mut result: U32 = x;
            result = result + 1;
            return result;
        }
    }'''
    _, c_src = _transpile(source)
    assert "result = result + 1;" in c_src


# ============================================
# 5. Struct + Function
# ============================================

def test_struct_with_function():
    source = '''module examples.structs {
        struct Point {
            x: U32,
            y: U32
        }
        fn get_x(p: Point) -> U32 {
            return p.x;
        }
    }'''
    header, c_src = _transpile(source)
    assert "typedef struct" in header
    assert "uint32_t x;" in header
    assert "uint32_t y;" in header
    assert "Point" in header
    assert "p.x" in c_src


# ============================================
# 6. Enum → typedef enum
# ============================================

def test_enum_codegen():
    source = '''module examples.enums {
        enum Direction {
            North,
            South,
            East,
            West
        }
    }'''
    header, _ = _transpile(source)
    assert "typedef enum" in header
    assert "Direction_North" in header
    assert "Direction_South" in header
    assert "} Direction;" in header
