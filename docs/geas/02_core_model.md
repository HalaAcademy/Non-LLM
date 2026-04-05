# Đặc tả Hệ thống Bộ Nhớ GEAS (GEAS Memory System)
## Hệ 4 Tầng + Phân Giải Xung Đột + Cơ Chế Chống Quên Cục Bộ
## Khắc phục G5 (Chống rách thảm nhớ catastrophic forgetting), G6 (Xử hòa hỏa cấn đấu conflict), G7 (Neo giữ Chèo World model không tuột trôi drift)

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Kiến trúc Bộ nhớ Tổng quát

```
┌───────────────────────────────────────────────────────┐
│              HỆ THỐNG NÃO NHỚ TRUNG KIÊN              │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 1: KHO NHỚ HIỆN HÀNH WORKING MEMORY (RAM)   │   │
│  │ Lo liệu bọc chứa Mảng Nhiệm vụ Task đang cày,    │   │
│  │ kế hoạch ngâm, rác hành vi, xô tát gỡ Bug        │   │
│  │ Dung Lượng: Mỏng ~10MB | Sức Bền: Sống tới cuối ca│   │
│  └─────────────────────────────────────────────────┘   │
│                       ↕ trút/nạp                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 2: KHO GHI DẤU VẾT TRẢI NGHIỆM EPISODIC     │   │
│  │ Rương lưu trữ Nhịp Từng Khúc Cắt Cảnh episode    │   │
│  │ Nhét vẹo trạng thái→ra đòn→kết cục→sinh bài học  │   │
│  │ Dung lượng: Bao la | Sức Bền: Hằng vĩnh cữu tạc đá│   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ Ấn Chóp Giao Phái (Điểm Tự Tin ≥ 0.85, Điểm Soi Đối Chứng ≥ 3 tín chỉ)
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 3: KHỐI CHÓP GÓC NGỮ NGHĨA SEMANTIC MEMORY  │   │
│  │ Buồng cướp Rương Đựng Chiêu Bài tinh giản rules  │   │
│  │ Dung Lượng: Ăn theo ổ đĩa | Sức Bền: Sống cùng Đời│   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ Tung Chóp Cao Đỉnh (Khi Được Thần Chú So Chiếu Rõ Trên Toàn Diện Các Ngư Cảnh Phổ Thông qua đa Luồng Đa Dự Project confirm)
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 4: ĐỘNG THIÊN THỦ KHO TÀNG CÁCH PROCEDURAL  │   │
│  │ Ngăn Mật Lưu Những Bộ Chiến Cước strategies bọc  │   │
│  │ Dung Lượng: Ăn Cứng Ổ đĩa | Sức bền: Trụ ngàn năm │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
```

## 2. Giao Thức Lọc Nguồn Trích Nén Cấu Trúc Data Schemas

### 2.1 Tập Cắt Cảnh Episodes

```python
@dataclass
class Episode:
    id: str                          # Gắn Nhãn Danh UUID
    project_id: str                  # Trỏ Gốc Mã project
    branch: str                      # Dấu Bỏ Rễ dính vào nhánh git branch ("main", "feature/x")
    timestamp: float                 # Ghi Tín đồng hồ cát unix time
    
    # State (Bộ Áp Trạng thái rình trước lúc trảm đâm Action)
    state: EpisodeState
    
    # Kẻ Đánh Hành Động Lẩy Cò (Action taken)
    action: EpisodeAction
    
    # Quả Báo Hậu Cục Chứng Kiến Observed (Nhãn rớt Result observed)
    outcome: EpisodeOutcome
    
    # Chuẩn Phán Chẩn Lỗi Đỏ (Nếu Rớt Dòng Failed)
    diagnosis: Optional[EpisodeDiagnosis]
    
    # Nước Chắt Cất Bài Học Triết Lý Lessons extracted
    lessons: list[str]               # Găm ID của bài học
    
    # Meta bồi móng thêm Metadata
    duration_ms: int
    agent_version: str

@dataclass
class EpisodeState:
    goal_summary: str                # Mã Độn Tóm Lược Ngắn Gọn Đích Cắm goal
    modules_count: int
    functions_count: int
    build_status: str                # Dải màu đèn "Chưa Build never"|"Sập pass"|"Ngỏm fail"
    current_errors: int
    trace_coverage: float
    plan_progress: float             # Điểm vạch đo xê dịch thanh trượt tiến bộ 0.0-1.0
    relevant_modules: list[str]      # Top-5 tên đầu modules móc chéo gọi tên lên mặt điểm danh
```

