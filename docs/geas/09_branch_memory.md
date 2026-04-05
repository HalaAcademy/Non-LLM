# Đặc tả Ký ức Lưu Trữ Theo Phân Nhánh (GEAS Branch-Aware Memory)
## Tối Ưu Quản Lý Ngưỡng Dữ Liệu Theo Môi Trường Git — Khắc phục G12: "Lỗ hổng dữ liệu khi chuyển nhánh"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Bài Toán Xung Đột Ngữ Cảnh Xuyên Nhánh (Context Collision Problem)

Khi Agent thực hiện đa nhiệm vụ trên các phân nhánh khác nhau (Git Branches), kiến thức được học từ nhánh này có thể không phù hợp hoặc gây lỗi cho nhánh khác.

**Ví dụ thực tế:**
- Tại nhánh `bugfix/safety`: Agent học được quy tắc "Ngưỡng Cảnh báo An toàn Safety Timeout System thiết lập bằng 50ms".
- Sau khi chuyển sang nhánh `feature/hev` (nhánh này vốn dĩ chốt thông số Timeout là 100ms): Nếu Agent bế kiến thức "50ms" đè vào, lập tức xung đột và sập lỗi toàn cục.

**Hậu quả**: Lỗi "Blind Memory" khiến khả năng ra quyết định của Agent bị sai lệch hoàn toàn khỏi Context đặc thù của Branch.

## 2. Giải Pháp Gắn Nhãn Ký Ức (Branch-Tagged Memory)

### 2.1 Mở rộng Khối Kiến Trúc Dữ Liệu (Schema Expansion)

Mọi Lesson/Episode được lưu lại đều phải đính kèm Context của Branch cụ thể.

```python
@dataclass
class Episode:
    # Các trường gốc của Episode
    
    # Bổ sung Meta parameters truy vết môi trường Branch
    branch: str                     # Tên Git Branch (e.g., "main", "bugfix/core")
    commit_hash: str                # SHA Commit Code Hash định tuyến mốc thời gian lưu
    merge_status: str               # Trạng thái hiện tại: "active", "merged_to_main", "abandoned"
```

### 2.2 Thuật Toán Truy Vấn Ưu Tiên Nhánh (Priority-Weighted Retrieval)

```python
class BranchAwareRetriever:
    def retrieve(self, query: MemoryQuery, current_branch: str, top_k: int = 5) -> list:
        # Cấp độ 1 (Tier 1): Chọn Lọc Dữ liệu sinh ra từ chính Nhánh đang đứng (Ưu tiên Cao Nhất)
        tier1 = self.db.query("""
            SELECT * FROM lessons WHERE branch = ? AND status = 'active'
            ORDER BY relevance_score DESC LIMIT ?
        """, [current_branch, top_k])
        
        # Cấp độ 2 (Tier 2): Chọn Dữ liệu sinh ra từ nhánh chung "Main/Master" (Kiến thức Hệ thống chuẩn)
        tier2 = self.db.query("""
            SELECT * FROM lessons WHERE branch = 'main' AND status = 'active'
            ORDER BY relevance_score DESC LIMIT ?
        """, [top_k])
        
        # Cấp độ 3 (Tier 3): Chọn các Cửa Nhánh Khác Ngang Hàng (Có cảnh báo rủi ro Context hẹp)
        tier3 = self.db.query("""
            SELECT * FROM lessons WHERE branch != ? AND branch != 'main' AND status = 'active'
        """, [current_branch])
        
        # Sắp xếp và Gán Trọng Số Ưu Tiên (Priority Weighting)
        results = []
        for l in tier1: results.append(ScoredLesson(l, priority=1.0))
        for l in tier2: results.append(ScoredLesson(l, priority=0.8))
        for l in tier3: results.append(ScoredLesson(l, priority=0.3, flag="other_branch_warning"))
        
        return self._deduplicate_and_sort(results)[:top_k]
```

### 2.3 Quản Lý Vòng Đời Theo Diễn Biến Nhánh Git (Branch Lifecycle Synchronization)

Hệ thống Agent Lắng nghe các File Changes Monitor qua Git Checkout:

```python
class BranchMemoryManager:
    def on_branch_create(self, branch_name: str, base_branch: str):
        """Khi Nhánh mới khởi tạo, Agent ghi nhận Base Pointer thừa kế kiến thức gốc."""
        pass
    
    def on_branch_merge(self, source_branch: str, target_branch: str):
        """Khi Pull Request thành công (Merged): Chỉ số Confidence của các Lesson trong nhánh tăng, và nhãn tag target được update."""
        # lesson.confidence *= 1.15
        # lesson.merge_status = "merged"
        pass
    
    def on_branch_abandon(self, branch_name: str):
        """Khi một Branch bị cấm/bỏ dở: Những Dataset liên kết vào đây sẽ nhận Cờ Cảnh Báo Abandoned Data, giảm cực hạn chỉ số Tín Nhiệm."""
        # UPDATE lessons SET status = 'abandoned_branch', confidence = confidence * 0.5
        pass
```

### 2.4 Chiến Lược Resolving Khi Trùng Chéo Bài Học Ở Nhiều Nhánh

```python
def resolve_cross_branch_conflict(self, lesson_a, lesson_b):
    """Xử lý độ xung đột khi truy vết ở Cấp độ Multiverse Branches."""
    
    # Nguyên Tắc 1: Merge Wins — Kiến thức của Nhánh đã Merge Master sẽ Đè Lên kiến thức Của Nhánh Còn Lưng Chừng.
    if lesson_a.merge_status == "merged" and lesson_b.merge_status != "merged":
        return lesson_a
    
    # Nguyên Tắc 2: Scope Isolation — Nếu cả hai Nhánh hoạt động Độc Lập, Phân Ly Đóng Khung Context Không Can Thiệp Nhau.
    lesson_a.context += f" [Note: Context Restricted in Branch {lesson_a.branch}]"
    lesson_b.context += f" [Note: Context Restricted in Branch {lesson_b.branch}]"
    return [lesson_a, lesson_b]  
```

## 3. Tích Hợp API Lõi Git

```python
class GitIntegration:
    """Tương tác trực tiếp và Real-time với Hệ thống Kiểm Soát Phiên Bản Git Của User."""
    def get_current_branch(self) -> str: pass
    def get_current_commit(self) -> str: pass
    def get_changed_files(self) -> list[str]: pass
```
