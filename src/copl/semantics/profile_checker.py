"""Profile Checker — Kiểm tra ràng buộc Profile cho COPL.

Implement theo spec `docs/copl/03_effect_system.md` §3 và `docs/copl/08_module_error_handling.md` §7:
- Forbidden types per profile
- Forbidden effects per profile (delegate to EffectChecker)  
- Cross-profile call validation
- lower block chỉ valid trong embedded/kernel
"""

from dataclasses import dataclass
from typing import Set, Optional, List, Dict
from copl.semantics.effect_checker import Profile, Effect, ALLOWED_EFFECTS


# Forbidden types per profile theo Spec 02_type_system.md §5
FORBIDDEN_TYPES: Dict[Profile, Set[str]] = {
    Profile.PORTABLE: set(),  # Không cấm type, chỉ cấm effects
    Profile.EMBEDDED: {"String", "Vec", "HashMap", "Box"},  # Cấm heap-dependent types
    Profile.KERNEL:   {"String", "Vec", "HashMap"},  # Giống embedded nhưng cho phép panic
    Profile.BACKEND:  set(),  # Cho tất cả
    Profile.SCRIPTING: set(),  # Cho tất cả
}

# Profiles cho phép lower blocks
LOWER_ALLOWED_PROFILES = {Profile.EMBEDDED, Profile.KERNEL}

# Profiles cho phép panic-inducing functions
PANIC_FORBIDDEN_PROFILES = {Profile.PORTABLE, Profile.EMBEDDED}


@dataclass
class ProfileDiagnostic:
    code: str
    message: str
    line: int = 0
    col: int = 0


class ProfileChecker:
    """Bộ kiểm tra Profile constraints cho module.
    
    Kiểm tra:
    1. Forbidden types (String cấm trong embedded, etc.)
    2. Lower blocks chỉ cho phép trong embedded/kernel
    3. Panic-inducing constructs (unwrap, assert, panic) cấm trong embedded
    """
    
    def __init__(self, profile: Profile = Profile.EMBEDDED):
        self.profile = profile
        self.diagnostics: List[ProfileDiagnostic] = []
    
    def check_module(self, module_node) -> List[ProfileDiagnostic]:
        """Entry point: Kiểm tra profile constraints cho toàn bộ module."""
        self.diagnostics = []
        
        for item in getattr(module_node, 'items', []):
            item_type = type(item).__name__
            
            # Check lower blocks
            if item_type in ('LowerBlock', 'LowerConstDecl', 'LowerStructDecl'):
                self._check_lower_allowed(item)
            
            # Check function bodies for forbidden patterns    
            if item_type == 'FunctionDecl':
                self._check_function(item)
        
        return self.diagnostics
    
    def _check_lower_allowed(self, node):
        """Lower blocks chỉ valid trong embedded/kernel."""
        if self.profile not in LOWER_ALLOWED_PROFILES:
            line = getattr(node, 'line', 0)
            col = getattr(node, 'col', 0)
            name = getattr(node, 'name', '<unknown>')
            self.diagnostics.append(ProfileDiagnostic(
                code="E801",
                message=f"Lower declaration '{name}' not allowed in profile '{self.profile.value}'. "
                        f"Lower blocks require profile 'embedded' or 'kernel'.",
                line=line, col=col
            ))
    
    def _check_function(self, fn_node):
        """Kiểm tra function body cho forbidden patterns."""
        if fn_node.body:
            self._scan_for_forbidden_types(fn_node.body)
            if self.profile in PANIC_FORBIDDEN_PROFILES:
                self._scan_for_panic_patterns(fn_node.body)
    
    def _scan_for_forbidden_types(self, node):
        """Quét AST node tìm usage của forbidden types."""
        if node is None:
            return
        
        forbidden = FORBIDDEN_TYPES.get(self.profile, set())
        if not forbidden:
            return
        
        # Kiểm tra type annotations trong let statements
        node_type = type(node).__name__
        if node_type == 'LetStmt':
            type_ann = getattr(node, 'type_ann', None)
            if type_ann:
                type_name = self._extract_type_name(type_ann)
                if type_name in forbidden:
                    self.diagnostics.append(ProfileDiagnostic(
                        code="E401",
                        message=f"Type '{type_name}' not allowed in profile '{self.profile.value}'.",
                        line=getattr(node, 'line', 0),
                        col=getattr(node, 'col', 0)
                    ))
        
        # Recurse
        for attr_name in ['statements', 'items']:
            children = getattr(node, attr_name, None)
            if children and isinstance(children, (list, tuple)):
                for child in children:
                    self._scan_for_forbidden_types(child)
        
        for attr_name in ['body', 'value', 'expr', 'then_block', 'else_block']:
            child = getattr(node, attr_name, None)
            if child is not None and hasattr(child, '__class__') and child.__class__.__module__ != 'builtins':
                self._scan_for_forbidden_types(child)
    
    def _scan_for_panic_patterns(self, node):
        """Quét AST node tìm panic-inducing patterns (unwrap, expect, panic, assert)."""
        if node is None:
            return
        
        node_type = type(node).__name__
        
        # Check method calls: .unwrap(), .expect()
        if node_type == 'MethodCallExpr':
            method = getattr(node, 'method', '')
            if method in ('unwrap', 'expect'):
                self.diagnostics.append(ProfileDiagnostic(
                    code="E601",
                    message=f"Panic-inducing method '.{method}()' not allowed in profile '{self.profile.value}'.",
                    line=getattr(node, 'line', 0),
                    col=getattr(node, 'col', 0)
                ))
        
        # Check function calls: panic!(), assert!()
        if node_type == 'CallExpr':
            callee = getattr(node, 'callee', None)
            if callee and type(callee).__name__ == 'IdentifierExpr':
                if callee.name in ('panic', 'assert'):
                    self.diagnostics.append(ProfileDiagnostic(
                        code="E601",
                        message=f"Panic-inducing function '{callee.name}()' not allowed in profile '{self.profile.value}'.",
                        line=getattr(node, 'line', 0),
                        col=getattr(node, 'col', 0)
                    ))
        
        # Recurse through children
        for attr_name in ['statements', 'items', 'args']:
            children = getattr(node, attr_name, None)
            if children and isinstance(children, (list, tuple)):
                for child in children:
                    self._scan_for_panic_patterns(child)
        
        for attr_name in ['body', 'value', 'expr', 'obj', 'left', 'right',
                          'then_block', 'else_block', 'callee', 'operand']:
            child = getattr(node, attr_name, None)
            if child is not None and hasattr(child, '__class__') and child.__class__.__module__ != 'builtins':
                self._scan_for_panic_patterns(child)
    
    def _extract_type_name(self, type_ann) -> str:
        """Lấy tên type từ type annotation node."""
        if hasattr(type_ann, 'name'):
            return type_ann.name
        if hasattr(type_ann, 'names') and type_ann.names:
            return type_ann.names[-1]
        return ""
    
    def is_type_allowed(self, type_name: str) -> bool:
        """Kiểm tra type có được phép trong profile hiện tại không."""
        forbidden = FORBIDDEN_TYPES.get(self.profile, set())
        return type_name not in forbidden
    
    def is_effect_allowed(self, effect: Effect) -> bool:
        """Kiểm tra effect có được phép trong profile hiện tại không."""
        allowed = ALLOWED_EFFECTS.get(self.profile, set())
        return effect in allowed or effect == Effect.PURE
