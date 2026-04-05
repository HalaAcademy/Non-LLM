# Cơ chế Biên Dịch Tích Hợp Gia Số COPL (Incremental Compilation)
## Khắc phục Cấn Vấn đề Scale#2: "Build Lại Từ Đầu Đống dự án code 30GB là Không Thế Chấp Nhận Xét Trên Yêu Cầu Tốc Độ"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Bài toán rào cản

```
Lên giàn Build 1 dự án 30GB tính đường khép vòng bọc hết thủ công (Full compile):
  Trượt quét 500,000 files × đi tuần qua 6 cữ lưới (6 passes) = Chờ mất ~30 phút đồng hồ

Người Lập Trình (Developer) nhấp sửa vặt 1 dòng 1 file → Trả giá bằng sự ngắt cứng phải ngồi chờ 30 phút?
Tác Tử Trí Tuệ (AI agent) cập nhật vi chỉnh sửa 1 file → Cũng câm nín ôm hận chờ 30 phút rãnh cho mỗi ván bài lặp lại vòng iteration?
Không bao giờ được phép chấp nhận! (Not acceptable).
```

## 2. Giải pháp Mũi Nhọn: Luân Chuyển Biên dịch Kiểu Incremental Áp Dụng Rà Mạch Khớp Dependency

### Tuyên Tôn Luật Cốt Yếu Của Thuật Toán:

```
Thấy Tín Hiệu Sửa Nhẹ 1 File đổi → Chỉ Kích hoạt lệnh dựng lại các đối tác bị hỏng (Only recompile):
  1. Trực chỉ Chính file code bị thay đổi đó
  2. Bất kỳ Mảng Tệp files nào ôm Tình trạng Trực Lập Ràng buộc (DIRECTLY depend) ăn trực diện vào điểm API Lớp Ngoài Public vừa bị phẫu thuật của cái mã file kia.
  3. Từ Chối Build Lại Tuyệt đối (Skip) với muôn vàn các mảng files nằm chết yên phăng phắc vì chúng chỉ trích xuất hàm dựa lên các hàm public API Không Hề Đụng Tới (UNCHANGED).
```

### 2.1 Cỗ Máy Cảm biến Bắt Trúng Sự Thay Đổi (Change Detection)

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
                # Trạng thái File đã suy suyển — Nhưng câu hỏi phải hỏi là: Sâu xa thì code nào bị biến dạng chìm?
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

### 2.2 Thuật Soát Bảng Điểm Kích Hoạt Luồng Dựng Code (Recompilation Set Computation)

```python
class IncrementalScheduler:
    def compute_recompile_set(self, changes: ChangeSet, dep_graph: DepGraph) -> set[str]:
        to_recompile = set()
        
        for file, change_type in changes.items():
            # Mặc định ép chết cứng một lệnh: luôn đập lại lệnh build cho file dính dấu tay cộm hóa
            to_recompile.add(file)
            
            if change_type == ChangeType.BODY_ONLY:
                # Phát hiện rà Trúng cờ: File chỉ bị đục sửa nội hàm giấu kín (internal change) → Hệ Thống Rễ Kênh Ăn Bám Ở Ngoài (dependents) Mừng Rỡ Yên Ấn Và Miễn Recompile
                pass
            
            elif change_type in (ChangeType.API_CHANGED, ChangeType.NEW, ChangeType.DELETED):
                # Phát giác Chấn Động Làm Nhàu Vỏ Bọc Mặt Tiền (Public API) bị vỡ → Tung kèn rốc đập bẹp & Build lại tập trung Toàn Bộ khối tệp mã Dependent Ăn Ký Sinh Trực Trực Hệ
                dependents = dep_graph.get_direct_dependents(file)
                to_recompile.update(dependents)
                
                # Check Kiểm tra tiếp chớp lốc Vòng Domino có gãy rễ sâu xuống nữa không: Thấy Code Ăn Ký Sinh sau đi Build Lại Cấu Kiến Sang Mã Mới Bị Chạm nến Mất Form Dễ Thương Thì Ép Gọi Gọi Lây Sóng Thần Nữa...
                for dep in dependents:
                    old_api = self.cache.get_public_api(dep)
                    new_api = self.recompile_and_get_api(dep)
                    if old_api != new_api:
                        # Thảm họa Dây Chuyền Bùng Nổ Cuốn Lây Lan Xuống Toàn Quân Đoàn Code Dependents (Thế hệ Cháu Chắt) 
                        to_recompile.update(dep_graph.get_direct_dependents(dep))
        
        return to_recompile
```

### 2.3 Phân Định "Public API" (Vỏ Mở Ngoài Củ) là Tức Chỉ những thành tố nào?

