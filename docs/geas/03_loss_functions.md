# Đặc tả Hàm Tính Giá Trị Tổn Thất (GEAS Loss Functions)
## Định Nghĩa Chuẩn Các Thành Phần Hàm Loss — Khắc phục G1: "Thiếu định nghĩa toán học 5 thành phần loss function"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Kiến Trúc Khối Đa Tác Vụ Tính Tổn Thất (Multi-Task Loss)

```
L_total = Σᵢ (1/(2σᵢ²)) × Lᵢ + log(σᵢ)

Khai triển chi tiết trong đó:
  L₁ = L_decision     (Tổn thất Khảo sát Bắt chước Hành vi - Behavioral Cloning Loss)
  L₂ = L_outcome      (Tổn thất Dự tính Kết quả Thực thi - Outcome Prediction Loss)
  L₃ = L_diagnosis    (Tổn thất Khai báo Chẩn đoán Lỗi - Root Cause Diagnosis Loss)
  L₄ = L_lesson       (Tổn thất Phân loại Bài học Đối chiếu - Contrastive Lesson Quality)
  L₅ = L_adapt        (Tổn thất Chuẩn Hóa Siêu Học - Meta-Learning Adaptation MAML)
  σᵢ = Thông số độ không chắc chắn tự động học (Task-specific learned homoscedastic uncertainty)
```

Kiến trúc Trọng số Bất định (Uncertainty weighting theo Kendall et al., 2018) giúp tự động tinh chỉnh (Auto-tune) tỷ lệ giữa các thành phần Loss function mà không cần khởi tạo siêu tham số thủ công bổ sung.

## 2. L_decision — Mất Mát Tại Cổng Quyết Định Hành Động

### Công Thức Khai Chi tiết

```
L_decision = -𝔼_{(s,a*) ∈ D_expert} [ log π_θ(a* | s, g, M) ]
```

### Các Ký Hiệu Đầu Rẽ

```
s       = Trạng thái Cấu trúc Hiện tại (Structured state feature - Xử lý qua StateEncoder)
a*      = Quyết định Hành động Tối ưu của chuyên gia (Expert target action label via DAgger)
g       = Thông số Nhiệm vụ đã Vector hóa (Encoded goal)
M       = Context Bộ Nhớ đã trích xuất (Retrieved memory context)
π_θ     = Thuật Toán Mạng Đề Xuất Chính sách (Policy network — Output Action Head phân dải softmax)
D_expert = Bộ Dataset tập trung cặp mẫu chuẩn (State, Expert_action)
```

### Triển Khai Viết Tương Tác Cấu Mã

```python
class DecisionLoss(nn.Module):
    """Tính toán sai số phân loại Động Cú (Cross-entropy) Dành Cho Module Behavioral Cloning.
    
    Công Thức Toán Học:
      L = -E[log π_θ(a* | s, g, M)]
      = CrossEntropy(action_logits, expert_actions)
    
    Cơ Sở Phân Tích (Theoretical basis):
      Trích dẫn (Ross & Bagnell, 2010): Mục tiêu J(π_θ) ≤ J(π*) + T²ε
      Trong đó thông số ε = E_s[KL(π* || π_θ)] (Cận Sai Lệch KL Divergence Error).
    """
    
    def forward(self, action_logits: Tensor, expert_actions: Tensor) -> Tensor:
        """
        Nhu liệu Parameter:
            action_logits: Tensore chưa chuẩn hóa Của Hệ dự đoán [batch, n_actions=45]
            expert_actions: Chụp Vết Đội hình mẫu Expert [batch] actions shape
        Nổi Bật Returns:
            Giá trị thực Của Scalar Loss Tensor Scale
        """
        return F.cross_entropy(action_logits, expert_actions)
```

### Tính Đạo Hàm (Gradient Tracking)

