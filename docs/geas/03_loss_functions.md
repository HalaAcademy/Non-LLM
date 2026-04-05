# Đặc tả Hàm Giá Trị Mất Mát GEAS (GEAS Loss Functions Specification)
## Chuẩn Hóa Định Nghĩa Từng Số Hạng — Khắc phục G1: "Thiếu định nghĩa toán học 5 thành phần loss function"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Tổng quan Tổ hàm Đa Đích Tối ưu (Multi-Task Loss)

```
L_tổng = Σᵢ (1/(2σᵢ²)) × Lᵢ + log(σᵢ)

Tróc tỉa phân tách trong đó:
  L₁ = L_decision     (Phép Thuật Phỏng Hình Giống Biểu Cảm behavioral cloning)
  L₂ = L_outcome      (Trò Mở Bài Tiên Trí Đoán Kết Cục outcome prediction)
  L₃ = L_diagnosis    (Mũi Dao Phân Tích Chỉ Đích Thối Rễ root cause classification)
  L₄ = L_lesson       (Tụ Đỉnh Chất Lượng Bài Học Nhả Ra lesson quality — Dùng đòn ép dãn contrastive)
  L₅ = L_adapt        (Mồi Nhử Sinh Kê Độ Bật Nhảy Nhanh meta-learning adaptation)
  σᵢ = Các Chỉ số Dịch số Sai lệch Ứng theo task-specific linh ứng tự bù đắp learned uncertainty (homoscedastic)
```

Quy chuẩn Trọng Số Nắn Lót Mượt Cú Dịch Ngược Lệnh Tính (Uncertainty weighting theo Kendall et al., 2018) giúp tự xoay trở lực kéo giữ hài hoà thăng bằng các hàm băm mất mát (losses) mà vô can khỏi việc vặn nút xoay số chỉnh tay thủ công.

## 2. Tổ hàm L_decision — Mất Mát Tại Ngả Bốc Trút Quyết Định Hàm Action

### Định Nghĩa Ký Tự

```
L_decision = -𝔼_{(s,a*) ∈ D_expert} [ log π_θ(a* | s, g, M) ]
```

### Thẩm Soi Ý Nghĩa Mã Thành Phần

```
s       = Khuôn trạng thái đã cô bọt đúc rễ (structured state - qua màn StateEncoder)
a*      = Quyết trút Mốc Đinh đánh từ Nhãn Lệnh gốc chuấn xác xuất sắc từ ngón tay chuyên gia (expert action label qua DAgger)
g       = Bao lưới Goal đã nén đóng mã
M       = Bầu bọc Rút Tủy Trích Não Bộ Nhớ Memory đã triệu nạp retrieved
π_θ     = Thuật Mạng Chính Sách Đệm Thở policy network (Bộ chóp Ngõ Lùi Action Head → bung lọng softmax)
D_expert = Băng mâm dữ liệu mẫu cúng nạp các cặp ghép hòm (state biến động trạng thái, expert_action điểm mặt quyết ý cao nhân)
```

### Triển khai Mã Nền

```python
class DecisionLoss(nn.Module):
    """Trượt Đẩy Đai Phỏng Phím Hành Vi Behavioral cloning đánh ép bốc nhụy đâm chọn action.
    
    Quy giải Tôn Nghiêm Toán học:
      L = -E[log π_θ(a* | s, g, M)]
      = CrossEntropy(action_logits, expert_actions) (Đo Vắt Chéo Hư Tổn Phân Kỳ)
    
    Giá bợ Đỡ Luận Điểm Nền (Theoretical basis):
      Trích Luận mâm Ross & Bagnell (2010): Vòng Kê J(π_θ) ≤ J(π*) + T²ε
      nhổ gộp có ε = E_s[KL(π* || π_θ)]
    """
    
    def forward(self, action_logits: Tensor, expert_actions: Tensor) -> Tensor:
        """
        Khều gọi Mảng Bọt:
            action_logits: Nặng trĩu độ phủ lô batch nguyên chất rớt [batch, n_actions=45] raw model
            expert_actions: Hộp đong Đóng Khuôn Chì điểm Mặt list [batch] actions
        Trả ra:
            thang đánh mất mát vô hướng scalar loss
        """
        return F.cross_entropy(action_logits, expert_actions)
```

