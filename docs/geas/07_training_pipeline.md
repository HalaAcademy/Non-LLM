# Đặc tả Quản Trị Đường Ống Huấn Luyện (GEAS Training Pipeline)
## Cấu Hình 6 Giai Đoạn Đào Tạo & Cơ Chế Giám Sát Hội Tụ — Khắc phục G10+G11

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Chuỗi Chu Trình Đào Tạo Phân Cấp (Training Phases)

```
Giai đoạn 1: Hành Vi Mô Phỏng  │ Giai đoạn 2: Bổ sung Outcome │ Giai đoạn 3: Bổ sung Chẩn đoán
L = L_decision             │ L += L_outcome            │ L += L_diagnosis
Dữ liệu: ~2K Tập mồi cơ sở │ Dữ liệu: ~4K Tập Episodes │ Dữ liệu: ~6K Tập Episodes
────────────────────────── │ ───────────────────────── │ ─────────────────────────
Giai đoạn 4: Học qua Bài học  │ Giai đoạn 5: Tối ưu Cấp Tốc  │ Giai đoạn 6: Triển Khai Thực Tiễn
L += L_lesson              │ L += L_adapt              │ L_total + Hàm Phạt Giới Hạn (EWC)
Dữ liệu: ~8K Tập Episodes  │ Dữ liệu: ~12K Tập Episodes│ Huấn luyện Trực Tuyến Đổ Dồn (Continuous)
```

## 2. Tiêu Chuẩn Cấu Chức Huấn Luyện Các Pha

### Pha 1: Đào Tạo Bắt Chước (Imitation Learning/Behavioral Cloning)

```python
def train_phase1(model, dataset, config):
    """Mô-đun Huấn Luyện Agent sao chép lại hành vi (Actions) của chuyên gia lập trình."""
    target_metrics = {
        "action_accuracy": 0.60,     # Độ chính xác Mô phỏng đạt ≥ 60%.
        "loss_decision": 0.50,       # Chỉ số Cross-entropy của hàm quyết định duy trì < 0.5.
    }
```

### Pha 2: Dự Trù Kết Quả (Outcome Prediction)

```python
def train_phase2(model, dataset, config):
    """Mô-đun Tính toán Tỉ lệ Kết Quả Tối Ưu (Thành công/Lỗi Biên Dịch/Lỗi Logic)."""
    target_metrics = {
        "action_accuracy": 0.65,
        "outcome_accuracy": 0.70,    # Độ chính xác dự tính kết quả sau hành động.
    }
```

### Pha 3: Hệ Thống Chẩn Đoán Lỗi (Root-Cause Diagnosis)

```python
def train_phase3(model, dataset, config):
    """Mô-đun Xác định Cấu trúc Lỗi dựa trên Hệ phân tích Điểm Lỗi Hệ thống."""
    target_metrics = {
        "action_accuracy": 0.70,
        "outcome_accuracy": 0.75,
        "diagnosis_accuracy": 0.60,  # Xếp hạng độ chuẩn xác của Nguyên Nhân Gốc.
    }
    # Yêu cầu Phân lô dữ liệu: Chỉ tập trung học tập trên các chuỗi Fail (Khuyến khuyết).
```

### Pha 4: Nén và Lọc Chất Lượng Cấu Trúc (Lesson Quality Assessment)

```python
def train_phase4(model, dataset, config):
    """Mô-đun Dũa Dữ Liệu qua các điểm chặn đối nghich (Contrastive Filtering)."""
    target_metrics = {
        "lesson_retrieval_precision": 0.70,  # Xác thực Tỷ Lệ gọi lại bài học một cách chuẩn xác cho Agent.
    }
```

### Pha 5: Phương Thức Cập Nhật Siêu Thích Chú (Meta-Learning Adaptation)

