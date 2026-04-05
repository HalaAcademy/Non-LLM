# Đặc tả Kiến trúc GEAS (GEAS Architecture Specification)
## Chi tiết 12 Module Lõi — Khắc phục G3: "Thiếu giao thức liên kết giữa các module"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Nguyên lý Kiến trúc

1. **Điều hướng qua Tin nhắn (Message-Driven)**: Các Module giao tiếp truyền tải độc quyền qua các gói tin nhắn (typed messages), cấm xài chung state chồng chéo.
2. **Khả năng Phục dựng (Replay-able)**: Toàn bộ messages được lưu dập log → Cho cớ rà soát dựng lại y đúc mọi luồng tái lưu về sau.
3. **Mô-đun cắm ráp (Pluggable)**: Mọi chiếc module đóng giao thức interface kín cổng → tha hồ tráo gỡ implementation thay lõi.
4. **An toàn Chống Chết Chùm (Fail-Safe)**: Module lỗi ngắt gãy sập sẽ không kéo theo chết ngỏm toàn mạng loop của agent.

## 2. Sơ đồ Quan hệ Module (Dependency Graph)

```
                    ┌─────────────────┐
                    │   NGƯỜI DÙNG    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  1. Phiên dịch  │
                    │    Mục tiêu     │
                    └───┬─────────┬───┘
                        │         │
              ┌─────────▼──┐  ┌──▼──────────┐
              │ 2. Quản lý │  │ 3. Xây World│
              │  Bộ Nhớ    │  │ Model Cảnh  │
              └─────┬──────┘  └──┬──────────┘
                    │            │
                    └──────┬─────┘
                    ┌──────▼──────┐
                    │4. Bộ Chỉ Huy│
                    │ Lên Kế Hoạch│
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │5. Động Hệ   │
                    │ Chính Sách  │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │6. Tay Sai   │────► Nền tảng COPL
                    │ Thi Hành    │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │7. Kẻ Dò Vết │◄─── Trả kết quả Compiler
                    │ Quan Sát    │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │8. Chuyên gia│
                    │ Chẩn đoán lỗi
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │9. Cỗ Máy    │
                    │ Tư Duy Ngẫm │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │10. Học Viện │
                    │ Trích Bài   │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │11. Kẻ Nạp   │
                    │ Ký Ức       │
                    └──────┬──────┘
                    ┌──────▼──────┐
                    │12. Chuyên   │
                    │ Sinh Báo Cáo│
                    └─────────────┘
```

## 3. Đặc tả Từng Module Điểm

### Module 1: Goal Interpreter (Diễn dịch Mục tiêu)

```
Nhiệm vụ: Parsing giải nghĩa yêu cầu thô sơ của User → Rút trích ra Yêu cầu Chuẩn + Ràng Thuộc Constraints.
Đầu vào: Thông báo Task chay (text/JSON)
Đầu ra thẻ Message: GoalParsedMsg { requirement_graph, constraints, missing_info }
Phụ thuộc: None (Vì là chóp đón điểm vào tiên phong)

Chức trách:
  - Phân tích cữ văn tự nhiên nhập viện của task
  - Ép ra các Yêu cầu Nghiệp vụ
  - Ép ra các Điều kiện phi hàm (chuẩn MCU limit, safety limit)
  - Thấy Cấu trúc mờ mịt → bật câu hỏi phản vệ hỏi ngược User clarify
  - Vẽ sơ đồ mạng yếp cầu rễ ban đầu

Giao diện gọi API:
  fn parse_goal(task: Task) -> GoalParsedMsg
  fn clarify(questions: List<Question>) -> GoalParsedMsg  // Bước sau khi nhận User hỏa mù trả lời
```

### Module 2: Memory Manager (Bộ Quản Lý Nhớ)