### Xâu Đáy Trượt Mảng Dốc Gradient

```
∂L/∂θ = -𝔼 [ (1(a=a*) - π_θ(a|s)) × ∂log π_θ(a|s)/∂θ ]

Điều Diệu Cự Ý (Intuition): Giờ đẩy thốc cái tảng đá trọng lực xác suất sụp dán rí dúi về phía cái quyết ý lệnh chuẩn vàng expert action xịn, \
           vung chân đá văng rớt đi bọn bọc không phải dân chóp tể expert mạo danh.
```

## 3. Tổ Hàm L_outcome — Mất mát Lúc Nhập Đồng Đoán Kết Cục

### Định Nghĩa Ký Tự

```
L_outcome = -𝔼_{(s,a,o) ∈ D} [ Σ_k o_k × log f_θ(o_k | s, a) ]
```

### Thẩm Soi Lòng

```
o_k ∈ {Thắng success, Lỗi Trớ syntax compile_error_syntax, Lỗi Lệch Khuôn compile_error_type,
       Nát Đáy Phanh Biên compile_error_effect, Chìm Mỏ Test test_failure, Phụt Giờ Cúp Đuôi timeout, Trơ lỳ no_change, Nổ banh não chưa rõ unknown}
f_θ    = Bộ Lọng Rọ chóp Đoán kết outcome prediction head (Cửa outcome Head → thắt bím softmax)
D      = Buồng Cuộn Chứa các chùm ba (state, action, outcome)
```

### Triển khai Mã Nền

```python
class OutcomePredictionLoss(nn.Module):
    """Khối Cross-entropy quẳng Đa Thể class multi nắn đoán kết cục Outcome.
    
    Niềm cậy Giáo Ly Nền (Theoretical basis):
      Quang luồng cấn trượt Cross-entropy chung mâm với softmax sẽ dựng ra một máy tính dự mỗ ổn hằng consistent estimator \
      hòa mình cho cái giá trị đích thực P(outcome | state, action).
      Thuật MLE consistency vững trãi chứng minh từ (Cramér, năm 1946).
    """
    
    def forward(self, outcome_logits: Tensor, true_outcomes: Tensor) -> Tensor:
        return F.cross_entropy(outcome_logits, true_outcomes)
```

### Thể thức Trói Vòng trong Mạch Agent Loop

```python
# Chắn phanh: Ngay trước giờ Hoàng Đạo đánh sập cầu thả action, Hãy Mượn hồn Đoán quẻ kết cục predicted outcome trước đã
predicted_outcome = model.outcome_head(h_cls)
if argmax(predicted_outcome) == "compile_error":
    # Agent có cái ngàm Quyền Năng TRÁNH KHÔNG THÈM CHẠY cái đòn bẩn xịt lệnh đó nữa mà bẻ càng lái lách sang cái bến chọn lựa chóp cành an toàn hơn Action chọn khác đi
    # → Ép rút ngắn thời gian đổ máu phí hơi của luồng build vô mộng cycles ngáo
    action = policy.select_alternative(state)
```

## 4. L_diagnosis — Giá Suy Tư Gỡ Cắm Rễ Tính Nguyên Nhân Mầm Mống

### Định Nghĩa Chữ Toán

```
L_diagnosis = -𝔼_{(o,s,cause) ∈ D_fail} [ log g_θ(cause | o, s, history) ]
```

### Thẩm Soi Khí

```
o       = Quả Quét ra lỗi quan sát (failure)
s       = Trạng Phanh lật giật đùng đúng lúc đụng lỗi
cause   = Chỉ Mục Lỗi bị cắm sừng chỉ mặt mọt bọt anot (chọn trong hòm 15 categories gốc)
history = Căn Quả Nhịp Bước trước đó recent action
g_θ     = Tay Cửa Hưng Đón Rà Chẩn Bắt Bệnh diagnosis head (→ trói vào ngọn softmax chọt Causes)
D_fail  = Phễu Giỏ lọc những hồi ức ôm rác failure nhú đắng
```