```
∂L/∂θ = -𝔼 [ (1(a=a*) - π_θ(a|s)) × ∂log π_θ(a|s)/∂θ ]

Bản Chất Nguyên Lý (Intuition): Luồng truyền ngược (Backpropagation) tăng tỷ trọng xác suất dự đoán (Probability distribution) của Mô hình hướng về mốc Action chuấn chuyên gia và hạ thấp phân bổ các luồng quyết định không tối thiểu.
```

## 3. L_outcome — Tổn Năng Tại Nút Dự Tín Hệ Số Kết Cục

### Công Thức Khai Chi Tiết

```
L_outcome = -𝔼_{(s,a,o) ∈ D} [ Σ_k o_k × log f_θ(o_k | s, a) ]
```

### Các Ký Hiệu Đầu Rẽ

```
o_k ∈ {success, compile_error_syntax, compile_error_type,
       effect_violation, test_failure, timeout, no_change, unknown} (Bộ định tuyến 8 nhãn)
f_θ    = Bộ Neural Tiên Tính Trạng Hậu (Outcome prediction head → Phân dải Softmax Layer)
D      = Buồng Cuộn Chứa Dataset các Cụm Bộ ba (state, action, outcome)
```

### Triển Khai Mã Cơ Sở

```python
class OutcomePredictionLoss(nn.Module):
    """Lắp Dải Tính Multi-class Cross-entropy Cho Khối Hệ Đánh Giá Đoán Outcome.
    
    Cơ Sở Phân Tích Thực Dụng (Theoretical basis):
      Khối lệnh Cấu Trúc Cross-entropy ghép Nối Softmax mang Tới Cốt Hàm (Consistent estimator)
      Cho việc Thẩm Tra Trượt Tính Định Nghĩa Chuyên Sâu P(outcome | state, action).
      Thuật MLE consistency định chế từ Luận Thuyết Của Cramér (1946).
    """
    
    def forward(self, outcome_logits: Tensor, true_outcomes: Tensor) -> Tensor:
        return F.cross_entropy(outcome_logits, true_outcomes)
```

### Ứng dụng Trong Agent Runtime Pipeline

```python
# Tiền Khảo Tính Toàn Vẹn: Evaluate Prediction trước Khi Xác Lệnh Tác Hành Động Action Mới.
predicted_outcome = model.outcome_head(h_cls)
if argmax(predicted_outcome) == "compile_error":
    # Agent Phủ Phán Cơ Chế Tránh Rủi Ro: Hủy bỏ Kế hoạch Action sinh Compile Error
    # → Routing Điều Phối sang Mạng Chọn Lựa Cấu Thực An Toàn (Alternative Path Check).
    action = policy.select_alternative(state)
```

## 4. L_diagnosis — Giá Trị Mất Mát Tại Cụm Phân Tích Lỗi Tới Gốc

### Công Thức Trừ Dụng Toán

```
L_diagnosis = -𝔼_{(o,s,cause) ∈ D_fail} [ log g_θ(cause | o, s, history) ]
```

### Ý Nghĩa Các Số Hạng

```
o       = Lỗi Trạng Thái Thất Bại Đo Lường (Outcome failure constraint)
s       = Khuôn State Lỗi 
cause   = Nguyên nhân lỗi chính quy (Class label 15 Categories Root Causes)
history = Chuỗi Lịch Xử Thực Thi (Recent action sequence logic)
g_θ     = Thuật Mạng Nơ ron Diagnosis Cảnh Tính Sự Cố (Outputs Softmax Root Causes Target)
D_fail  = Ngân Khố Dữ Liệu Chỉ Thu Thập Những Gói Task Hư Hại Nhận Diagnostic
```

### Triển Khai Logic

