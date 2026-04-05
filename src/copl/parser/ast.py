"""COPL Abstract Syntax Tree (AST).

Định nghĩa toàn bộ các cấu trúc cây nội hàm được Parser xuất ra.
Spec reference: docs/copl/01_grammar_spec.md
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Union


@dataclass
class ASTNode:
    """Class gốc của mọi AST node, luôn chứa vị trí."""
    line: int
    col: int


# ==============================================================================
# 1. TYPES
# ==============================================================================

@dataclass
class ASTType(ASTNode):
    pass


@dataclass
class PrimitiveType(ASTType):
    name: str


@dataclass
class NamedType(ASTType):
    names: list[str]
    generic_args: list[ASTType] = field(default_factory=list)


@dataclass
class ArrayType(ASTType):
    elem_type: ASTType
    size: int


@dataclass
class TupleType(ASTType):
    elements: list[ASTType]


@dataclass
class PointerType(ASTType):
    elem_type: ASTType


@dataclass
class OptionalType(ASTType):
    inner: ASTType


@dataclass
class ResultType(ASTType):
    ok_type: ASTType
    err_type: ASTType


@dataclass
class FnType(ASTType):
    params: list[ASTType]
    ret_type: ASTType


# ==============================================================================
# 2. EXPRESSIONS
# ==============================================================================

@dataclass
class Expr(ASTNode):
    pass


@dataclass
class LiteralExpr(Expr):
    kind: str  # 'int', 'float', 'string', 'char', 'bool'
    value: Union[str, int, float, bool]


@dataclass
class IdentifierExpr(Expr):
    name: str


@dataclass
class QualifiedNameExpr(Expr):
    names: list[str]


@dataclass
class BinaryExpr(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class UnaryExpr(Expr):
    op: str
    operand: Expr


@dataclass
class CallExpr(Expr):
    callee: Expr
    args: list[Expr]


@dataclass
class MemberAccessExpr(Expr):
    obj: Expr
    member: str


@dataclass
class IndexExpr(Expr):
    obj: Expr
    index: Expr


@dataclass
class MethodCallExpr(Expr):
    obj: Expr
    method: str
    args: list[Expr]


@dataclass
class TryExpr(Expr):
    expr: Expr


@dataclass
class BlockExpr(Expr):
    statements: list['Stmt']
    final_expr: Optional[Expr] = None


@dataclass
class StructFieldInit:
    name: str
    value: Expr


@dataclass
class StructLiteralExpr(Expr):
    name: QualifiedNameExpr
    fields: list[StructFieldInit]


@dataclass
class ArrayLiteralExpr(Expr):
    elements: list[Expr]


@dataclass
class IfExpr(Expr):
    condition: Expr
    then_block: BlockExpr
    else_block: Union[BlockExpr, 'IfExpr', None]


@dataclass
class MatchArm:
    pattern: 'Pattern'
    body: Union[Expr, BlockExpr]


@dataclass
class MatchExpr(Expr):
    expr: Expr
    arms: list[MatchArm]


# ==============================================================================
# 3. PATTERNS
# ==============================================================================

@dataclass
class Pattern(ASTNode):
    pass


@dataclass
class WildcardPattern(Pattern):
    pass


@dataclass
class IdentifierPattern(Pattern):
    name: str


@dataclass
class LiteralPattern(Pattern):
    value: LiteralExpr


@dataclass
class OrPattern(Pattern):
    left: Pattern
    right: Pattern


# ==============================================================================
# 4. STATEMENTS
# ==============================================================================

@dataclass
class Stmt(ASTNode):
    pass


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class LetStmt(Stmt):
    name: str
    is_mut: bool
    type_ann: Optional[ASTType]
    value: Expr


@dataclass
class AssignStmt(Stmt):
    lvalue: Expr
    op: str
    value: Expr


@dataclass
class ReturnStmt(Stmt):
    value: Optional[Expr]


@dataclass
class BreakStmt(Stmt):
    pass


@dataclass
class ContinueStmt(Stmt):
    pass


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_block: BlockExpr
    else_block: Union[BlockExpr, 'IfStmt', None]


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: BlockExpr


@dataclass
class CriticalSectionStmt(Stmt):
    body: BlockExpr


# ==============================================================================
# 5. DECLARATIONS (Module Items)
# ==============================================================================

@dataclass
class Item(ASTNode):
    pass


@dataclass
class UseDecl(Item):
    path: QualifiedNameExpr
    alias: Optional[str]
    is_wildcard: bool = False
    use_list: list[str] = field(default_factory=list)


@dataclass
class FieldDecl:
    name: str
    type_ann: ASTType


@dataclass
class StructDecl(Item):
    name: str
    is_pub: bool
    fields: list[FieldDecl]
    generic_params: list[str]


@dataclass
class EnumVariant:
    name: str
    tuple_types: list[ASTType] = field(default_factory=list)
    struct_fields: list[FieldDecl] = field(default_factory=list)


@dataclass
class EnumDecl(Item):
    name: str
    is_pub: bool
    variants: list[EnumVariant]
    generic_params: list[str]


@dataclass
class TypeAliasDecl(Item):
    name: str
    type_expr: ASTType
    generic_params: list[str] = field(default_factory=list)


@dataclass
class Param:
    name: str
    type_ann: ASTType


@dataclass
class ContractBlock:
    pre: list[Expr] = field(default_factory=list)
    post: list[Expr] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)


@dataclass
class EffectAnnotation:
    effects: list[str]


@dataclass
class FunctionSig(ASTNode):
    name: str
    is_pub: bool
    params: list[Param]
    ret_type: ASTType
    generic_params: list[str] = field(default_factory=list)
    contract: Optional[ContractBlock] = None
    effects: Optional[EffectAnnotation] = None


@dataclass
class FunctionDecl(Item):
    sig: FunctionSig
    body: BlockExpr


@dataclass
class TraitDecl(Item):
    name: str
    is_pub: bool
    items: list[Union[FunctionSig, TypeAliasDecl]]
    generic_params: list[str] = field(default_factory=list)
    trait_bounds: list[QualifiedNameExpr] = field(default_factory=list)


@dataclass
class ImplDecl(Item):
    type_expr: ASTType
    trait_name: Optional[QualifiedNameExpr]
    functions: list[FunctionDecl]
    generic_params: list[str] = field(default_factory=list)


@dataclass
class LowerStructField:
    name: str
    type_ann: ASTType
    offset: int
    is_volatile: bool


@dataclass
class LowerStructDecl(Item):
    name: str
    target: str
    fields: list[LowerStructField]


@dataclass
class ConstDecl(Item):
    name: str
    is_pub: bool
    type_ann: ASTType
    value: Expr

@dataclass
class StaticDecl(Item):
    name: str
    is_pub: bool
    is_mut: bool
    type_ann: ASTType
    value: Expr

@dataclass
class LowerConstDecl(Item):
    name: str
    type_ann: ASTType
    target: str
    address: int


@dataclass
class DictionaryBlock(Item):
    """Đại diện cho @context, @platform, @trace."""
    kind: str  # '@context', '@platform', '@trace'
    fields: dict[str, Union[LiteralExpr, QualifiedNameExpr, list[str]]]


@dataclass
class ASTModule(ASTNode):
    name: QualifiedNameExpr
    items: list[Item]