### Triển khai

```python
class DiagnosisLoss(nn.Module):
    """Mảng Lưới Bủa Cấu Đoán chia Root cause rễ thâm canh với bộ ép chia cục đánh tạ class weighting.
    
    Trọng Cử Thả neo lệnh Đong Đưa Weighted CE này lên bàn cân là Cớ vì có một số cái Tội Cội Rễ hiếm hờ ít nhó mặt (VD như dependency_cycle bị quấn vòng cọ quậy) \
    thường chìm tít đáy bóng nhưng lại Cực Trầm Trọng Chí Chết màng nếu dính thì thôi rồi lượm ơi. Ngặt nỗi dính ít nên phải buff cân nặng nó lên.
    
    Giá Luận Học Nghề Nền (Theoretical basis):
      Rải nhịp trảm chéo mảng Phân cấp Dọc Lưới Hierarchical classification giật điểm cải thiện độ tít trúng phóc vọt nhún accuracy phi mã lên 15-20% theo bẳng đong đếm của \
      (Silla & Freitas, ghi lại từ 2011).
    """
    
    # Cân đong Tạ Hạng Tội: Các tội ít mớm xuất hiện nhưng Trọc Đỉnh Trầm Trọng phải Vát Gánh Siêu Nặng Lên X2 X3 đánh Thốc:
    CAUSE_WEIGHTS = {
        "type_mismatch": 1.0,        # Phổ Điểm Đại trà (Rẻ rúng)
        "missing_import": 1.0,       # Chung Mâm dễ đoán (Kém Lực)
        "circular_dependency": 3.0,  # Ít Chạm Mép mà Hốc Vô thì Giết Cả Đàn Lũ (Nặng cực X3 dồn lực hù họa cho sợ)
        "architecture_violation": 3.0, # X3 (Đập vỡ kiến trúc - Tội Cố Sát Động Trời Trảm Ngay)
        "requirement_gap": 2.0,
        "unknown": 0.5,             # Phũ Tội Mù - Hợp lý dìm Đè rẻ rúng nó xuống vũng sình
    }
    
    def forward(self, diag_logits: Tensor, true_causes: Tensor,
                class_weights: Tensor) -> Tensor:
        return F.cross_entropy(diag_logits, true_causes, weight=class_weights)
```

## 5. Tổ hàm L_lesson — Chất Điểm Chân Vàng Bài Học Ép Khuôn

### Định Nghĩa Chữ

```
L_lesson = -𝔼_{(l, ctx⁺, ctx⁻)} [ log σ(sim(l, ctx⁺) - sim(l, ctx⁻)) ]
```

### Soi Lõm

```
l       = Phôi chèn Điểm Ngấm rễ bọc của bài học (Kéo lõi từ dải chữ lesson text → rồi cuộn nó qua máy vò dũi embedding model nén màng)
ctx⁺    = Không Điểm Ngữ Lọt Mịn (positive context - Cánh lọt trường hợp đút bài học vào lọt khe cứu chúa ăn ngay)
ctx⁻    = Vũng Ngục Dội Khúc Kẹt (negative context - Ném bài khôn sai ngõ vấp ngã mặt té văng không ăn nhập)
sim     = Đòn Đo Nọc Dấu chéo đọ sát sự trôi Khớp cosine similarity chập dính nơi chân không vô ảnh embedding space
σ       = Thổi dải Lọng hàm sigmoid vút hình nón
```

### Áp Phím Lệnh

