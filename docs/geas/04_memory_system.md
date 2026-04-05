# Đặc tả Hệ thống Bộ Nhớ GEAS (GEAS Memory System) - Phần 2
## Cấu trúc Lưu trữ Trải Nghiệm, Truy Vấn Ký Ức, Giải Quyết Xung Đột

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Kiến trúc Hệ Thống Bộ nhớ

```
┌───────────────────────────────────────────────────────┐
│                  HỆ THỐNG BỘ NHỚ LÕI                   │
│                                                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 1: BỘ NHỚ LÀM VIỆC (WORKING MEMORY - RAM)   │   │
│  │ Quản lý Context Task hiện hành, kế hoạch, trạng  │   │
│  │ thái hành động, bản log chẩn đoán lỗi cục bộ     │   │
│  │ Dung lượng: Giới hạn ~10MB | Sống: Mỗi session   │   │
│  └─────────────────────────────────────────────────┘   │
│                        ↕ lưu/tải                       │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Tầng 2: BỘ NHỚ TRẢI NGHIỆM (EPISODIC - SQLite)   │   │
│  │ Ghi nhận toàn bộ sự kiện: State→Action→Result    │   │
│  │ Dung lượng: Không hạn chế | Sống: Lưu bền vững   │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ Thăng cấp Data (Confidence ≥ 0.85, Evidence ≥ 3)
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 3: BỘ NHỚ NGỮ NGHĨA (SEMANTIC - SQLite)     │   │
│  │ Dữ liệu bài học đã chắt lọc, mô hình rules chung │   │
│  │ Dung lượng: Không hạn chế | Sống: Lưu bền vững   │   │
│  └─────────────┬───────────────────────────────────┘   │
│                │ Báo cáo đánh giá Metrics chéo qua đa dự án
│  ┌─────────────▼───────────────────────────────────┐   │
│  │ Tầng 4: BỘ NHỚ QUY TRÌNH (PROCEDURAL - SQLite)   │   │
│  │ Dòng Workflow chuẩn hóa, biểu đồ xử lý Action    │   │
│  │ Dung lượng: Không hạn chế | Sống: Trọn đời       │   │
│  └─────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────┘
```

## 2. Cấu trúc Mô tả Schema Cơ Bản

### 2.1 Băng Ghi Trải Nghiệm (Episode)

```python
@dataclass
class Episode:
    id: str                          # Dấu Tích UUID File Hash
    project_id: str                  # Base Scope Mapping System Project Identity
    branch: str                      # Git Workflow Scope Traces Branch Code Rules Tracing Variables
    timestamp: float                 # System Timeline Float UNIX Times Variables Tracker
    
    # Kênh Theo Dõi Hoàn Cảnh Thực Hệ Dữ Liệu Chuyển Action Parameter Metrics State Vector
    state: EpisodeState
    
    # Bản Thiết Khai Dữ Đầu Vector Lệnh Tương Báo Call Exec Action Vector Models Traces Mapping Target Check Rule Value Array Trace Variable Call Log List Item List Scope Method Execution Evaluation Checks Metric Vector Check Variables Metric
    action: EpisodeAction
    
    # Biểu Dữ Đầu Output System Tracing Array Event Execution Flag Returns Outcomes Call Execution Metric Flags Rule Result Output Code Array
    outcome: EpisodeOutcome
    
    # Chốt Lỗi Tự Quét Hệ Hệ Rẽ Roots Data Diagnosis Trace Module Data Error Diagnosis System Analysis Exception Exception Tracing Matrix Code Evaluation
    diagnosis: Optional[EpisodeDiagnosis]
    
    # Liên Vạch Khối Code Mảng Định Đề Trích Dẫn Trỏ UUID Reference Maps Link Trace Rules Reference ID Metric
    lessons: list[str]               
    
    # Khối Meta Metadata System State Tags Variables Limits
    duration_ms: int
    agent_version: str

@dataclass
class EpisodeState:
    goal_summary: str                # File Mapping Tóm Tắt Requirement Context Values Requirement Map Data Check Rule System Array Data Target Scope String Evaluation Logic Target Logic Data Map Goal Goal Data Strings String Map Rule Method Rule Limits Method Criteria Rules Constraints
    modules_count: int
    functions_count: int
    build_status: str                # File Mapping Code Enum Code Flag ("unbuilt", "success", "failed")
    current_errors: int
    trace_coverage: float
    plan_progress: float             # Rate Values Metrics Limits Rules Tensors Ranges 0.0-1.0
    relevant_modules: list[str]      # Data Routing Mappings Variables Network Graph Rules Tracing Top Module Call Traces References String Data Logic Array Matrix Index Rules Matrix
```