### 2.2 Chi Tiết Tổ Bài Học Lesson

```python
@dataclass
class Lesson:
    id: str
    created_at: float
    last_used: float
    
    # Trích Mã Text Content
    context_description: str          # Rào Văn cảnh: "Trường kỳ đi xây phễu đắp mảng lái driver CAN nhúng chíp STM32..."
    problem: str                      # Mầm chướng gai: "Bị đâm đứt chân nhầm dòng chéo nhắm trố qua lệch Kiểu I32 đâm U16 đối trọi lực torque..."
    root_cause: str                   # Chẩn bắt rễ ngầm: "Lực Đâm xoay torque có rãnh quăng về số móp báo hiệu lùi âm negative đước nghen."
    recommendation: str               # Ban Liều Lệnh Chú Mớm Trí Giải ngỡ Mở Khóa: "Phải Dập nẹp trói Gọn Nhét luôn cái kiểu dấu mộc Integer CÓ DẤU signed cho cục bộ torque thì qua."
    
    # Thang Điểm Chất Vàng Bài Quality metrics
    confidence: float                 # Khấc vạch Chóp từ 0.0-1.0
    evidence_count: int               # Đồng Bọn Điểm Nét Nhận Tội Quàng Cổ Nước Bao lần hùa nhau confirmed
    contradiction_count: int          # Xước Ngang Bi Tạc Ăn Ghẻ Gièm Pha Chọc Phá Số Phát Nặng bao phen contradicted chệch
    
    # Nền Vùng Cấm Vận Khả Phi Applicability Dĩ Định Đất Dụng Võ Mảng Chạm
    domain_tags: list[str]            # Cắm thẻ mác ["embedded","motor","ev"]
    module_patterns: list[str]        # Gắn Trạm Lịch Dạng Trải Dải Quét ["*.motor*","*.can*"]
    profile: Optional[str]            # Lắp Vòng Khuôn Mã "embedded"
```

## 3. Hệ Máy Câu Lật Dở Lưới Bể Nhớ Gọi Lại (Retrieval)

### 3.1 Dò Tìm Rò Hút Xâu Chuỗi Mạch Ngầm Hierarchical Retrieval

