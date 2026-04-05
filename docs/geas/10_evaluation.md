# Đặc tả Đánh Giá & Thước Đo Khúc Căn GEAS (Evaluation & Benchmarks)
## Thang Điểm Mét Đo Sòng Phẳng — Khắc phục G10: "Chưa Có Cam Kết Hội Tụ Học Nhả"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Không Gian Chiều Đo Lường (Evaluation Dimensions)

| Chiều Kích Phẳng Dimension | Bóp Nắm Bắt Cái Gì | Đích Ngắm Xuyên Tâm Tới |
|---|---|---|
| Tỷ Lệ Ăn Nhịp Tác Vụ (Task Success Rate) | Số Phần Trăm % Nhiệm Vụ Vặn Xong Mỹ Mãn Mà Chẳng Thở Oải Nhờ Cứu Viện Con Người | ≥70% |
| Điểm Chạm Lệnh Vun Giòn (Action Accuracy) | Mức % Quyết Đóng Chọn Chuẩn Y Xì Rập Cố Vấn Tôn Gia | ≥80% |
| Chuẩn Bắt Mạch Bệnh (Diagnosis Accuracy) | % Trúng Sảng Điểm Nọc Mầm Chẩn Lỗi Rễ Cốt Root cause | ≥75% |
| Tinh Khối Chuẩn Gốc Rễ Bài Học (Lesson Quality) | Mức Kéo Chọn Nảy Đúng Trọng Bài Vàng Đắp Cho Trúng Vấp | ≥70% |
| Hiệu Ứng Bám Cơ Rút Gon Bước Gõ (Efficiency) | Số Vạch Đo Lệnh So Đọ Cân Kéo Tương Vấn Chuyên Gia Ráp | Ăn Điểm Móp ≤2x Chuyên Gia |
| Tốc Cuộn Rate Học Bóng Trí (Learning Rate) | Điểm Phết Phá Điểm Chạm Cảm Trăm Tiến Tuốt Dấu Qua Các Ván project | Cầm Kim Giác Đo Được Sát Số |

## 2. Vạn Kiếm Bộ Càn Quét Điểm Benchmark

### 2.1 COPL-Bench-20

```
20 Cục Quả Tạ Thép Task Cho Bóp Mép Nặn Nắn Đánh Giá Thẳng Tay Thôi Thúc:

Đai Cấp Dễ Rớt 1 (5 vũng bài tasks): Bập Mảng Buồng module đơn rẽ bới
  Bench-01: Khuôn Váp struct đắp rễ nối 3 hàm function
  Bench-02: Điền Băng Vét Triển Trait vào Ngôi type Đã Chôn
  Bench-03: Va Nốt Giã Chết 3 Quả Bug Type Căn Lỗi Găm Mủ code
  Bench-04: Đắp Vá Hòm Khóa Contract Cúp Trói Vòng Nhảy Cả 5 functions
  Bench-05: Khởi Chạo Dựng module Ngấu Profile Chuẩn + Xốc Effect Gắn
  ...

Vòm Cấp Rễ Trạc Găm Chéo Khó Nhằn 2 (8 nốt tasks):  
  Bench-06: Rút Mảng Tấn Công Sinh Kép CAN driver (Nền cõi MCAL)
  Bench-11: Sang Bằng Phẳng Vuốt Trụ Móng Khấp Bậc Code Rác Tạp refactor Cho Vuông Ống Vẩy Lớp layered
  Bench-14: Băm Chạm Xé Cụm Làm Dự Án Bự EVCU Tuyệt Hảo Trấn Trọn
  Bench-20: Rũ Bọc Áp Khúc Toàn Diện Giấu Kép Trục Hệ (Require → code → test → báo cáo trọn gói)
```

### 2.2 Điểm Sổ Chấm Thu Lưới Săn (Scoring)

```python
class Benchmark:
    def score(self, task: BenchTask, agent_result: AgentResult) -> BenchScore:
        return BenchScore(
            # Đòn Đâm Cột Trụ Đáy Primary
            success=agent_result.task_completed,
            steps=agent_result.total_steps,
            expert_steps=task.expert_steps,
            efficiency=task.expert_steps / max(1, agent_result.total_steps),
            
            # Cân Khối Vàng Đóng Nét Quality
            build_success=agent_result.final_build_success,
            trace_coverage=agent_result.final_trace_coverage,
            
            # Sức Trườn Bước Kéo Phanh Learning
            lessons_extracted=len(agent_result.lessons),
            errors_self_corrected=agent_result.self_corrections,
        )
```

## 3. Khối Điểm Chỉ Tiêu Rắn (Key Metrics)

### 3.1 Nhíp Tróc Điểm Phá Task (Task Success Rate - TSR)

