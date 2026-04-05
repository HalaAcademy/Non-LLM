"""TDD Tests cho Phase 9: Incremental Compilation.

Kiểm tra:
- CompileCache: CRUD operations, SQLite persistence
- ChangeDetector: NEW/CHANGED/DELETED detection
- IncrementalScheduler: recompile set computation
- PublicAPIExtractor: API hash stability
"""
import pytest
import os
import sys
import tempfile
import shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from copl.incremental import (
    CompileCache, ChangeDetector, ChangeType, ChangeEntry,
    IncrementalScheduler, PublicAPIExtractor, IncrementalResult,
    hash_file
)


# ============================================
# 1. hash_file utility
# ============================================

def test_hash_file_deterministic(tmp_path):
    f = tmp_path / "test.copl"
    f.write_text("module examples.test {}")
    h1 = hash_file(str(f))
    h2 = hash_file(str(f))
    assert h1 == h2
    assert len(h1) == 64  # SHA256 hex

def test_hash_file_changes_on_modify(tmp_path):
    f = tmp_path / "test.copl"
    f.write_text("version 1")
    h1 = hash_file(str(f))
    f.write_text("version 2")
    h2 = hash_file(str(f))
    assert h1 != h2


# ============================================
# 2. CompileCache
# ============================================

def test_cache_create_db(tmp_path):
    cache = CompileCache(str(tmp_path))
    assert os.path.exists(os.path.join(str(tmp_path), '.copl_cache', 'cache.db'))
    cache.close()

def test_cache_update_and_get(tmp_path):
    cache = CompileCache(str(tmp_path))
    cache.update("foo.copl", "abc123", "api_hash_1", '{"name":"foo"}')
    
    assert cache.get_hash("foo.copl") == "abc123"
    assert cache.get_api_hash("foo.copl") == "api_hash_1"
    assert cache.get_cached_sir("foo.copl") == '{"name":"foo"}'
    cache.close()

def test_cache_is_valid(tmp_path):
    f = tmp_path / "test.copl"
    f.write_text("module examples.valid {}")
    
    cache = CompileCache(str(tmp_path))
    file_hash = hash_file(str(f))
    cache.update(str(f), file_hash, "api1")
    
    assert cache.is_valid(str(f)) is True
    
    # Modify file → cache invalid
    f.write_text("module examples.modified {}")
    assert cache.is_valid(str(f)) is False
    cache.close()

def test_cache_all_files(tmp_path):
    cache = CompileCache(str(tmp_path))
    cache.update("a.copl", "h1", "a1")
    cache.update("b.copl", "h2", "a2")
    
    files = cache.all_files()
    assert len(files) == 2
    assert "a.copl" in files
    assert "b.copl" in files
    cache.close()

def test_cache_remove(tmp_path):
    cache = CompileCache(str(tmp_path))
    cache.update("a.copl", "h1", "a1")
    cache.remove("a.copl")
    assert cache.get_hash("a.copl") is None
    cache.close()

def test_cache_stats(tmp_path):
    cache = CompileCache(str(tmp_path))
    cache.update("a.copl", "h1", "a1")
    cache.update("b.copl", "h2", "a2")
    stats = cache.stats()
    assert stats["total_cached"] == 2
    cache.close()


# ============================================
# 3. ChangeDetector
# ============================================

def test_detect_new_file(tmp_path):
    f = tmp_path / "new.copl"
    f.write_text("module examples.new {}")
    
    cache = CompileCache(str(tmp_path))
    detector = ChangeDetector()
    changes = detector.detect_changes([str(f)], cache)
    
    assert len(changes) == 1
    assert changes[0].change_type == ChangeType.NEW
    cache.close()

def test_detect_unchanged_file(tmp_path):
    f = tmp_path / "stable.copl"
    f.write_text("module examples.stable {}")
    
    cache = CompileCache(str(tmp_path))
    cache.update(str(f), hash_file(str(f)), "api1")
    
    detector = ChangeDetector()
    changes = detector.detect_changes([str(f)], cache)
    
    # No changes detected
    assert len(changes) == 0
    cache.close()