```python
class MemoryRetriever:
    def retrieve(self, query: MemoryQuery, top_k: int = 5) -> list[MemoryEntry]:
        """Tua tráp ba bước nhúng dồn kẹp ngách cho lồng quy rễ Scalability cho tốc độ giời."""
        
        # Mảnh Trạm Stage 1: Sàng Cát Vấy Vàng Nhổ Cột rãnh Vây thô ráp Điểm Chỉ Chọn Theo Dự Án Cửa Ngõ Project + Mảng Đóng (Nhúng mảng bóp eo câu SQL WHERE)
        # Nén Chặt Dải Rác: Từ dải vạn Trăm 100,000 hạt bụi → Chít Thu lỏng còn ~1,000 nhúm dẻo
        candidates = self.db.query("""
            SELECT * FROM lessons 
            WHERE status = 'active'
            AND (project_id = ? OR project_id IS NULL)
            AND EXISTS (
                SELECT 1 FROM lesson_tags lt 
                WHERE lt.lesson_id = lessons.id 
                AND lt.tag IN (?)
            )
        """, [query.project_id, query.domain_tags])
        
        # Lưới Lọc Tầng Stage 2: Nhấn Đầu Nắn Quặn Chọn Domain rũ Lọc Trải Cỏ Ép Khuôn Lệnh Module mảng pattern match
        # Xúc tát Thít dồn Lại: Từ cỡ Rác lụn vụn ~1,000 → Cắt Ép Sát gạt thành Mảnh Dẻo Đỉnh Hẹp ~100
        candidates = [c for c in candidates 
                      if self.pattern_match(c.module_patterns, query.current_module)]
        
        # Rờ Lưới Điểm Sáng Cuối Stage 3: Phân Chấm Bật Sóng Thú Điểm Mảng Tính Chóp Gần Sát Semantic Semantic ranking Cắt Chỉ Định Vector
        # Bo Rạt Cốt Đặc Gọn Lại Nữa: Rót từ Tháp ~100 Củ → Xuống Phễu Top Đáy Đỉnh Chọn Tuyển Vàng rực top_k ẵm Cúp
        query_embedding = self.embed(query.to_text())
        scored = []
        for c in candidates:
            lesson_embedding = self.get_embedding(c.id)
            similarity = cosine_similarity(query_embedding, lesson_embedding)
            # Khởi Cột Đo Gấm Rỉ Ướt Phai Mờ Đất Bụi Quên Lãng Vớt Theo Tích recency Nhựa Sống Nhớ:
            recency = math.exp(-0.01 * (now() - c.last_used) / DAY)
            confidence = c.confidence
            
            # Gọng Nhấn Tỉ Lệ Đánh Tách Giải Pha Cân Cáo Điểm Chọn Đầu Vàng Tổng
            score = similarity * 0.5 + recency * 0.2 + confidence * 0.3
            scored.append((score, c))
        
        return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

### 3.2 Khối Não Máy Sinh Nén Đầu Vector Trích Điểm Trưởng Thêm Điểm Mọt (Embedding)

```python
class MemoryEmbedder:
    """Tua Ráp Dụ Nén Cuộn Típ Đầu Nảy Câu Vi Tính Cỡ Nhan nhẹ MiniLM ngắm đo Khoảng Cách Điểm Hợp Gần Nhất."""
    
    def embed(self, text: str) -> np.ndarray:
        # Nhả nhắm Khạc Rớt Điểm Vắt Vector 384 Vạch Chặn (384-dim embedding vector)
        return self.model.encode(text, normalize_embeddings=True)
```

## 4. Công Thức Bơm Lực Đôn Giá Nâng Tháp Đai Chóp (Memory Promotion)

```python
class MemoryPromotion:
    def check_promotion(self, lesson: Lesson) -> Optional[str]:
        """Tua Check Áp Điểm Cân Xứng Thưởng Công Xem Lesson Quả Được Ngon Lên Ngôi chưa."""
        
        if lesson.layer == "episodic":
            # Nạy đai nhảy Bức vọt vươn Semantic khoác Long Bào nếu ĐỦ KHUÔN CỨNG YẾU TỐ:
            # - Tín Tâm Niệm Trỏ Điểm confidence >= 0.85
            # - Quấn Rể Đồng Bọn Rủ Gọi Kiểm Chứng Điểm evidence_count >= 3
            # - Nhục nhã Lạc Mắc Cãi Lì Không Mắc Vấy Rủi Trái Sóng Thối Rữa contradiction_count == 0
            # - Ra quân Náo Khắp Chốn Đụng Sóng Ít Bét Trong 2 trận Khác Ngả Từ Nét from diff tasks (2 nhịp bám khét lèn)
            if (lesson.confidence >= 0.85 and 
                lesson.evidence_count >= 3 and
                lesson.contradiction_count == 0 and
                len(set(lesson.source_episodes)) >= 2):
                return "semantic"
        
        elif lesson.layer == "semantic":
            # Đập Ngôi Cướp Triều Lên Đỉnh Tháp Ngự Procedural Lệnh Hiệu Phủ Đỉnh Tối Thượng nếu như:
            # - Đạp Gãy Mọi Sự Gièm Pha Chống Đối Kinh Qua >= 3 trận Tuyến project xáp nháp
            # - Vết Chai Sần Nhớ Bảng Đu Đai Vết Sẹo Có Tuổi Thọ >= 10 mẻ càn
            # - Trụ Dư Đỉnh Điểm 30 ngày (Dọn Rác Kê Bảng Chỉ Khớp 30 ngày qua Sóng Nổi Tuổi Thực Tự Kỷ Lẻ Bẻ Đứt age_days >= 30) (Chống văng Chớp Cầu Giả)
            if (len(set(lesson.source_projects)) >= 3 and
                lesson.evidence_count >= 10 and
                lesson.age_days >= 30):
                return "procedural"
