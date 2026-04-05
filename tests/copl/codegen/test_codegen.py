import pytest

from copl.lexer.lexer import Lexer
from copl.parser import parse
from copl.semantics.analyzer import SemanticAnalyzer
from copl.codegen.transpiler import CTranspiler

def run_codegen(source: str) -> tuple[str, str]:
    """Helper compiler pipeline: trả về (header_content, src_content)."""
    lexer = Lexer()
    tokens, lex_diags = lexer.tokenize(source)
    if lex_diags.has_errors():
        for err in lex_diags.errors():
            print(err)
        return "", ""

    ast_items, parse_diags = parse(tokens, filename="<test>")
    if parse_diags.has_errors():
        for err in parse_diags.errors():
            print(err)
        return "", ""

    analyzer = SemanticAnalyzer()
    analyzer.analyze(ast_items)
    if analyzer.diags.has_errors():
        for err in analyzer.diags.errors():
            print(err)
        return "", ""

    transpiler = CTranspiler(filename="<test>")
    header, src = transpiler.transpile(ast_items)
    return header, src

def test_transpile_empty_module():
    header, src = run_codegen("module examples.code {}")
    assert "<test>_h" in header.lower()
    assert "<TEST>_H" in header

def test_transpile_struct_decl():
    source = """
    module sys.data {
        struct Point {
            x: I32,
            y: I32,
        }
    }
    """
    header, src = run_codegen(source)
    assert "typedef struct {" in header
    assert "int32_t x;" in header
    assert "int32_t y;" in header
    assert "} Point;" in header

def test_transpile_function_basic():
    source = """
    module math {
        pub fn add(a: I32, b: I32) -> I32 {
            let mut sum: I32 = a + b;
            return sum;
        }
    }
    """
    header, src = run_codegen(source)
    
    # Check prototype in header
    assert "int32_t add(int32_t a, int32_t b);" in header
    
    # Check body in source
    assert "int32_t add(int32_t a, int32_t b) {" in src
    assert "int32_t sum = a + b;" in src
    assert "return sum;" in src

def test_lower_target_c_block():
    source = """
    module examples.drivers {
        lower_const REG1: *U32 @target c = 0x4000;

        pub fn poke() -> Void {
            lower @target c {
                REG1[0] |= 1;
                REG1[0] &= ~2;
            }
        }
    }
    """
    header, src = run_codegen(source)
    
    # Header should define macro
    assert "#define REG1 ((uint32_t*)0x4000)" in header

    # Src should contain the raw expressions
    assert "REG1[0] |= 1;" in src
    assert "REG1[0] &= ~2;" in src

def test_array_mapping():
    source = """
    module examples.pkg {
        struct Packet {
            data: [U8; 8],
        }

        pub fn read(pkt: Packet) -> Void {
            lower @target c {
                pkt.data[0] = 5;
            }
        }
    }
    """
    header, src = run_codegen(source)
    
    # header check
    assert "uint8_t* data;" in header
    
    # src check, index expression
    assert "pkt.data[0] = 5;" in src