def test_detect_modified_file(tmp_path):
    f = tmp_path / "mod.copl"
    f.write_text("version 1")
    
    cache = CompileCache(str(tmp_path))
    cache.update(str(f), hash_file(str(f)), "api1")
    
    f.write_text("version 2")
    
    detector = ChangeDetector()
    changes = detector.detect_changes([str(f)], cache)
    
    assert len(changes) == 1
    assert changes[0].change_type == ChangeType.API_CHANGED
    cache.close()

def test_detect_deleted_file(tmp_path):
    cache = CompileCache(str(tmp_path))
    cache.update("gone.copl", "h1", "a1")
    
    detector = ChangeDetector()
    changes = detector.detect_changes([], cache)  # file not in list
    
    assert len(changes) == 1
    assert changes[0].change_type == ChangeType.DELETED
    cache.close()


# ============================================
# 4. IncrementalScheduler
# ============================================

def test_scheduler_body_only_no_cascade():
    scheduler = IncrementalScheduler()
    changes = [ChangeEntry("a.copl", ChangeType.BODY_ONLY)]
    dep_graph = {"a.copl": ["b.copl", "c.copl"]}
    
    recompile = scheduler.compute_recompile_set(changes, dep_graph)
    
    # BODY_ONLY → only a.copl, NOT dependents
    assert recompile == {"a.copl"}

def test_scheduler_api_changed_cascades():
    scheduler = IncrementalScheduler()
    changes = [ChangeEntry("a.copl", ChangeType.API_CHANGED)]
    dep_graph = {"a.copl": ["b.copl", "c.copl"]}
    
    recompile = scheduler.compute_recompile_set(changes, dep_graph)
    
    # API_CHANGED → a + dependents
    assert recompile == {"a.copl", "b.copl", "c.copl"}

def test_scheduler_new_file():
    scheduler = IncrementalScheduler()
    changes = [ChangeEntry("new.copl", ChangeType.NEW)]
    dep_graph = {}
    
    recompile = scheduler.compute_recompile_set(changes, dep_graph)
    assert recompile == {"new.copl"}

def test_scheduler_deleted_file():
    scheduler = IncrementalScheduler()
    changes = [ChangeEntry("gone.copl", ChangeType.DELETED)]
    dep_graph = {"gone.copl": ["user.copl"]}
    
    recompile = scheduler.compute_recompile_set(changes, dep_graph)
    
    # Deleted file → recompile dependents (not the deleted file itself)
    assert recompile == {"user.copl"}

def test_scheduler_skip_set():
    scheduler = IncrementalScheduler()
    all_files = ["a.copl", "b.copl", "c.copl", "d.copl"]
    recompile = {"a.copl", "b.copl"}
    
    skip = scheduler.compute_skip_set(all_files, recompile)
    assert skip == {"c.copl", "d.copl"}


# ============================================
# 5. PublicAPIExtractor
# ============================================

def test_api_hash_deterministic():
    from copl.lexer import Lexer
    from copl.parser import parse
    
    source = '''module examples.api_test {
        pub struct Point { x: U32, y: U32 }
        pub fn get_x(p: Point) -> U32 { return p.x; }
    }'''
    
    lexer = Lexer()
    tokens, _ = lexer.tokenize(source)
    ast_node, _ = parse(tokens, filename="<test>")
    
    extractor = PublicAPIExtractor()
    h1 = extractor.extract_api_hash(ast_node)
    h2 = extractor.extract_api_hash(ast_node)
    assert h1 == h2
    assert len(h1) == 16  # truncated SHA256


# ============================================
# 6. IncrementalResult
# ============================================

def test_incremental_result():
    result = IncrementalResult(total_files=10, recompiled=2, cached=8)
    assert result.cache_hit_rate == 0.8
    d = result.to_dict()
    assert d["cache_hit_rate"] == "80.0%"
