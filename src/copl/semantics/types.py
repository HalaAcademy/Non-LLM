"""Hệ thống Type logic cho phân tích ngữ nghĩa (Semantic Analyzer).

File này chứa cấu trúc biểu diễn kiểu dữ liệu cho COPL (Type Representation).
Nó khác với `ast.py` ở chỗ: `ast.py` chứa Type do người dùng "nhập vào" (vd: chuỗi "U32"),
còn file này chứa kiểu dữ liệu Lõi (vd: đối tượng `PrimitiveType(U32)`) đã được Semantic
Analyzer validation và binding.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Union

class BaseType:
    """Class nội tại biểu diễn cấu trúc gốc của 1 kiểu dữ liệu."""
    def is_assignable_to(self, other: 'BaseType') -> bool:
        """Kiểm tra có thể gán giá trị kiểu này cho kiểu kia không."""
        # Mặc định phải cùng hệ type
        return self == other
        
    def __eq__(self, other):
        return type(self) == type(other)
        
    def __str__(self):
        return "UnknownType"

@dataclass
class PrimitiveType(BaseType):
    """Kiểu dữ liệu cơ bản: U8, I8, F32, Bool, vv..."""
    name: str  # Ví dụ: "U32", "Bool"

    def is_assignable_to(self, other: 'BaseType') -> bool:
        if not isinstance(other, PrimitiveType):
            return False
        # Chặn ngặt nghèo, cùng PrimitiveType mới assignable 
        # (Chưa hỗ trợ implicit cast)
        return self.name == other.name
        
    def __eq__(self, other):
        return isinstance(other, PrimitiveType) and self.name == other.name

    def __str__(self):
        return self.name

@dataclass
class ArrayType(BaseType):
    """Kiểu mảng: [U8; 8]"""
    element_type: BaseType
    size: Optional[int] = None # Size cố định hoặc là None nếu là slice
    
    def is_assignable_to(self, other: 'BaseType') -> bool:
        if not isinstance(other, ArrayType):
            return False
        if not self.element_type.is_assignable_to(other.element_type):
            return False
        if other.size is not None and self.size != other.size:
            # Mảng fix-size phải cùng size
            return False
        return True
        
    def __eq__(self, other):
        return isinstance(other, ArrayType) and self.element_type == other.element_type and self.size == other.size

    def __str__(self):
        size_str = str(self.size) if self.size is not None else ""
        return f"[{str(self.element_type)}; {size_str}]"

@dataclass
class TupleType(BaseType):
    """Kiểu tuple (U32, String)"""
    element_types: List[BaseType]

    def is_assignable_to(self, other: 'BaseType') -> bool:
        if not isinstance(other, TupleType) or len(self.element_types) != len(other.element_types):
            return False
        return all(t1.is_assignable_to(t2) for t1, t2 in zip(self.element_types, other.element_types))
        
    def __eq__(self, other):
        if not isinstance(other, TupleType): return False
        return self.element_types == other.element_types
        
    def __str__(self):
        return f"({' ,'.join(str(t) for t in self.element_types)})"

@dataclass
class StructType(BaseType):
    """Biểu diễn kiểu của 1 khai báo Struct."""
    name: str # Tên Struct như 'CanPdu'
    
    # Ở Type Checking, có thể cần link thẳng StructType tới StructDecl Node trong AST.
    # Ta có thể thiết lập tham chiếu weak ref hoặc chỉ dựa vào Scope.
    
    def is_assignable_to(self, other: 'BaseType') -> bool:
        return isinstance(other, StructType) and self.name == other.name

    def __eq__(self, other):
        return isinstance(other, StructType) and self.name == other.name

    def __str__(self):
        return self.name

@dataclass
class EnumType(BaseType):
    """Biểu diễn kiểu của 1 khai báo Enum."""
    name: str # Tên Enum như 'Direction'

    def is_assignable_to(self, other: 'BaseType') -> bool:
        return isinstance(other, EnumType) and self.name == other.name

    def __eq__(self, other):
        return isinstance(other, EnumType) and self.name == other.name

    def __str__(self):
        return self.name

@dataclass
class PointerType(BaseType):
    """Type C-Pointer (chỉ dành cho code `lower @target`)."""
    target_type: BaseType
    is_mut: bool = False

    def is_assignable_to(self, other: 'BaseType') -> bool:
        if not isinstance(other, PointerType):
            return False
        if self.is_mut and not other.is_mut:
            return False # Không thể gán ptr mut cho non-mut ngầm định nếu ngặt nghèo (trong C thì ngược lại, nhưng thiết kế an toàn COPL sẽ khác)
        return self.target_type.is_assignable_to(other.target_type)

    def __str__(self):
        prefix = "*mut " if self.is_mut else "*const "
        return f"{prefix}{str(self.target_type)}"

class VoidType(BaseType):
    """Kiểu Unit/Void (Hàm không trả về gì)."""
    def __str__(self):
        return "()"

class BottomType(BaseType):
    """Kiểu Never/Bottom Type (v.d: Return expression return type này vì nó dừng cờ chạy)."""
    
    def is_assignable_to(self, other: 'BaseType') -> bool:
        # Bottom type (`!`) có thể được ép kiểu ẩn sang mọi type khác (ví dụ: gán let x: U32 = return 5;)
        return True
        
    def __str__(self):
        return "!"
        
@dataclass
class GenericType(BaseType):
    """Result<T, E> hoặc std::vec::Vec<T>"""
    base: str # Result
    args: List[BaseType]
    
    def __str__(self):
        return f"{self.base}<{', '.join(str(x) for x in self.args)}>"
        
    def is_assignable_to(self, other: 'BaseType') -> bool:
        if not isinstance(other, GenericType) or self.base != other.base:
            return False
        if len(self.args) != len(other.args): return False
        return all(t1.is_assignable_to(t2) for t1, t2 in zip(self.args, other.args))
        
    def __eq__(self, other):
        if not isinstance(other, GenericType): return False
        return self.base == other.base and self.args == other.args