```python
class LessonQualityLoss(nn.Module):
    """Mũi Vuốt Song Rãnh Sót Ép Khoán (Contrastive loss) cạo điểm phán sắc xảo độ bén nhạy của hạt dũa tinh chất lesson embedding.
    
    Ngắm Băng Đứt Kệnh Sứ Mạng Ý đồ Đích: Bóp ép Cỗ Đầu não Luyện Sao Nhoán cho Cái Khuôn của những cái Tinh Châu hạt Phôi Lớp Lessons nó \
    SÁP SỊT GẦN KHÍT BẾN NHẤT so Với Đám Bè phái Mảng Các Ngữ Cảnh Xài Tấu Ngon Mượt (ctx⁺), \
    Với cả TÁCH LÌA XA RÚT DI KHOẢNG NGÚT NGÀN Khỏi cái nùi bọn rác Ngữ cảnh Mắm Tôm Trái Nết Hợp chệch (ctx⁻) trật rãnh.
    
    Đỡ Lưng (Theoretical basis):
      Trích dẫn Arora et al. (đầu 2019): Dấu Trượt Cấn Áp Ngược Contrastive learning trôi ngoằn ngoèo rướn lên rồi hội tụ đè trúng chóp đỉnh chạm mốc tối đẳng \
      cực hóa trọn thu về những hạt nén dồn căng điểm mutual information tinh anh mấu chốt I(lesson; context).
    """
    
    def __init__(self, embedding_dim=256, temperature=0.07):
        super().__init__()
        self.temperature = temperature
        self.lesson_encoder = nn.Sequential(
            nn.Linear(512, 256),  # Nhập dây Cốt Não Bộ hidden state
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

## 6. Sóng Hàm L_adapt — Đo Điểm Siêu Nhạy Bắt Lẹ Tổ Học Đổi Hướng Nhanh

### Khái Lược Bản Mạo (Dán Thẻ Định Tuyến Phái MAML)

```
L_adapt = 𝔼_{τ ∈ tasks} [ L_decision(θ'_τ) ]

Chi nhỏ Phủ Soi:
  θ'_τ = θ - α × ∇_θ L_decision(θ; D_τ^support)
  
  D_τ^support = Nắm nhỏ hạt vãi li ti túi xách hành trang gọi hỗ trợ nhét vội quấn của Task Mới Lạ Nước τ (VD Nhón rón rén 5 con điểm mẫu vãi nhẹ)
  α = Chỉ dấu Trọng Vận Mức Hấp Tạp inner (Vẽ Khung mảng cạo lấy chót gót vẩy thường cỡ móc rate điểm = 0.01)
```

### Khẩu Gọi Điểm Mã

```python
class AdaptationLoss(nn.Module):
    """Máy Quay Sát Luồng Tiên Cáo Giả Tấu phái học lẹ kiểu MAML-style meta-learning loss.
    
    Cắm Chốt Sứ Mệnh Quyền Nghĩa (Goal): Huấn Điểm nhả Khởi Nháp Đầu param rễ cọc θ làm sao Mà Ở Đó Một Mống Ánh Điểm Ấy CÓ KHẢ NĂNG TIẾN CẮT PHỌT RẼ SÓNG PHÓNG LẸ BÃO TAP  (QUICKLY adapt) \
    Đẻ Mánh Vót Trổ Sang Liền Đổi Làn Được Lép Cho Cái Khối Chữ Task Mới Tóc Bực Xa lạ Chỉ Bằng Vi Cá Vái Mấy Cọng Chút Nhỏ Examples Mồi Điểm.
    
    Tính Đo Múc Mạng Lý luận:
      Sổ Chéo Fallah et al. (đời 2020): Chi Lăng Đánh Lệnh Nhánh MAML Rớt Ổ Hội Trụ Về Đích Hái Ngót Ở Cái Độ dớp Trôi Rate Tốc Độ O(1/√K) \
      Sau K bước quăng xa điệu bộ ngàn dặm ngoại vi outer steps, Chỉ cần Đốp được Nếp β-smooth ρ-Lipschitz Láng bóng.
    """
    
    def __init__(self, inner_lr=0.01, inner_steps=5):
        super().__init__()
        self.inner_lr = inner_lr
        self.inner_steps = inner_steps
    
    def forward(self, model, task_batch: list[TaskData]) -> Tensor:
        meta_loss = 0.0
        
        for task in task_batch:
            # Tách Lớp Rã Bọc Nhão Chia Khuyên Xé Nhíp cho Support Dẫn Tấu và Query Rà Đánh Giấy Query Ngầm evaluate
            support, query = task.split(ratio=0.5)
            
            # Vòng Siết Eo Lõi inner: lách dẻo Nhún bẻ khớp Bám vào task Nương Đệm Bộ Support Mềm Trợ Trấn
            adapted_params = dict(model.named_parameters())
            for step in range(self.inner_steps):
                support_loss = self.compute_decision_loss(model, support, adapted_params)
                grads = torch.autograd.grad(support_loss, adapted_params.values(), 
                                           create_graph=True)
                adapted_params = {
                    name: param - self.inner_lr * grad
                    for (name, param), grad in zip(adapted_params.items(), grads)
                }
            
            # Vòng Cuộn Băng Trói Cảo Vòng Ôm Lớn Ngoài Outer: Chụm Khíp Ép CÂN Rọ Rà Vớt Check Cứu Viện Lên Quân query Vòng query set bằng Trâm Biến Lõm adapted params
            query_loss = self.compute_decision_loss(model, query, adapted_params)
            meta_loss += query_loss
        
        return meta_loss / len(task_batch)
```

## 7. Khối Vẹn Toàn Cụm Túm Mạng Ép Phễu Multi-Task Loss Tổng

```python
class GEASMultiTaskLoss(nn.Module):
    """Búa Phân Vạch Nhượng Trọng Hồn Hệ Uncertainty-weighted multi-task loss.
    
    L = Σᵢ (1/(2σᵢ²)) Lᵢ + log(σᵢ)
    
    Ký Diệu Chữ σᵢ Đây Đứt Rằng LÀ LOẠI CÁI TRỌNG CỌC GÓC LÚNG LIẾNG CHU CHÉO TỰ THẢ NHÚN TỰ TÍNH (LEARNABLE parameters) — Rứt Quyền Bãi Trách Khỏi Cái Vụ Chót Vá Vặn Chỉnh Điểm Cân Xoay weight Tay Bằng Răng Trắng.
    
    Góc Kê Mép Lý Tưởng Tôn Giả:
      Sớ Phản Chấn Kendall, Gal & Cipolla (tỉ mỉ 2018): Khối Homoscedastic uncertainty bự rách \
      tước được vỏ Cũ Tách Sinh Mầm Từ Góc Khuôn Cờ Luân Hồi Nháp Bayesian, Tạo Ra Phẩm Độ Hiệu Ứng Bám Ngấn Nhất Rơi Vào Nấc Tuyệt Diệu Tối Đa Thần Tích Của Thế Mảng Nhồi Lắc Đa Hệ Trận multi-task.
    """
    
    def __init__(self):
        super().__init__()
        # Túm Khỏa Tự Giác Sinh Biến Thuốc Lắc Tham số learnable log-variance dành đệm thắt Cho Trái Tuyến Riêng Biệt Từng Điểm Mỗi Đầu Task
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

## 8. Tuần Cử Lịch Áp Máy Bơm Nắn Rèn Nháp Bọc Huấn Luyện (Training Schedule)

```
Thời Thế Phase Lõi 1 (Mô Phỏng Phá Kiểu Giả Tấu Imitation): L = L_decision + L_outcome
Thời Mở Bước 2 (Chỏm Chẩn Đảo Soát Diagnosis):              L = L_decision + L_outcome + L_diagnosis  
Trần Khoái Phase Lõi 3 (Bơm Tống Điểm Khai Thông Mạch Full): L = L_decision + L_outcome + L_diagnosis + L_lesson
Lập Đỉnh Phase Đỉnh 4 (Cú Siêu Di Viện Meta):               L = Bắn Full + L_adapt (Kích Lửa Điểm Máu Ngầm Thức Tỉnh Chớp Vọt sau khi đạt 10K episodes vòng lăn lộn)
```
