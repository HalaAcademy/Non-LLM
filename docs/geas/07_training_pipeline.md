# Đặc tả Đường ống Huấn luyện GEAS (Training Pipeline)
## Quá trình Huấn luyện 6 Pha Đỉnh Cao với Cam Kết Hội Tụ Đích — Khắc phục G10+G11

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Dàn Đai Pha Luyện (Training Phases)

```
Pha 1: Mô phỏng Dấu Vết  │ Pha 2: +Đoán Ngọn   │ Pha 3: +Bác Sĩ Chẩn
L = L_decision           │ L += L_outcome      │ L += L_diagnosis
~2K cục episodes mồi     │ ~4K episodes        │ ~6K episodes
──────────────────────── │ ─────────────────── │ ───────────────────
Pha 4: +Rút Mép Học      │ Pha 5: +Mượn Ảnh    │ Pha 6: Vung Lò Ra Trận
L += L_lesson            │ L += L_adapt        │ Rút Full Loss + EWC (Máy ép Chống Lỏng Quên)
~8K episodes             │ ~12K episodes       │ Cứ quay luân hồi miết Continuous
```

## 2. Dẫn Mổ Chi Tiết Đoạn Pha

### Pha 1: Trườn Mạch Luyện Phỏng Hàm Hành Vi (Imitation Learning)

```python
def train_phase1(model, dataset, config):
    """Nắm bắt Cảm Nhịp vung đòn múa Action Tựa sát rạt theo Cố Vấn Chuyên Gia (behavioral cloning)."""
    # Khới Nhịp Rút Cọc Hàm Mỏ AdamW Tốc Mượt
    target_metrics = {
        "action_accuracy": 0.60,     # Nhại Bám phíp đúng bài đòn Tiên Nhân cỡ 60%
        "loss_decision": 0.50,       # Cờ xô lệch đụng Cross-entropy lún < 0.5
    }
```

### Pha 2: Ghép Cánh Mắt Thần Dự Kết Cục (Outcome Prediction)

```python
def train_phase2(model, dataset, config):
    """Lắp Vòng Móc Bắt Bói kết Đỉnh (Thắng/Thua) Từ quả đòn đấm Action."""
    target_metrics = {
        "action_accuracy": 0.65,
        "outcome_accuracy": 0.70,    # Nhắm Trúng Đờn Có Lọt Khe Build Sập hay Sang
    }
```

### Pha 3: Gắn Viết Chẩn Đáy Nguồn (Diagnosis)

```python
def train_phase3(model, dataset, config):
    """Gắn Nọng Rà Sót Đáy Lỗi Tìm Rễ Gốc cho Cú Rớt Khung Bại Trận (failure episodes)."""
    target_metrics = {
        "action_accuracy": 0.70,
        "outcome_accuracy": 0.75,
        "diagnosis_accuracy": 0.60,  # Xọc trúng cuống rễ
    }
    # Chỉ Xoáy Lò Luyện Trên Phiến Lá Bệnh failure
```

### Pha 4: Thẩm Soi Chuẩn Bài Học (Lesson Quality)

```python
def train_phase4(model, dataset, config):
    """Tróc Ép Vát Bọt Lọc Chuẩn Màng Lesson dũa contrastive."""
    target_metrics = {
        "lesson_retrieval_precision": 0.70,  # Ngậm Gọi Móm Rút Ra Khớp Bài Mẹo Cần Thiết
    }
```

### Pha 5: Đòn Siêu Nhún Bẩy Não Ám (Meta-Learning)

```python
def train_phase5(model, dataset, config):
    """Đính Móc MAML Kích Thích Nhát Đột Biến Phản Xạ Gấp Chỏm Mới."""
    target_metrics = {
        "few_shot_accuracy": 0.60,   # Phản hồi nhảy vọt điểm sau 5 mồi nhấp mẫu thử dạng dị
    }
```

### Pha 6: Quăng Cày Trận Thực (Production - Chạy Không Nghỉ)

