"""Incremental Compilation — Phase 9.

Implement theo Spec `docs/copl/11_incremental_compilation.md`:
- ChangeDetector: phát hiện file thay đổi qua SHA256 hash
- CompileCache: SQLite cache cho SIR/diagnostics/API hash
- IncrementalScheduler: tính recompile set dựa dependency graph
- PublicAPIExtractor: hash public API để phát hiện API_CHANGED vs BODY_ONLY
"""

import os
import hashlib
import json
import sqlite3
import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


class ChangeType(Enum):
    NEW = "new"
    BODY_ONLY = "body_only"
    API_CHANGED = "api_changed"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


@dataclass
class ChangeEntry:
    file_path: str
    change_type: ChangeType
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None


class PublicAPIExtractor:
    """Trích xuất Public API hash từ AST module.
    
    Public API = tập hợp signatures của tất cả pub items.
    Nếu API hash thay đổi → dependents phải recompile.
    Nếu chỉ body thay đổi → dependents safe.
    """
    
    def extract_api_hash(self, ast_module) -> str:
        """Trích xuất và hash public API từ AST module."""
        api_elements = []
        
        for item in getattr(ast_module, 'items', []):
            is_pub = getattr(item, 'is_pub', False)
            item_type = type(item).__name__
            
            if item_type == 'FunctionDecl':
                sig = item.sig
                params_str = ",".join(
                    f"{p.name}:{self._type_str(p.type_ann)}" for p in sig.params
                )
                ret_str = self._type_str(sig.ret_type) if sig.ret_type else "void"
                pub_marker = "pub:" if is_pub else ""
                api_elements.append(f"{pub_marker}fn:{sig.name}({params_str})->{ret_str}")
                
            elif item_type == 'StructDecl':
                fields_str = ",".join(
                    f"{f.name}:{self._type_str(f.type_ann)}" for f in item.fields
                )
                pub_marker = "pub:" if is_pub else ""
                api_elements.append(f"{pub_marker}struct:{item.name}{{{fields_str}}}")
                
            elif item_type == 'EnumDecl':
                variants_str = ",".join(v.name for v in item.variants)
                pub_marker = "pub:" if is_pub else ""
                api_elements.append(f"{pub_marker}enum:{item.name}{{{variants_str}}}")
                
            elif item_type == 'ConstDecl':
                type_str = self._type_str(item.type_ann) if item.type_ann else "auto"
                api_elements.append(f"const:{item.name}:{type_str}")
                
            elif item_type in ('LowerConstDecl', 'LowerStructDecl'):
                api_elements.append(f"lower:{item.name}")
        
        # Sort cho deterministic hash
        api_elements.sort()
        api_string = "|".join(api_elements)
        return hashlib.sha256(api_string.encode('utf-8')).hexdigest()[:16]
    
    def _type_str(self, type_ann) -> str:
        if type_ann is None:
            return "void"
        if hasattr(type_ann, 'name'):
            return type_ann.name
        if hasattr(type_ann, 'names'):
            return ".".join(type_ann.names)
        return "unknown"