```
TSR = (Xấp Tổng Úp Tasks Đã Gom Kết Toàn Diện Mỹ Mãn) / (Trọc Liện Rổ Tasks Nắm Lại Đụng Ngón Vô Đóng)

Chỉ Điểm Ngạch Cổng Bóp:
  Dằn Sau Pha Súc Huấn 1: TSR ≥ 30% (Cho rổ Trạm Dễ Nhẹ Level 1)
  Sau Tút Gọt Cựa Pha 3:  TSR ≥ 60% (Lướt càn đủ bãi cấp levels)
  Quất Rẽ Thượng Bậc Cục Pha 5: TSR ≥ 70%
  Vung Sức Ngai Lên Ngọn Ở Production (Khởi 6 Nguyệt Lắn Ván): TSR ≥ 80%
```

### 3.2 Tác Vụ Ăn Trúng (Action Accuracy - AA)

```
Độ So Kéo Y Xì Ngòi Bút:
AA = Σ 1(aᵢ = a*ᵢ) / N
(Với aᵢ Là ngòi bút nã của Đặc vụ, Và a*ᵢ Lại Ngọn Vàng Gõ Trúc Tôn Gia Tạc)

Do có điểm Chạm Rãnh Hợp Lệ Của Cùng 1 Giải Pháp Đè Nhau Nút Đụng Nhiều Chéo Mép: Lấy Thêm Số Nghĩa Theo top-3
```

### 3.3 Đo Cuộn Trục Điểm Bắt Bệnh (Diagnosis Accuracy - DA)

```
DA = (Số Cuội Rễ Chẩn Úp Đúng Bắt Vòi Nọc) / (Lỗ Thất Bại Tè Le Bệ)
Đè Đo Chéo Xát Lên Miếng Gắn 15 Tầng Mã Bệnh. 
```

### 3.4 Sóng Trục Bật Đường Đẩy Điểm Chạp Khúc Học Mạch (Learning Curve)

```
Trục Gióng Nhảy Đảo: Trọc Phản Cột TSR Tương Đo Chiếu Cấu Mảng Các Project Cắm Số Luợng Cắn Xong

Sóng Tự Tại Sức Vuốt Vụt: Nháp Đáy Theo Hình Bậc Thang Cóc Tuyệt Chép Tăng dần
  Dự rào thứ 1:   TSR lỏng ~40%
  Sang Vách Chướng số 10:  TSR nẹp ~75%
  Vuốt Vọt Qua Nắm 20:  TSR xé ~80%  (Áp Phả Chạm Móc Nghẽn Sàn Đáy Trần)

Điểm Nổ Thất Thoát Gãy Lỗ Trống: Rạch Chứa Cắt Phẳng Lì Không Bật Ngóc Lên Hoặc Ngắm Rớt Tuột Vấp Bực Hạ Điểm Sóng Điểm Khẳng Định Bệnh Học Của Quỷ AI Lủng Đứt.
```

### 3.5 Bát Tỉ Độ Trườn Bước Mỏi Nhịp Cân Ép (Efficiency Ratio - ER)

```
ER = Phím Nhịp Bước Ráp Chuyên Gia / Bước Bộ Non Nớt AI Agent
Ngấp Ngoé ER = 1.0 Chóp Khủng Khiếp Tuyệt Bút Không Vấp Gõ So Lo Tầm Kéo Cắn Cùng Bác Chuyên Gia
Chênh Lệch ER = 0.5 Óc Múa Đo Đi Bước Chập Rập Cỡ Nhai Nát X2 Thời Gian So Cơ Trí Đội

Điểm Neo Thét Ngắt Chọn: ER ≥ 0.5 (Bo lọt kẹp quanh giới biên Ranh Giới Chênh X2 Quá Lố So Vụ Chuyên Gia Là Tốt Dày)
```

## 4. Khuôn Điệp Lịch Cào Điểm (Evaluation Protocol)

```python
def evaluate(model, benchmark: list[BenchTask]) -> EvalReport:
    # Cuống Lập Sàn Rửa Trắng Bễ Nhớ Gốc Lắp Đo (Fresh memory)
    # So Chiếu Cấu Điểm Phán Lược Trọn Vẹn Đè Qua Bức
    pass # Cắt Giảm Logic Để Gom Lệnh
```

## 5. Mắt Soi Trữ Ván Cày Tròn Chặn Continuous Monitoring

```python
class ProductionMonitor:
    def report_weekly(self) -> WeeklyReport:
        # Báo Lọt Danh Tiếng Cứ Đùn Mỗi Tuần Tạc Gắn Thông Biên
        # Rò Tỉ Tỷ Điểm Rót Dây TSR
        # Dóc Trắng Những 5 Lời Cứ Bài Trái Thói Ăn Mấu Sai Cục Ngoạn Nhất Để Lo
        pass # Rút Ngắn Hàm Code Để Tối Giản
```
