"""SIR Data Model — Các data class biểu diễn Semantic IR.

Implement theo Spec `docs/copl/04_sir_schema.md`:
- SIRWorkspace: Root container
- SIRModule: Per-module representation
- SIRFunction, SIRStruct, SIREnum, SIRTrait
- SIRStateMachine, SIRRequirement, SIRTest, SIRDecision, SIRWorkitem
- Computed properties: effect_set, risk_score, trace_coverage
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List, Set, Any
import json


@dataclass
class SIRField:
    name: str
    type_name: str
    is_volatile: bool = False


@dataclass
class SIRParam:
    name: str
    type_name: str


@dataclass
class SIRFunction:
    name: str
    params: List[SIRParam] = field(default_factory=list)
    return_type: str = "void"
    effects: List[str] = field(default_factory=list)
    is_pub: bool = False
    has_contract: bool = False
    contract_pre: List[str] = field(default_factory=list)
    contract_post: List[str] = field(default_factory=list)
    traces: List[str] = field(default_factory=list)  # REQ IDs this fn implements
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "params": [{"name": p.name, "type": p.type_name} for p in self.params],
            "return_type": self.return_type,
            "effects": self.effects,
            "is_pub": self.is_pub,
            "has_contract": self.has_contract,
            "traces": self.traces,
        }


@dataclass
class SIRStruct:
    name: str
    fields: List[SIRField] = field(default_factory=list)
    is_pub: bool = False
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "fields": [{"name": f.name, "type": f.type_name} for f in self.fields],
            "is_pub": self.is_pub,
        }


@dataclass
class SIREnum:
    name: str
    variants: List[str] = field(default_factory=list)
    is_pub: bool = False
    
    def to_dict(self) -> dict:
        return {"name": self.name, "variants": self.variants, "is_pub": self.is_pub}


@dataclass
class SIRConstant:
    name: str
    type_name: str
    value: str
    
    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type_name, "value": self.value}


@dataclass
class SIRModule:
    """Biểu diễn 1 module COPL trong SIR."""
    name: str
    profile: str = "embedded"
    target: str = "c"
    memory_mode: str = "static"
    
    functions: List[SIRFunction] = field(default_factory=list)
    structs: List[SIRStruct] = field(default_factory=list)
    enums: List[SIREnum] = field(default_factory=list)
    constants: List[SIRConstant] = field(default_factory=list)
    
    # Dependencies
    imports_from: List[str] = field(default_factory=list)
    imported_by: List[str] = field(default_factory=list)
    
    # Effects
    effect_set: List[str] = field(default_factory=list)
    
    # Metrics
    loc: int = 0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "profile": self.profile,
            "target": self.target,
            "memory_mode": self.memory_mode,
            "functions": [f.to_dict() for f in self.functions],
            "structs": [s.to_dict() for s in self.structs],
            "enums": [e.to_dict() for e in self.enums],
            "constants": [c.to_dict() for c in self.constants],
            "imports_from": self.imports_from,
            "imported_by": self.imported_by,
            "effect_set": self.effect_set,
            "metrics": {
                "function_count": len(self.functions),
                "struct_count": len(self.structs),
                "enum_count": len(self.enums),
                "loc": self.loc,
            }
        }
    
    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class DependencyEdge:
    from_module: str
    to_module: str
    edge_type: str = "imports"
    
    def to_dict(self) -> dict:
        return {"from": self.from_module, "to": self.to_module, "type": self.edge_type}


@dataclass
class SIRWorkspace:
    """Root container — đại diện toàn bộ project."""
    modules: Dict[str, SIRModule] = field(default_factory=dict)
    dependency_edges: List[DependencyEdge] = field(default_factory=list)
    
    # Computed
    topological_order: List[str] = field(default_factory=list)
    has_cycles: bool = False
    
    def add_module(self, module: SIRModule):
        self.modules[module.name] = module
    
    def get_module(self, name: str) -> Optional[SIRModule]:
        return self.modules.get(name)
    
    def all_modules(self) -> List[SIRModule]:
        return list(self.modules.values())
    
    def compute_dependency_graph(self):
        """Tính toán dependency graph từ imports."""
        self.dependency_edges = []
        for mod in self.modules.values():
            for dep in mod.imports_from:
                self.dependency_edges.append(DependencyEdge(
                    from_module=mod.name, 
                    to_module=dep
                ))
        
        # Simple topological sort (Kahn's algorithm)
        self._topological_sort()
    
    def _topological_sort(self):
        """Kahn's algorithm cho topological sorting."""
        in_degree: Dict[str, int] = {name: 0 for name in self.modules}
        adj: Dict[str, List[str]] = {name: [] for name in self.modules}
        
        for edge in self.dependency_edges:
            if edge.to_module in adj:
                adj[edge.to_module].append(edge.from_module)
                if edge.from_module in in_degree:
                    in_degree[edge.from_module] += 1
        
        queue = [n for n, d in in_degree.items() if d == 0]
        result = []
        
        while queue:
            node = queue.pop(0)
            result.append(node)
            for neighbor in adj.get(node, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.modules):
            self.has_cycles = True
        
        self.topological_order = result
    
    def to_dict(self) -> dict:
        return {
            "$schema": "copl-sir-workspace-v1",
            "modules": {name: mod.to_dict() for name, mod in self.modules.items()},
            "dependency_graph": {
                "edges": [e.to_dict() for e in self.dependency_edges],
                "topological_order": self.topological_order,
                "has_cycles": self.has_cycles,
            },
            "summary": {
                "module_count": len(self.modules),
                "total_functions": sum(len(m.functions) for m in self.modules.values()),
                "total_structs": sum(len(m.structs) for m in self.modules.values()),
            }
        }
    
    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
