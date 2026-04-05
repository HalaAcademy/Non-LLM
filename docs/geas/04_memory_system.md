# Đặc tả Hệ thống Bộ Nhớ GEAS (GEAS Memory System)
## Hệ 4 Tầng + Phân Giải Xung Đột + Cơ Chế Chống Quên Thảm Hại
## Khắc phục G5 (quên thảm hại), G6 (xung đột thông tin), G7 (lệch pha mô hình thế giới)

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Kiến trúc Bộ nhớ

```
┌───────────────────────────────────────────────────────┐
│                  HỆ THỐNG BỘ NHỚ                       │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 1: BỘ NHỚ LÀM VIỆC (WORKING MEMORY - RAM)   │   │
│  │ Task hiện hành, kế hoạch, hành động, lỗi mới bị  │   │
│  │ Dung lượng: ~10MB | Sống: trong 1 phiên (session)│   │
│  └─────────────────────────────────────────────────┘   │
│                        ↕ gỡ/nạp                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 2: BỘ NHỚ TRẢI NGHIỆM (EPISODIC - SQLite)   │   │
│  │ Mỗi nhịp: trạng thái→hành động→kết quả→bài học   │   │
│  │ Dung lượng: Không hạn chế | Sống: Vĩnh viễn      │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ thăng cấp (độ tự tin ≥ 0.85, kiểm chứng ≥ 3)
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 3: BỘ NHỚ NGỮ NGHĨA (SEMANTIC - SQLite)     │   │
│  │ Các bài học tổng quát hóa, quy tắc thiết kế      │   │
│  │ Dung lượng: Không hạn chế | Sống: Vĩnh viễn      │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ thăng cấp (xác nhận qua nhiều dự án)
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 4: BỘ NHỚ QUY TRÌNH (PROCEDURAL - SQLite)   │   │
│  │ Các luồng làm việc, chiến lược đỉnh, biểu mẫu    │   │
│  │ Dung lượng: Không hạn chế | Sống: Vĩnh viễn      │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
```

## 2. Cấu trúc Dữ liệu Schema

### 2.1 Trải nghiệm (Episode)

```python
@dataclass
class Episode:
    id: str                          # Mã UUID
    project_id: str                  # Dự án nào
    branch: str                      # Nhánh xử lý ("main", "feature/x")
    timestamp: float                 # Thời gian unix
    
    # Tình thế trước khi hành động
    state: EpisodeState
    
    # Quyết định tung đòn
    action: EpisodeAction
    
    # Thấy kết cục trả về
    outcome: EpisodeOutcome
    
    # Bác sĩ bắt mạch phân tích (nếu lỗi)
    diagnosis: Optional[EpisodeDiagnosis]
    
    # Rút nắn ra cục bài học
    lessons: list[str]               # ID bài học
    
    # Theo dõi thẻ phụ metadata
    duration_ms: int
    agent_version: str

@dataclass
class EpisodeState:
    goal_summary: str                # Chốt gọn đích vạch ra
    modules_count: int
    functions_count: int
    build_status: str                # "chưa_build"|"đâm_thủng"|"ngập_lỗi"
    current_errors: int
    trace_coverage: float
    plan_progress: float             # Đo chặng 0.0-1.0
    relevant_modules: list[str]      # top-5 modules liên quấn
```

### 2.2 Tích Bài học (Lesson)

```python
@dataclass
class Lesson:
    id: str
    created_at: float
    last_used: float
    
    # Nội văn Trích đúc
    context_description: str          # "Lúc đụng màn viết CAN driver cho STM32 chip"
    problem: str                      # "Dính chưởng lệch kiểu I32 đè I16 chỗ vòng lặp"
    root_cause: str                   # "Rễ nguyên nhân là do gán số kiểu âm mà quên tạc dấu"
    recommendation: str               # "Răn đe: Nhớ vác mác signed integer kẹp trói cho lọt nấc"
    
    # Điểm đánh Nhãn Chất Lượng
    confidence: float                 # 0.0-1.0
    evidence_count: int               # Lưu tích tụ số vết kiểm chứng ăn khớp
    contradiction_count: int          # Ghi vạch số ranh lệch lạc đấm chéo ngoe
    
    # Chốt màng Áp Vực Ứng Dụng
    domain_tags: list[str]            # ["embedded","motor","ev"]
    module_patterns: list[str]        # ["*.motor*","*.can*"]
    profile: Optional[str]            # Lắp "embedded"
```

## 3. Hệ Máy Truy Tìm Ký Ức (Retrieval)

### 3.1 Dò theo Phân Lớp Màng lọc (Hierarchical Retrieval)

