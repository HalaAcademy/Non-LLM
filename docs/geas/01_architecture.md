# Đặc tả Kiến trúc GEAS (GEAS Architecture Specification)
## Chi tiết Hệ thống 12 Module Lõi — Khắc phục G3: "Thiếu giao thức liên kết giữa các module"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Nguyên lý Thiết kế Kiến trúc

1. **Điều hướng qua Thông điệp (Message-Driven)**: Các Module trong hệ thống giao tiếp thông qua các định dạng thông báo (typed messages) tiêu chuẩn, loại bỏ hoàn toàn việc chia sẻ trạng thái chung (shared state) nhằm tránh xung đột dữ liệu.
2. **Khả năng Phục hồi Tái hiện (Replay-able)**: Tất cả `messages` được lưu trữ dạng Event Log, cho phép tái thiết lập (replay) chính xác trạng thái và luồng xử lý của hệ thống (Agent loop) vào bất kỳ thời điểm nào.
3. **Mô-đun Độc lập (Pluggable Interface)**: Mỗi module được đóng gói với giao diện `Interface` chuẩn, cho phép thay thế (mock test) hoặc nâng cấp thuật toán nội bộ mà không làm gãy đổ hệ thống.
4. **An toàn Hệ thống (Fail-Safe)**: Khi một module phát sinh Exception, lỗi sẽ được cô lập, hệ thống điều hướng `fallback` tự động thay vì dẫn đến toàn vẹn Crash của Agent.

## 2. Sơ đồ Quan hệ Phụ thuộc Module (Dependency Graph)

```
                    ┌─────────────────┐
                    │   NGƯỜI DÙNG    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  1. Phân tích   │
                    │    Mục tiêu     │
                    └───┬─────────┬───┘
                        │         │
              ┌─────────▼──┐  ┌──▼──────────┐
              │ 2. Quản lý │  │ 3. Xây World│
              │  Bộ Nhớ    │  │ Model       │
              └─────┬──────┘  └──┬──────────┘
                    │            │
                    └──────┬─────┘
                    ┌──────▼──────┐
                    │4. Bộ Lập    │
                    │ Kế Hoạch    │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │5. Động cơ   │
                    │ Chính Sách  │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │6. Thực thi  │────► Nền tảng cấu trúc COPL
                    │ Hành động   │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │7. Quan sát  │◄─── Kết quả Trả về từ Compiler
                    │ Kết quả     │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │8. Hệ thống  │
                    │ Chẩn đoán   │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │9. Động cơ   │
                    │ Tự Đánh giá │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │10. Trích xuất│
                    │ Bài Học      │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │11. Hợp nhất │
                    │ Bộ nhớ      │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │12. Sinh     │
                    │ Báo Cáo     │
                    └─────────────┘
```

## 3. Đặc tả API Từng Module

### Module 1: Goal Interpreter (Phân tích Mục tiêu)

```
Nhiệm vụ: Phân tích ngữ nghĩa yêu cầu (text/JSON) từ phía Người Dùng → Trích xuất các yêu cầu ràng buộc (Constraints) hợp lệ.
Đầu vào: Thông báo định dạng Task
Đầu ra: Message định dạng GoalParsedMsg { requirement_graph, constraints, missing_info }
Phụ thuộc: None

Chức năng chi tiết:
  - Phân tích cú pháp NLP để bóc tách luồng yêu cầu chức năng.
  - Phân tích các giới hạn hệ thống (e.g. constraints cho hệ MCU).
  - Yêu cầu làm rõ thông tin nếu gặp Ambiguity trong yêu cầu của User.
  - Khởi tạo Requirement Graph cơ sở.

Giao diện API:
  fn parse_goal(task: Task) -> GoalParsedMsg
  fn clarify(questions: List<Question>) -> GoalParsedMsg
```

### Module 2: Memory Manager (Trình Quản Lý Bộ Nhớ)

