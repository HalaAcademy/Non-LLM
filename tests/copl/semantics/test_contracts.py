"""TDD Tests cho Phase 5c: Contract Checker.

Kiểm tra:
- ContractChecker validates contract blocks
- Budget literal validation
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from copl.semantics.contract_checker import ContractChecker


# ============================================
# 1. Duration literal validation
# ============================================

def test_valid_duration_ms():
    checker = ContractChecker()
    checker._validate_duration_literal("1ms", "test_fn")
    assert len(checker.diagnostics) == 0

def test_valid_duration_us():
    checker = ContractChecker()
    checker._validate_duration_literal("10us", "test_fn")
    assert len(checker.diagnostics) == 0

def test_valid_duration_s():
    checker = ContractChecker()
    checker._validate_duration_literal("1s", "test_fn")
    assert len(checker.diagnostics) == 0

def test_invalid_duration():
    checker = ContractChecker()
    checker._validate_duration_literal("100hz", "test_fn")
    assert len(checker.diagnostics) == 1
    assert checker.diagnostics[0].code == "E702"

# ============================================
# 2. Size literal validation
# ============================================

def test_valid_size_kb():
    checker = ContractChecker()
    checker._validate_size_literal("1KB", "test_fn")
    assert len(checker.diagnostics) == 0

def test_valid_size_b():
    checker = ContractChecker()
    checker._validate_size_literal("256B", "test_fn")
    assert len(checker.diagnostics) == 0

def test_invalid_size():
    checker = ContractChecker()
    checker._validate_size_literal("100bits", "test_fn")
    assert len(checker.diagnostics) == 1
    assert checker.diagnostics[0].code == "E703"

# ============================================
# 3. Module-level contract count
# ============================================

def test_contract_checker_empty_module():
    """Module không có contract → count = 0."""
    from copl.lexer import Lexer
    from copl.parser import parse
    source = '''
    module examples.test_contract {
        fn add(a: U32, b: U32) -> U32 {
            return a + b;
        }
    }
    '''
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename="<test>")
    
    checker = ContractChecker()
    diags = checker.check_module(ast_node)
    assert checker.contract_count == 0
    assert len(diags) == 0
