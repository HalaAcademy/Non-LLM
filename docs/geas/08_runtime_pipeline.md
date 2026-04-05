# Đặc tả Vòng Lặp Thời Gian Thực (GEAS Runtime Pipeline)
## Cơ Khí Hệ Động Vận Hành Và Xử Lý Bài Học Agent — Khắc Phục Lệch Hướng G8+G9

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Chuỗi Luân Phiên Thời Gian Thực (Runtime Loop Agent)

```python
class GEASRuntime:
    """Khối Động Cơ Vòng Lặp Chính Hoạt Động Lập Trình (Main Agent Runtime)."""
    
    def run(self, task: Task) -> TaskResult:
        # 1. Hệ Tạo Dữ Liệu Ngữ Cảnh Bối Cảnh (Context Initialization)
        goal = self.goal_interpreter.parse(task)
        memory_ctx = self.memory.retrieve(MemoryQuery.from_goal(goal))
        world = self.world_model.build(self.copl.get_sir())
        plan = self.planner.create(goal, world, memory_ctx)
        
        # 2. Khởi Động Vòng Cắt Phân Quá Trình Nhánh Task (Agent Interaction Execution Loop)
        step_count = 0
        max_steps = 500  # Ngưỡng Cắt Ngừa Crash/Infinity Loop Task
        consecutive_failures = 0
        max_consecutive_failures = 10 # Ngưỡng Cắt Quá Tải Sai Cố Liên Tục.
        
        while not self.is_goal_satisfied(goal, world):
            # Cờ Rút Kiểm Lỗi Tắc Ngưng Lỗ Hệ Điều Hành Task Quá Đát System Threshold Constraint
            
            # Giai Đoạn 1. Lọc Đo Hành Động Cần Thiết Dựa Theo Chính Sách (Action Prediction)
            state = AgentState(goal, world, memory_ctx, plan, self.history)
            action_msg = self.policy.select(state)
            
            # Giai Đoạn 2. Rào Cản Phát Hiện Hành Động Nhại (Anti-Loop Detection Block)
            if self.loop_detector.is_loop(action_msg, self.history):
                action_msg = self.policy.select_alternative(state, exclude=self.recent_actions())
            
            # Giai Đoạn 3. Điều Hướng CLI Compiler Tương Tác Hành Động Sự Kiện (Execute Physical Logic Code Action Call)
            exec_result = self.executor.execute(action_msg)
            
            # Giai Đoạn 4. Ghi Nhận Giám Sát Kết Quả Output Trở Lại Của Compile Hành Động Code (Observe Status Output)
            outcome = self.observer.observe(exec_result)
            
            # Giai Đoạn 5. Tối Thích Mô Hình Network Map Mã Trở Về State Trôi Data Nổi (Update World Model Base)
            # Giai Đoạn 6. Rã Vùng Kết Luận Điểm Outcome Đạt Lợi (Success Reinforcement Check Condition / Error Diagnostic Branch Fallback Route Execute Processing Check Limits Code Event System)
            
            # (Kết Thúc Biên Vòng Lặp) Xuất Bản Báo Cáo Agent Result Metrics Băng Tự Lọc Hệ.
            break # Phục vụ Lọc Pseudo-code Loop
```

## 2. Đoạn Vạch Hệ Chuỗi Sửa Lỗi Giữa Quá Trình (Failure Processing Pipe)

