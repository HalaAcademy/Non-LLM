# Đặc tả Ký ức Lọc Từ Phân Nhánh GEAS (Branch-Aware Memory)
## Củng Cố Ranh Giới Ký Ức Theo Nhánh — Khắc phục Scale#3: "Ký ức bị mù hướng nhánh, không biết đang nằm ở nhánh nào"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Nan Giải Điểm Mù (Problem)

```
Một khi Bể Trí Nhớ Bị Mù Khơi Tịt Hướng Nhánh:

  Đặc Vụ Cắm Chốt Ở nhánh "bugfix/safety" vọc code
    → Học Rút Ruột Kéo ra: "Bấm ngàm timeout mức chui lưới an toàn safety timeout phải là 50ms"
    
  Rồi Tên Đặc Vụ Quất Thẳng Bóng Nhảy Qua Nhóm nhánh "feature/hev"
    → Lục Moi Óc Tòi Ra Quên Bài cũ: "Phán là safety timeout chỉ 50ms thôi"
    → ĐỜI OÁI OĂM: Nhánh feature/hev này NÓ VẪN DÙNG CÁI MỐC CŨ 100ms! (Vì chưa bị vá)
    → Bể Óc Nổ Tung vì Đặc Vụ Loạn Nhịp Chặt Bước Confused Sấp Mặt
```

## 2. Đường Tháo Kẹt: Đóng Thẻ Ký Ức Đi Liền Nhánh (Branch-Tagged Memory)

### 2.1 Banh Trướng Khuông Rương Đựng Schema

```python
@dataclass
class Episode:
    # ... mớ ruột cũa phần Episode ...
    
    # Bọc Cấu Rào Xung Quanh Branch Cành Nhánh (Branch context)
    branch: str                     # Ghìm Nhãn "main", "feature/hev", "bugfix/safety"
    commit_hash: str                # Chốt Sổ Cọc Báo Điểm Tọa Độ commit lúc ấy
    merge_status: str               # Tình trạng Hóa Đỉnh: "Còn Ngọ Nguậy active"|"Quy Về Cội Nhập Lòng Mẹ merged_to_main"|"Bụi Hóa Bỏ rơi abandoned"
```

### 2.2 Sóng Quét Ký Ức Ngửi Rành Lưới Nhánh Mọc

```python
class BranchAwareRetriever:
    def retrieve(self, query: MemoryQuery, current_branch: str, top_k: int = 5) -> list:
        # Nhóm Chóp Trấn Đỉnh Rễ Mức 1: Bới Lọc Tranh Cúp Từ Tại Đúng Nhánh Đang Quẫy (Niềm Tin Dồi Dào Sắt Đá Nhất)
        tier1 = self.db.query("""
            SELECT * FROM lessons WHERE branch = ? AND status = 'active'
            ORDER BY relevance_score DESC LIMIT ?
        """, [current_branch, top_k])
        
        # Nhóm Bạc Mức 2: Kéo Sợi Tơ Vói Sang Rễ Tổng Mẹ 'main' (Kiểm Chứng Tốt Dày Dạn)
        tier2 = self.db.query("""
            SELECT * FROM lessons WHERE branch = 'main' AND status = 'active'
            ORDER BY relevance_score DESC LIMIT ?
        """, [top_k])
        
        # Nhóm Rẻ Rúng Mức 3: Ngó Ló Sang Bài Khôn Của Kẻ Hàng Xóm Nhánh Cửa Ngang Kha Khác (Niềm tin Tịt - Gắn Cờ Cảnh Báo Có Khả Năng Rủi Ro Chệch Lối)
        tier3 = self.db.query("""
            ... WHERE branch != ? AND branch != 'main' ...
        """)
        
        # Xáo Bài Cuộn Nặng Nhẹ Lửa Ưu Tiên (priority weighting)
        results = []
        for l in tier1: results.append(ScoredLesson(l, priority=1.0))
        for l in tier2: results.append(ScoredLesson(l, priority=0.8))
        for l in tier3: results.append(ScoredLesson(l, priority=0.3, flag="other_branch"))
        
        # Cạo Mép Gọt Cắt Làm Trơn Khử Rác trùng Deduplicate 
        # (rút gọn phần mã sort và trả về)
        return results[:top_k]
```

### 2.3 Phá Hồn Luân Hồi Nháy Sinh Nhánh Sống Branch Lifecycle

```python
class BranchMemoryManager:
    def on_branch_create(self, branch_name: str, base_branch: str):
        """Bào Ngóc Nhú Lên 1 cành nhánh mới keng: Lôi Nhận Cáo Gia Sản Từ Nhánh Bố mẹ gốc."""
        # INSERT INTO branch_context ...
    
    def on_branch_merge(self, source_branch: str, target_branch: str):
        """Quả Đích Sập Nối Chốt Sổ Cưới Merge thành công: Nhấc Quan Phẩm Bê Tráp Bài Lên Thẳng Nhánh Cưới."""
        # Khi Lesson Mảng Nhúc Nhích Xác Minh Qua Lò Cưới → Nhấc Cúp Vọt Đẩy target
        # lesson.confidence *= 1.1  # Nảy Điểm Vút Lực Tự Phục
        # lesson.merge_status = "merged"
    
    def on_branch_abandon(self, branch_name: str):
        """Khi Nhánh Bị Quét Lái Vào Ổ Bụi rác Hóa Tro (abandoned): Cập Bảng Ném cờ mông lung hạ Vụt Niềm Tin Cho Nhánh Này."""
        # Cứu Bàn Cụp Áp Trục Niềm Tin vỡ lở: UPDATE lessons SET status = 'abandoned_branch', confidence = confidence * 0.5
```

### 2.4 Cửa Trạm Vét Rác Mâu Thuẫn Chặn Chéo Qua Nhiều Nhánh (Conflict Resolution Across Branches)

```python
def resolve_cross_branch_conflict(self, lesson_a, lesson_b):
    """Giằng Xé Khi 2 bên Nhánh Nhào Lên Chỏ Lưỡi Đâm Nghịch Về Cùng Xoay Quanh 1 Điểm Cốt."""
    
    # Bóc Gói Của Lạ 1: Kẻ Một Nhánh Cưới Rồi, Một Đứa Lép Vế Trơ Trơ Chưa → Đứa Cưới Được Sống (Merged wins)
    if lesson_a.merge_status == "merged" and lesson_b.merge_status != "merged":
        return lesson_a
    
    # Khúc Gậy Mắc Kẹt 2: Hai Đứa Cùng Ợ Sống Khỏa Ở 2 Cành Nghênh Nhau → Ghì Chặt Nón Áo Và Giữ Vợ Trọn Cả 2 Đứa Chặn Tags Rõ (giữ song hành Context tách bạch)
    lesson_a.context += f" (Chỉ mớm khớp ở cành nhánh {lesson_a.branch})"
    lesson_b.context += f" (Chỉ mớm khớp trên cành nhánh {lesson_b.branch})"
    return [lesson_a, lesson_b]  # Thả rông cả 2 đứa về
```

## 3. Xiết Sát Hợp Đồng Chung Sóng Git

```python
class GitIntegration:
    """Nẹp Sát Vùng Bóng Git Bày Mâm Nắm Thâm Căn Hành Trạng Hiện Của Git Cây."""
    # - get_current_branch: Rình Sủa Nhánh Gốc
    # - get_current_commit: Chụp Gáy Commit
    # - get_changed_files: Xóc Điểm Mạch COPL Lòi Vút Lên Quét Thay Đổi
```