```
Nhiệm vụ: Xử lý hoạt động lưu trữ (Store), truy vấn (Retrieve) và quản lý khối lượng DB 4 tầng memory.
Đầu vào: Yêu cầu MemoryQuery, Bản ghi Episodes, Lessons.
Đầu ra: Message định dạng MemoryRetrievedMsg { relevant_episodes, lessons, procedures }
Phụ thuộc: Database SQLite, MiniLM Embedding model

Chức năng chi tiết:
  - Quản trị toàn vẹn Episodic Memory (Bộ nhớ Trải nghiệm).
  - Quản trị quy tắc của Semantic Memory (Bộ nhớ Ngữ nghĩa).
  - Giám sát Procedural Memory (Luồng chiến lược Workflow).
  - Cung ứng truy vấn Vector chéo (Vector Search) dựa trên Text Embedding.
  - Xác nhận xung đột nội dung, dọn dẹp các mục Data cũ (Data Compaction).
  - Xử lý Routing Branch-aware Retrieval dựa vào mã nhãn Git branches.

Giao diện API:
  fn store_episode(episode: Episode) -> EpisodeId
  fn store_lesson(lesson: Lesson) -> LessonId
  fn retrieve(query: MemoryQuery, top_k: int) -> MemoryRetrievedMsg
  fn resolve_conflict(a: Lesson, b: Lesson, ctx: Context) -> Lesson
  fn compact() -> CompactionReport
  fn get_stats() -> MemoryStats
```

### Module 3: World Model Builder (Khởi tạo Mô hình Thế Giới)

```
Nhiệm vụ: Đồng bộ liên tục và trực quan hóa toàn bộ Trạng thái Dự án (Project State).
Đầu vào: Cấu trúc SIR đại diện từ quá trình Compiler COPL, File system changes.
Đầu ra: Message định dạng WorldModelUpdatedMsg { project_graph, changes_since_last }
Phụ thuộc: COPL SIR Query Interface (Contract #1)

Chức năng chi tiết:
  - Sinh Network Graph trích lục từ chuỗi mã hệ thống COPL SIR.
  - Giám sát độ che phủ Test, liên mô hình Modules, Dependency trees.
  - Chống trôi lệch thông số (State drift) trong quá trình Action Executor thay đổi Code files.
  - Export API tìm nạp các module trạng thái phụ tùng trong toàn mảng.

Giao diện API:
  fn build_from_sir(sir: SIRWorkspace) -> WorldModel
  fn update_incremental(sir_diff: SIRDiff) -> WorldModelUpdatedMsg
  fn query_module(name: str) -> ModuleInfo
  fn query_dependencies(name: str) -> List<Dependency>
  fn get_project_health() -> ProjectHealth
  fn sync_check() -> SyncResult
```

### Module 4: Hierarchical Planner (Quản Trị Kế Hoạch Đa Tầng)

```
Nhiệm vụ: Cấu trúc hóa Luồng Task đa tầng từ cao độ đến các thực thi Step Task nhỏ lẻ.
Đầu vào: GoalParsedMsg, WorldModel, MemoryRetrievedMsg.
Đầu ra: Message định dạng PlanCreatedMsg { phases, current_step, estimated_completion }
Phụ thuộc: Module 1, 2, 3

Chức năng chi tiết:
  - Phân rã Goal → Phase quy trình → Task vi mô → Step cụ thể.
  - Ứng dụng mô hình phụ thuộc (Graph Dependency) đảm bảo luồng ưu tiên Bottom-up execution cho các kiến trúc code nền.
  - Ước tính hao tổn định mức nỗ lực (Effort tracking).
  - Tự động thay đổi và sắp xếp lại kế hoạch (Replan) khi Action gặp lỗi (Error Check).

Giao diện API:
  fn create_plan(goal: GoalParsedMsg, world: WorldModel, mem: MemoryRetrievedMsg) -> Plan
  fn get_next_step() -> PlanStep
  fn replan(reason: ReplanReason) -> PlanRevisedMsg
  fn mark_step_done(step_id: StepId) -> Plan
  fn get_progress() -> PlanProgress
```

### Module 5: Policy Engine (Động cơ Hoạch định Chiến lược)

```
Nhiệm vụ: Tính toán xác suất (Action probablity) và đề cử lệnh thực thi Action.
Đầu vào: Tín hiệu PlanStep, WorldModel, MemoryContext.
Đầu ra: Message định dạng ActionSelectedMsg { action, confidence, reasoning }
Phụ thuộc: Neural Network Core Model Layer, Module 2, 3, 4

Chức năng chi tiết:
  - Chuyển đổi AgentState → Token Input Tensor đưa vào phân tích Model.
  - Áp dụng kỹ thuật Forward Pass qua Layer Model tạo vùng dải Action Prediction.
  - Ràng buộc phân nhánh để ra Tín hiệu Quyết Chọn cuối cùng.
  - Tạo cấu đồ Minh bạch giải trình (Log Reasoning) về các cơ chế lựa chọn.
  - Thiết lập Check limit chống kẹt vòng lặp (Loop Detection) để ngừng vòng thao tác trùng lặp sai.

Giao diện API:
  fn select_action(state: AgentState) -> ActionSelectedMsg
  fn get_action_space() -> List<ActionDef>
  fn update_policy(lesson: Lesson) -> None
```

