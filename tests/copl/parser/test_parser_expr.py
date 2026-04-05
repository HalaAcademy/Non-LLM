import pytest
from copl.lexer import Lexer
from copl.parser import Parser
from copl.parser.ast import (
    BinaryExpr, IdentifierExpr, LiteralExpr, UnaryExpr, IndexExpr, CallExpr
)

def _parse_expr(source: str):
    lexer = Lexer()
    tokens, diags = lexer.tokenize(source)
    assert not diags.has_errors()
    
    # Bỏ qua token EOF
    if tokens and tokens[-1].type.name == "EOF":
        tokens.pop()
        
    parser = Parser(tokens)
    return parser.parse_expr()

def test_pratt_literal_and_identifier():
    expr = _parse_expr("42")
    assert isinstance(expr, LiteralExpr)
    assert expr.value == "42"

    expr_id = _parse_expr("my_var")
    assert isinstance(expr_id, IdentifierExpr)
    assert expr_id.name == "my_var"

def test_pratt_binary_precedence():
    # 1 + 2 * 3 => 1 + (2 * 3)
    expr = _parse_expr("1 + 2 * 3")
    assert isinstance(expr, BinaryExpr)
    assert expr.op == "+"
    assert isinstance(expr.right, BinaryExpr)
    assert expr.right.op == "*"

def test_pratt_unary_precedence():
    # -1 + 2 => (-1) + 2
    expr = _parse_expr("-1 + 2")
    assert isinstance(expr, BinaryExpr)
    assert expr.op == "+"
    assert isinstance(expr.left, UnaryExpr)
    assert expr.left.op == "-"

def test_pratt_parentheses():
    # (1 + 2) * 3
    expr = _parse_expr("(1 + 2) * 3")
    assert isinstance(expr, BinaryExpr)
    assert expr.op == "*"
    assert isinstance(expr.left, BinaryExpr)
    assert expr.left.op == "+"

def test_pratt_postfix():
    # arr[0]()
    expr = _parse_expr("arr[0]()")
    assert isinstance(expr, CallExpr)
    assert isinstance(expr.callee, IndexExpr)
    assert isinstance(expr.callee.obj, IdentifierExpr)
    assert expr.callee.obj.name == "arr"