```python
class MemoryRetriever:
    def retrieve(self, query: MemoryQuery, top_k: int = 5) -> list[MemoryEntry]:
        """Bộ lọc chia 3 nấc để đảm đương tính Scale vút tầm."""
        
        # Màng 1: Lọc Nhanh Gốc theo Điểm Nhấn Dự án + Tag cắm (xài SQL WHERE)
        # Giảm tải: Từ 100,000 mục nát vụn → Rút tóm còn ~1,000 mục
        candidates = self.db.query(""" ... """)
        
        # Màng 2: Ép Vết Lọc cạn theo cấu trúc module
        # Gọt Sắc Lại: Từ cỡ ~1,000 → Cắt Sát Phễu chỉ ~100
        candidates = [c for c in candidates 
                      if self.pattern_match(c.module_patterns, query.current_module)]
        
        # Màng 3: So Soắn Điểm Chuẩn Semantic Ranking Đọ Nháy Điểm Vector Emdedding
        # Lập Đỉnh Vót Cuối: Lọc từ ~100 chắt lòi ra Cúp top_k ngon nhất ăn chắc
        query_embedding = self.embed(query.to_text())
        scored = []
        for c in candidates:
            # Cân Đóng Đểm Gộp Phán Tổng Lực Chọn:
            # 50% Điểm khít similarity + 20% Độ còn nhựa Tươi Mới recency + 30% Độ Trấn Khẳng Định Tự tin
            score = similarity * 0.5 + recency * 0.2 + c.confidence * 0.3
            scored.append((score, c))
        
        return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

## 4. Xóa Rã Thế Kẹt Lỗi Mâu Thuẫn (AGM Belief Revision)

### Thiết trát Gỡ Xung đột (Conflict Resolution)

```python
class ConflictResolver:
    """Khung tháp giải dãn vắt lối cắm giải Xung đột AGM chuyển hóa phù hộ xài cho Bài Học.
    Gồm quy nạp 4 lối thoát hẻm khi có biến đánh lộn bài:
    """
    
    def resolve(self, conflict: Conflict, context: Context) -> Resolution:
        # Đường Gỡ 1: Chẻ Mảnh Cảnh Context (Context scoping)
        # Bẻ mảng phân định: Thẻ Bài A để dành chốn Embedded, Vỏ Lỗi B giữ phần cho Backend
        if self.can_scope_by_context(conflict): return Resolution(action="scope", ...)
        
        # Đường Gỡ 2: Đo Trọng Áp Lực Kiện Chứng (Evidence weighting)
        # Bên Nào Đắp Đa Kiểm Chứng Nặng Cân Hơn -> Chiếm Thượng Phong Át Trắng
        if score_new > score_old * 1.5: return Resolution(action="replace", ...)
        
        # Đường Gỡ 3: Thế Tuổi Trẻ Chọt Chức (Recency)
        # Khoản mốc mới đắp vừa lấn cấn tươi ngon sẽ ép bật cũa kỹ chìm nát đi
        if conflict.new_lesson.created_at > conflict.existing_lesson.created_at + 90*DAY:
             return Resolution(action="replace", ...)
             
        # Đường Cụt Cuối 4: Cắm Biển Bảng Ngập Ngừng Ranh Dính Cho Hai Thẳng Khịa Nhau ôm Uncertain (Nghẽn báo động)
        return Resolution(action="mark_uncertain", flag_for_review=True)
```

## 5. Mệnh Khóa Trấn Càn Quét Chống Lệch Khớp Quên Tàn Tạ EWC

```python
class EWCRegularizer:
    """Công Công Mành Khóa Chống Trôi Căn Đầu Mối Catastrophic Forgetting (Elastic Weight Consolidation).
    
    Chống lại vấp bốc bay Lệch Đai Xích khi Đè Cấy Code Cho Môi Trường Mới, Lực EWC Thúc Trói Vòng Khóa Phạt Nặng:
    Cú Phạt L_ewc = L_current + (λ/2) × Σᵢ Fᵢ × (θᵢ - θ*ᵢ)²
    """
    # Khối mã đã luợc giản đi
```

## 6. Đoạn Vạch Bộ Sinh Đồng Giao Mạch World Model Cùng Với SIR (Bisimulation Sync)

```python
class WorldModelSync:
    """Dọn Trắng Nắn Tỉnh Lại Mã Mô Hình Trăng Vỡ (World Model) chệch Trật Sóng so với Sổ Sinh Tử Compiler (COPL SIR).
    Bồi Đồng bấu Bisimulation Check gọt sát độ chính xác."""
    
    def sync(self, world_model: WorldModel, sir: SIRWorkspace) -> SyncResult:
        # Bước lóc nhấc Hash kiểm vạch đổi thay (hash-based change detection)
        # Gõ Dũi Đập lại cập cho đúng khớp SIR graph vệt (structural equivalence)
        pass
```
