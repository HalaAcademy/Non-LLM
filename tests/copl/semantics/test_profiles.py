"""TDD Tests cho Phase 5b: Profile Checker.

Kiểm tra:
- Forbidden types enforcement
- Lower blocks chỉ cho phép trong embedded/kernel
- Panic patterns detection trong embedded
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from copl.semantics.profile_checker import (
    ProfileChecker, Profile, FORBIDDEN_TYPES, LOWER_ALLOWED_PROFILES
)


# ============================================
# 1. Forbidden types per profile
# ============================================

def test_embedded_forbids_string():
    assert "String" in FORBIDDEN_TYPES[Profile.EMBEDDED]

def test_embedded_forbids_vec():
    assert "Vec" in FORBIDDEN_TYPES[Profile.EMBEDDED]

def test_backend_allows_all_types():
    assert len(FORBIDDEN_TYPES[Profile.BACKEND]) == 0

def test_scripting_allows_all_types():
    assert len(FORBIDDEN_TYPES[Profile.SCRIPTING]) == 0


# ============================================
# 2. Lower block allowed profiles
# ============================================

def test_lower_allowed_in_embedded():
    assert Profile.EMBEDDED in LOWER_ALLOWED_PROFILES

def test_lower_allowed_in_kernel():
    assert Profile.KERNEL in LOWER_ALLOWED_PROFILES

def test_lower_not_allowed_in_portable():
    assert Profile.PORTABLE not in LOWER_ALLOWED_PROFILES

def test_lower_not_allowed_in_backend():
    assert Profile.BACKEND not in LOWER_ALLOWED_PROFILES


# ============================================
# 3. Integration: ProfileChecker trên AST thực
# ============================================

def _parse_copl(source: str):
    from copl.lexer import Lexer
    from copl.parser import parse
    lexer = Lexer()
    tokens, lex_diags = lexer.tokenize(source)
    ast_node, parse_diags = parse(tokens, filename="<test>")
    return ast_node

def test_profile_checker_embedded_allows_lower():
    """Embedded profile cho phép lower blocks."""
    source = '''
    module examples.test_profile {
        lower_const CAN1: *U32 @target c = 0x40006400;
    }
    '''
    ast_node = _parse_copl(source)
    checker = ProfileChecker(profile=Profile.EMBEDDED)
    diags = checker.check_module(ast_node)
    # Không có lỗi E801 vì embedded cho phép lower
    assert len([d for d in diags if d.code == 'E801']) == 0

def test_profile_checker_portable_rejects_lower():
    """Portable profile cấm lower blocks → E801."""
    source = '''
    module examples.test_profile {
        lower_const CAN1: *U32 @target c = 0x40006400;
    }
    '''
    ast_node = _parse_copl(source)
    checker = ProfileChecker(profile=Profile.PORTABLE)
    diags = checker.check_module(ast_node)
    e801 = [d for d in diags if d.code == 'E801']
    assert len(e801) > 0
    assert "portable" in e801[0].message.lower()