```python
def train_phase5(model, dataset, config):
    """Phương Thức Bổ Trợ MAML giúp Model phản xạ tốt và tự tối ưu trong các Tác Vụ Mới Không Giám Sát."""
    target_metrics = {
        "few_shot_accuracy": 0.60,   # Cải thiện tỷ lệ thành công mô hình với vài ví dụ Few-Shot (N < 5 mẫu).
    }
```

### Pha 6: Hoạt Động Trên Môi Trường Thực Tế (Production Loop)

```python
def train_phase6(model, config):
    """Tiến trình Hoạt Động Triển Khai kết hợp Hệ Thống Chống Lảng Quên (EWC Constraint)."""
    ewc = EWCRegularizer(lambda_ewc=1000)
    
    while True:
        # Vòng Lặp Trực Tuyến Continual Learning Limit.
        # Bổ Sung Tập dữ liệu mới + Cân Bằng Trọng Vector Neural Model.
        pass
```

## 3. Kiến Trúc Shaping Hàm Thưởng (Reward Shaping) - Khắc Phục G11

### Sự Cố Thiết Kế Lõi Cũ Sparse Reward (Reward Khan Hiếm)
Nếu chỉ chờ Agent làm đúng tới cuối Dự án (Mission Completed) mới cấp tính điểm Thưởng (Reward = 1) và nếu thất bại thì nhận điểm số 0, quá trình học tập sẽ rất khó đạt điểm cân bằng. Khi ấy, Agent sẽ cần hàng trăm bước thực thi mỗi ngày để ngẫu nhiên đạt thành công, một tỉ lệ thất bại quá cao gây thoái trào việc Huấn Luyện Mô Hình. 

### Quy Trình Phân Đổ Rải Điểm (Dense Shaped Reward Pattern)

```python
class RewardShaper:
    def compute_reward(self, state_before, action, state_after, outcome) -> float:
        reward = 0.0
        
        # 1. Thưởng Bước: Build Successfully Code Change (+0.5)
        # 2. Thưởng Gỡ: Sửa Code khắc phục đi Lỗi Răng Cưa Cũ (+0.1)
        # 3. Phạt Thêm Lỗi Mới: Vô ý Thêm Code gây Lỗi Nâng Cao (-0.15 phạt Mỗi Lỗi Index)
        # 4. Thưởng Tích Phát: Cải Thiện Chỉ Số Che Phủ Trace Coverage (+0.2 Mỗi Cọc Nảy 10% Limits)
        # 5. Thưởng Hoàn Tất: Hoàn Thành Nhánh Giai Đoạn Dự Án Con (+0.3)
        # 6. Phạt Nghẽn Cổ Chai: Lặp Các Vòng Lặp Lỗi Lặp Cũ Mà Không Sửa (-0.2/Lần Lặp)
        # 7. Phạt Hành Vi Thừa: Chạy Action No-op Mất Hiệu Qủa (-0.1)
        # 8. Thưởng Nhận Nhiệm Vụ Chót: Bàn Giao Thống Nhất Test Đạt Tổng Nhiệm Vụ (+1.0)
        return reward
```

## 4. Quản Lý Đỉnh Dừng Học Phân Tuyến (Model Convergence Monitoring)

```python
class ConvergenceMonitor:
    """Mô-đun kiểm soát quá trình Early Stopping chống Overfitting và Cạn Vòng Học Mới."""
    
    # Check 1: Khối Hàm Tổn Thất Loss Đi Đến Ranh Cận Đới Convergence Range.
    # Check 2: Điểm Target Metric đã vượt Ngưỡng Threshold Expectation Limits.
    # Check 3: Sự Dao Động Biểu Đồ Gradient Giữ Tần Cân Bằng Vượt Quá Thời Gian Tolerance Exhausted.
    # Cơ Chế Xóa Cấp: Nếu qua 20 Checks Epochs nhưng Hệ Số Loss Không Cạn Điển Limit, Vẫn Lắp Cờ Đỉnh Dừng 'Training Convergence Finalized'.
```