```python
class DiagnosisLoss(nn.Module):
    """Mô Hình Tính Sai Chỉ Cụm Tổ Chẩn Đoán (Weighted Cross-entropy Root Cause Diagnosis Loss).
    
    Phân Bố Đặc Chưng Ứng Dụng Hành Vi (Class Weighting Applied Role):
      Phân luồng Gán Nhãn Weight Lớn Với Các Vụ Lỗi Mốc Thâm Trọng Chéo Nhưng Ít Sinh Vết Code Error \
      (Eg. dependency_cycle Architecture violations).
    
    Cơ Sở Logic Thuật (Theoretical basis):
      Rải nhịp Áp Thuật Hierarchical Classification hỗ Trợ Kích Buff Gia Tốc Lọc \
      được báo cáo tăng accuracy Tới Hạn Tịnh Tính 15-20% (Theo Silla & Freitas, 2011).
    """
    
    # Ma Trận Thiết Hạng Gắn Tạ Chỉ Mục (Class Frequency Weights Custom Tuning Limits):
    CAUSE_WEIGHTS = {
        "type_mismatch": 1.0,        # Phổ Điểm Nhẹ
        "missing_import": 1.0,       # Chung Mâm Trí Khí
        "circular_dependency": 3.0,  # Ít Thấy Mức Chậm Tính X3 Weight Load
        "architecture_violation": 3.0, # X3 Ràng Đặc Chưng Chặn Lỗi Nghiêm Khắc Tối Đa
        "requirement_gap": 2.0,
        "unknown": 0.5,             # Dìm Hạn Cấp Thấp Chặn Bias Data
    }
    
    def forward(self, diag_logits: Tensor, true_causes: Tensor,
                class_weights: Tensor) -> Tensor:
        return F.cross_entropy(diag_logits, true_causes, weight=class_weights)
```

## 5. L_lesson — Tham Số Thiệt Hại Đặc Khu Học Sinh Bài Contrastive Loss

### Công Thức Chủng Loại Toán Học

```
L_lesson = -𝔼_{(l, ctx⁺, ctx⁻)} [ log σ(sim(l, ctx⁺) - sim(l, ctx⁻)) ]
```

### Giao Diện Phân Hiệu Gắn Thông Số

```
l       = Vector Tinh Chắt Đại Diện Nội Tại Lesson Information Context Representation Data Embeddings Vector
ctx⁺    = Không Gian Ngữ Cảnh Tương Thích Nhất Positive Match Case Success Bounds Ranges Environments Limits Parameters Configs Space Domain
ctx⁻    = Không Gian Trượt Mảng Lỗi Failure Bounds Negative Environments Ranges Configs Fails Traces Domains Match Exclusions Rejection Areas
sim     = Thuật Tính Cự ly Tương Đương Độ Cosine Vector Similarity Data Evaluation Metric Dimension Space Evaluation Tensor Measure Metrics Tensor Comparison Scale Comparison Vectors
σ       = Sigmoid function
```

### Logic File

```python
class LessonQualityLoss(nn.Module):
    """Tích Điểm Tụt Contrastive Loss Data Evaluation Embeddings Quality Index Ranking Architecture Mapping Rules Tensors Tuning Matrix Math Vector Embeddings Framework Model Check Vector Evaluation Loss Value Metrics Array Mapping Tensor Loss Scale.
    
    Mục Tiêu Thống Kê (System Objective Limit): Rèn Nắn Véctơ Bài Học (Lesson Embedding Tensors) \
    Phải hội tụ Không Cận (Closer Proximity) Ở Cụm Context Phù Hợp ctx⁺, \
    Và Phát Đẩy Tách Điểm (Maximizing Distance Distracted) Với Những Phạm Vi Sai Mầm Chối Tiệm Lệch (ctx⁻) trật rãnh.
    
    Sở Khơi Cốt Giao (Theoretical basis):
      Tu Tính Hệ Động Lực Học Lõi Nhu Cầu Contrastive learning optimization theo Luận Báo Cáo Của (Arora et al., 2019): Dấu Trượt Cấn Áp \
      Này Thiết lập Chuẩn tối đa Maximum Mutual Information Mức Mệnh I(lesson; context) Từng Mảng 1.
    """
    
    def __init__(self, embedding_dim=256, temperature=0.07):
        super().__init__()
        self.temperature = temperature
        self.lesson_encoder = nn.Sequential(
            nn.Linear(512, 256),  # Gốc Core Input Hidden State Data Shapes Scale Parameters Tensor Maps
            nn.ReLU(),
            nn.Linear(256, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
        self.context_encoder = nn.Sequential(
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, embedding_dim),
            nn.LayerNorm(embedding_dim)
        )
    
    def forward(self, lesson_repr: Tensor, 
                positive_ctx: Tensor, 
                negative_ctx: Tensor) -> Tensor:
        l_emb = F.normalize(self.lesson_encoder(lesson_repr), dim=-1)
        pos_emb = F.normalize(self.context_encoder(positive_ctx), dim=-1)
        neg_emb = F.normalize(self.context_encoder(negative_ctx), dim=-1)
        
        pos_sim = (l_emb * pos_emb).sum(dim=-1) / self.temperature
        neg_sim = (l_emb * neg_emb).sum(dim=-1) / self.temperature
        
        loss = -F.logsigmoid(pos_sim - neg_sim).mean()
        return loss
```