### Module 6: Action Executor (Bộ Thực Thi Lệnh Tương Tác)

```
Nhiệm vụ: Mô đun gắn giao thức IO (Input/Output Interface) để can thiệp vật lý lên Source code.
Đầu vào: Message định dạng ActionSelectedMsg
Đầu ra: Message định dạng ExecutionResultMsg { outcome, artifacts_changed, duration }
Phụ thuộc: COPL Action Interface (Contract #4)

Chức năng chi tiết:
  - Khởi tạo File Code `.copl` / Patch cập nhật file.
  - Giao tiếp CLI với COPL Compiler (Lệnh build, type check, test check).
  - Thu thập kết quả Output Log (Xác định mã stdout, stderr luồng error).
  - Thiết lập quy trình dừng nếu hệ thống vượt quá cấu hình Timestamp Threshold.

Danh sách Action Catalog API:
  create_module(name, content)      → Khởi tạo Source File mới
  modify_module(name, patch)        → Vá Code hiện thực
  delete_module(name)               → Thu hồi chức năng
  build(target)                     → Gọi luồng build đích
  build_check_only()                → Quét Static Analyzer
  run_tests(suite)                  → Render chuỗi Test Runner Engine
  emit_artifacts()                  → Tích xuất tài liệu Code Artifacts
  query_sir()                       → Chụp bảng tham số SIR System

Giao diện API:
  fn execute(action: Action) -> ExecutionResultMsg
  fn get_supported_actions() -> List<ActionDef>
```

### Module 7: Outcome Observer (Trình Quan sát Kết cục)

```
Nhiệm vụ: Đánh giá trạng thái thành bại (Success/Failure status) sau mỗi bước nhúng Executor đi kèm.
Đầu vào: Message định dạng ExecutionResultMsg
Đầu ra: Message định dạng OutcomeObservedMsg { outcome_class, diagnostics, metrics }
Phụ thuộc: COPL Diagnostic Data (Contract #2)

Chức năng chi tiết:
  - Phân loại lỗi Output Trạng thái: Success | compile_error_syntax | compile_error_type | 
    effect_violation | test_failure | timeout | unknown
  - Chuẩn quy thông số (Parser Error Diagnostics) về dạng định dạng có cấu trúc rõ ràng.
  - Cập nhật số liệu Metrics (Compile time tốn, Test Result coverage báo cáo).
  - Báo động khẩn nếu phát hiện sự cố hệ Regression (Tính lùi bước code).

Giao diện API:
  fn observe(result: ExecutionResultMsg) -> OutcomeObservedMsg
  fn classify_outcome(result: ExecutionResultMsg) -> OutcomeClass
```

### Module 8: Diagnoser (Mô đun Chẩn đoán Root-Cause Lỗi)

```
Nhiệm vụ: Phân tích cốt lõi của nguyên căn lỗi (Root Causes Analysis).
Đầu vào: Tín hiệu OutcomeObservedMsg, WorldModel, Agent History Action
Đầu ra: Message định dạng DiagnosisCompleteMsg { root_cause, affected_modules, fix_strategy }
Phụ thuộc: Module 7, 3

Chức năng chi tiết:
  - Kết nối cấu trúc Diagnostic Tree → Phát hiện ngọn nguồn của Lỗi Dịch (Sử dụng Rule-based mapping và Machine-learned heuristic).
  - Phát báo số lượng Component Modules chịu liên đới (Cascading Error Trace).
  - Ưu tiên phương án Fix (Lấy chiến dịch Action Resolve qua Module Procedural Memory).
  - Phân hạng (Rank) Độ Tín Nhiệm (Confidence Score) cho từng phương thức Fix.

Danh sách Taxonomy phân vùng Lỗi Căn Bản:
  syntax_error                  → Lỗi cú pháp biểu thức gốc
  type_mismatch                 → Xung đột kiểu dữ liệu (Mismatched typings)
  undefined_symbol              → Sai khác thư viện biến Variables/Functions imports
  circular_dependency           → Loop gãy Modules (Dependency cycles)
  effect_violation              → Vi phạm Profile System Effects Framework
  missing_contract              → Lỗi báo khuyết luồng pre/post execution conditions
  architecture_violation        → Gãy ranh phân tách Module Boundaries
  requirement_gap               → Gap khoảng trống logic lập trình yêu cầu tính năng
  test_failure                  → Gãy đổ Module Verification Test suites

Giao diện API:
  fn diagnose(outcome: OutcomeObservedMsg, world: WorldModel) -> DiagnosisCompleteMsg
  fn get_known_causes() -> List<RootCause>
```

