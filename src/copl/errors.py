"""
COPL Compiler — Error Codes and Diagnostics

Error code ranges (từ docs/copl/08_module_error_handling.md):
  E001–E099: Syntax errors (Lexer/Parser)
  E101–E199: Type errors
  E301–E399: Effect/Import errors
  E401–E499: Memory errors
  E501–E599: Module/Visibility errors
  E601–E699: Error handling violations
  E701–E799: Contract errors
  E801–E899: Lowering errors
  E901–E999: Context entity errors
  W001–W999: Warnings (non-fatal)
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"


@dataclass(frozen=True)
class SourceLocation:
    """Vị trí trong source code."""
    file: str
    line: int
    col: int
    end_line: int = 0
    end_col: int = 0

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.col}"


@dataclass
class Diagnostic:
    """
    Một lỗi hoặc cảnh báo từ compiler.

    Format output:
        src/main.copl:12:5: error [E101] Type mismatch: expected U32, found Bool
        Suggested fix: Cast với 'expr as U32'
    """
    code: str              # "E101", "W101"
    severity: Severity
    message: str
    location: SourceLocation
    suggested_fix: str = ""
    notes: list[str] | None = None

    def __str__(self) -> str:
        prefix = f"{self.location}: {self.severity.value} [{self.code}]"
        lines = [f"{prefix} {self.message}"]
        if self.suggested_fix:
            lines.append(f"  Suggested fix: {self.suggested_fix}")
        if self.notes:
            for note in self.notes:
                lines.append(f"  note: {note}")
        return "\n".join(lines)


class COPLError(Exception):
    """Base exception cho compiler-generated errors."""

    def __init__(self, diagnostic: Diagnostic) -> None:
        self.diagnostic = diagnostic
        super().__init__(str(diagnostic))


class LexError(COPLError):
    """Lỗi từ Lexer (E001, E002)."""
    pass


class ParseError(COPLError):
    """Lỗi từ Parser (E001–E099)."""
    pass


class TypeCheckError(COPLError):
    """Lỗi từ Type Checker (E101–E199)."""
    pass


class EffectError(COPLError):
    """Lỗi từ Effect Checker (E301–E399)."""
    pass


class MemoryError(COPLError):
    """Lỗi từ Memory/Profile Checker (E401–E499)."""
    pass


class ModuleError(COPLError):
    """Lỗi từ Module system (E501–E599)."""
    pass


class ContractError(COPLError):
    """Lỗi từ Contract Checker (E701–E799)."""
    pass


# ============================================================
# Error factory functions — để tạo Diagnostic nhanh
# ============================================================

def err_unexpected_token(
    found: str, expected: str, loc: SourceLocation
) -> Diagnostic:
    """E001: Unexpected token."""
    return Diagnostic(
        code="E001",
        severity=Severity.ERROR,
        message=f"Unexpected token '{found}', expected '{expected}'",
        location=loc,
        suggested_fix=f"Replace '{found}' với '{expected}'",
    )


def err_unterminated_string(loc: SourceLocation) -> Diagnostic:
    """E002: Unterminated string literal."""
    return Diagnostic(
        code="E002",
        severity=Severity.ERROR,
        message="Unterminated string literal",
        location=loc,
        suggested_fix="Thêm dấu '\"' để đóng string",
    )


def err_type_mismatch(
    expected: str, found: str, loc: SourceLocation
) -> Diagnostic:
    """E101: Type mismatch."""
    return Diagnostic(
        code="E101",
        severity=Severity.ERROR,
        message=f"Type mismatch: expected '{expected}', found '{found}'",
        location=loc,
    )


def err_unknown_type(name: str, loc: SourceLocation) -> Diagnostic:
    """E103: Unknown type."""
    return Diagnostic(
        code="E103",
        severity=Severity.ERROR,
        message=f"Unknown type '{name}'",
        location=loc,
        suggested_fix=f"Kiểm tra tên type hoặc thêm 'use' import",
    )


def err_effect_violation(
    effect: str, profile: str, loc: SourceLocation
) -> Diagnostic:
    """E301: Effect not allowed in profile."""
    return Diagnostic(
        code="E301",
        severity=Severity.ERROR,
        message=f"Effect '{effect}' không được phép trong profile '{profile}'",
        location=loc,
        suggested_fix=f"Xóa effect '{effect}' hoặc đổi profile",
    )


def err_heap_in_static(loc: SourceLocation) -> Diagnostic:
    """E401: Heap allocation in static memory mode."""
    return Diagnostic(
        code="E401",
        severity=Severity.ERROR,
        message="Heap allocation không cho phép trong memory_mode = static",
        location=loc,
        suggested_fix="Dùng static array thay vì dynamic allocation",
    )


def err_private_access(
    item: str, module: str, loc: SourceLocation
) -> Diagnostic:
    """E501: Accessing private item from outside module."""
    return Diagnostic(
        code="E501",
        severity=Severity.ERROR,
        message=f"'{item}' là private — không thể truy cập từ module ngoài '{module}'",
        location=loc,
        suggested_fix=f"Thêm 'pub' trước khai báo '{item}' nếu cần export",
    )


def err_pointer_outside_lower(loc: SourceLocation) -> Diagnostic:
    """E501: Pointer type outside lower context."""
    return Diagnostic(
        code="E501",
        severity=Severity.ERROR,
        message="Pointer type '*T' chỉ hợp lệ bên trong lower block, lower_struct, hoặc lower_const",
        location=loc,
        suggested_fix="Di chuyển khai báo vào trong lower block",
    )


def err_circular_dependency(cycle: str, loc: SourceLocation) -> Diagnostic:
    """E502: Circular module dependency."""
    return Diagnostic(
        code="E502",
        severity=Severity.ERROR,
        message=f"Circular dependency detected: {cycle}",
        location=loc,
    )


def err_cross_profile_call(
    caller_profile: str, callee_profile: str,
    forbidden_effect: str, loc: SourceLocation
) -> Diagnostic:
    """E510: Cross-profile call effect violation."""
    return Diagnostic(
        code="E510",
        severity=Severity.ERROR,
        message=(
            f"Profile '{caller_profile}' không được phép gọi function "
            f"có effect '{forbidden_effect}' (từ profile '{callee_profile}')"
        ),
        location=loc,
        suggested_fix="Kiểm tra allowed_effects matrix trong docs/copl/08_module_error_handling.md",
    )


def err_critical_section_outside_embedded(loc: SourceLocation) -> Diagnostic:
    """E503: critical_section outside embedded/kernel."""
    return Diagnostic(
        code="E503",
        severity=Severity.ERROR,
        message="'critical_section' chỉ hợp lệ trong profile = embedded hoặc kernel",
        location=loc,
    )


def warn_wildcard_import(module: str, loc: SourceLocation) -> Diagnostic:
    """W101: Wildcard import discouraged."""
    return Diagnostic(
        code="W101",
        severity=Severity.WARNING,
        message=f"Wildcard import 'use {module}.*' có thể gây shadowing không rõ ràng",
        location=loc,
        suggested_fix=f"Dùng explicit import: use {module}.{{item1, item2}}",
    )


class DiagnosticBag:
    """Thu thập nhiều diagnostics — không dừng ở lỗi đầu tiên."""

    def __init__(self) -> None:
        self._items: list[Diagnostic] = []

    def add(self, diag: Diagnostic) -> None:
        self._items.append(diag)

    def has_errors(self) -> bool:
        return any(d.severity == Severity.ERROR for d in self._items)

    def errors(self) -> list[Diagnostic]:
        return [d for d in self._items if d.severity == Severity.ERROR]

    def warnings(self) -> list[Diagnostic]:
        return [d for d in self._items if d.severity == Severity.WARNING]

    def all(self) -> list[Diagnostic]:
        return list(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def print_all(self) -> None:
        for diag in self._items:
            print(diag)
        if self.has_errors():
            n = len(self.errors())
            print(f"\n{n} error(s) found.")