def hash_file(filepath: str) -> str:
    """SHA256 hash nội dung file."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


class CompileCache:
    """SQLite-backed compile cache.
    
    Lưu trữ: file_hash, public_api_hash, sir_json, diagnostics, compile_time
    """
    
    def __init__(self, project_dir: str):
        cache_dir = os.path.join(project_dir, '.copl_cache')
        os.makedirs(cache_dir, exist_ok=True)
        self.db_path = os.path.join(cache_dir, 'cache.db')
        self.db = sqlite3.connect(self.db_path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                public_api_hash TEXT NOT NULL,
                sir_json TEXT,
                diagnostics_json TEXT,
                compile_time_ms REAL,
                last_compiled REAL
            )
        """)
        self.db.commit()
    
    def get_hash(self, file_path: str) -> Optional[str]:
        row = self.db.execute(
            "SELECT file_hash FROM module_cache WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row[0] if row else None
    
    def get_api_hash(self, file_path: str) -> Optional[str]:
        row = self.db.execute(
            "SELECT public_api_hash FROM module_cache WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row[0] if row else None
    
    def get_cached_sir(self, file_path: str) -> Optional[str]:
        row = self.db.execute(
            "SELECT sir_json FROM module_cache WHERE file_path = ?", (file_path,)
        ).fetchone()
        return row[0] if row else None
    
    def update(self, file_path: str, file_hash: str, api_hash: str,
               sir_json: str = "", diagnostics_json: str = "[]",
               compile_time_ms: float = 0.0):
        self.db.execute("""
            INSERT OR REPLACE INTO module_cache 
            (file_path, file_hash, public_api_hash, sir_json, diagnostics_json, compile_time_ms, last_compiled)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_path, file_hash, api_hash, sir_json, diagnostics_json,
              compile_time_ms, time.time()))
        self.db.commit()
    
    def remove(self, file_path: str):
        self.db.execute("DELETE FROM module_cache WHERE file_path = ?", (file_path,))
        self.db.commit()
    
    def all_files(self) -> List[str]:
        rows = self.db.execute("SELECT file_path FROM module_cache").fetchall()
        return [r[0] for r in rows]
    
    def is_valid(self, file_path: str) -> bool:
        """Check cache validity via file hash."""
        cached_hash = self.get_hash(file_path)
        if cached_hash is None:
            return False
        if not os.path.exists(file_path):
            return False
        return cached_hash == hash_file(file_path)
    
    def stats(self) -> dict:
        total = self.db.execute("SELECT COUNT(*) FROM module_cache").fetchone()[0]
        return {"total_cached": total, "db_path": self.db_path}
    
    def close(self):
        self.db.close()


class ChangeDetector:
    """Phát hiện file thay đổi bằng cách so sánh hash."""
    
    def __init__(self, api_extractor: Optional[PublicAPIExtractor] = None):
        self.api_extractor = api_extractor or PublicAPIExtractor()
    
    def detect_changes(self, copl_files: List[str], cache: CompileCache) -> List[ChangeEntry]:
        """So sánh file list hiện tại với cache → trả về danh sách thay đổi."""
        changes = []
        current_files = set()
        
        for filepath in copl_files:
            current_files.add(filepath)
            current_hash = hash_file(filepath)
            cached_hash = cache.get_hash(filepath)
            
            if cached_hash is None:
                # File mới
                changes.append(ChangeEntry(
                    file_path=filepath,
                    change_type=ChangeType.NEW,
                    new_hash=current_hash
                ))
            elif current_hash != cached_hash:
                # File thay đổi — cần phân loại BODY_ONLY vs API_CHANGED
                # Ở đây ta dùng đơn giản: mark là API_CHANGED
                # (Full implementation cần parse lại và so API hash)
                changes.append(ChangeEntry(
                    file_path=filepath,
                    change_type=ChangeType.API_CHANGED,
                    old_hash=cached_hash,
                    new_hash=current_hash
                ))
            # else: UNCHANGED → không thêm vào list
        
        # Phát hiện file đã bị xóa
        for cached_file in cache.all_files():
            if cached_file not in current_files:
                changes.append(ChangeEntry(
                    file_path=cached_file,
                    change_type=ChangeType.DELETED
                ))
        
        return changes
    
    def detect_with_api_check(self, copl_files: List[str], cache: CompileCache,
                               parse_fn=None) -> List[ChangeEntry]:
        """Phiên bản nâng cao — parse file để so sánh API hash."""
        changes = []
        current_files = set()
        
        for filepath in copl_files:
            current_files.add(filepath)
            current_hash = hash_file(filepath)
            cached_hash = cache.get_hash(filepath)
            
            if cached_hash is None:
                changes.append(ChangeEntry(filepath, ChangeType.NEW, new_hash=current_hash))
            elif current_hash != cached_hash:
                # Parse và so API hash
                if parse_fn:
                    try:
                        ast_node = parse_fn(filepath)
                        if ast_node:
                            new_api_hash = self.api_extractor.extract_api_hash(ast_node)
                            old_api_hash = cache.get_api_hash(filepath)
                            
                            if old_api_hash and new_api_hash == old_api_hash:
                                change_type = ChangeType.BODY_ONLY
                            else:
                                change_type = ChangeType.API_CHANGED
                        else:
                            change_type = ChangeType.API_CHANGED
                    except Exception:
                        change_type = ChangeType.API_CHANGED
                else:
                    change_type = ChangeType.API_CHANGED
                
                changes.append(ChangeEntry(filepath, change_type, cached_hash, current_hash))
        
        for cached_file in cache.all_files():
            if cached_file not in current_files:
                changes.append(ChangeEntry(cached_file, ChangeType.DELETED))
        
        return changes


class IncrementalScheduler:
    """Tính recompile set dựa trên changes + dependency graph."""
    
    def compute_recompile_set(self, changes: List[ChangeEntry],
                               dep_graph: Dict[str, List[str]]) -> Set[str]:
        """Tính tập hợp files cần recompile.
        
        Args:
            changes: Danh sách thay đổi từ ChangeDetector
            dep_graph: file → list of files that import from it (dependents)
        
        Returns:
            Set of file paths cần recompile
        """
        to_recompile: Set[str] = set()
        
        for change in changes:
            if change.change_type == ChangeType.DELETED:
                # File bị xóa → cần recompile dependents
                dependents = dep_graph.get(change.file_path, [])
                to_recompile.update(dependents)
                continue
            
            # Luôn recompile file bị thay đổi
            to_recompile.add(change.file_path)
            
            if change.change_type == ChangeType.BODY_ONLY:
                # Chỉ body thay đổi → dependents không cần recompile
                pass
            elif change.change_type in (ChangeType.API_CHANGED, ChangeType.NEW):
                # API thay đổi → cascade recompile dependents
                dependents = dep_graph.get(change.file_path, [])
                to_recompile.update(dependents)
        
        return to_recompile
    
    def compute_skip_set(self, all_files: List[str],
                          recompile_set: Set[str]) -> Set[str]:
        """Files có thể skip (dùng cache)."""
        return set(all_files) - recompile_set


@dataclass
class IncrementalResult:
    """Kết quả của incremental build."""
    total_files: int = 0
    recompiled: int = 0
    cached: int = 0
    changes: List[ChangeEntry] = field(default_factory=list)
    compile_time_ms: float = 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        if self.total_files == 0:
            return 0.0
        return self.cached / self.total_files
    
    def to_dict(self) -> dict:
        return {
            "total_files": self.total_files,
            "recompiled": self.recompiled,
            "cached": self.cached,
            "cache_hit_rate": f"{self.cache_hit_rate:.1%}",
            "compile_time_ms": round(self.compile_time_ms, 2),
            "changes": [
                {"file": c.file_path, "type": c.change_type.value}
                for c in self.changes
            ]
        }
