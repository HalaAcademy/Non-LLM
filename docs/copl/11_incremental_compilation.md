# Cơ chế Biên Dịch Tích hợp Gia số COPL (Incremental Compilation)

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Vấn Đề Về Hiệu Suất Biên Dịch (Performance Problem)

```
Thời gian biên dịch toàn bộ (Full compile) một dự án 30GB:
  Duyệt 500,000 files × 6 quá trình phân tích (passes) = Thời gian chờ xử lý ~30 phút.

Lập trình viên (Developer) thay đổi 1 dòng code ở một file → Máy móc phải biên dịch và chờ 30 phút.
AI Agent cập nhật mã nguồn phụ → Cần chờ quá trình compile lại 30 phút cho mỗi vòng lặp chức năng.
Điều này là không thể đáp ứng được trong thực tế tác vụ vòng lặp phản hồi nhanh (Not acceptable).
```

## 2. Giải Pháp: Biên Dịch Chênh Lệch Dựa Trên Đồ Thị Phụ Thuộc (Dependency-Aware Incremental Compilation)

### Quy Tắc Chốt Biên Dịch Gia Số:

```
Khi phát hiện một tệp bị chỉnh sửa → Chỉ biên dịch lại nhóm bị ảnh hưởng (Only recompile):
  1. File mã nguồn trực tiếp bị thay đổi.
  2. Bất kỳ các tệp nào phụ thuộc trực tiếp (DIRECTLY depend) vào Public API của file vừa sửa đổi.
  3. Bỏ qua (Skip) toàn bộ các tệp mã nguồn nếu sự thay đổi tại mã cơ sở không làm ảnh hưởng tính nhất quán của giao tiếp Public API.
```

### 2.1 Cảm Biến Cập Nhật Thay Đổi Phát Sinh (Change Detection)

```python
class ChangeDetector:
    def detect_changes(self, workspace: str, cache: CompileCache) -> ChangeSet:
        changes = ChangeSet()
        
        for file in walk_copl_files(workspace):
            file_hash = hash_file(file)
            cached_hash = cache.get_hash(file)
            
            if cached_hash is None:
                changes.add(file, ChangeType.NEW)
            elif file_hash != cached_hash:
                # File đã thay đổi. Cần kiểm tra xem mã thay đổi có ảnh hưởng public API không.
                old_public_api = cache.get_public_api(file)
                new_public_api = self.extract_public_api(file)
                
                if old_public_api == new_public_api:
                    changes.add(file, ChangeType.BODY_ONLY)
                else:
                    changes.add(file, ChangeType.API_CHANGED)
        
        for cached_file in cache.all_files():
            if not exists(cached_file):
                changes.add(cached_file, ChangeType.DELETED)
        
        return changes
```

### 2.2 Tính Toán Lịch Trình Biên Dịch Lại (Recompilation Set Computation)

```python
class IncrementalScheduler:
    def compute_recompile_set(self, changes: ChangeSet, dep_graph: DepGraph) -> set[str]:
        to_recompile = set()
        
        for file, change_type in changes.items():
            # Luôn biên dịch lại file trực tiếp bị thay đổi
            to_recompile.add(file)
            
            if change_type == ChangeType.BODY_ONLY:
                # Thay đổi logic nội bộ (internal change) → Tệp phụ thuộc (dependents) không cần build lại
                pass
            
            elif change_type in (ChangeType.API_CHANGED, ChangeType.NEW, ChangeType.DELETED):
                # Public API bị ảnh hưởng → Cần biên dịch toàn bộ các file Dependent trực tiếp
                dependents = dep_graph.get_direct_dependents(file)
                to_recompile.update(dependents)
                
                # Kiểm tra hệ quả dây chuyền: Nếu tệp phụ thuộc biên dịch xong thay đổi tiếp Public API, thì đánh dấu tiếp nhánh ảnh hưởng
                for dep in dependents:
                    old_api = self.cache.get_public_api(dep)
                    new_api = self.recompile_and_get_api(dep)
                    if old_api != new_api:
                        # Sự đổ vỡ giao tiếp lây lan xuống hệ thống liên quan (Cascading failures)
                        to_recompile.update(dep_graph.get_direct_dependents(dep))
        
        return to_recompile
```

### 2.3 Tiêu Chí Xác Định Public API