### Module 9: Reflection Engine (Mô đun Tự Đánh Giá)

```
Nhiệm vụ: Thu thập dữ liệu Meta-reasoning để tối ưu và thay đổi trạng thái tiến bộ bản thân cấu hình agent.
Đầu vào: DiagnosisCompleteMsg, Action History Logs, Tiêu Chuẩn Kế Hoạch PlanStep
Đầu ra: ReflectionDoneMsg { insights, plan_adjustments, self_assessment }
Phụ thuộc: Module 8, 4

Chức năng chi tiết:
  - Truy vết lỗi trùng lặp đệ quy (Recurrent Pattern Failures check).
  - Thẩm định độ chuẩn xác của Planner System (Báo hiệu nếu Lộ trình Kế Hoạch Plan ko khả thi thực chiến).
  - Sàng lọc và cảnh báo về mức độ Performance của mô hình hiện đại.
  - Can thiệp đề xuất bổ sung thêm Steps Cận Vệ Back-up Plan nếu bắt nhận lỗ hổng Logic Plan cũ.
  - So khớp lại độ tương quan với dữ liệu cấu trúc Historical Event Pattern trong quá khứ.

Giao diện API:
  fn reflect(diagnosis: DiagnosisCompleteMsg, history: ActionHistory) -> ReflectionDoneMsg
```

### Module 10: Lesson Learner (Mô đun Trích xuất Cấu Trúc Khối Bài Học)

```
Nhiệm vụ: Chuyển đổi dữ liệu Reflection thô sơ thành Structured Rule Pattern (Lesson Unit).
Đầu vào: Khối ReflectionDoneMsg, Tập Record Episodes
Đầu ra: Message định dạng LessonExtractedMsg { lessons, confidence, applicability }
Phụ thuộc: Module 9

Chức năng chi tiết:
  - Render thông số dữ liệu Insights → Đúc khối Bài Học Pattern Hóa (Lesson Formatted Schema).
  - Khởi tạo nhãn tính phân định Confidence Score (Dựa trên thông kê Evidence Trọng Số Mật độ Mẫu Code Vượt Qua).
  - Xếp định thẻ Tags Scope Context (Hoàn cảnh tương ứng để kích hoạt rules bài học).
  - Tạo rào định Tuyến (Deduplication Check) khi phân lọc Lesson đã tồn kho → Cập nhật Index Thống kê Evidence ++ lên cọng Lesson Data DB.
  - Đẩy Flag Cảnh Báo Lỗi về Khối Memory Resolution nếu bắt tín hiệu mâu thuẫn hệ điều quy.

Schema Chuẩn của Lesson Block Unit:
  context           → Điều kiện bối cảnh dự án
  problem           → Đặc thù mã Vấn Đề Bug Error Issue Exception Type
  root_cause        → Căn cơ chốt lõi ngầm
  solution          → Giải phương Mẫu đệ trị fix Pattern
  confidence        → Điểm Tự Tín Xác Nhận Định Mức ML Scoring
  evidence          → Bằng Chứng Số lượng UUID Episodes Reference
  applicability     → Trải dài Hệ Profile Limits Constraint Scope Range Domain

Giao diện API:
  fn extract_lessons(reflection: ReflectionDoneMsg, episode: Episode) -> List<Lesson>
```

### Module 11: Memory Assimilator (Mô đun Đồng Hóa Bộ Nhớ Cấu Trúc Mới)

```
Nhiệm vụ: Thẩm định giá trị lưu trữ và Đồng Hóa Nạp data (Assimilate Data) vào DB Database RAM.
Đầu vào: Dạng Message LessonExtractedMsg
Đầu ra: Thẻ Message MemoryUpdatedMsg { new_entries, promoted, conflicts_resolved }
Phụ thuộc: Module 2, 10

Chức năng chi tiết:
  - Khởi Lưu (Persist) Episodes Data luân chuyển vào Không gian Episodic Memory Node Layers.
  - Phân tích đánh giá chuẩn Promotion Metric → Đẩy (Promote) Khối Cấu Học Tốt Nhập Khu Đất Semantic Rule Core DB.
  - Xét duyệt gỡ rối Xung Đột (Resolve conflicts) cấu trúc giữa các Pattern Lesson Tương tự khác bối cảnh Context.
  - Nhập trát Procedural Memory nếu hệ Model gom độ tương đồng đa Project Levels.
  - Thiết lập thông số bảo mật Ràng Chống Quên EWC Elastic Regularize Weights Penalty (Chống Catastrophic Forgetting).

Giao diện API:
  fn assimilate(lessons: List<Lesson>, episode: Episode) -> MemoryUpdatedMsg
```

