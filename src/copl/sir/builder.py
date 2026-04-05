"""SIR Builder — Xây dựng SIR từ AST đã phân tích.

Pipeline: AST (parsed) → SIRBuilder → SIRWorkspace
"""

from copl.sir.model import (
    SIRWorkspace, SIRModule, SIRFunction, SIRStruct, SIREnum,
    SIRConstant, SIRField, SIRParam
)
from copl.parser import ast


class SIRBuilder:
    """Chuyển đổi AST Module → SIR Module."""
    
    def __init__(self):
        self.workspace = SIRWorkspace()
    
    def build_module(self, ast_module: ast.ASTModule, profile: str = "embedded") -> SIRModule:
        """Xây dựng SIR từ 1 AST Module."""
        # Module name
        if hasattr(ast_module.name, 'names'):
            mod_name = ".".join(ast_module.name.names)
        else:
            mod_name = str(ast_module.name)
        
        sir_module = SIRModule(name=mod_name, profile=profile)
        
        for item in ast_module.items:
            item_type = type(item).__name__
            
            if item_type == 'FunctionDecl':
                sir_fn = self._build_function(item)
                sir_module.functions.append(sir_fn)
                
            elif item_type == 'StructDecl':
                sir_struct = self._build_struct(item)
                sir_module.structs.append(sir_struct)
                
            elif item_type == 'LowerStructDecl':
                sir_struct = self._build_struct(item)
                sir_module.structs.append(sir_struct)
                
            elif item_type == 'EnumDecl':
                sir_enum = self._build_enum(item)
                sir_module.enums.append(sir_enum)
                
            elif item_type == 'ConstDecl':
                sir_const = self._build_const(item)
                sir_module.constants.append(sir_const)
                
            elif item_type == 'LowerConstDecl':
                sir_const = SIRConstant(
                    name=item.name,
                    type_name=self._extract_type_name(item.type_ann),
                    value=str(getattr(item, 'address', ''))
                )
                sir_module.constants.append(sir_const)
                sir_module.effect_set = list(set(sir_module.effect_set + ["register"]))
                
            elif item_type == 'UseDecl':
                path = getattr(item, 'path', None)
                if path and hasattr(path, 'names'):
                    dep_module = ".".join(path.names[:-1]) if len(path.names) > 1 else path.names[0]
                    if dep_module not in sir_module.imports_from:
                        sir_module.imports_from.append(dep_module)
        
        self.workspace.add_module(sir_module)
        return sir_module
    
    def _build_function(self, fn_node) -> SIRFunction:
        """Build SIR Function from AST FunctionDecl."""
        sig = fn_node.sig
        
        params = []
        for p in sig.params:
            params.append(SIRParam(
                name=p.name,
                type_name=self._extract_type_name(p.type_ann)
            ))
        
        ret_type = self._extract_type_name(sig.ret_type) if sig.ret_type else "void"
        
        effects = []
        eff_ann = getattr(sig, 'effects', None) or getattr(fn_node, 'effects', None)
        if eff_ann and isinstance(eff_ann, (list, tuple)):
            effects = list(eff_ann)
        
        has_contract = hasattr(fn_node, 'contract') and fn_node.contract is not None
        
        return SIRFunction(
            name=sig.name,
            params=params,
            return_type=ret_type,
            effects=effects,
            is_pub=getattr(fn_node, 'is_pub', False),
            has_contract=has_contract,
        )
    
    def _build_struct(self, struct_node) -> SIRStruct:
        fields = []
        for f in struct_node.fields:
            fields.append(SIRField(
                name=f.name,
                type_name=self._extract_type_name(f.type_ann),
                is_volatile=getattr(f, 'is_volatile', False)
            ))
        return SIRStruct(
            name=struct_node.name,
            fields=fields,
            is_pub=getattr(struct_node, 'is_pub', False)
        )
    
    def _build_enum(self, enum_node) -> SIREnum:
        variants = [v.name for v in enum_node.variants]
        return SIREnum(
            name=enum_node.name,
            variants=variants,
            is_pub=getattr(enum_node, 'is_pub', False)
        )
    
    def _build_const(self, const_node) -> SIRConstant:
        return SIRConstant(
            name=const_node.name,
            type_name=self._extract_type_name(const_node.type_ann),
            value=str(getattr(const_node, 'value', ''))
        )
    
    def _extract_type_name(self, type_ann) -> str:
        if type_ann is None:
            return "void"
        if hasattr(type_ann, 'name'):
            return type_ann.name
        if hasattr(type_ann, 'names'):
            return ".".join(type_ann.names)
        return "unknown"
    
    def build_workspace(self) -> SIRWorkspace:
        """Finalize: compute dependency graph."""
        self.workspace.compute_dependency_graph()
        return self.workspace
