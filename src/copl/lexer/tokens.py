"""COPL Lexer — Token types và Token dataclass.

Spec reference: docs/copl/01_grammar_spec.md (Lexical Grammar)
                docs/copl/08_module_error_handling.md (Error codes E001, E002)

Tất cả keywords của COPL được định nghĩa ở đây.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # ================================================================
    # KEYWORDS — Module/Visibility
    # ================================================================
    MODULE = auto()
    PUB = auto()
    USE = auto()
    AS = auto()

    # ================================================================
    # KEYWORDS — Declarations
    # ================================================================
    FN = auto()
    STRUCT = auto()
    ENUM = auto()
    TRAIT = auto()
    IMPL = auto()
    TYPE = auto()         # type alias
    CONST = auto()
    STATIC = auto()

    # ================================================================
    # KEYWORDS — Lowering (hardware interface)
    # ================================================================
    LOWER = auto()           # lower fn(...)
    LOWER_STRUCT = auto()    # lower_struct Name ...
    LOWER_CONST = auto()     # lower_const NAME: T = addr

    # ================================================================
    # KEYWORDS — State machine
    # ================================================================
    STATE_MACHINE = auto()
    TRANSITION = auto()
    INITIAL = auto()
    ACTION = auto()

    # ================================================================
    # KEYWORDS — Context entities
    # ================================================================
    REQUIREMENT = auto()
    DECISION = auto()
    WORKITEM = auto()
    TEST = auto()
    TEST_SUITE = auto()
    RISK = auto()

    # ================================================================
    # KEYWORDS — Control flow
    # ================================================================
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    LOOP = auto()
    MATCH = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    CRITICAL_SECTION = auto()

    # ================================================================
    # KEYWORDS — Variable binding
    # ================================================================
    LET = auto()
    MUT = auto()

    # ================================================================
    # KEYWORDS — Other
    # ================================================================
    SPAWN = auto()
    VOLATILE = auto()        # volatile keyword trong lower_struct field

    # ================================================================
    # PRIMITIVE TYPES (keywords)
    # ================================================================
    BOOL = auto()
    U8 = auto();  U16 = auto();  U32 = auto();  U64 = auto();  USIZE = auto()
    I8 = auto();  I16 = auto();  I32 = auto();  I64 = auto();  ISIZE = auto()
    F32 = auto(); F64 = auto()
    CHAR = auto()
    STRING_KW = auto()       # String (type keyword, not string literal)
    UNIT = auto()            # Unit

    # ================================================================
    # BUILT-IN VALUE CONSTRUCTORS
    # ================================================================
    TRUE = auto()
    FALSE = auto()
    SOME = auto()
    NONE = auto()
    OK = auto()
    ERR = auto()
    RESULT = auto()

    # ================================================================
    # ANNOTATIONS (@xxx)
    # ================================================================
    AT_CONTEXT = auto()      # @context
    AT_PLATFORM = auto()     # @platform
    AT_TRACE = auto()        # @trace
    AT_CONTRACT = auto()     # @contract
    AT_EFFECTS = auto()      # @effects
    AT_TARGET = auto()       # @target
    AT_OFFSET = auto()       # @offset
    AT = auto()              # @ (generic fallback)

    # ================================================================
    # LITERALS
    # ================================================================
    INTEGER_LIT = auto()     # 42, 0xFF, 0b1010, 0o77, 1_000_000
    FLOAT_LIT = auto()       # 3.14, 1.0e-5, 2.5E+3
    STRING_LIT = auto()      # "hello world"
    CHAR_LIT = auto()        # 'a', '\n', '\xFF'

    # ================================================================
    # IDENTIFIERS
    # ================================================================
    IDENT = auto()           # foo, my_var, CamelCase, _private

    # ================================================================
    # OPERATORS — Arithmetic
    # ================================================================
    PLUS = auto()            # +
    MINUS = auto()           # -
    STAR = auto()            # *
    SLASH = auto()           # /
    PERCENT = auto()         # %

    # ================================================================
    # OPERATORS — Comparison
    # ================================================================
    EQ = auto()              # ==
    NEQ = auto()             # !=
    LT = auto()              # <
    GT = auto()              # >
    LTE = auto()             # <=
    GTE = auto()             # >=

    # ================================================================
    # OPERATORS — Logical
    # ================================================================
    AND = auto()             # &&
    OR = auto()              # ||
    NOT = auto()             # !

    # ================================================================
    # OPERATORS — Bitwise
    # ================================================================
    BITAND = auto()          # &
    BITOR = auto()           # |
    BITXOR = auto()          # ^
    BITNOT = auto()          # ~
    SHL = auto()             # <<
    SHR = auto()             # >>

    # ================================================================
    # OPERATORS — Assignment
    # ================================================================
    ASSIGN = auto()          # =
    PLUS_ASSIGN = auto()     # +=
    MINUS_ASSIGN = auto()    # -=
    STAR_ASSIGN = auto()     # *=
    SLASH_ASSIGN = auto()    # /=
    PERCENT_ASSIGN = auto()  # %=
    BITOR_ASSIGN = auto()    # |=
    BITAND_ASSIGN = auto()   # &=
    BITXOR_ASSIGN = auto()   # ^=
    SHL_ASSIGN = auto()      # <<=
    SHR_ASSIGN = auto()      # >>=

    # ================================================================
    # OPERATORS — Special
    # ================================================================
    ARROW = auto()           # ->
    FAT_ARROW = auto()       # =>
    QUESTION = auto()        # ?
    DOTDOT = auto()          # ..
    DOUBLE_COLON = auto()    # ::

    # ================================================================
    # DELIMITERS
    # ================================================================
    LPAREN = auto()          # (
    RPAREN = auto()          # )
    LBRACE = auto()          # {
    RBRACE = auto()          # }
    LBRACKET = auto()        # [
    RBRACKET = auto()        # ]
    SEMICOLON = auto()       # ;
    COLON = auto()           # :
    COMMA = auto()           # ,
    DOT = auto()             # .
    PIPE = auto()            # | (pattern matching)
    HASH = auto()            # # (attribute?)
    UNDERSCORE = auto()      # _ (wildcard pattern standalone)

    # ================================================================
    # SPECIAL TOKENS
    # ================================================================
    EOF = auto()             # End of file
    COMMENT = auto()         # // ... (thường bị skip)
    BLOCK_COMMENT = auto()   # /* ... */ (thường bị skip)
    INVALID = auto()         # Ký tự không nhận ra


# ================================================================
# KEYWORD MAP — string → TokenType
# ================================================================
KEYWORDS: dict[str, TokenType] = {
    # Module/Visibility
    "module": TokenType.MODULE,
    "pub": TokenType.PUB,
    "use": TokenType.USE,
    "as": TokenType.AS,

    # Declarations
    "fn": TokenType.FN,
    "struct": TokenType.STRUCT,
    "enum": TokenType.ENUM,
    "trait": TokenType.TRAIT,
    "impl": TokenType.IMPL,
    "type": TokenType.TYPE,
    "const": TokenType.CONST,
    "static": TokenType.STATIC,

    # Lowering
    "lower": TokenType.LOWER,
    "lower_struct": TokenType.LOWER_STRUCT,
    "lower_const": TokenType.LOWER_CONST,

    # State machine
    "state_machine": TokenType.STATE_MACHINE,
    "transition": TokenType.TRANSITION,
    "initial": TokenType.INITIAL,
    "action": TokenType.ACTION,

    # Context entities
    "requirement": TokenType.REQUIREMENT,
    "decision": TokenType.DECISION,
    "workitem": TokenType.WORKITEM,
    "test": TokenType.TEST,
    "test_suite": TokenType.TEST_SUITE,
    "risk": TokenType.RISK,

    # Control flow
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "loop": TokenType.LOOP,
    "match": TokenType.MATCH,
    "return": TokenType.RETURN,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "critical_section": TokenType.CRITICAL_SECTION,

    # Variable binding
    "let": TokenType.LET,
    "mut": TokenType.MUT,

    # Other
    "spawn": TokenType.SPAWN,
    "volatile": TokenType.VOLATILE,
    "_": TokenType.UNDERSCORE,

    # Primitive types
    "Bool": TokenType.BOOL,
    "U8": TokenType.U8,
    "U16": TokenType.U16,
    "U32": TokenType.U32,
    "U64": TokenType.U64,
    "USize": TokenType.USIZE,
    "I8": TokenType.I8,
    "I16": TokenType.I16,
    "I32": TokenType.I32,
    "I64": TokenType.I64,
    "ISize": TokenType.ISIZE,
    "F32": TokenType.F32,
    "F64": TokenType.F64,
    "Char": TokenType.CHAR,
    "String": TokenType.STRING_KW,
    "Unit": TokenType.UNIT,

    # Built-in constructors
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "Some": TokenType.SOME,
    "None": TokenType.NONE,
    "Ok": TokenType.OK,
    "Err": TokenType.ERR,
    "Result": TokenType.RESULT,
}

# Annotation map: "@word" → TokenType
ANNOTATION_KEYWORDS: dict[str, TokenType] = {
    "context": TokenType.AT_CONTEXT,
    "platform": TokenType.AT_PLATFORM,
    "trace": TokenType.AT_TRACE,
    "contract": TokenType.AT_CONTRACT,
    "effects": TokenType.AT_EFFECTS,
    "target": TokenType.AT_TARGET,
    "offset": TokenType.AT_OFFSET,
}


@dataclass(frozen=True)
class Token:
    """
    Một token từ COPL source.

    Attributes:
        type:     Loại token
        value:    Giá trị text gốc trong source
        line:     Dòng (1-indexed)
        col:      Cột (1-indexed)
        filename: Tên file nguồn
    """
    type: TokenType
    value: str
    line: int
    col: int
    filename: str = "<input>"

    def is_keyword(self) -> bool:
        return self.type in _KEYWORD_TYPES

    def is_literal(self) -> bool:
        return self.type in (
            TokenType.INTEGER_LIT,
            TokenType.FLOAT_LIT,
            TokenType.STRING_LIT,
            TokenType.CHAR_LIT,
            TokenType.TRUE,
            TokenType.FALSE,
        )

    def is_type_keyword(self) -> bool:
        return self.type in _TYPE_KEYWORDS

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, {self.line}:{self.col})"


# Pre-computed sets for fast lookup
_KEYWORD_TYPES: frozenset[TokenType] = frozenset(KEYWORDS.values())

_TYPE_KEYWORDS: frozenset[TokenType] = frozenset({
    TokenType.BOOL,
    TokenType.U8, TokenType.U16, TokenType.U32, TokenType.U64, TokenType.USIZE,
    TokenType.I8, TokenType.I16, TokenType.I32, TokenType.I64, TokenType.ISIZE,
    TokenType.F32, TokenType.F64,
    TokenType.CHAR, TokenType.STRING_KW, TokenType.UNIT,
})