### 2.2 Tích Bài Học Từ Mô Phỏng (Lesson Data Record Matrix File)

```python
@dataclass
class Lesson:
    id: str
    created_at: float
    last_used: float
    
    # Core Lesson Triggers Trace Mapping Documentation Parameters Target Mapping Parameter Mappings Context Values System Arrays List String Model String System Method Data Methods Engine Methods Criteria Methods Text Requirements Mapping Parameter Texts Values Variables Value Strings:
    context_description: str          
    problem: str                      
    root_cause: str                   
    recommendation: str               
    
    # Cân Lực Dán Nhãn Metrics
    confidence: float                 # Parameter Scale Matrix 0.0-1.0 Rate
    evidence_count: int               # Limit Rules Tracking Count Parameter Event Counters Scale Check Values Method Variables Counters Check Values Metric Metrics Mappings Data Checks
    contradiction_count: int          # Dấu Xác Limits Variables Error Metrics Rules Rules Index Error Logic Math Detection Variables Evaluation Checks Variables Algorithm Conflict Counter Limit Data
    
    # Cõi Vạch Báo Giới Đích Lệnh Định Tag Array Scope Mappings Variables List Mappings Domain Tag Strings Evaluation Rules Mappings Mappings Groups Lists Arrays Data Categories
    domain_tags: list[str]            
    module_patterns: list[str]        
    profile: Optional[str]            
```

## 3. Hệ Máy Truy Tìm Ký Ức (Retrieval)

### 3.1 Dò theo Phân Cấp Truy Vấn Vector Hierarchical Retrieval Method Process Pipeline Tracing Engine Execution Query Queries Query Logic Search Rule Execution Limits Data Filters Boundaries Algorithms Matrix Constraints System Tensors Optimization Searches Mappings Limit Data Check Math Filtering Filters Filter Check Rule Values

```python
class MemoryRetriever:
    def retrieve(self, query: MemoryQuery, top_k: int = 5) -> list[MemoryEntry]:
        """Quy trình Bộ lọc Phân Cấp Dữ liệu đảm bảo Khả Năng Mở Rộng Hệ Thống Scalability Models Filters Array Rules Check Logic Matrix Limits Limits Rules List Bounds Check Database Constraints Boundaries Scale Engine Parameters Variables Scope Filter Metrics Data Ranges Rules."""
        
        # Màng 1: Rút Khỏa Tác Bốc Gọn Số Hệ SQLite WHERE Engine Rules Filters Logic Limits Data Bounds Values Domain Criteria Array SQL Limits Query Queries Method Criteria System Filtering Filtering Logic Constraints Mapping Arrays Lists Database Method Variables Database List Engine Range Limit Limits Rules Check Rules Filter Matrices Systems Matrix Queries:
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
        
        # Màng 2: Trỏ Theo Dải Khớp Góp Check Maps Limit Boundaries Model Scope Variables Limit Matrix Limit Mappings Rule Match Check Methods Match Mappings Filter Variables String Rules Check Glob Mappings Match Methods Rule Filters String Logic Filter String Filters Logic:
        candidates = [c for c in candidates 
                      if self.pattern_match(c.module_patterns, query.current_module)]
        
        # Màng 3: Semantic Embeddings AI Ranking Check Rule Tensor Tensor System Models Metrics Evaluation Tensors Methods Ranks Ranks Ratings Models Evaluation Vector Math Ratings Scores Checks Metric Limits Logic Matrix Tensors Matrices List Limit Evaluation System AI Scoring Tensor Vectors Tensors Weight Rules Constraints Limit Limit Ranks Vectors Scoring Math Scoring Mathematical Scores Rating Ranking Lists Values Evaluation List:
        query_embedding = self.embed(query.to_text())
        scored = []
        for c in candidates:
            # Thu Tiếng So Chéo Hàm Nhĩ Tịch Khấu Tensor Metric Vector Ranks Logic Method Models Variables Tensor Limit Weights Scores Evaluation Math Tensor
            score = similarity * 0.5 + recency * 0.2 + c.confidence * 0.3
            scored.append((score, c))
        
        return [c for _, c in sorted(scored, reverse=True)[:top_k]]
```