### Module 12: Report Generator (Trình Trích Lưu Sinh Báo cáo)

```
Nhiệm vụ: Viết xuất file Docs Metadata (Markdowns/Logs files) tương thích giao tiếp User Interface.
Đầu vào: Màng WorldModel, Data Hệ Lên Kế Hoạch Plan, Memory Buffer Data, Chuỗi Lệnh Lessons Learn
Đầu ra: Cấu trúc Document Report (markdown file format), AI Handoff Giai Khúc Context Bundle.
Phụ thuộc: Module 2, 3, 4

Chức năng chi tiết:
  - Xuất bản tài liệu cấu trúc (Architecture Specifications documents generation).
  - Kết xuất Code Trace Coverage File báo cáo lưới giăng module.
  - In ấn sổ tay Lessons Learned Report Matrix file.
  - Cập Nhật Bảng Progress Report Checkpoints (Status Trackers Sprint Board).
  - Tự Động Xây Luồng Handoff System Context Configuration (Bundle AI Memory Cache context cho phiên chuyển giao AI agent sau đó).

Giao diện API:
  fn generate_report(type: ReportType) -> Report
  fn generate_all_reports() -> List<Report>
```

## 4. Tóm Tắt Quy Trình Luồng Dữ Liệu Liên Kết (Data Flow Pipeline)

```
Tiến trình Nhận Yêu cầu Công tác (User Task Initiate)
  → [1] Module Goal Interpreter → Tín hiệu GoalParsedMsg
  → [2] Module Memory Manager → Tín hiệu MemoryRetrievedMsg
  → [3] Module World Model Builder → Tín hiệu WorldModelUpdatedMsg
  → [4] Module Planner → Tín hiệu PlanCreatedMsg
  → [5] Module Policy Engine → Tín hiệu ActionSelectedMsg
  → [6] Module Action Executor → Tín hiệu ExecutionResultMsg (Tương tác vật lý tới Compiler COPL)
  → [7] Module Observer → Tín hiệu OutcomeObservedMsg
  → [8] Module Diagnoser → Tín hiệu DiagnosisCompleteMsg (Kích hoạt khi gặp trạng thái Error)
  → [9] Module Reflector → Tín hiệu ReflectionDoneMsg
  → [10] Module Learner → Tín hiệu LessonExtractedMsg
  → [11] Module Assimilator → Tín hiệu MemoryUpdatedMsg
  → [12] Module Reporter → File Document Reports Outcome System
  → Vòng luân hồi Loop Replay quay trở lại Node [4] hoặc Node [5] để kết thúc điều kiện (goal satisfied condition).
```

## 5. Phương Lược Xử Lí Ngoại Lệ (Exception & Fallback Error Handling)

```
Khi Mạng Lưới Kiến Trúc Chặn Phát Lỗi Component Gặp Bug Hệ Thống (Module Exception Code Crash):
  1. Module cô lập sinh Error Message File (module name, stack traces input, local exception block log file event tracing).
  2. Broadcasting ErrorMsg tới Hệ Quản Trị Trung Tâm (Central Event Bus) → Nâng cao Cảnh giác Awareness Modules Blocks System.
  3. Áp Dụng Chế Độ Trượt Thoát Lỗi Mềm Tử Hệ System (Fallback execution policy paths):
     - Action Executor: Áp dụng Retry loop policy mechanism thắt hẹp cấu hình Action Limit.
     - Diagnoser: Chuyển vị thông số Lỗi Mờ "Unknown" Root Cause Index Classification.
     - Policy Engine: Chấp nhận lựa chọn Action an toàn Null Mode/ No-op operation / Undo revert git checkouts rollbacks logic block.
     - Hành Trình Planner: Tích Chọn Block dấu X Cờ Đỏ đánh trượt (Mark Failed Status) và chuyển trỏ nhánh Point Plan node next check steps logic steps routing execution.
  4. NGUYÊN LÝ THIẾT YẾU CỐT LÕI (INVARIANT RULE): Không Hệ Điểm Nào Trên Network Module Agent Loop Được Phép Dẫn Sự Cố Nút Cổ Chai Trỏ Sập Tịt Node Agent Loop Pipeline (Zero-Crash Agent System Protocol Tolerance Limit Policy Level Constraint).
```
