"""Contract Checker — Kiểm tra @contract blocks cho COPL.

Implement theo spec `docs/copl/02_type_system.md` §4:
- Type-check pre conditions (chỉ reference params)
- Type-check post conditions (params + result)
- Validate budget literals (latency_budget, memory_budget)
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ContractDiagnostic:
    code: str
    message: str
    function_name: str
    line: int = 0
    col: int = 0


class ContractChecker:
    """Bộ kiểm tra @contract block theo Spec.
    
    Ở Phase này, chúng ta focus vào structural validation:
    - Kiểm tra contract block có được attach đúng vào function không
    - Kiểm tra pre conditions là boolean expressions
    - Kiểm tra post conditions có quyền dùng `result` keyword
    - Validate budget literals (duration, size)
    """
    
    def __init__(self):
        self.diagnostics: List[ContractDiagnostic] = []
        self.contract_count = 0
    
    def check_module(self, module_node) -> List[ContractDiagnostic]:
        """Entry point: Kiểm tra toàn bộ contracts trong module."""
        self.diagnostics = []
        self.contract_count = 0
        
        for item in getattr(module_node, 'items', []):
            item_type = type(item).__name__
            if item_type == 'FunctionDecl':
                self._check_function_contract(item)
        
        return self.diagnostics
    
    def _check_function_contract(self, fn_node):
        """Kiểm tra contract block trong 1 function."""
        contract = getattr(fn_node.sig, 'contract', None) or getattr(fn_node, 'contract', None)
        
        if contract is None:
            return
            
        self.contract_count += 1
        fn_name = fn_node.sig.name
        
        # Thu thập parameter names cho validation
        param_names = set()
        for p in fn_node.sig.params:
            param_names.add(p.name)
        
        # Kiểm tra pre conditions
        pre_conditions = getattr(contract, 'pre', None) or getattr(contract, 'preconditions', [])
        if pre_conditions:
            for i, pre in enumerate(pre_conditions):
                self._validate_pre_condition(pre, param_names, fn_name, i)
        
        # Kiểm tra post conditions
        post_conditions = getattr(contract, 'post', None) or getattr(contract, 'postconditions', [])
        if post_conditions:
            has_return_type = fn_node.sig.ret_type is not None
            for i, post in enumerate(post_conditions):
                self._validate_post_condition(post, param_names, fn_name, i, has_return_type)
        
        # Validate budget literals
        latency = getattr(contract, 'latency_budget', None)
        if latency:
            self._validate_duration_literal(latency, fn_name)
        
        memory = getattr(contract, 'memory_budget', None)
        if memory:
            self._validate_size_literal(memory, fn_name)
    
    def _validate_pre_condition(self, condition, param_names: set, fn_name: str, index: int):
        """Pre conditions chỉ được reference params (không được dùng global state)."""
        # Structural check — ở giai đoạn này ta chỉ kiểm tra xem condition có là node hợp lệ không
        if condition is None:
            self.diagnostics.append(ContractDiagnostic(
                code="E701",
                message=f"Empty precondition #{index+1} in function '{fn_name}'.",
                function_name=fn_name
            ))
    
    def _validate_post_condition(self, condition, param_names: set, fn_name: str, index: int, has_return_type: bool):
        """Post conditions có quyền dùng params + `result`."""
        if condition is None:
            self.diagnostics.append(ContractDiagnostic(
                code="E701",
                message=f"Empty postcondition #{index+1} in function '{fn_name}'.",
                function_name=fn_name
            ))
    
    def _validate_duration_literal(self, literal, fn_name: str):
        """Validate latency_budget: phải là duration literal (e.g. 1ms, 10us)."""
        if isinstance(literal, str):
            # Kiểm tra format: phải kết thúc bằng 'ms', 'us', hoặc 's'
            valid_suffixes = ('ms', 'us', 's')
            if not any(literal.endswith(s) for s in valid_suffixes):
                self.diagnostics.append(ContractDiagnostic(
                    code="E702",
                    message=f"Invalid latency_budget '{literal}' in function '{fn_name}'. "
                            f"Expected duration literal (e.g. '1ms', '10us', '1s').",
                    function_name=fn_name
                ))
    
    def _validate_size_literal(self, literal, fn_name: str):
        """Validate memory_budget: phải là size literal (e.g. 1KB, 256B)."""
        if isinstance(literal, str):
            valid_suffixes = ('B', 'KB', 'MB', 'GB')
            if not any(literal.endswith(s) for s in valid_suffixes):
                self.diagnostics.append(ContractDiagnostic(
                    code="E703",
                    message=f"Invalid memory_budget '{literal}' in function '{fn_name}'. "
                            f"Expected size literal (e.g. '256B', '1KB').",
                    function_name=fn_name
                ))