```python
class PublicAPI:
    """Đối tượng băm (Hashing) cấu trúc mã giao diện module — Nhằm định tuyến cache hiệu quả"""
    
    def extract(self, module: ASTModule) -> APIHash:
        api_elements = []
        
        for item in module.items:
            if item.visibility == "pub":
                match item:
                    case Function(name, params, ret_type, effects):
                        api_elements.append(f"fn:{name}:{params}:{ret_type}:{effects}")
                    case Struct(name, fields):
                        api_elements.append(f"struct:{name}:{fields}")
                    case Enum(name, variants):
                        api_elements.append(f"enum:{name}:{variants}")
                    case Trait(name, methods):
                        api_elements.append(f"trait:{name}:{methods}")
                    case TypeAlias(name, target):
                        api_elements.append(f"type:{name}:{target}")
                    case Const(name, type, value):
                        api_elements.append(f"const:{name}:{type}:{value}")
        
        return hash(tuple(sorted(api_elements)))
```

## 3. Bộ Nhớ Tạm Biên Dịch (Compile Cache)

```python
class CompileCache:
    """Hệ quản trị CSDL bộ nhớ Cache lưu trữ dữ liệu từ các chu kỳ phiên build."""
    
    CACHE_DIR = ".copl_cache/"  # Lữu trữ tại thư mục root của dự án
    
    def __init__(self, project_dir: str):
        self.db = sqlite3.connect(f"{project_dir}/.copl_cache/cache.db")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                public_api_hash TEXT NOT NULL,
                sir_json TEXT NOT NULL,          -- Lưu bản Semantic IR JSON của module
                tir_json TEXT,                    -- Lưu bản Target IR JSON (nếu module tương đương đã được dịch)
                diagnostics_json TEXT,
                compile_time_ms INTEGER,
                last_compiled REAL
            )
        """)
    
    def is_valid(self, file: str) -> bool:
        """Kiểm tra hiệu lực của bộ cache dựa trên hàm hashing tệp mã nguồn."""
        row = self.db.execute(
            "SELECT file_hash FROM module_cache WHERE file_path = ?", 
            (file,)
        ).fetchone()
        if not row:
            return False
        return row[0] == hash_file(file)
    
    def get_cached_sir(self, file: str) -> Optional[SIRModule]:
        """Tái sử dụng trích xuất báo cáo SIR trực tiếp nếu luồng cache hợp lệ (valid)."""
        if self.is_valid(file):
            row = self.db.execute(
                "SELECT sir_json FROM module_cache WHERE file_path = ?", (file,)
            ).fetchone()
            return SIRModule.from_json(row[0])
        return None
```

## 4. Mô Hình Định Lượng Hiệu Năng Thời Gian (Performance Estimation Model)

```
Biên dịch toàn bộ mã dự án (Full compile):          500,000 files × 0.5ms = 250s (~4.1 min)
Biên dịch 1 luồng tệp nội bộ:                       1 file + Tái dịch khoảng ~20 file Dependents = 21 files × 0.5ms = ~10.5ms
Sửa một cấu trúc hàm ở nhiều luồng độc lập:         10 files + ~50 tập file phụ thuộc = 60 files × 0.5ms = ~30ms
Sửa phân mảnh gốc của API Core:                     1 file + Buộc load build ~100 tập Dependents cấp 1 + Lây lan ~200 nhánh phụ thuộc = Tái nạp 300 files × 0.5ms = ~150ms 

→ Kết Quả Biên Dịch Gia số (Incremental compile): Thời gian < 1s cho hàng trăm tập tính chất luồng code thông thường cập nhật (typical changes) ✅
→ Hoạt động Build Full system diễn ra vào lúc: Khởi tạo dữ liệu lần Compile đầu tiên HOẶC khi quy hoạch lại gốc thiết kế kỹ thuật kiến trúc hạ tầng quá mạnh.
```

## 5. Phương Chức Giám Sát Cập Nhật Theo Thời Gian Thực (Watch Mode)

```python
class WatchCompiler:
    """Chức năng Theo dõi Tệp (FileSystem Watcher) kết hợp quy trình Dịch Incremental Mode."""
    
    def watch(self, project_dir: str, target: str):
        observer = FileSystemObserver(project_dir, pattern="*.copl")
        
        # Phiên kiểm tra thiết lập Full Compile ở quá trình Start
        self.full_compile(project_dir, target)
        
        # Bắt đầu nghe và dò dữ kiện chỉnh sửa System file
        for event in observer.events():
            changes = self.change_detector.from_event(event)
            recompile_set = self.scheduler.compute_recompile_set(changes)
            
            print(f"Bắt sự thay đổi (Change Detected): {event.file} → Tiến hành Build lại {len(recompile_set)} module liên quan")
            
            for module_file in self.topological_sort(recompile_set):
                result = self.compile_single(module_file)
                self.cache.update(module_file, result)
                
                if result.errors:
                    print(f"  ❌ Lỗi Biên dịch (Compilation Failed): {module_file}: {len(result.errors)} Lỗi")
                else:
                    print(f"  ✅ Thành công (Compiled Successfully): {module_file}")
```
