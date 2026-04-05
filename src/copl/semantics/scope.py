"""Trình quản lý Scope, Symbol lưu trữ dữ liệu Biến, Hàm, Struct."""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional, Dict

from copl.semantics.types import BaseType

class SymbolKind(Enum):
    VARIABLE = auto()     # let x; params
    FUNCTION = auto()     # fn run()
    STRUCT = auto()       # struct App
    ENUM = auto()         # enum Direct
    VARIANT = auto()      # Ok, North
    CONSTANT = auto()     # const PI / lower_const
    MODULE = auto()       # module std / mod logic;

@dataclass
class Symbol:
    name: str # Định danh gốc
    kind: SymbolKind
    type_info: Optional[BaseType] = None
    is_mut: bool = False
    
    # Có thể lưu trữ metadata của Node AST (dành cho diagnostic báo dòng lỗi ở code cũ)
    node: Optional[object] = None # Tham chiếu tới Node gốc sinh ra symbol này

class Scope:
    """Tầm vực hoạt động của scope. Tra cứu Local rồi tới Global."""
    def __init__(self, parent: Optional['Scope'] = None, name: str = "local"):
        self.parent = parent
        self.name = name
        self.symbols: Dict[str, Symbol] = {}
        
    def define(self, sym: Symbol) -> bool:
        """Định nghĩa symbol mới ở current scope. Trả về False nếu bị trùng."""
        if sym.name in self.symbols:
            return False
        self.symbols[sym.name] = sym
        return True
        
    def resolve(self, name: str, current_only: bool = False) -> Optional[Symbol]:
        """Lookup symbol theo chuỗi tên."""
        # Handle lookup ngay tại block này
        if name in self.symbols:
            return self.symbols[name]
        
        # Nếu ko tìm thấy, ngước lên scope cha
        if not current_only and self.parent is not None:
            return self.parent.resolve(name)
            
        return None

class SymbolTable:
    """Quản lý các đối tượng Scope tập trung."""
    def __init__(self):
        # Scope cao nhất để nhét các builtin type
        self.global_scope = Scope(name="global")
        self.current_scope = self.global_scope
        
        self._init_builtins()

    def _init_builtins(self):
        from copl.semantics.types import PrimitiveType
        # Đưa các Built-in System Entity vào map
        # VD: Các lệnh / struct luôn truy cập được
        pass
        
    def enter_scope(self, name: str = "block") -> Scope:
        """Mở 1 block scope con."""
        new_scope = Scope(parent=self.current_scope, name=name)
        self.current_scope = new_scope
        return new_scope
        
    def exit_scope(self):
        """Đóng block con và trỏ về cha."""
        if self.current_scope.parent is not None:
            self.current_scope = self.current_scope.parent

    def define(self, sym: Symbol) -> bool:
        """Chặn lối tắt gọi `define` thẳng từ table."""
        return self.current_scope.define(sym)

    def resolve(self, name: str, current_only: bool = False) -> Optional[Symbol]:
        return self.current_scope.resolve(name, current_only)