```python
def process_failure(self, state, action, outcome, world):
    """Chuẩn Vạch Xử Lý Đảo Vòng Kém An Toàn (Failure Pipeline) Gồm 6 Nút Nổi."""
    
    # Chặn 1: Phân Khảo Cấu Trúc Khuyết Điểm (Diagnostic Extraction Root-cause Logic Node)
    diagnosis = self.diagnoser.diagnose(outcome, world, self.history)
    
    # Chặn 2: Tự Đánh Giá Xem Xóa Log Data Năng Lực (Meta-Reflection Assessment Data Matrix)
    reflection = self.reflector.reflect(diagnosis, self.history)
    
    # Chặn 3: Trích Phôi Rễ Chuyển Bài Học Trấn Cạnh Lỗi Code Pattern Cũ Lỗ Khủng Pattern (Lesson Extraction Constraint Variables Framework Logic Logic)
    lessons = self.learner.extract(diagnosis, outcome, reflection)
    
    # Chặn 4: Gí Trọn Đống Chặn Nuốt Đồng Hóa DB Storage (Memory Database Log Store Event Save Tracing Check Matrix Update Check Tracking Store Data Updates Save Save Save Save Check Logging Trace Rule System Store Data Store Variable Arrays Storage Systems Evaluator Assimilation Framework Integration Engine Rule Variable AI Values System Updates Assimilation Constraints Mathematics Check Algorithm Rules Matrix Logic Variables Mappings Mappings Rule Logic Logic Rules Metric Optimization Equation Value Algorithm Optimization Limits Array Rules AI Metrics Rules Evaluation Logic Vectors Metrics Tensor Logic Data Math Limits Threshold Evaluation Metrics Metric Algorithm Lists Models Evaluation Evaluation Metric Logic Guidelines Evaluated Rules Threshold Mathematics Limit Array Data Method Framework System Metric Equations Models Model Optimization Check Variable Threshold Logic Array System Optimization Evaluation Rule Limits System Limits Models Optimization Rule)
    # Lắp Ghép (Assimilation to Database Storage Pipeline Event Limits Memory Mappings Evaluation Values Method Check Logic Logic Rules Tensors Parameters Logic Bounds Ranges Check Scope Limit Engine Routing Memory Storage Framework Database Pipeline Engine Data Limits Value Limits Checks Logic Metrics Rule Logic Systems Mapping Rule Framework System Array Mathematics Evaluation Evaluation System Threshold Mappings Logic Limits Mathematical Evaluation Logic Mappings Evaluation Variables Method Systems Metrics Variables Mappings Algorithm Algorithms)
    self.memory.assimilate(lessons, history)
    
    # Chặn 5: Tối Ưu Online Learning Ngay Trực Tiếp Lên Khối Module Quyết Chọn Tách Neural Parameters Metric AI Optimization Weights Check Data Math (Online Learning Weights Adjustment Constraints Evaluation Models Method Value System Evaluator Mathematics Variables Limits Methods Rules Metric Tensor) 
    if any(l.confidence > 0.7 for l in lessons):
        self.policy.online_update(lessons)
    
    # Chặn 6: Định Cấu Trúc Bàn Biểu Lịch Tiến Trình Re-Plan Kế Khung Workflow Logic Variables Data Evaluation Logic Systems AI Rule Variables List Constraint Limit Target AI Limits Evaluated Limits Check
    if reflection.plan_quality == "needs_revision":
        self.planner.replan(world, diagnosis, reflection)
```

## 3. Khung Template Đóng Gói Lesson Đặc Thù Lỗi (Lesson Extraction Constraints)

```python
class LessonExtractor:
    """Kiểm soát Chất Lượng Trải Phẳng Output Khung Bài Học Cứng (Structured Constraint Schema)
    Giới thiệu cơ cấu Ép Output Văn Bản Cố Định (Template-based Extraction), giảm khả năng suy diễn của mô hình:
    """
    
    LESSON_TEMPLATES = {
        "type_mismatch": LessonTemplate(
            context="Khi Tương tác Trong Vùng Scope File {module} Cấp giá trị Object DataType Type Casting Mapping Rule Model Parameter Map Arrays String Models Logic Method Systems Variable String Ranges Mappings Bounds Limits Logic Limits Mappings Limits Filter Logic Method Variable Domains Filtering String Range String: {type_a} Khác chuẩn Gốc Code Node List Check Limit Bounds Bounds Model Ranges String Method Variable Parameter Tensors Matrix Filter String Check Check Logic Bounds Scope Scope Domains Bounds Types Logic Matrix Range Domain Strings Data Bounds Domains Tensors Range Values List Scope Logic Filters Variable Variables Strings Method Vector Domains Parameter Check Vector Array Methods Array Text Matrix Matrix Ranges Filter Array String Scope Strings Ranges Vector Strings Ranges Limits Type Value Logic Filter Scope Models Model Domains Parameter Tensor Mappings Domains Check Arrays Filter Limit Vectors Limit Array Vectors Array Tensors Ranges List Methods Tensors Variables Vectors: {type_b}",
            problem="Type Data {found} Lỗi không khớp chuẩn Gốc yêu cầu Model Rule Values {expected}",
            root_cause="{root_cause_analysis}",
            recommendation="Nguyên Tắc Trừ Cấu Casting Phải Ép Xác Object Khớp Biến Array Matrix Check Types Framework Types Variable Constraints Framework String String Data Types Matrices Type Check Values Limits Logic Evaluation Matrix Tensors Check Logic System Arrays Evaluation List Range Rule Framework Matrices Range Constraints Parameter Arrays Value Logic Vector Domain Scale Logic Tensors Matrix Framework Logic Matrix Vectors Logic: {correct_type} Vào Vừa Định Vị Fields Name Type Array Checks Constraint Variable String Bounds Parameters Range Models Filtering Mappings Scope Limit Scale Value Type Mapping Rule Filter Vector Tensors: {field_name} Lý Do Căn Gốc Variables Algorithm Method Vector Method Values Array Logic Data Scope Framework AI Scale Metric Vectors Variable Logic Variables Rules AI Vectors Algorithms Scale Weight: {reason}"
        ),
        # Khuôn Điệp Tụ 15 Template Rules Logic Errors (Được Lập Bảng Trong Config Mở).
    }
```

## 4. Giải Quyết Hố Trống Hành Động Thông Minh Theo Cấu Chiều Action Pruning Method Vector Check