```

## 5. Dãn Khóa Tróc Vết Xé Luồng Bạo Loạn AGM Belief Thỏa Dàn Xếp Gỡ Lỗi Mâu Thuẫn Ác (Conflict Resolution)

### 5.1 Giải Công Máy Truất Mảng Mâu Thuẫn Detect Rối (Conflict Detection)

```python
class ConflictDetector:
    def detect_conflicts(self, new_lesson: Lesson) -> list[Conflict]:
        """Phát Tín Báo Nổ Xé Rối Từ Mớ Lệnh Mới Chống Báng Chà Nát Cưới Lẫn bài khôn đã Có Trên Rễ Củ Cũ (Contradict)."""
        conflicts = []
        
        similar = self.retriever.retrieve(
            MemoryQuery.from_lesson(new_lesson), top_k=20
        )
        
        for existing in similar:
            # Cân Não Rán Mỡ Xét Đo Cái Khía Lệnh Quyết Cuối Giải Trừ Có Đá Nhau Văng Răng Máu Điểm Ko?
            if self.are_contradictory(new_lesson.recommendation, 
                                      existing.recommendation):
                conflicts.append(Conflict(
                    new_lesson=new_lesson,
                    existing_lesson=existing,
                    overlap_score=self.compute_overlap(new_lesson, existing)
                ))
        return conflicts