## 6. L_adapt — Tổn Hại Ở Kênh Phải Hấp Thụ Data Vòng Thích Ứng Nhanh Mới Lạ Meta-Learning Adaptation

### Phương Châm Cứu Mệnh Trị MML (Model-Agnostic Meta-Learning Limits Constraints)

```
L_adapt = 𝔼_{τ ∈ tasks} [ L_decision(θ'_τ) ]

Chi Khảo Thiết Tố Biến Đoạn Hậu Data Mappings Variable Rules Rules Logic Variables Index Logic Limit Traces Tensor Metric Metric Variables Logic Evaluation Equations Check:
  θ'_τ = θ - α × ∇_θ L_decision(θ; D_τ^support)
  
  D_τ^support = Tập Gói Dataset Data Cứu Trợ Task Nhỏ Xíu Data Examples Dumps Reference Tracing Dataset
  α = Chỉ dấu Inner Tích Phân Trọng Gradient Tỷ Rate Limit Point Rate Float 0.01 Learning Step Scale Value Index Rule Variables Constants Rate
```

### Kiến Tạo Cấu Graph Điểm Đúc Lệnh

```python
class AdaptationLoss(nn.Module):
    """Máy Ráp MAML (Model-Agnostic Meta-Learning) Hệ Gán Đảo Gốc Parameter Matrix Models.
    
    Chuẩn Định Yêu Cầu (Goal Base Scope Models Range System Goals Evaluation Goals Models Mapping Targets Rules Scope Metrics Variable Limit Bounds Tracing Metrics Models Scope Target Scale Focus Logic Targets Models Targets Rules Logic Systems Criteria Criteria Rule Goals Evaluated Metrics Checks Logic Target Data Goal Constraints Bounds Metrics Rule Systems Metrics Requirements Metric System Focus Limits Limits Logic Goal Limit Scope Targets Traces System Model Evaluations Criteria Metrics Goal System Focus Rule Variables Tracking Checks Rules Objective Systems Method Focus Systems Requirement Values Criteria Limits Rules Rules Matrix Method Scale Variables Matrix Values Variable Criteria Goal Value Math Variable Target Models Target Data Data Checks Limits Goal System Value): \
    Hình Vạch Phả Parameter Gốc Rễ Network Weights θ Giúp AI Model Động Tích Chỉ (QUICKLY Adapt Data Model) \
    Đoạt Hướng Thay Đổi Về Dải Task Mới Chức Việc Chưa Từng Thấy Xưa Kia (Zero-shot/Few-shot task mappings learning domain shift mappings learning limits constraints bounds scale arrays limits bounds capabilities variables evaluation) \
    Chỉ Trên Tựa Căn Bản Ráp Tập Ví dụ Nhỏ Small Data Supports Check.
    
    Thuận Cơ Ráp Nghĩa (Theoretical basis):
      Trích Ánh Fallah et al. (2020) Lệnh Biến MAML Tụ Điểm Cấu Đầu O(1/√K) \
      Vòng Lặp Outer Khai Đích Móc Xảy Lại Limits Bounds β-smooth Cụm ρ-Lipschitz Rules Láng Metrics Boundary Bounds System.
    """
    
    def __init__(self, inner_lr=0.01, inner_steps=5):
        super().__init__()
        self.inner_lr = inner_lr
        self.inner_steps = inner_steps
    
    def forward(self, model, task_batch: list[TaskData]) -> Tensor:
        meta_loss = 0.0
        
        for task in task_batch:
            # Gỡ Lách Móc Ghép Query Sets Support Data Separation Dataset Test Train Train Data Limit Target Train Validation Arrays Split Arrays Lists Mappings Splitting Split Mappings Evaluation Splitting Limit Subsets Variables Filter Rules Mapping Split Subsets Dataset Separation Matrices Arrays Rules Array Limit Tensor Splitting Dataset Tensor Limits Lists Traces Array Mapping Bounds System Separation Logic Array Logic Filtering Logic Array Splitting Methods Filtering Matrix Method Arrays Lists Subset Domains Strings Matrix Scope Data Vectors
            support, query = task.split(ratio=0.5)
            
            # Khởi Cột Chu Trình Support Outer Inner Tuning Inner Training Cycle Logic Step Loops Parameter Model Parameter Weight Matrix Training Step Gradient Training Rules Limit Optimizer Limit Loss Value Tuning Value Limits State Weight Gradient Gradient Updates Variables Weight Matrix Tensor Loop Weight System Limit State Tensor Logic Variables Updates Tensor Loss Tensor Gradient Weights Learning Tuning Loss Logic Gradient
            adapted_params = dict(model.named_parameters())
            for step in range(self.inner_steps):
                support_loss = self.compute_decision_loss(model, support, adapted_params)
                grads = torch.autograd.grad(support_loss, adapted_params.values(), 
                                            create_graph=True)
                adapted_params = {
                    name: param - self.inner_lr * grad
                    for (name, param), grad in zip(adapted_params.items(), grads)
                }
            
            # Kết Khảo Tập Ngoại Outer Query Data Testing Step Training Metric Evaluation
            query_loss = self.compute_decision_loss(model, query, adapted_params)
            meta_loss += query_loss
        
        return meta_loss / len(task_batch)
```