```
Nhiệm vụ: Cất giữ, Tìm dò, Nắm chóp toàn bộ buồng tầng trí nhớ memory.
Đầu vào: Yêu cầu MemoryQuery, Chuỗi Episodes, Chuỗi Lessons.
Đầu ra thẻ: MemoryRetrievedMsg { relevant_episodes, lessons, procedures }
Phụ thuộc thiết yếu: DB SQLite, Nhạc cụ lõi embedding model

Chức trách:
  - Giữ rương trọn gói chuỗi hồi ký (episodic memory)
  - Giữ nhót bảo vệ rương quy y (semantic memory)
  - Giữ nắp vòm sổ tay quy trình (procedural memory)
  - Nghếch móc lôi ra các khối memory hợp cảnh từ truy vấn query tống xuống
  - Dãn gỡ mâu thuẫn cho những cuộn lessons chĩa mũi dùi đâm lẫn nhau
  - Cứa xén ném kho archive dọn mảnh rác trí nhớ nhăn nheo thừa thải
  - Lôi lấy chóp cành mã branch-aware retrieval

Giao diện:
  fn store_episode(episode: Episode) -> EpisodeId
  fn store_lesson(lesson: Lesson) -> LessonId
  fn retrieve(query: MemoryQuery, top_k: int) -> MemoryRetrievedMsg
  fn resolve_conflict(a: Lesson, b: Lesson, ctx: Context) -> Lesson
  fn compact() -> CompactionReport
  fn get_stats() -> MemoryStats
```

### Module 3: World Model Builder (Kiến Thiết Trạng Thái Thế Giới)

```
Nhiệm vụ: Giữ Rõ Sợi Dây Lập Bảng Mô Hình Định Danh toàn khối code project state.
Đầu vào: Mã SIR nén ngầm từ COPL compiler, Trạng thái xoay vần file system.
Đầu ra thẻ: WorldModelUpdatedMsg { project_graph, changes_since_last }
Phụ thuộc trói: Cáp Truy Vấn Thông SIR COPL Query Interface (Hợp đồng #1)

Chức trách:
  - Xây trát Sơ đồ Project graph dệt từ chuỗi mã SIR
  - Khới cọc theo dõi vết độ chín modules, dependencies, độ lấp test trace coverage
  - Canh phao chống thưa trượt drift khi lấn sửa files
  - Dâng API query cắm rễ chọc tìm cấu hình mống project

Giao diện:
  fn build_from_sir(sir: SIRWorkspace) -> WorldModel
  fn update_incremental(sir_diff: SIRDiff) -> WorldModelUpdatedMsg
  fn query_module(name: str) -> ModuleInfo
  fn query_dependencies(name: str) -> List<Dependency>
  fn get_project_health() -> ProjectHealth
  fn sync_check() -> SyncResult
```

### Module 4: Hierarchical Planner (Quản Trị Kế Hoạch Đa Tầng)

```
Nhiệm vụ: Cắm đinh thả giòng Tạo lặp quy củ nhiều tuyến Task phân rã màng multi-level.
Đầu vào: Lõi GoalParsedMsg, Sa bàn WorldModel, Buồng nhớ hệt MemoryRetrievedMsg.
Đầu ra thẻ: PlanCreatedMsg { phases, current_step, estimated_completion }
Lực bám Phụ thuộc: Khối Module 1, 2, 3

Chức trách:
  - Rã nát Goal → các luồng phases → tác nháp tasks → chia ngóc steps
  - Đi xâu dọc theo thứ tự khóa lệnh rào module dependent (bắt chóp rễ ngược bottom-up cho nền tảng khối layered)
  - Gánh thước đo hao tốn effort per task
  - Trông giữ cảnh giác chọc thủng rác nghẽn task do đợi code bám chéo
  - Gõ kẻ lại bài plan lúc thấy sai hoặc được dấm thêm thông tin mới

Giao diện:
  fn create_plan(goal: GoalParsedMsg, world: WorldModel, mem: MemoryRetrievedMsg) -> Plan
  fn get_next_step() -> PlanStep
  fn replan(reason: ReplanReason) -> PlanRevisedMsg
  fn mark_step_done(step_id: StepId) -> Plan
  fn get_progress() -> PlanProgress
```

### Module 5: Policy Engine (Động Cơ Chọn Cơ Chế Đi Tiếp)

