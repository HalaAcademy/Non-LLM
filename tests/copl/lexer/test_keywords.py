"""Tests cho Lexer — Keywords và Identifiers.

Spec reference: docs/copl/01_grammar_spec.md Section 2.1 (Keywords)
"""

import pytest
from copl.lexer import Lexer, TokenType


def lex(source: str) -> list[tuple[TokenType, str]]:
    """Helper: tokenize và trả về list (type, value). Bỏ EOF."""
    lexer = Lexer()
    tokens, diags = lexer.tokenize(source)
    assert not diags.has_errors(), f"Unexpected lex errors: {[str(d) for d in diags.errors()]}"
    return [(t.type, t.value) for t in tokens if t.type != TokenType.EOF]


def lex_types(source: str) -> list[TokenType]:
    return [t for t, _ in lex(source)]


# ================================================================
# Module/Visibility keywords
# ================================================================

class TestModuleKeywords:
    def test_module(self):
        assert lex_types("module") == [TokenType.MODULE]

    def test_pub(self):
        assert lex_types("pub") == [TokenType.PUB]

    def test_use(self):
        assert lex_types("use") == [TokenType.USE]

    def test_as(self):
        assert lex_types("as") == [TokenType.AS]


# ================================================================
# Declaration keywords
# ================================================================

class TestDeclarationKeywords:
    def test_fn(self):
        assert lex_types("fn") == [TokenType.FN]

    def test_struct(self):
        assert lex_types("struct") == [TokenType.STRUCT]

    def test_enum(self):
        assert lex_types("enum") == [TokenType.ENUM]

    def test_trait(self):
        assert lex_types("trait") == [TokenType.TRAIT]

    def test_impl(self):
        assert lex_types("impl") == [TokenType.IMPL]

    def test_type(self):
        assert lex_types("type") == [TokenType.TYPE]

    def test_const(self):
        assert lex_types("const") == [TokenType.CONST]

    def test_static(self):
        assert lex_types("static") == [TokenType.STATIC]


# ================================================================
# Lowering keywords (đặc biệt của COPL)
# ================================================================

class TestLoweringKeywords:
    def test_lower(self):
        assert lex_types("lower") == [TokenType.LOWER]

    def test_lower_struct(self):
        """lower_struct phải là 1 token duy nhất, không phải lower + _ + struct."""
        result = lex("lower_struct")
        assert result == [(TokenType.LOWER_STRUCT, "lower_struct")]

    def test_lower_const(self):
        """lower_const phải là 1 token duy nhất."""
        result = lex("lower_const")
        assert result == [(TokenType.LOWER_CONST, "lower_const")]

    def test_lower_vs_lower_struct(self):
        """'lower ' (với space) → LOWER, 'lower_struct' → LOWER_STRUCT."""
        result = lex("lower lower_struct lower_const")
        assert result == [
            (TokenType.LOWER, "lower"),
            (TokenType.LOWER_STRUCT, "lower_struct"),
            (TokenType.LOWER_CONST, "lower_const"),
        ]


# ================================================================
# State machine keywords
# ================================================================

class TestStateMachineKeywords:
    def test_state_machine(self):
        assert lex_types("state_machine") == [TokenType.STATE_MACHINE]

    def test_transition(self):
        assert lex_types("transition") == [TokenType.TRANSITION]

    def test_initial(self):
        assert lex_types("initial") == [TokenType.INITIAL]


# ================================================================
# Context entity keywords
# ================================================================

class TestContextEntityKeywords:
    def test_requirement(self):
        assert lex_types("requirement") == [TokenType.REQUIREMENT]

    def test_decision(self):
        assert lex_types("decision") == [TokenType.DECISION]

    def test_workitem(self):
        assert lex_types("workitem") == [TokenType.WORKITEM]

    def test_test(self):
        assert lex_types("test") == [TokenType.TEST]

    def test_test_suite(self):
        """test_suite phải là 1 token."""
        assert lex("test_suite") == [(TokenType.TEST_SUITE, "test_suite")]

    def test_risk(self):
        assert lex_types("risk") == [TokenType.RISK]


# ================================================================
# Control flow keywords
# ================================================================

class TestControlFlowKeywords:
    def test_if(self): assert lex_types("if") == [TokenType.IF]
    def test_else(self): assert lex_types("else") == [TokenType.ELSE]
    def test_while(self): assert lex_types("while") == [TokenType.WHILE]
    def test_for(self): assert lex_types("for") == [TokenType.FOR]
    def test_in(self): assert lex_types("in") == [TokenType.IN]
    def test_loop(self): assert lex_types("loop") == [TokenType.LOOP]
    def test_match(self): assert lex_types("match") == [TokenType.MATCH]
    def test_return(self): assert lex_types("return") == [TokenType.RETURN]
    def test_break(self): assert lex_types("break") == [TokenType.BREAK]
    def test_continue(self): assert lex_types("continue") == [TokenType.CONTINUE]

    def test_critical_section(self):
        """critical_section là 1 keyword."""
        assert lex("critical_section") == [(TokenType.CRITICAL_SECTION, "critical_section")]

    def test_let(self): assert lex_types("let") == [TokenType.LET]
    def test_mut(self): assert lex_types("mut") == [TokenType.MUT]


