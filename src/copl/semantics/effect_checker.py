"""Effect System — Hệ thống Hiệu ứng COPL.

Implement theo spec `docs/copl/03_effect_system.md`:
- 9 Effect types: pure, io, heap, network, fs, interrupt, register, panic, async
- Ma trận allowed_effects per profile (5 profiles)
- Transitive effect inference qua function call graph
- Annotation mismatch detection
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Set, Optional, Dict, List


class Effect(Enum):
    """9 loại hiệu ứng theo Spec §2.1"""
    PURE = "pure"
    IO = "io"
    HEAP = "heap"
    NETWORK = "network"
    FS = "fs"
    INTERRUPT = "interrupt"
    REGISTER = "register"
    PANIC = "panic"
    ASYNC = "async"


class Profile(Enum):
    """5 Profiles theo Spec 00_overview.md §5"""
    PORTABLE = "portable"
    EMBEDDED = "embedded"
    KERNEL = "kernel"
    BACKEND = "backend"
    SCRIPTING = "scripting"


# Ma trận 5×9: allowed_effects(profile) theo Spec §3
ALLOWED_EFFECTS: Dict[Profile, Set[Effect]] = {
    Profile.PORTABLE: {Effect.PURE},
    Profile.EMBEDDED: {Effect.PURE, Effect.REGISTER, Effect.INTERRUPT},
    Profile.KERNEL:   {Effect.PURE, Effect.REGISTER, Effect.INTERRUPT, Effect.PANIC},
    Profile.BACKEND:  {Effect.PURE, Effect.IO, Effect.HEAP, Effect.NETWORK, Effect.FS, Effect.PANIC, Effect.ASYNC},
    Profile.SCRIPTING: set(Effect),  # Tất cả effects đều được phép
}


@dataclass
class EffectSet:
    """Tập hợp các Effect của 1 hàm hoặc 1 module.
    
    Rule: Nếu tập rỗng → hàm là pure.
    """
    effects: Set[Effect] = field(default_factory=set)
    
    @property
    def is_pure(self) -> bool:
        return len(self.effects) == 0 or self.effects == {Effect.PURE}
    
    def add(self, effect: Effect):
        if effect != Effect.PURE:
            self.effects.add(effect)
    
    def union(self, other: 'EffectSet') -> 'EffectSet':
        return EffectSet(self.effects | other.effects)
    
    def is_subset_of(self, allowed: Set[Effect]) -> bool:
        """Kiểm tra tất cả effects có nằm trong tập allowed không."""
        non_pure = self.effects - {Effect.PURE}
        return non_pure.issubset(allowed - {Effect.PURE})
    
    def get_violations(self, allowed: Set[Effect]) -> Set[Effect]:
        """Trả về tập các effects vi phạm (không nằm trong allowed)."""
        non_pure = self.effects - {Effect.PURE}
        return non_pure - (allowed - {Effect.PURE})
    
    def __str__(self):
        if self.is_pure:
            return "[pure]"
        return f"[{', '.join(e.value for e in sorted(self.effects, key=lambda x: x.value))}]"


@dataclass 
class EffectDiagnostic:
    """Một diagnostic liên quan đến Effect System."""
    code: str       # E301, E302, E303, W302
    message: str
    function_name: str
    line: int = 0
    col: int = 0


class EffectChecker:
    """Bộ kiểm tra Effect System cho toàn bộ module.
    
    Workflow:
    1. Quét function declarations, thu thập declared effects (@effects [...])
    2. Suy luận inferred effects từ body (transitive qua function calls)
    3. So khớp declared vs inferred
    4. Kiểm tra vs profile allowed_effects
    """
    
    def __init__(self, profile: Profile = Profile.EMBEDDED):
        self.profile = profile
        self.function_effects: Dict[str, EffectSet] = {}  # fn_name -> inferred effects
        self.declared_effects: Dict[str, Optional[EffectSet]] = {}  # fn_name -> declared effects (None = not declared)
        self.diagnostics: List[EffectDiagnostic] = []
        self.module_effect_set = EffectSet()
    
    def check_module(self, module_node, symbol_table=None) -> List[EffectDiagnostic]:
        """Entry point: Kiểm tra effects cho toàn bộ module.
        
        Args:
            module_node: ASTModule node
            symbol_table: Optional symbol table from semantic analyzer
        
        Returns:
            List of EffectDiagnostics
        """
        self.diagnostics = []
        
        # Bước 1: Thu thập declared effects từ @effects annotations
        self._collect_declarations(module_node)
        
        # Bước 2: Suy luận effects từ function bodies
        self._infer_effects(module_node)
        
        # Bước 3: Validate declared vs inferred  
        self._validate_annotations()
        
        # Bước 4: Validate effects vs profile
        self._validate_profile()
        
        # Tính module-level effect set (union of all functions)
        for fn_name, es in self.function_effects.items():
            self.module_effect_set = self.module_effect_set.union(es)
        
        return self.diagnostics
    
    def _collect_declarations(self, module_node):
        """Pass 1: Thu thập @effects annotations từ function declarations."""
        for item in getattr(module_node, 'items', []):
            item_type = type(item).__name__
            
            if item_type == 'FunctionDecl':
                fn_name = item.sig.name
                effects_ann = getattr(item.sig, 'effects', None) or getattr(item, 'effects', None)
                
                if effects_ann and isinstance(effects_ann, (list, tuple)) and len(effects_ann) > 0:
                    es = EffectSet()
                    for eff_str in effects_ann:
                        try:
                            es.add(Effect(eff_str))
                        except ValueError:
                            pass  # Ignore unknown effects for now
                    self.declared_effects[fn_name] = es
                else:
                    self.declared_effects[fn_name] = None  # Not declared
                    
            elif item_type in ('LowerBlock', 'LowerConstDecl', 'LowerStructDecl'):
                # lower declarations tự động có effect [register]
                fn_name = getattr(item, 'name', None)
                if fn_name:
                    es = EffectSet()
                    es.add(Effect.REGISTER)
                    self.declared_effects[fn_name] = es
                    self.function_effects[fn_name] = es
    
    def _infer_effects(self, module_node):
        """Pass 2: Suy luận effects từ function bodies.
        
        Hiện tại: Heuristic-based inference.
        - Tìm call expressions → nếu callee đã có known effects, propagate.
        - Tìm các pattern specific: lower blocks → register.
        """
        for item in getattr(module_node, 'items', []):
            item_type = type(item).__name__
            
            if item_type == 'FunctionDecl':
                fn_name = item.sig.name
                inferred = EffectSet()
                
                # Duyệt body tìm call expressions
                if item.body:
                    self._infer_from_body(item.body, inferred)
                
                self.function_effects[fn_name] = inferred
    
    def _infer_from_body(self, body_node, effect_set: EffectSet):
        """Recursive inference từ AST body node."""
        if body_node is None:
            return
            
        node_type = type(body_node).__name__
        
        # Nếu là call expression → kiểm tra callee effects
        if node_type == 'CallExpr':
            callee = getattr(body_node, 'callee', None)
            if callee:
                callee_name = None
                if type(callee).__name__ == 'IdentifierExpr':
                    callee_name = callee.name
                elif type(callee).__name__ == 'QualifiedNameExpr':
                    callee_name = callee.names[-1] if callee.names else None
                
                if callee_name and callee_name in self.function_effects:
                    # Transitive propagation: callee hiệu ứng → caller
                    callee_effects = self.function_effects[callee_name]
                    for eff in callee_effects.effects:
                        effect_set.add(eff)
            
            # Recurse into call args
            for arg in getattr(body_node, 'args', []):
                self._infer_from_body(arg, effect_set)
                
        # Duyệt children chung
        for attr_name in ['statements', 'items']:
            children = getattr(body_node, attr_name, None)
            if children and isinstance(children, (list, tuple)):
                for child in children:
                    self._infer_from_body(child, effect_set)
        
        # Duyệt single-child attributes
        for attr_name in ['expr', 'value', 'body', 'left', 'right', 'obj', 'operand',
                          'then_block', 'else_block', 'condition']:
            child = getattr(body_node, attr_name, None)
            if child is not None and hasattr(child, '__class__') and child.__class__.__module__ != 'builtins':
                self._infer_from_body(child, effect_set)
    
    def _validate_annotations(self):
        """Pass 3: So sánh declared vs inferred effects."""
        for fn_name, declared in self.declared_effects.items():
            if declared is None:
                continue  # Không khai báo → skip
                
            inferred = self.function_effects.get(fn_name, EffectSet())
            
            # E303: Khai báo pure nhưng có side effect
            if declared.is_pure and not inferred.is_pure:
                self.diagnostics.append(EffectDiagnostic(
                    code="E303",
                    message=f"Function '{fn_name}' declared as @effects [pure] but uses effects: {inferred}",
                    function_name=fn_name
                ))
            
            # W302: Inferred effects vượt declared
            if not inferred.is_pure:
                extra = inferred.effects - declared.effects - {Effect.PURE}
                if extra:
                    self.diagnostics.append(EffectDiagnostic(
                        code="W302",
                        message=f"Function '{fn_name}' uses effect(s) {{{', '.join(e.value for e in extra)}}} not listed in @effects",
                        function_name=fn_name
                    ))
    
    def _validate_profile(self):
        """Pass 4: Kiểm tra effects vs profile allowed_effects."""
        allowed = ALLOWED_EFFECTS.get(self.profile, set())
        
        for fn_name, es in self.function_effects.items():
            violations = es.get_violations(allowed)
            if violations:
                self.diagnostics.append(EffectDiagnostic(
                    code="E301",
                    message=f"Effect(s) {{{', '.join(e.value for e in violations)}}} not allowed in profile '{self.profile.value}' (function '{fn_name}')",
                    function_name=fn_name
                ))
    
    def get_function_effects(self, fn_name: str) -> EffectSet:
        return self.function_effects.get(fn_name, EffectSet())
    
    def get_module_effects(self) -> EffectSet:
        return self.module_effect_set
