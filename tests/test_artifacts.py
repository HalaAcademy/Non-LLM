"""TDD Tests cho Phase 8: Artifact Engine.

Kiểm tra:
- Summary card generation (per module)
- Dependency graph JSON
- Project summary
- File I/O: toàn bộ artifacts được ghi đúng
"""
import pytest
import json
import os
import tempfile
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from copl.sir.model import SIRWorkspace, SIRModule, SIRFunction, SIRStruct, SIRField, SIRParam
from copl.artifacts.engine import ArtifactEngine


def _build_test_workspace() -> SIRWorkspace:
    ws = SIRWorkspace()
    
    m1 = SIRModule(name="mcal.can", profile="embedded", effect_set=["register", "interrupt"])
    m1.functions.append(SIRFunction(name="can_init", params=[
        SIRParam("base", "U32"), SIRParam("baud", "U32")
    ], return_type="Bool", effects=["register"]))
    m1.structs.append(SIRStruct(name="CanPdu", fields=[
        SIRField("id", "U32"), SIRField("dlc", "U8")
    ]))
    ws.add_module(m1)
    
    m2 = SIRModule(name="bsw.canif", profile="embedded", imports_from=["mcal.can"])
    m2.functions.append(SIRFunction(name="canif_transmit", return_type="Bool"))
    ws.add_module(m2)
    
    ws.compute_dependency_graph()
    return ws


# ============================================
# 1. Summary Card
# ============================================

def test_summary_card_structure():
    ws = _build_test_workspace()
    engine = ArtifactEngine(ws)
    card = engine.build_summary_card(ws.get_module("mcal.can"))
    
    assert card["$schema"] == "copl-summary-card-v1"
    assert card["module_name"] == "mcal.can"
    assert card["profile"] == "embedded"
    assert card["metrics"]["function_count"] == 1
    assert card["metrics"]["struct_count"] == 1
    assert "register" in card["effects"]

def test_summary_card_functions():
    ws = _build_test_workspace()
    engine = ArtifactEngine(ws)
    card = engine.build_summary_card(ws.get_module("mcal.can"))
    
    assert len(card["functions"]) == 1
    assert card["functions"][0]["name"] == "can_init"
    assert card["functions"][0]["return_type"] == "Bool"


# ============================================
# 2. Dependency Graph
# ============================================

def test_dependency_graph():
    ws = _build_test_workspace()
    engine = ArtifactEngine(ws)
    graph = engine.build_dependency_graph()
    
    assert graph["$schema"] == "copl-dependency-graph-v1"
    assert len(graph["nodes"]) == 2
    assert len(graph["edges"]) == 1
    assert graph["edges"][0]["from"] == "bsw.canif"
    assert graph["edges"][0]["to"] == "mcal.can"
    assert graph["computed"]["has_cycles"] is False


# ============================================
# 3. Project Summary
# ============================================

def test_project_summary():
    ws = _build_test_workspace()
    engine = ArtifactEngine(ws)
    summary = engine.build_project_summary()
    
    assert summary["module_count"] == 2
    assert summary["total_functions"] == 2
    assert summary["total_structs"] == 1
    assert "register" in summary["all_effects"]


# ============================================
# 4. File I/O — emit_all
# ============================================

def test_emit_all_creates_files():
    ws = _build_test_workspace()
    engine = ArtifactEngine(ws)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        generated = engine.emit_all(tmpdir)
        
        # Should have: 2 summary cards + dep graph + project summary + manifest = 5
        assert len(generated) == 5
        
        # Check files exist
        for path in generated:
            assert os.path.exists(path), f"File not found: {path}"
        
        # Check summary card content
        card_path = os.path.join(tmpdir, "summary_cards", "mcal.can.json")
        assert os.path.exists(card_path)
        with open(card_path) as f:
            card = json.load(f)
        assert card["module_name"] == "mcal.can"
        
        # Check manifest
        manifest_path = os.path.join(tmpdir, "manifest.json")
        with open(manifest_path) as f:
            manifest = json.load(f)
        assert manifest["module_count"] == 2
        assert manifest["bundle_version"] == "1.0"