```
Nhiệm vụ: Lựa đong nẩy số chỉ Điểm Cú Hành Động (Action) tối ưu trong hoàn bích cục diện.
Đầu vào: Mắt Xích PlanStep, Khối Thế Giới WorldModel, Túi khôn MemoryContext.
Đầu ra: ActionSelectedMsg { action, confidence, reasoning }
Phụ thuộc: Não Model Nơ ron Neural Mạng Core Model, Module 2, 3, 4

Chức trách:
  - Bọc nén cấu đồ State → Thả vào Input cho Model nuốt
  - Chạy mô phỏng vòng đệm đánh thông forward pass → Bán kính phổ rải hành động action
  - Giáng phán Quyết chọn (Bốc thủ khoa argmax hay đùn bốc mẫu)
  - Vẽ nắn lý do bào chữa reasoning minh bạch cớ tại sao chọn nhịp cờ đó
  - Lệnh khóa cổ cấm luẩn quẩn mắc kẹt vòng loop (Cấm sủa lại đòn trật lẫy)

Giao diện:
  fn select_action(state: AgentState) -> ActionSelectedMsg
  fn get_action_space() -> List<ActionDef>
  fn update_policy(lesson: Lesson) -> None  // Online bồi trích đắp trí khôn
```

### Module 6: Action Executor (Tên Đao Phủ Xuất Trảm Lệnh Thực Hành)

```
Nhiệm vụ: Mân mó Bóp cò đánh cờ chạy Action phập trực tiếp trên COPL nền tảng.
Đầu vào: Lệnh ActionSelectedMsg
Đầu ra: ExecutionResultMsg { outcome, artifacts_changed, duration }
Phùng Hợp Cắm Chốt: Hợp Tác Kẽ Lệnh COPL Action (Chợp hợp Đồng Hợp Tác #4)

Chức trách:
  - Dốc ngược Ý đồ siêu thực abstract action → Xuống hành vi vật lý máy móc COPL operation
  - Nã Gõ/Viết Mới lên file source cục diện .copl
  - Ngéo cò kẹt bắn COPL compiler (bồi mồi nốc build, check test, xả artifacts)
  - Nuốt chửng thông quản đầu móm output của file lệnh rớt xuống (từ rãnh báo lỗi stderr, hòm stdout)
  - Giữ cầu an toàn Timeout

Bổ cày Action catalog phân dải:
  create_module(name, content)      → xuất thả tay gõ .copl file
  modify_module(name, patch)        → trét áp đắp vữa sửa changes
  delete_module(name)               → tước đao xé thẻ file
  build(target)                     → bóp sườn gáy gọi copm build
  build_check_only()                → gióng dò check lỗi mã type, syntax check
  run_tests(suite)                  → xòe mở test runner
  emit_artifacts()                  → gõ máy artifact engine gõ tôm
  query_sir()                       → nhấc xem bói SIR snapshot snapshot

Giao diện:
  fn execute(action: Action) -> ExecutionResultMsg
  fn get_supported_actions() -> List<ActionDef>
```

### Module 7: Outcome Observer (Thẩm Khảo Quan Trắc Kết Cục)

```
Nhiệm vụ: Duyệt Nhìn Lỗ Vết Quét Rác Kết Cục Outcome đánh mấu trúng trật.
Đầu vào: Thông báo mớ hỗn ExecutionResultMsg
Đầu ra: Trả bảng OutcomeObservedMsg { outcome_class, diagnostics, metrics }
Giao Kết: Trạm nhận Lỗi từ Hợp đồng COPL Diagnostic (Hợp đồng Cắm chéo số #2)

Chức trách:
  - Ép phân loại hậu vận outcome: Thắng success | Rách Biên dịch compile_error | Tổn kiểu type_error | 
    Trật Hiệu ứng effect_violation | Rớt Test test_failure | Trôi Giờ timeout | Chịu mù unknown
  - Kéo bảng chữ lèo bèo dài sòng diagnostics mớ xá từ compiler → Dịch mã lại dễ hiểu
  - Soát gác đo điểm hệ metrics (Mất nhiêu phút Compile compile time, chỉ số độ test càn lướt)
  - Nắm chóp thụt lùi ngáng Regression báo hiệu đợt lỗi ma quỷ lạ hoắc nhú ra

Giao diện:
  fn observe(result: ExecutionResultMsg) -> OutcomeObservedMsg
  fn classify_outcome(result: ExecutionResultMsg) -> OutcomeClass
```

