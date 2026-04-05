# Đặc tả Mô hình Nền tảng (GEAS Core Model & Memory System)
## Hệ 4 Tầng + Phân Giải Xung Đột + Cơ Chế Ngăn Chặn Mất Mát Thông Tin

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Kiến trúc Khối Truy Vấn Vector

### Thuật Toán Truy Vấn Phân Cấp (Hierarchical Retrieval)

```python
class MemoryRetriever:
    def retrieve(self, query: MemoryQuery, top_k: int = 5) -> list[MemoryEntry]:
        """Quy trình Lọc và Tìm kiếm dữ liệu theo 3 giai đoạn tối ưu hiệu năng Database."""
        
        # Giai đoạn 1: Lọc dữ liệu thô bằng truy vấn SQL (Sàng lọc ban đầu theo tag dự án)
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
        
        # Giai đoạn 2: Lọc sâu thông qua Regular Expression Matching cho từng Module Cụ thể
        candidates = [c for c in candidates 
                      if self.pattern_match(c.module_patterns, query.current_module)]
        
        # Giai đoạn 3: Tính toán Cosine Similarity để so mức độ tương đồng giữa Embeddings Vector Tensors
        query_embedding = self.embed(query.to_text())
        scored = []
        for c in candidates:
            lesson_embedding = self.get_embedding(c.id)
            similarity = cosine_similarity(query_embedding, lesson_embedding)
            
            # Áp dụng hàm suy giảm tính theo thời gian Recency (Exponential Decay)
            recency = math.exp(-0.01 * (now() - c.last_used) / DAY)
            confidence = c.confidence
            
            # Công thức tính điểm Ranking tổng hợp
            score = similarity * 0.5 + recency * 0.2 + confidence * 0.3
            scored.append((score, c))
        
        return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

### Bộ Chuyển Đổi Vector (Embeddings)

```python
class MemoryEmbedder:
    """Tạo Embeddings Tensor thông qua kiến trúc mô hình Transformer."""
    
    def embed(self, text: str) -> np.ndarray:
        # Lớp mã hóa tạo ra Embedding vector có kích thước 384 dimensions
        return self.model.encode(text, normalize_embeddings=True)
```

## 2. Tiêu Chuẩn Thăng Hạng Bộ Nhớ (Memory Promotion)

```python
class MemoryPromotion:
    def check_promotion(self, lesson: Lesson) -> Optional[str]:
        """Kiểm tra điều kiện để đánh giá thăng hạng dữ liệu (từ Episodic lên Semantic/Procedural)."""
        
        if lesson.layer == "episodic":
            # Điều kiện chuyển sang Tầng Semantic (Ngữ nghĩa):
            # - Tỉ lệ tự tin Confidence cao (>= 0.85).
            # - Được xác thực qua ít nhất 3 bằng chứng (Evidence count).
            # - Không phát sinh trạng thái lỗi logic (Contradiction count == 0).
            # - Xuất phát từ ít nhất 2 vụ việc (Episodes) khác nhau.
            if (lesson.confidence >= 0.85 and 
                lesson.evidence_count >= 3 and
                lesson.contradiction_count == 0 and
                len(set(lesson.source_episodes)) >= 2):
                return "semantic"
        
        elif lesson.layer == "semantic":
            # Điều kiện chuyển sang Tầng Procedural (Quy trình):
            # - Được áp dụng hợp lệ qua trên 3 Dự án khác nhau.
            # - Mật độ sử dụng cao: Trên 10 lần kiểm chứng Evidence.
            # - Mức tuổi đời đánh giá ổn định: Trên 30 ngày (Age > 30).
            if (len(set(lesson.source_projects)) >= 3 and
                lesson.evidence_count >= 10 and
                lesson.age_days >= 30):
                return "procedural"
```

## 3. Quản Trị Hệ Xung Đột AGM (Conflict Resolution)

### 3.1 Giải Thuật Phát Hiện Xung Đột (Conflict Detection)

```python
class ConflictDetector:
    def detect_conflicts(self, new_lesson: Lesson) -> list[Conflict]:
        """Phát hiện lỗi Logic hoặc sự mâu thuẫn giữa 2 Lessons hoạt động chồng chéo."""
        conflicts = []
        
        similar = self.retriever.retrieve(
            MemoryQuery.from_lesson(new_lesson), top_k=20
        )
        
        for existing in similar:
            if self.are_contradictory(new_lesson.recommendation, 
                                      existing.recommendation):
                conflicts.append(Conflict(
                    new_lesson=new_lesson,
                    existing_lesson=existing,
                    overlap_score=self.compute_overlap(new_lesson, existing)
                ))
        return conflicts
```

### 3.2 Bộ Giải Quyết Mâu Thuẫn AGM (Re-solving Conflict)

```python
class ConflictResolver:
    """Xử lý mâu thuẫn hệ thống thông qua giao thức Belief Constraint Resolution.
    Tuân thủ các điều kiện: 
    1. Closure: Cấu trúc Graph mượt và độc lập.
    2. Inclusion: Rút gọn điểm sai khác tối thiểu (Minimum Logic Change).
    3. Consistency: Không tạo vòng lặp nghịch lý.
    """
    
    def resolve(self, conflict: Conflict, context: Context) -> Resolution:
        # Hướng 1: Tách biệt và phân loại Phạm Vi (Context Scoping Limit)
        if self.can_scope_by_context(conflict):
            return Resolution(
                action="scope",
                detail="Tách biệt nhóm Context riêng biệt rành mạch.",
                add_context_constraints=True
            )
        
        # Hướng 2: Xác thực theo Trọng số Kiểm Chứng (Evidence Weighting Mass Control)
        score_new = conflict.new_lesson.evidence_count * conflict.new_lesson.confidence
        score_old = conflict.existing_lesson.evidence_count * conflict.existing_lesson.confidence
        
        if score_new > score_old * 1.5: return Resolution(action="replace", deprecate=conflict.existing_lesson.id)
        if score_old > score_new * 1.5: return Resolution(action="reject")
        
        # Hướng 3: Tính ưu tiên cho Dữ liệu Gần Nhất (Recency Timestamps Limit)
        if conflict.new_lesson.created_at > conflict.existing_lesson.created_at + 90*DAY:
            return Resolution(action="replace", detail="Sử dụng dữ liệu độ tương thi cao.")
        
        # Hướng 4: Dán cờ Suspend báo treo và chờ Review (Review Flag Marking)
        return Resolution(action="mark_uncertain", flag_for_review=True)
```

## 4. Chuẩn Hóa Ràng Buộc EWC (Elastic Weight Consolidation)

```python
class EWCRegularizer:
    """Ràng buộc tính ổn định của hệ thống Vector tránh tình trạng lãng quên toàn bộ Model Layers.
    
    Thuật toán EWC Tối ưu Điểm Phạt (Penalty Constraints Loss Variables):
    L_ewc = L_current + (λ/2) × Σᵢ Fᵢ × (θᵢ - θ*ᵢ)²
    """
    pass
```

## 5. Tổ Chức Đồng Bộ Hệ State Models Graph (World Model Sync)

```python
class WorldModelSync:
    """Xử lý rà soát bất đối xứng Architecture Graph (Bisimulation Graph Sync Control) kết nối World Model và COPL SIR."""
    
    def sync(self, world_model: WorldModel, sir: SIRWorkspace) -> SyncResult:
        # Bước kiểm định và Mapping thông số kiến trúc dựa trên cơ cấu Hash Equivalences Tracking.
        pass 
```
