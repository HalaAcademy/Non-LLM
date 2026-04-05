# Đặc tả Hệ Đánh Giá & Benchmark COPL/GEAS (Evaluation & Benchmarks)
## Khung Đo Lường Chất Lượng Định Lượng (Quantitative Quality Metrics)

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Không Gian Số Liệu Đánh Giá (Evaluation Dimensions)

Hệ thống đánh giá năng lực của GEAS dựa vào bộ 6 Chỉ số đo lường hiệu suất chính (Key Performance Indicators):

| Chỉ Số Đánh Giá (Metric Dimension) | Ký Hiệu | Ý Nghĩa Chuyên Môn | Chỉ Tiêu Cấp Thấp Nhất (Threshold) |
|---|---|---|---|
| **Tỷ Lệ Hoàn Thành Tác Vụ** (Task Success Rate) | **TSR** | Tỷ lệ phần trăm tính chất hoàn thành Task End-to-End mà không cần User can thiệp. | **≥ 70%** (Production Level) |
| **Độ Chính Xác Hành Động** (Action Accuracy) | **AA** | Điểm So Sánh Khớp hành vi giữa AI Agent Action Selection và Lịch Sử Log Expert Hành Động Kỹ Sư. | **≥ 80%** |
| **Độ Chuẩn Xét Phân Tuyến Lỗi** (Diagnosis Accuracy)| **DA** | Tỉ lệ % tìm ra Đúng Nguyên Nhân Cốt Lõi (Root-Cause) của các lỗi Biên Dịch Thất Bại. | **≥ 75%** |
| **Tính Hợp Chuẩn Extract Bài Học** (Lesson Quality)| **LQ** | Xác suất Gọi đúng cấu trúc của Lesson Database trong Context truy vấn Similarity Cosine Search. | **≥ 70%** |
| **Hiệu Suất Thực Thi** (Efficiency Ratio)| **ER** | Tổng Tỷ số so sánh Số Lượng Hành Động của Agent (Steps) với Số Lượng Hành Động của Chuyên Gia. | Số Bước Tiêu Hao **≤ 2X** Chuyên Gia |
| **Tỉ Lệ Thích Ứng Học Nhanh** (Learning Rate/Curve) | **LRate** | Tỉ lệ Tiến bộ trong việc khôi phục và Đọc Kiến Thức từ các Lượt Học (Episodes). | Mạch Progress Không Đứt Gãy Tụt Lùi |

## 2. Bảng Mô Hình Đánh Giá Chuẩn Hóa: COPL-Bench-20

Bộ Khảo Sát Đánh giá GEAS sử dụng bộ **20 Bài Toán Mẫu Khó Tích Lũy (Target Tasks)** phân bổ dọc theo 3 Cấp Độ (Tiers):

### 2.1 Phạm Vi Bài Toán Cấp Độ Benchmarks (Target Suites)

- **Cấp độ 1 (Low-hanging Fruits - 5 Tasks):** Tác vụ khởi tạo File, Module, Cấu trúc Struct, định tuyến Data Mặc định.
  - Ví dụ: `Bench-01` (Tạo Header File chứa 3 Modules Struct có Dependencies).
- **Cấp độ 2 (Complex Logic Blocks - 8 Tasks):** Tác vụ Dựng Driver Kiến Trúc Hệ Ngoại Vi, System State, Lỗi Cấu Trúc Architecture Dependencies.
  - Ví dụ: `Bench-06` (Xây Dựng Khối CAN Driver Mapping Trong Sub-layer MCAL).
- **Cấp độ 3 (Full Stack Architectural System - 7 Tasks):** Tác vụ System Application Tích hợp Toàn diện (Toàn mảng EVCU, Multi-layers, Cấu trúc OSEK OS).
  - Ví dụ: `Bench-20` (Requirements -> Lập Trình Modules OSEK OS -> Tự Sinh Unit Test -> Generates Report Của File Hệ Thống).

### 2.2 Công Thức Chấm Điểm Thắng Thua (Scoring Algorithm)

```python
class Benchmark:
    """Class Đánh Giá Từng Bộ Agent Run theo Chuẩn Thông Số."""
    
    def score(self, task: BenchTask, agent_result: AgentResult) -> BenchScore:
        return BenchScore(
            # Tiêu Cực Cốt Lõi (Primary Direct Outcome Checks)
            success=agent_result.task_completed,
            steps=agent_result.total_steps,
            expert_steps=task.expert_steps,
            efficiency=task.expert_steps / max(1, agent_result.total_steps),
            
            # Cấu Trúc Khối Output Check File Quality Tích Lũy Bền Vững (Quality Validations)
            build_success=agent_result.final_build_success,
            trace_coverage=agent_result.final_trace_coverage,
            
            # Thuật Đo Học Machine Learning Progress Analytics
            lessons_extracted=len(agent_result.lessons),
            errors_self_corrected=agent_result.self_corrections,
        )
```

## 3. Kiến Trúc Toán Học Đo Lường

### 3.1 Giao Tính Học Hỏi Liên Hoàn (Learning Curve Monitor)

- Quỹ Đạo Chỉ Số Tiến Trình: Tỷ Lệ TSR So chiếu Cùng Dải Số Số Lượng Episodes System Training.
- Yêu Cầu Cấu Trúc Đạt Ngưỡng Lõi:
  - Cột mốc 1 (Sau 2k Episodes mồi): TSR Đạt Cấp ~40%.
  - Cột mốc 2 (Sau 8k Episodes Phân Chẩn): TSR Tăng ~75%.
  - Cốc mốc 3 (Tích lũy Phá Đảo System Final Runtime): TSR Lên >=80% Ổn Định Biên Độ Nhiệt.

- Sự Kiện Hủy Kéo Thụt Lùi: Bất kỳ sự rớt biểu đồ tụt liên tiếp qua >= 2 Epoch đánh dấu khả năng Catastrophic Forgetting.

### 3.2 Tần Số Năng Lượng Rút Gọn Tác Vụ (Efficiency Ratio - ER)

```
ER = Steps_of_Human_Expert_Baseline / Steps_of_AI_Agent
```
Ngưỡng Yêu Cầu (Pass Condition Limit): `ER ≥ 0.5`. (Tức Agent Không Chậm Quá Gấp 2 Lần Tốc Độ Xử Lý Chuyên Gia - Phạt Cấm Nếu Vi Phạm).

## 4. Quá Trình Automated Evaluation Protocol Giám Sát

```python
def evaluate(model, benchmark: list[BenchTask]) -> EvalReport:
    """Phiên Khảo Thí Test Module Tự Động Định Kỳ"""
    # 1. Reset Fresh Memory: Database khởi chạy trong Sandbox rỗng.
    # 2. Ráp Chuỗi Run Agent Loop.
    # 3. Quét Thu Thập Output So Chiếu Điểm.
    pass 
```

## 5. Giám Sát Real-Time Continuous Production (Production Monitor)

```python
class ProductionMonitor:
    def report_weekly(self) -> WeeklyReport:
        """Dashboard Report Hàng Tuần Về Tracking Chỉ Số TSR và Vệt Lùi System Lỗi Agent."""
        pass 
```