### Module 8: Diagnoser (Khoa Bệnh Học Phân Tích Lỗi Tiên Môn)

```
Nhiệm vụ: Trảo Gốc Cạo Cội rễ Tận rốn nguồn mắc mọt Root cause khi nảy sinh thất bại.
Đầu vào: OutcomeObservedMsg mớ quan sát lỗi, Sa bàn WorldModel, Tiểu sử Action vung tay vòng trước
Đầu ra: Trả phiến bài DiagnosisCompleteMsg { root_cause, affected_modules, fix_strategy }
Dính líu: Hệ Module 7, 3

Chức trách:
  - Bản họa triệu chứng bug → Móc nọc găm Rễ căn Root causes (Rà rule vạch hoặc rà mớ rút ruột máy learned)
  - Nhận điểm nhúm nhóm các module điếc đặc từ hiệu ứng lỗi liên ca chùm
  - Phím mớm cách Fix cứu cánh (gọi viện quân từ procédural memory nhả bài xài mẹo)
  - Xốc bài Xếp hạng mẹo fix (Rank fix) theo dòng suy nghĩ tính thành công

Kiểu mục Taxonomy Rễ Root Cause Thẩm Đinh:
  syntax_error (cú pháp thúi)           → sửa gõ lại expression
  type_mismatch (lệch tone kiểu)        → lót chỉnh annotation hay nhét đệm giá trị
  undefined_symbol (mất hút hình thù)   → bơm cấy import hoặc khai biến define
  circular_dependency (lặp ngáo quẩn)   → gỡ chóp rãnh modules đắp cấu lại
  effect_violation (hiệu ứng bị thủng)  → cạy lại profile hay tạt đường refactor
  missing_contract (thất tung giao kèo) → mớm nạp điều kiện pre/post conditions
  architecture_violation (đi bậy kiến trúc) → giật cờ thiết kế gọt lại module boundaries
  requirement_gap (kẹt lỗ hổng yêu cầu) → nặn nặn nhét nặn thêm rãnh Requirement
  test_failure (bể test ngập mặt)       → rũ bụi dò logic hoặc xốc xô nắn update test

Giao diện:
  fn diagnose(outcome: OutcomeObservedMsg, world: WorldModel) -> DiagnosisCompleteMsg
  fn get_known_causes() -> List<RootCause>
```

### Module 9: Reflection Engine (Ban Tự Kiểm Điểm Tư Duy Meta)

```
Nhiệm vụ: Suy tư, Nhìn nhận Phản ảnh (Meta-reasoning) độ đần hoặc sự nhặm lẹ sức mạnh Performance của thân chủ agent.
Đầu vào: DiagnosisCompleteMsg chẩn điểm sập lỗi, Nhật trình lôi cổ hành vi action, Phiếu ghi kế hoạch plan
Đầu ra: ReflectionDoneMsg { insights, plan_adjustments, self_assessment }
Nhờ rinh theo: Cánh tay Module 8, 4

Chức trách:
  - Suy xét dập chốt mẫu hình sai vấp mâm xôi failures (Tức có bị trúng vấp 1 lỗi té lần 2 dở không?)
  - Khoán đánh giá sự cắc cớ trong Plan đồ chất lượng (Có mờ mịt vague ko? Có chia vụn dập nham nhở ko?)
  - Đọc bóp bắt thóp điểm chí mạng yếu trong nhịp điệu strategy
  - Đàn Khải tấu Tích chỉnh bù lấp mớ plan
  - Đọ Vạch Chiến Thuật Lưỡi Hiện Hành Giăng Đối Ẩm với Phương Đồ Vết Dích Sắc Memory lịch sử từng hạ đo ván lúc thuở bé

Giao diện:
  fn reflect(diagnosis: DiagnosisCompleteMsg, history: ActionHistory) -> ReflectionDoneMsg
```

### Module 10: Lesson Learner (Cô Giáo Gõ Đầu Rút Điểm Phê Học Đạo)