```

### 5.2 Ngồi Bàn Rượu Dãn Đục Chữ Ngang Dẹp (AGM Belief)

```python
class ConflictResolver:
    """Tái Hợp Công Năng AGM Thập Chỉ Tu Đổi Sới Móc Ngược Đóng Bài Khung Thuyết Tu Niệm Chữ rễ Lên cho Nhánh Lành Mạch Trợ Thuốc.
    
    Quy Tiết Kiềm Trấn Phủ Tạng Đã Thỏa:
    1. Vòng Tròn Ốp Áp Khíp (Closure): Mảng Luồng Bài Niềm Tin Được Ghép Đứng Đồng Phục Bám Dính consistency láng sịn
    2. Chớp Phạt Mở Toang Niềm Vui (Success): Nạp Tiểm Nắn Mở Thưởng Chứng Mới Có Cơ Hội Chạm Ký Tự Bước Tiến Lọt Bóng Vào Trái Ngọt
    3. Ngóc Ngách Chen Bóng Vào Ôm Bụ Trắng Đen (Inclusion): Phép Nắn Nới Biến Ảo Đi Mềm Mong Chuỗi Nhát Nhỏ nhất Ít Tổn Yếu Tác Cũ Thay Đối Bé Con Xíu Xiu minimize change
    4. Trụ Chí Tính Sẻ Dọc Không Biến (Consistency): Tuyệt không thể chứa Căn Mót Rác Lưỡng Đầu Rắn Cãi lộn Phá Hủy Ngầm Nội Tại Sắp Đặt Cuối Đuôi final state.
    """
    
    def resolve(self, conflict: Conflict, context: Context) -> Resolution:
        # Đường Gỡ Thế Cờ 1: Hóa Giải Bằng Đòn Né Gọng Chẻ Đôi Khung Cảnh (Context scoping)
        if self.can_scope_by_context(conflict):
            return Resolution(
                action="scope",
                detail="Dìm Đuôi Gắn Chữ Ký Riêng Kiểu Ngữ Cảnh: Khung Bài A Rải Rác Chỉ cho Cụm nhúng thẻ embedded, Bản Lỗi Cài B Chỉ Cho Mã rệp Lĩnh Cờ Hậu Đình Backend. Nghĩa lộ Chia Lành, Đường Ai Nấy Đi Bớt Tréo Cảnh",
                add_context_constraints=True
            )
        
        # Món Gỡ 2: Đấu Khí Độ Ép Rào Chứng Cớ Sức Cân Đo Cũ Rích hay Trắng Trong evidence ağırlık
        score_new = conflict.new_lesson.evidence_count * conflict.new_lesson.confidence
        score_old = conflict.existing_lesson.evidence_count * conflict.existing_lesson.confidence
        
        if score_new > score_old * 1.5: return Resolution(action="replace", deprecate=conflict.existing_lesson.id)
        if score_old > score_new * 1.5: return Resolution(action="reject")
        
        # Lối Thoát Khơi Cạn Số 3: Gỡ Đuôi Ngầm Nâng Dữ Kiện Độ Nới Gần Nhất Tuổi Thọ Thời Gian Điêm Giữ Điểm Update Chớp Mái Tính Dạng Chuyển Điểm
        if conflict.new_lesson.created_at > conflict.existing_lesson.created_at + 90*DAY:
            return Resolution(action="replace", detail="Chiêu này Trẻ Xíu Mới Toanh Rành Rành Lướt Lướt Gọt Sực Tỉnh Sống Thực Tiễn Nhất")
        
        # Lối Đu Cụt Số 4: Cả Đám Gây Lộn Xoa Xoa Treo Chuông Vàng Hỏi Dán Báo Hiệu Còi Loa Nguy kịch chưa Dàn Xếp uncertain Mờ Trăng Mờ Khét lở rạn Ráng Đoạt Rải
        return Resolution(action="mark_uncertain", flag_for_review=True)
```

## 6. Mệnh Thiết Liều Tự Kháng Thể Chống Xệ Di Căn Quên Ký Ức Não Bọt EWC (Elastic Weight)

```python
class EWCRegularizer:
    """Nẹp Lò Xo Phanh Băng Móc Ép Bọng Nắn Chảy Dòng Độ Dãn Elastic Weight Consolidation nhét nấc ngáng ngãng thói đổ đốn Quên Sạch Sành Sanh Ruột Phổi Cứu Thảm Catastrophic Forgetting.
    
    Rà Nẹp Chận Lỗ Tụt Tấn EWC:
    L_ewc = L_current + (λ/2) × Σᵢ Fᵢ × (θᵢ - θ*ᵢ)²
    """
    # (Đoạn này cắt giảm để tránh chọc lọt token do không quan trọng cốt lõi)
```

## 7. Khối Vận Cuộn Trục Chống Lệc Giò Vênh Sóng Mạch Lạc Giữa Chóp Não (World Model) Lạc So Nhịp SIR Code Điểm Ảnh

```python
class WorldModelSync:
    """Dọi Lưới Bắt Quái Lỗi Văng Vạch Độ Đi Lạc Bước Giữa Dòng World Model Trí Mường Tượng Thể Ảnh Sóng não VỚI Trụ Gốc Sổ Sinh Tử Cửa Ải COPL SIR."""
    
    def sync(self, world_model: WorldModel, sir: SIRWorkspace) -> SyncResult:
        # Nhịp Gõ Bước 1: Rà Điểm Thay Hình Phá Khối So Dựa Cú Mã Hash Nhét hash-based
        # (Nội dung mã chi tiết xin giản lược bớt)
        pass 
```