# ================================================================
# Primitive type keywords (COPL types bắt đầu bằng chữ hoa)
# ================================================================

class TestPrimitiveTypes:
    def test_bool(self): assert lex_types("Bool") == [TokenType.BOOL]
    def test_u8(self): assert lex_types("U8") == [TokenType.U8]
    def test_u16(self): assert lex_types("U16") == [TokenType.U16]
    def test_u32(self): assert lex_types("U32") == [TokenType.U32]
    def test_u64(self): assert lex_types("U64") == [TokenType.U64]
    def test_usize(self): assert lex_types("USize") == [TokenType.USIZE]
    def test_i8(self): assert lex_types("I8") == [TokenType.I8]
    def test_i32(self): assert lex_types("I32") == [TokenType.I32]
    def test_f32(self): assert lex_types("F32") == [TokenType.F32]
    def test_f64(self): assert lex_types("F64") == [TokenType.F64]
    def test_char(self): assert lex_types("Char") == [TokenType.CHAR]
    def test_string(self): assert lex_types("String") == [TokenType.STRING_KW]
    def test_unit(self): assert lex_types("Unit") == [TokenType.UNIT]


# ================================================================
# Built-in constructors
# ================================================================

class TestBuiltinConstructors:
    def test_true(self): assert lex_types("true") == [TokenType.TRUE]
    def test_false(self): assert lex_types("false") == [TokenType.FALSE]
    def test_some(self): assert lex_types("Some") == [TokenType.SOME]
    def test_none(self): assert lex_types("None") == [TokenType.NONE]
    def test_ok(self): assert lex_types("Ok") == [TokenType.OK]
    def test_err(self): assert lex_types("Err") == [TokenType.ERR]


# ================================================================
# Identifiers
# ================================================================

class TestIdentifiers:
    def test_lowercase(self):
        assert lex("foo") == [(TokenType.IDENT, "foo")]

    def test_camel_case(self):
        assert lex("CanPdu") == [(TokenType.IDENT, "CanPdu")]

    def test_snake_case(self):
        assert lex("my_var") == [(TokenType.IDENT, "my_var")]

    def test_with_numbers(self):
        assert lex("var1") == [(TokenType.IDENT, "var1")]

    def test_starting_with_underscore(self):
        assert lex("_private") == [(TokenType.IDENT, "_private")]

    def test_all_underscore(self):
        assert lex("_") == [(TokenType.UNDERSCORE, "_")]

    def test_keyword_prefix_not_keyword(self):
        """'functions' bắt đầu bằng 'fn' nhưng là IDENT."""
        assert lex("functions") == [(TokenType.IDENT, "functions")]

    def test_multiple_identifiers(self):
        result = lex("foo bar baz")
        assert all(t == TokenType.IDENT for t, _ in result)
        assert [v for _, v in result] == ["foo", "bar", "baz"]


# ================================================================
# Annotations
# ================================================================

class TestAnnotations:
    def test_at_context(self):
        assert lex("@context") == [(TokenType.AT_CONTEXT, "@context")]

    def test_at_platform(self):
        assert lex("@platform") == [(TokenType.AT_PLATFORM, "@platform")]

    def test_at_trace(self):
        assert lex("@trace") == [(TokenType.AT_TRACE, "@trace")]

    def test_at_contract(self):
        assert lex("@contract") == [(TokenType.AT_CONTRACT, "@contract")]

    def test_at_effects(self):
        assert lex("@effects") == [(TokenType.AT_EFFECTS, "@effects")]

    def test_at_target(self):
        assert lex("@target") == [(TokenType.AT_TARGET, "@target")]

    def test_at_offset(self):
        assert lex("@offset") == [(TokenType.AT_OFFSET, "@offset")]

    def test_unknown_annotation(self):
        """Annotation không biết → AT token."""
        result = lex("@unknown")
        assert result == [(TokenType.AT, "@unknown")]


# ================================================================
# Complex: keyword context (không phải standalone)
# ================================================================

class TestKeywordsInContext:
    def test_module_declaration(self):
        result = lex_types("module mcal.can")
        assert result == [TokenType.MODULE, TokenType.IDENT, TokenType.DOT, TokenType.IDENT]

    def test_pub_fn(self):
        result = lex_types("pub fn")
        assert result == [TokenType.PUB, TokenType.FN]

    def test_lower_struct_name(self):
        result = lex_types("lower_struct CAN_TypeDef")
        assert result == [TokenType.LOWER_STRUCT, TokenType.IDENT]

    def test_let_mut(self):
        result = lex_types("let mut x")
        assert result == [TokenType.LET, TokenType.MUT, TokenType.IDENT]