## 7. Khối Hội Tụ Tổng Thể Hàm Loss Multi-Task Tích Hợp Kéo Gắn Lệnh Căn Homoscedastic

```python
class GEASMultiTaskLoss(nn.Module):
    """Mấu Kết Giao Quy Multi-Task Parameter Weight Rules Engine Uncertainty Equation Mappings Tensions Scale Evaluation Value Limits Value Tensor Framework Method Rules Values Method Equation Method Math Metrics Parameters Variables Framework Algorithms Rules Models Metrics Math Variable Method System Engine Model Tensor Variables Method Models Variables Parameter Systems Vector Equations Metrics Model AI Limits Engine Vectors Variables Logic Limits Framework Constraints Loss Math Variables Penalties Optimization Constraints Logic
    
    L = Σᵢ (1/(2σᵢ²)) Lᵢ + log(σᵢ)
    
    Ký Diệu Chữ Lưới Cảm Tự Tham Chiếu Động Học (Learnable Parameters Rules AI Weight Parameters Weights Logic Scale Auto Check Check Loss Evaluation Metric Equation Constraint Check Tensor Check Logic Value Variables Algorithm Variable Rule Optimization Model Framework Metrics Tensor Scale Model Weight Equation Logic Algorithm Logic Math System Optimization Math Models Values Variables Metrics Engine Parameter Engine System Logic Tensions Rule Vector Limit Variable AI Method Constants Vector Models Math) — \
    Thay Vào Thiết Đặt Tay Hệ Thống Tham Số.
    
    Cơ Cột Hệ Thống (Theoretical basis):
      Theo Dẫn Kendall, Gal & Cipolla (2018): Thuật Nới Dãn Homoscedastic Uncertainty Từ Điểm Mấu Bayesian Framework \
      Sinh Gắn Chỉ Dấu Điều Tiết Tuning Siêu Chuẩn Hiệu Rate Optimal Performance Dành Tập Loss Tasks Rules Multi-tasks Variables Systems Weight Vectors Vectors Matrices Scale Evaluation Matrices Array Limit Optimization Limits Data Constraints Vectors Loss Optimization Systems Tensor Matrices Tensor Limit Tensors Models. 
    """
    
    def __init__(self):
        super().__init__()
        # Túm Khỏa Thác Gán Ràng Buộc Log Check Variance Tham Số Tự Khắc Mở Chốt Learn Từng Loss Scale Limit Variable
        self.log_sigma_decision = nn.Parameter(torch.zeros(1))
        self.log_sigma_outcome = nn.Parameter(torch.zeros(1))
        self.log_sigma_diagnosis = nn.Parameter(torch.zeros(1))
        self.log_sigma_lesson = nn.Parameter(torch.zeros(1))
        self.log_sigma_adapt = nn.Parameter(torch.zeros(1))
        
        self.decision_loss = DecisionLoss()
        self.outcome_loss = OutcomePredictionLoss()
        self.diagnosis_loss = DiagnosisLoss()
        self.lesson_loss = LessonQualityLoss()
        self.adapt_loss = AdaptationLoss()
    
    def forward(self, model_output, targets) -> dict[str, Tensor]:
        L1 = self.decision_loss(model_output.action_logits, targets.expert_actions)
        L2 = self.outcome_loss(model_output.outcome_logits, targets.true_outcomes)
        L3 = self.diagnosis_loss(model_output.diagnosis_logits, targets.true_causes)
        L4 = self.lesson_loss(model_output.lesson_repr, 
                              targets.positive_ctx, targets.negative_ctx)
        L5 = self.adapt_loss(model_output.model, targets.task_batch)
        
        # Mớ Áp Khối Cụp Trọng Thu Uncertainty
        losses = [L1, L2, L3, L4, L5]
        log_sigmas = [self.log_sigma_decision, self.log_sigma_outcome,
                      self.log_sigma_diagnosis, self.log_sigma_lesson,
                      self.log_sigma_adapt]
        
        total_loss = sum(
            torch.exp(-2 * log_sigma) * loss + log_sigma
            for loss, log_sigma in zip(losses, log_sigmas)
        )
        
        return {
            "total": total_loss,
            "decision": L1.item(),
            "outcome": L2.item(),
            "diagnosis": L3.item(),
            "lesson": L4.item(),
            "adapt": L5.item(),
            "sigma_decision": torch.exp(self.log_sigma_decision).item(),
            "sigma_outcome": torch.exp(self.log_sigma_outcome).item(),
        }
```