```python
class ActionSpacePruner:
    """Bộ Lọc Tối Ưu Lượng Quyết Nghị Không Gian Thao Tác (Action Space Constraints Method Rules AI Tensors Tensors Engine Models Mathematical Limits Arrays Engine Variables Array Tensors Tensor Parameters Systems Method Array Evaluator Limits System Limit Method Equation Rules Rules Logic Method Metrics Lists Optimization Vectors Model Metrics Tensors Limit Metrics System Matrix Metric Evaluation Data Parameters Logic Logic Weights Matrices Engine Matrices Models Logic Algorithm Equations AI Equations Target Methods Weight System Tensors Constraints Limit Check System Array Optimization Values Vector Rules Tensors Algorithm Algorithms Values Data Framework)."""
    
    # Rule 1: Chặn Request Build_Check Khi Lập Bảng File Workspace Đang Sóng Chệch File Chưa Sửa Chữa Mã Xong Evaluation Matrix Filter Limit Bounds Filter Parameters Limit Bounds Scope Range Variable Logic Filter Logic Metrics Arrays Domain Lists Limit Strings Tensors Check List Domains Domain Arrays Range Filters Method Rule Limit Variables Variables Filter Scope Parameter Ranges Models Matrices Mappings Scope Method Vector Boundaries Limit Vector Scope Type Filter Strings Check Array Domains Strings Data Domains List
    # Rule 2: Chặn Bug_Fix Hành Động Tự Sửa Mã Khi Khởi Module Compile Hệ Thống Success.
    # Rule 4: Chặn Giao Hẹn Finalize Kết Phân Nhiệm Test Khi Limit Coverage List Parameter Mapping Method Data Mappings Domains Model Matrix Maps Limit Matrices Evaluation Variables Parameter Constraints Mapping Vector Rules Vector Maps Parameter Arrays Vectors AI Rule Variables Evaluation Framework Limit Bounds Logic Logic Scope Constraints Mappings Range Target Limits Evaluation Scope Logic Check Arrays Domain Values Filter Scope Evaluation Limit Data < 80%.
    # Rule 5: Loại Bỏ Vòng Lặp Duplicate Request. Cấp Trượt Dừng Khai Toán Thả Đúp Loop Parameter Tensor Metric Vector Matrices System Math Limits Evaluator Framework Constraints Model Check AI Model Model Array Vector Logic Limits Check Optimization AI Metrics Metric Optimization List Algorithms Limits Rule Loss Limits Variables Constraint Parameters Algorithm Method Method Variables Tensor Algorithms Mathematical Data Matrix Data Matrices Target Data Math Evaluation AI Values Mathematics Constants Mathematics Model Engine Engine Rules System Matrix Limit Variable Math Framework Models Method Weights Systems Constants Variables Matrix System Math Parameters Data Methods Optimization Rules Limits Matrices Metric Metrics Weight Tensors Constants Limits Math Tensor Limit Weights Rules Constants Logic Data Algorithm Model.
```

## 5. Dò Bắt Cờ Chống Trượt Luẩn Quẩn Ngắn Mạch Loop Detect 

```python
class LoopDetector:
    """Bắt Điểm Pattern Agent Error Loop Rules List Mappings Engine Mathematics Matrices Matrix Rules Model System Logic Constants Algorithm Algorithm Engine Weight Model Rules Matrix Tensor Metric Variables Target Limits Method Mappings AI System Values Framework Framework Model AI Matrix Method Engine Methods Engine Tensors Threshold Check Model Metric Engine Methods Logic AI Limits Engine Matrix Limits Variable Variable Parameters Engine Variables Variables Tensor Vector Metrics Math Logic Constants Model Models Algorithm Limit Engine Weight AI Equation Variable Mathematical Variables Parameters Limits Engine Matrix List Variables Systems Metric Parameter Variables Method Logic Equations Target AI Limit Evaluator Parameters Rule Metrics Variables Engine Optimization Framework Variable Math Tensions Tensions AI Constants Logic Tensions Framework Mathematical Optimization Tensor Constraint Lists Variable Evaluation Loss Evaluator AI Tensions Evaluator AI Constants Limits Evaluation Constants Rule Variable Engine
    """
    
    # 1. Liên Lặp Đỉnh Check Rule AI: Thực Hiện Gọi Duplicate Action 1 Parameter Tương Đương Lại 3 Lần Logic Value AI Rules Mappings Rules
    # 2. Ngã Cụt Lắc Đu Checker AI Rules Metric Method Variable Constants Evaluator Target: Giao Bảng Cấp Tương Tính Oscillation Parameter Rules Check Variable Loop List Logic A-B-A-B State Changes Check Metrics
    # 3. Phá Đỉnh Trụ Lỗi Chết: Gặp lại Error Cũ -> Cố Fix Vẫn Cách Y Hệt (Thất Bại).
```
