"""TDD Tests cho Phase 7: SIR Builder.

Kiểm tra:
- SIR data model (SIRModule, SIRFunction, SIRStruct)
- SIR Builder từ AST
- JSON serialization
- Dependency graph + topological sort
"""
import pytest
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from copl.sir.model import (
    SIRWorkspace, SIRModule, SIRFunction, SIRStruct, SIREnum,
    SIRField, SIRParam, DependencyEdge
)
from copl.sir.builder import SIRBuilder
from copl.lexer import Lexer
from copl.parser import parse


def _parse_copl(source: str):
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename="<test>")
    return ast_node


# ============================================
# 1. SIR Data Model Unit Tests
# ============================================

def test_sir_module_to_dict():
    mod = SIRModule(name="mcal.can", profile="embedded")
    mod.functions.append(SIRFunction(name="init", return_type="Bool"))
    mod.structs.append(SIRStruct(name="CanPdu", fields=[
        SIRField(name="id", type_name="U32"),
        SIRField(name="dlc", type_name="U8"),
    ]))
    
    d = mod.to_dict()
    assert d["name"] == "mcal.can"
    assert d["profile"] == "embedded"
    assert len(d["functions"]) == 1
    assert d["functions"][0]["name"] == "init"
    assert len(d["structs"]) == 1
    assert d["metrics"]["function_count"] == 1
    assert d["metrics"]["struct_count"] == 1

def test_sir_module_to_json():
    mod = SIRModule(name="mcal.can")
    j = mod.to_json()
    parsed = json.loads(j)
    assert parsed["name"] == "mcal.can"

def test_sir_workspace_add_module():
    ws = SIRWorkspace()
    m1 = SIRModule(name="mcal.can")
    m2 = SIRModule(name="bsw.canif")
    ws.add_module(m1)
    ws.add_module(m2)
    assert len(ws.all_modules()) == 2

def test_sir_workspace_dependency_graph():
    ws = SIRWorkspace()
    m1 = SIRModule(name="mcal.can")
    m2 = SIRModule(name="bsw.canif", imports_from=["mcal.can"])
    ws.add_module(m1)
    ws.add_module(m2)
    ws.compute_dependency_graph()
    
    assert len(ws.dependency_edges) == 1
    assert ws.dependency_edges[0].from_module == "bsw.canif"
    assert ws.dependency_edges[0].to_module == "mcal.can"
    assert ws.has_cycles is False

def test_sir_workspace_topological_order():
    ws = SIRWorkspace()
    m1 = SIRModule(name="mcal.can")
    m2 = SIRModule(name="bsw.canif", imports_from=["mcal.can"])
    m3 = SIRModule(name="services.vcu", imports_from=["bsw.canif"])
    ws.add_module(m1)
    ws.add_module(m2)
    ws.add_module(m3)
    ws.compute_dependency_graph()
    
    order = ws.topological_order
    assert order.index("mcal.can") < order.index("bsw.canif")
    assert order.index("bsw.canif") < order.index("services.vcu")

def test_sir_workspace_to_json():
    ws = SIRWorkspace()
    ws.add_module(SIRModule(name="mcal.can"))
    j = ws.to_json()
    parsed = json.loads(j)
    assert parsed["$schema"] == "copl-sir-workspace-v1"
    assert "mcal.can" in parsed["modules"]


# ============================================
# 2. SIR Builder Integration Tests
# ============================================

def test_sir_builder_from_ast():
    source = '''module examples.can_driver {
        struct CanPdu {
            id: U32,
            dlc: U8,
            data: [U8; 8]
        }
        
        enum CanStatus {
            Ok,
            Error,
            Timeout
        }
        
        fn can_init(base: U32, baud: U32) -> Bool {
            let status: Bool = true;
            return status;
        }
    }'''
    
    ast_node = _parse_copl(source)
    assert ast_node is not None
    
    builder = SIRBuilder()
    sir_module = builder.build_module(ast_node)
    
    assert sir_module.name == "examples.can_driver"
    assert len(sir_module.functions) == 1
    assert sir_module.functions[0].name == "can_init"
    assert sir_module.functions[0].return_type == "Bool"
    assert len(sir_module.functions[0].params) == 2
    
    assert len(sir_module.structs) == 1
    assert sir_module.structs[0].name == "CanPdu"
    assert len(sir_module.structs[0].fields) == 3
    
    assert len(sir_module.enums) == 1
    assert sir_module.enums[0].name == "CanStatus"
    assert "Ok" in sir_module.enums[0].variants

def test_sir_builder_lower_const():
    source = '''module examples.hw_defs {
        lower_const CAN1: *U32 @target c = 0x40006400;
    }'''
    
    ast_node = _parse_copl(source)
    assert ast_node is not None
    
    builder = SIRBuilder()
    sir_module = builder.build_module(ast_node)
    
    assert len(sir_module.constants) == 1
    assert sir_module.constants[0].name == "CAN1"
    assert "register" in sir_module.effect_set

def test_sir_builder_json_roundtrip():
    source = '''module examples.simple {
        fn add(a: U32, b: U32) -> U32 {
            return a + b;
        }
    }'''
    
    ast_node = _parse_copl(source)
    builder = SIRBuilder()
    builder.build_module(ast_node)
    ws = builder.build_workspace()
    
    j = ws.to_json()
    parsed = json.loads(j)
    
    assert "examples.simple" in parsed["modules"]
    mod = parsed["modules"]["examples.simple"]
    assert mod["functions"][0]["name"] == "add"
    assert mod["metrics"]["function_count"] == 1
