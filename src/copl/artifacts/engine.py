"""Artifact Engine — Sinh artifacts từ SIR.

Implement theo Spec `docs/copl/10_artifact_engine.md`:
- Summary Cards (JSON per module)
- Dependency Graph (JSON)
- Project Summary
- AI Bundle directory structure
"""

import os
import json
from datetime import datetime, timezone
from typing import List
from copl.sir.model import SIRWorkspace, SIRModule


class ArtifactEngine:
    """Sinh artifacts từ SIR workspace."""
    
    COMPILER_VERSION = "copc-0.2.0"
    
    def __init__(self, workspace: SIRWorkspace):
        self.workspace = workspace
    
    def emit_all(self, output_dir: str) -> List[str]:
        """Sinh toàn bộ artifacts vào output_dir.
        
        Returns:
            List of generated file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        generated = []
        
        # 1. Summary cards
        cards_dir = os.path.join(output_dir, "summary_cards")
        os.makedirs(cards_dir, exist_ok=True)
        for module in self.workspace.all_modules():
            card = self.build_summary_card(module)
            path = os.path.join(cards_dir, f"{module.name}.json")
            self._save_json(path, card)
            generated.append(path)
        
        # 2. Dependency graph
        graph = self.build_dependency_graph()
        path = os.path.join(output_dir, "dependency_graph.json")
        self._save_json(path, graph)
        generated.append(path)
        
        # 3. Project summary
        summary = self.build_project_summary()
        path = os.path.join(output_dir, "project_summary.json")
        self._save_json(path, summary)
        generated.append(path)
        
        # 4. Manifest
        manifest = self.build_manifest()
        path = os.path.join(output_dir, "manifest.json")
        self._save_json(path, manifest)
        generated.append(path)
        
        return generated
    
    def build_summary_card(self, module: SIRModule) -> dict:
        """Build summary card cho 1 module theo Schema Spec §2."""
        return {
            "$schema": "copl-summary-card-v1",
            "module_name": module.name,
            "profile": module.profile,
            "target": module.target,
            "memory_mode": module.memory_mode,
            "metrics": {
                "function_count": len(module.functions),
                "struct_count": len(module.structs),
                "enum_count": len(module.enums),
                "constant_count": len(module.constants),
                "loc": module.loc,
            },
            "effects": module.effect_set,
            "dependencies": {
                "imports_from": module.imports_from,
                "imported_by": module.imported_by,
            },
            "functions": [f.to_dict() for f in module.functions],
            "structs": [s.to_dict() for s in module.structs],
            "enums": [e.to_dict() for e in module.enums],
            "compiler_version": self.COMPILER_VERSION,
        }
    
    def build_dependency_graph(self) -> dict:
        """Build dependency graph JSON theo Spec §3."""
        nodes = []
        for mod in self.workspace.all_modules():
            nodes.append({
                "id": mod.name,
                "type": "module",
                "profile": mod.profile,
            })
        
        edges = [e.to_dict() for e in self.workspace.dependency_edges]
        
        return {
            "$schema": "copl-dependency-graph-v1",
            "nodes": nodes,
            "edges": edges,
            "computed": {
                "topological_order": self.workspace.topological_order,
                "has_cycles": self.workspace.has_cycles,
            }
        }
    
    def build_project_summary(self) -> dict:
        """Build project-level summary."""
        total_functions = sum(len(m.functions) for m in self.workspace.all_modules())
        total_structs = sum(len(m.structs) for m in self.workspace.all_modules())
        total_enums = sum(len(m.enums) for m in self.workspace.all_modules())
        
        all_effects = set()
        for m in self.workspace.all_modules():
            all_effects.update(m.effect_set)
        
        return {
            "$schema": "copl-project-summary-v1",
            "module_count": len(self.workspace.modules),
            "total_functions": total_functions,
            "total_structs": total_structs,
            "total_enums": total_enums,
            "all_effects": sorted(list(all_effects)),
            "has_dependency_cycles": self.workspace.has_cycles,
            "compiler_version": self.COMPILER_VERSION,
        }
    
    def build_manifest(self) -> dict:
        """Build bundle manifest."""
        return {
            "bundle_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "compiler_version": self.COMPILER_VERSION,
            "module_count": len(self.workspace.modules),
        }
    
    def _save_json(self, path: str, data: dict):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