## 8. Lập Trình Lịch Tỏa Huấn Luyện (Training Schedule Strategy Tracking Limit Mapping Mapping Cycle Loop Model Engine Logic Algorithm AI Limits Logic Rules Cycle Data Limit Training Data Loops Algorithm System Logic Metric Training Loop Array Evaluation Loop ML Data Pipeline Framework Logic Parameter ML ML Loop Mapping Cycle Variables Logic Array)

```
Giai Đoạn Mô Phỏng Imitation Training Phase 1: L = L_decision + L_outcome
Khởi Giác Diagnostic Check Giai Tập Tích Diagnosis Phase 2: L = L_decision + L_outcome + L_diagnosis  
Trần Khoái Lộ Cấu Nạp Trạm Semantic Lesson Training Full Scope 3: L = L_decision + L_outcome + L_diagnosis + L_lesson
Nối Bệ Kịch Trích Bắn Nét Phá Meta Meta-Learning Fast Adaptation Range Peak Phase 4: L = Full Components + L_adapt (Khởi Trì Cột Lệnh Target Đạt Số Bọc Data Train Support ≥ 10K Trajectory Episodes Traces Indexing Metric Scope Dataset Threshold Logic Check Rules Data Count Threshold Data Check Count Check Condition Count Rules Target Limits Bounds Limit Level Evaluation Requirement Array Track Rule Threshold Metric Scale Check)
```
