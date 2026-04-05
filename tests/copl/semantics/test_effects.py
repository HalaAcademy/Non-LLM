"""TDD Tests cho Phase 5a: Effect System.

Kiểm tra:
- EffectSet operations
- Ma trận allowed_effects per profile
- EffectChecker inference trên AST thực 
- Annotation mismatch detection
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from copl.semantics.effect_checker import (
    Effect, Profile, EffectSet, EffectChecker, ALLOWED_EFFECTS
)


# ============================================
# 1. Unit tests cho EffectSet
# ============================================

def test_effect_set_empty_is_pure():
    es = EffectSet()
    assert es.is_pure is True

def test_effect_set_pure_only_is_pure():
    es = EffectSet({Effect.PURE})
    assert es.is_pure is True

def test_effect_set_register_is_not_pure():
    es = EffectSet()
    es.add(Effect.REGISTER)
    assert es.is_pure is False
    assert Effect.REGISTER in es.effects

def test_effect_set_add_pure_keeps_pure():
    es = EffectSet()
    es.add(Effect.PURE)
    assert es.is_pure is True

def test_effect_set_union():
    a = EffectSet({Effect.REGISTER})
    b = EffectSet({Effect.INTERRUPT})
    c = a.union(b)
    assert Effect.REGISTER in c.effects
    assert Effect.INTERRUPT in c.effects

def test_effect_set_str():
    es = EffectSet()
    assert str(es) == "[pure]"
    es.add(Effect.REGISTER)
    assert "register" in str(es)


# ============================================
# 2. Unit tests cho allowed_effects matrix
# ============================================

def test_portable_only_pure():
    allowed = ALLOWED_EFFECTS[Profile.PORTABLE]
    assert allowed == {Effect.PURE}

def test_embedded_allows_register_interrupt():
    allowed = ALLOWED_EFFECTS[Profile.EMBEDDED]
    assert Effect.REGISTER in allowed
    assert Effect.INTERRUPT in allowed
    assert Effect.HEAP not in allowed
    assert Effect.IO not in allowed

def test_kernel_allows_panic():
    allowed = ALLOWED_EFFECTS[Profile.KERNEL]
    assert Effect.PANIC in allowed
    assert Effect.REGISTER in allowed

def test_backend_allows_network():
    allowed = ALLOWED_EFFECTS[Profile.BACKEND]
    assert Effect.NETWORK in allowed
    assert Effect.IO in allowed
    assert Effect.HEAP in allowed
    assert Effect.REGISTER not in allowed

def test_scripting_allows_all():
    allowed = ALLOWED_EFFECTS[Profile.SCRIPTING]
    for eff in Effect:
        assert eff in allowed


# ============================================
# 3. Tests cho EffectSet violation detection
# ============================================

def test_effect_set_is_subset():
    es = EffectSet({Effect.REGISTER, Effect.INTERRUPT})
    allowed = ALLOWED_EFFECTS[Profile.EMBEDDED]
    assert es.is_subset_of(allowed) is True

def test_effect_set_violation_detection():
    es = EffectSet({Effect.REGISTER, Effect.HEAP})
    allowed = ALLOWED_EFFECTS[Profile.EMBEDDED]
    violations = es.get_violations(allowed)
    assert Effect.HEAP in violations
    assert Effect.REGISTER not in violations

def test_effect_set_no_violations():
    es = EffectSet({Effect.PURE})
    allowed = ALLOWED_EFFECTS[Profile.PORTABLE]
    violations = es.get_violations(allowed)
    assert len(violations) == 0


# ============================================
# 4. Integration tests: EffectChecker trên AST thực
# ============================================

def _parse_copl(source: str):
    """Helper: parse COPL source → AST."""
    from copl.lexer import Lexer
    from copl.parser import parse
    lexer = Lexer()
    tokens, lex_diags = lexer.tokenize(source)
    ast_node, parse_diags = parse(tokens, filename="<test>")
    return ast_node

def test_effect_checker_lower_blocks_are_register():
    """lower blocks tự động có effect [register]."""
    source = '''
    module examples.test_effects {
        lower_const CAN1: *U32 @target c = 0x40006400;
    }
    '''
    ast_node = _parse_copl(source)
    checker = EffectChecker(profile=Profile.EMBEDDED)
    diags = checker.check_module(ast_node)
    # Không nên có lỗi vì embedded cho phép register
    errors = [d for d in diags if d.code.startswith('E')]
    assert len(errors) == 0

def test_effect_checker_profile_violation():
    """Effect register vi phạm khi trong profile portable."""
    source = '''
    module examples.test_effects {
        lower_const CAN1: *U32 @target c = 0x40006400;
    }
    '''
    ast_node = _parse_copl(source)
    checker = EffectChecker(profile=Profile.PORTABLE)
    diags = checker.check_module(ast_node)
    # Portable không cho phép register → phải có E301
    e301 = [d for d in diags if d.code == 'E301']
    assert len(e301) > 0