```python
def train_phase6(model, config):
    """Ống Nước Bơm Liên Hoàn Dập Nêm Họng Ngáp Chống Khô Quên EWC."""
    ewc = EWCRegularizer(lambda_ewc=1000)
    
    while True:  # Chạy XuyÊn Đêm Tràn Giấc Ở Lò Production
        # Cày Gom New data
        # Vuốt Lọc Ép Model Nén Bắn Lửa Học Miết
```

## 3. Tạo Điểm Nhấm Nẩy Thưởng (Reward Shaping) - Xử Cái Gai G11

### Hố Sụp
```
Nếu Nhắm Đòn Ngây Ngô Naive:
  Ván Đổ Cày Trọn Vẹn project_complete → Cho Móng Cắn Chút Kẹo: Rớt Điểm Thưởng +1
  Rớt Rách Gánh Cụt not_complete → Phũ Cho Bọc Mắm Tôm: Điểm Thưởng 0
  
Lỗi Túm Váy Lại Là: Nếu Rải Thẻ Vậy Cái Bộ Não Đầu Sỏ Đặc Vụ AI sẽ Ăn Chay Thiền Đói Ngoạm ZERO Kẹo Liên Miên Đâm Trọn Trăm Cú Nhịp Nả (hundreds of steps) Cho Đấu Mà Nó Lọt Tóp Thành Công. Vô Vị Bạc Nhược! Tuyệt Lỗ Phím Đòn Mớm Mượt Lấy Ánh Sáng Để Học Tập Cho Các Khúc Ngã Xoáy Bẻ Cua Ở Giữa Đi Đoạn Đường.
```

### Cách Đỡ Hở: Rải Đều Mật Thơm Đoạn (Dense Shaped Reward)

```python
class RewardShaper:
    def compute_reward(self, state_before, action, state_after, outcome) -> float:
        reward = 0.0
        
        # Món 1: Dọng Cờ Chớp Lọt Ổ Build (+0.5)
        # Món 2: Vá Lỗi Cho Giảm (- Lỗi Bớt 1 con Ghi Nợ Ăn +0.1)
        # Món 3: Cẩu Thả Ngấm Lỗi Sinh Thêm Bu Rác (- Tụt Âm Liền 0.15 phạt mỗi cục rác vãi mới)
        # Món 4: Nhất Trace Lợp Sóng Check Tăng Điểm Càn Lướt (+0.2 Mỗi Cọc Nảy Lên Được 10%)
        # Món 5: Đã Khép Gói Bước Khúc Xong Gọn (+0.3)
        # Món 6: Ngu Chết Chùm Ngoan Cố Một Tội Vướng Nhay Nhấp Lại Chết Tiếp Chỗ Đó (- Âm Liên Tục 0.2)
        # Món 7: Đứng Điếc Tịt Ngòi Cắn Môi Trơ Ra Không Góp Gì no-op (- Phạt 0.1 cho tội rỗi hơi nhấp phím)
        # Món 8: Vinh Quang Chạm Đích Bến Cuối Kết Cùng (+1.0 Ghi nhận vung đập Mãn Cục Tàn Game Trận Thắng Múa Task Xong Đẹp)
        return reward
```

## 4. Ngọn Cờ Trông Giữ Nén Đọng Dừng Khi Lực Đi Vắt Kệt Sự Ép Sóng Điểm Chóp Hội Tụ (Convergence Monitoring)

```python
class ConvergenceMonitor:
    """Phi Hút Máy Soi Chặn Hẹp Quá Đà (early stopping)."""
    # Mắt Thần 1: Hàm Lực Lỗi Ngộp Loss Quăn Chúi Đáy Chưa Dính?
    # Mắt Vòng 2: Mức Nẩy Xới Điểm Chọt Vúng Bay Thụt Qua Độ San Phẳng Phẳng Chưa?
    # Chốt Đoán Đo Lường Dốc 3: Nguồn Tơ Lực Đi Cụt Đường Cạn Nhẵn Tuột Chân Nghét Sự Bứt Lên patience exhausted?
    # Nếu Đi Mòn Cỏ Tịt Cả Chuỗi Hạt 20 nhịp Cạn Sạch → Co Chân Ngắt Cầu Gõ Trượt Trỏ Convergence Rớt Máy CONVERGED Hội Tụ Hoàn Tốt Xong Phim Học Ế Đạn.
```