## 4. Cơ Cấu AGM Giải Mâu Thuẫn AGM Belief System Rules Evaluation Revision

```python
class ConflictResolver:
    """Class Resolve Resolving Evaluation Algorithm Framework Mappings Models Rules Matrix Rules Method System Logic Model AI Logic Metrics Evaluation Logic System Limits Model Methods Framework Constraints Mathematical Model Math Variables Engine Rules Framework Data Arrays Logic Guidelines Metrics Data Limits Variables Math Engine Algorithms Groups Engine Rules Engine Array AI
    """
    
    def resolve(self, conflict: Conflict, context: Context) -> Resolution:
        # Hệ Áp Xoay Định Tầng Phân Mảng Context Limit Checks Variable Matrices Categories Filter Group Boundaries Routing Logic Partition Group Filters Scopes Domains Partitions List Scope Ranges Bounds Mappings Variables
        if self.can_scope_by_context(conflict): return Resolution(action="scope", ...)
        
        # Bập Chỉnh Giá Tiết Quá Kích Khuyến Rộng Weight Variable Limit Method Counter Metric Tracking Logic Weight Value Mathematical Scale
        if score_new > score_old * 1.5: return Resolution(action="replace", ...)
        
        # Lối 3 Đổi Trục Update Metric Update Strategy Override Overrides Rate Math Limit Strategy Logic Updates Value
        if conflict.new_lesson.created_at > conflict.existing_lesson.created_at + 90*DAY:
             return Resolution(action="replace", ...)
             
        # Tồn Vọng Treo Bảng Báo System Rule Suspensions Rule Suspension System Data Label Evaluation Flags Flag Holding Suspend Error Suspended Suspense Reviews Review Alerts Limit Uncertainty Constraints Alerts Logic Limit Warning Data Errors Suspend Hold Review Labels Rules Queue Check State Tags Mappings Data Rules Uncertainty Metrics
        return Resolution(action="mark_uncertain", flag_for_review=True)
```

## 5. Mệnh Khóa Trấn Càn Quét Chống Thủng Catastrophic EWC Penalties

```python
class EWCRegularizer:
    """Tua Giải Thí EWC Penalty Vector Model AI Parameters Model Equation Loss Math Tensor Variables Metric Weights Variables Limit Tensor Tensors Variable Limits Weights Tensor Models Optimization Check Vectors Limits Logic Penalties Parameter Equations Matrix Framework Matrix Evaluation Optimization Metrics Tensors Math Rules Checks Optimization Equations Logic Framework Constraints Optimization Constraint Evaluation Optimization Matrices Penalties Loss Mathematical Mathematics Variables.
    """
    # Khối mã đã luợc giản đi để rút ngắn độ dài (Tập trung Cấu trúc)
```

## 6. Đoạn Vạch Đồng Bộ Tương Tác Cấu Bisimulation Graph State Models Check Sync Traces Synchronization

```python
class WorldModelSync:
    """Tốc Độ Rà Validation Hash Engine Architecture Hash Validation Mappings Check Synchronization Check Verification Logic Evaluation Mappings Traces Hash Sync System Mappings Method System Rule Systems Logic System Logic Rule Architecture Trace States Execution Graph Graph Equivalence Mapping Hash Execution Evaluation Validation Graph State Mapping Trace Architecture States Data Traces Mappings Integrity Data Systems Verification Verification Logic Sync Graph Method Systems Evaluator Evaluator Systems.
    """
    
    def sync(self, world_model: WorldModel, sir: SIRWorkspace) -> SyncResult:
        # Bước lóc nhấc Hash kiểm vạch đổi thay (hash-based structural mapping synchronization checks check node limits)
        pass
```