```python
class PublicAPI:
    """Phiên hàm Hash băm cấu trúc mã giao thức Lưới public cho giao diện module — Nhỡ đâu vỏ này bị gãy, Đống phụ thuộc ăn nhờ ở lại đành trôi chu kỳ nộp lệnh compile build tốn phí."""
    
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

## 3. Khay Bộ Nhớ Dữ Liệu Cache Trữ Điểm (Compile Cache)

```python
class CompileCache:
    """Cụm CSDL Giữ Bản Mẫu Cache dai dẳng lâu dài cho các vết Build trước đó."""
    
    CACHE_DIR = ".copl_cache/"  # Lưu thẳng lên project root
    
    def __init__(self, project_dir: str):
        self.db = sqlite3.connect(f"{project_dir}/.copl_cache/cache.db")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS module_cache (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                public_api_hash TEXT NOT NULL,
                sir_json TEXT NOT NULL,          -- Trữ bản đóng băng kết khối chuẩn của SIR rành rẽ của khối module
                tir_json TEXT,                    -- Cất trữ luôn TIR (với điều kiện nó chót đã được ép khuôn build)
                diagnostics_json TEXT,
                compile_time_ms INTEGER,
                last_compiled REAL
            )
        """)
    
    def is_valid(self, file: str) -> bool:
        """Đọ So thông tin để duyệt Xem Bản Cache còn tính tinh gọn hiệu lực (valid) lừa đảo không."""
        row = self.db.execute(
            "SELECT file_hash FROM module_cache WHERE file_path = ?", 
            (file,)
        ).fetchone()
        if not row:
            return False
        return row[0] == hash_file(file)
    
    def get_cached_sir(self, file: str) -> Optional[SIRModule]:
        """Câu Gọi Dữ Kiện SIR lấy từ kho xài thẳng mà miễn phí thủ tục Đập Bật Load Compile recompiling."""
        if self.is_valid(file):
            row = self.db.execute(
                "SELECT sir_json FROM module_cache WHERE file_path = ?", (file,)
            ).fetchone()
            return SIRModule.from_json(row[0])
        return None
```

## 4. Đo Mô Hình Ước Đoán Hiệu Năng Vận Hành Tính Theo Mốc Giây Tíc Tắc (Performance Model)

```
Trường Lệnh đập Full compile mới chát:     500,000 files × 0.5ms = 250s (Cả mớ bùng mất ~4 min)
Sửa 1 file đơn câm:    1 file + Kéo thêm chừng ~20 mạng Dependents theo quy luật = 21 đội × 0.5ms = 10.5ms tút lẹ
Sửa giáp lá cà tay bo thay một lèo 10 files:  10 + Sóng xô đẩy kéo đổ ~50 domino cascade = 60 chóp × 0.5ms = 30ms loáng cái xong.
Sửa Đổi Lộ Thiết Kế Gãy Nhánh 1 API Gốc Rễ Đáy Chuỗi:     1 file thay đổi + Gọi lệnh Đập Mới Lôi Xuống Rễ Nhánh ~100 mạng Dependents con + Gây sấm dậy chuyền cho ~200 nhánh cháu cascade = Tổng gom nén 300 con mảng file × 0.5ms = 150ms 

→ Kết Quả Biên Dịch Cộng dồn bằng Gia số (Incremental compile): <1s siêu nhẹ siêu nhanh Tối Thư Giãn Dành Cho Hàng trăm các nhịp Cập Code Thay Đổi Cọc (typical changes) ✅
→ Trận đánh Đập Đi Phá Chén Bê Tông Làm Build Rebuild cồng kềnh Cực Mệnh (Full rebuild): chỉ diễn ra ở LẦN KHỞI CHÁT CĂM MŨI CODE BUILD ĐẦU TIÊN của chu kỳ HOẶC sau 1 Quả địa chấn đập phá Kiến trúc cấu trúc đại công trường mà thôi.
```

## 5. Phương Chế Trực Canh Lỗi Dòng Nóng (Watch Mode)

```python
class WatchCompiler:
    """Máy Quay Chụp Quét Quét Luôn Rình Nhìn File System Vòng Tròn Theo Cấu Khối Dịch Incremental Watcher vòng Cục bộ Mắt Điểm."""
    
    def watch(self, project_dir: str, target: str):
        observer = FileSystemObserver(project_dir, pattern="*.copl")
        
        # Mở điểm phát đạn Khai hỏa Sơ Khai Initial full compile
        self.full_compile(project_dir, target)
        
        # Ngáp Mắt Mổ Rình Chỉnh Code
        for event in observer.events():
            changes = self.change_detector.from_event(event)
            recompile_set = self.scheduler.compute_recompile_set(changes)
            
            print(f"Trạng Thái Cọ Bật Thay Mới Xong: {event.file} → Xốc nách đập build ép khởi tấu biên dịch {len(recompile_set)} cục module")
            
            for module_file in self.topological_sort(recompile_set):
                result = self.compile_single(module_file)
                self.cache.update(module_file, result)
                
                if result.errors:
                    print(f"  ❌ Hổ thẹn Đen Ngòm Buôn Mảng Lỗi: {module_file}: {len(result.errors)} Lỗi Bấm Nút Buộc câm")
                else:
                    print(f"  ✅ Rót Chén Thành Công Xanh Mướt Nhẹ Mượt: {module_file}")
```