```
Nhiệm vụ: Vắt ruột Ép dịch rút cục vàng Lesson Mẹo Đi Rắn structured từ kinh qua sa trường trầy trợt.
Đầu vào: ReflectionDoneMsg trích đoạn soi tâm tư, Nhật ký ngấn mã episode
Đầu ra: Phái bùa Lệnh LessonExtractedMsg { lessons, confidence, applicability }
Theo gót nương bóng: Tổ Module 9

Chức trách:
  - Pha chế Reflection Ngẫm → Thổi hồn vào khuôn đúc bài học cấu rập structured lesson
  - Tặng số phiếu chỉ điểm Tín Mệnh Giao confidence score (Dựa trên cục vàng bằng chứng đo lường)
  - Vạch rõ cõi lãnh thổ sử dụng applicability context (Luật bài này nhét lọt đánh xáp lá cà trận nào thì ăn)
  - Rà cờ phang nhận Giác: Lesson Trùng Mắt Không? → Lấy gom cọng điểm thắt điểm evidence nhét lấn
  - Thấy Ngáo Ngáo Chọi Nhầm Bài Đang Sống Cũ → Giương mỏ cờ Mâu Thuẫn báo Trạm Resolution gỡ lỗi

Khung xương Bài Lesson:
  context (Khung chóp thế vị): Mảnh miếng đệm xài cho trường hợp quái nào?
  problem (Ghút Hố Sụt): Oái oăm nào thọc bánh xe rọt?
  root_cause (Lỗi Cội Rễ): Bới vì cớ xui nào mà ngắc óc?
  solution (Cao Kiến Ngự Liều): Mũi dao bọc gân nào nín giải quật gãy nó?
  confidence (Phím Trắc Độ Thật): Đủ rổ tín nhiệm ẵm tin mình thắng hông?
  evidence (Tang Xác): Bốc ra đám rễ danh sách tập episodes xác quy cớ hụ còi
  applicability (Cột Ngắm Kềm Áp): Giới Cõi domain (embedded, CAN, safety, bla bla...)

Giao diện:
  fn extract_lessons(reflection: ReflectionDoneMsg, episode: Episode) -> List<Lesson>
```

### Module 11: Memory Assimilator (Bệ Nén Đồng Hóa Hấp Thụ Cấy Ký Ức Não)

```
Nhiệm vụ: Buông dây Cấy ép hạt nhân nảy nở bài mới vào guồng thắt dập buồng chứa hệ Memory system.
Đầu vào: Thông hàm mớm LessonExtractedMsg
Đầu ra: Thẻ phím báo MemoryUpdatedMsg { new_entries, promoted, conflicts_resolved }
Phò Tá Cho Mượn Lực: Hệ Module 2, 10

Chức trách:
  - Cất hòm Cất Giấu chòm dải episodes cho thẳng ruột nạp buồng trải nghiệm episodic memory
  - Điểm nhẵn điểm độ rà check xem Lesson có đắc đạo nhảy đẳng lên cấp phật semantic promotion ko
  - Giải cứu Vong lặp đấu đá Xung Đột mưu trí chéo nhau ngang ngược
  - Châm ngấm nặn Procedural rương tay nghề nếu đánh hơi nhịp pattern đi vóng sóng
  - Bắn Áp mài Bơm ép độ giãn cơ regularize EWC (đè quên lỏng não) thả giọt vào chóp model weights weights

Giao diện:
  fn assimilate(lessons: List<Lesson>, episode: Episode) -> MemoryUpdatedMsg
```

### Module 12: Report Generator (Vòi In Bản Thiết Khai Báo Cáo Document)

```
Nhiệm vụ: Quay In Bơm Gập Xếp Giấy Cấu đồ Artifacts Rõ Nghĩa Để Loạt Mắt Chữ Human Con người ngấu nghiến.
Đầu vào: Bản Bố WorldModel, Đồ án Plan, Khối Màng Não Memory, Cụm Nhả Lessons
Đầu ra: Reports văn chỉ (markdown), Cụm Xả dọn chòi chứa AI bundle đẩy gói
Ghế Nắp Nâng Phụ Thuộc: Khóm Module 2, 3, 4

Chức trách:
  - Cuộn Xả Reports văn bài trúc Architecture
  - Bọc Trát Trừu phủ Trace coverage (báo màng lưới rà rách)
  - Thả Khía Cuộn Bài Học Phơi Bày Ngọt Rẽ lessons learned report
  - Tống Gắn Đuôi Báo Cáo Chuyển Động Chấm progress report
  - Chạm Mớ Bundle AI Update mới toanh tươm tất dâng Cúng bàn giao Chuyển kíp gác chéo ca handoff

Giao diện:
  fn generate_report(type: ReportType) -> Report
  fn generate_all_reports() -> List<Report>
```

## 4. Tóm Vạch Dòng Nước Lệnh Luân Lưu (Data Flow Summary)

```
Chạm Đạt Từ User Task
  → [1] Module Goal Interpreter nhấp vạch → Nẩy thẻ GoalParsedMsg
  → [2] Buồng Cội Memory Manager lật giở → Trích dẫn MemoryRetrievedMsg
  → [3] Bàn Trác World Model xây vạch → In Cảnh WorldModelUpdatedMsg
  → [4] Tướng Mưu Planner Trải Lộ → Hạ lệnh PlanCreatedMsg
  → [5] Kín Định Policy Cân Não Phân Kế → Rút thẻ ActionSelectedMsg
  → [6] Tên Cấm Vệ Executor Hành Lệnh → Chui Ống Kết Quả ExecutionResultMsg (Dùng sức thông qua COPL)
  → [7] Lưới Quan Sát Observer Ngó Lủng → Ghim Tín Chớp OutcomeObservedMsg
  → [8] Bác Sĩ Diagnoser Bắt Mạch Bệnh → Phán Bản DiagnosisCompleteMsg (Dùng khi Thất trận failure)
  → [9] Túi Khôn Reflector Nằm Suy Sụp Tỉnh Ngộ → Rút Lọc ReflectionDoneMsg
  → [10] Phủ Đạo Learner Thấm Nọc Kinh Điển → Gặt Hái LessonExtractedMsg
  → [11] Tẩy Hồn Nạp Assimilator → Chôn Cất Quả Túi MemoryUpdatedMsg
  → [12] Vòi Reporter Sục Tăm In Báo → Nhả Cáo Reports
  → Vòng Chuyển Bánh Canh Dẫn Lại Chóp Bước loop [4] hoặc tua [5] Cho Tới Khi Cắn Trái Đạt Phỉ goal satisfied mãn nguyện
```

## 5. Thể thức Bơm Trụ Cách Xử Lỗi Kẹt Chéo Các Hệ Module Nhau (Error Handling)

```
Ngộ Nhỡ Tới Khúc Có Một Đứa Module Tự Đu Mình Ném Lỗi Nổ Bug exception gãy xương:
  1. Hãy Chập Nén Lỗi Phích kèm Rổ Mốc Thời Điểm (module, input, stack trace) đánh log
  2. Tung Còi Băm Tín Xâm Lan Lỗi Phím ErrorMsg cho Toàn Trạm bus → Kể cả Cả Dàn modules nắm tróp xững Cáo awareness
  3. Bật Phích Bọc Khung Bền Hạ Độ Lún Trật Đi Fallback (Kiểu thoát lùi thân):
     - Tại chóp Đao Phủ Executor: gồng sức gõ nếp lại Retry nhè nhẹ kéo co action ốm bé mọn hẹp lại 
     - Mắt Y Lý Diagnoser: ngậm cục nghẹn đẩy mã mắm "unknown" dán mù root cause cắm nhăng cho xong
     - Cục Chóp Policy: Gắp Rút chóp lá chắn phòng thủ Action nhét mình rút mai rùa (no-op im ngủ hay lòi điếc undo)
     - Khối Trí Đạo Planner: Nện còng tay phế ngay cái điểm nhịp Blocked vào plan current step, rục rịch xách màng thử đi sang rẽ nhánh gõ the next kế tiếp
  4. TUYỆT PHÁP Đóng Thép: Không bao giờ được phép để sập cái lọng vòng tua vĩnh viễn crash chết đứng của đại não agent loop.
```
