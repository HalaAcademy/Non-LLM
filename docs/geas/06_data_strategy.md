# Đặc tả Chiến Lược Dữ Liệu (GEAS Data Bootstrapping Strategy)
## Quy trình Huấn luyện 3 Giai đoạn DAgger — Khắc phục G4: "Bài toán thiếu Khởi tạo Dữ liệu"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Bài Toán Khởi Phân Dữ Liệu

Quá trình khởi tạo Mô hình GEAS đối mặt với vấn đề "Con gà - Quả trứng":
- Yêu cầu cấu trúc: Để hệ thống có thể tự học (Training), cần có số lượng lớn dữ liệu cấu trúc (Data Episodes) ghi nhận các thao tác chuẩn của con người.
- Thách thức: Phải có con người thực hiện các thao tác thủ công, được ghi nhận đúng chuẩn của hệ thống Episodes. Nếu không có dữ liệu khởi tạo, Hệ thống AI sẽ không có định hướng cơ bản. 

**Giải pháp đề xuất**: Sử dụng phương pháp **DAgger (Dataset Aggregation)** kết hợp vòng lặp luân phiên 3 giai đoạn (Con người - Học Nửa Giám Sát - Tự Tương Tác).

## 2. Giao thức DAgger 3 Giai Đoạn (Dataset Aggregation)

### Giai đoạn 1: Khởi Tạo Tệp Dữ Liệu Chuyên Gia (Tháng 1-2)

- Các Kỹ sư Phần Mềm sẽ trực tiếp thao tác và giải quyết bài toán mã nguồn, sử dụng nền tảng COPL.
- Mọi nút bấm, lệnh gọi (Action), và phản hồi hệ thống (Outcome) đều được ghi nhận (Logging) thành các Episode.

**Phạm vi Phân Lớp Task Khởi tạo (20 Tasks Core):**
- **Cấp độ Cơ bản (Level 1):** Khởi tạo Module đơn giản, khai báo biến (Struct), và viết các hàm cơ bản (Functions).
- **Cấp độ Mở rộng (Level 2):** Điều hướng thiết kế Architecture, sửa lỗi Type Casting, lập cấu hình Contract Rules.
- **Cấp độ Phức Tạp (Level 3):** Xây dựng Cấu trúc Layered, kiến tạo State Machine, đo đạc thông số Trace và Test cases.

**Phân Bổ Kế Hoạch Đo Lường:**
- 1 Task tiêu thụ trung bình 30-100 thao tác (Actions) = Tương đương 30-100 Episodes.
- Tổng Dữ liệu: 20 Tasks × 60 Episodes = Khoảng ~1,200 Tập Lệnh Khởi đầu (Golden Dataset).

### Giai đoạn 2: Tương Tác & Hiệu Chỉnh Có Giám Sát (Tháng 3-4)

1. Cập nhật Model Base với tập 1,200 Episodes để học các quy luật nền tảng.
2. Khởi chạy Mô phỏng (Simulated Execution) để GEAS xử lý các bài toán độc lập.
3. Nếu Agent rớt luồng hoặc đưa lệnh sai, các chuyên gia sẽ ghi đè và Hiệu Chỉnh Hành Động (Action Correction).
4. Các bản vá của Chuyên Gia sẽ được đóng gói lại thành các Lesson/Episode mới và nạp ngược lại vào Cơ sở Dữ liệu.
5. Vòng lặp tái cấu trúc Model (Retraining process) sẽ được thực hiện thường xuyên.

### Giai đoạn 3: Tự Thẩm Định (Self-Play) (Tháng 5+)

- Mô hình hoạt động Độc lập (Autonomous Loop).
- Khả năng thẩm định tính đúng/sai hoàn toàn chuyển sang kết quả xác thực từ COPL Compiler:
  - Phản hồi **Thành công (Build Success/Test Passed)**: System tự động gắn cờ Tích cực (Positive Reinforcement).
  - Phản hồi **Lỗi (Compile Error/Fail)**: System tự động kích hoạt Module Diagnostic để phân tích Root-Cause, vá sửa (Self-Correction), và đóng gói bài học (Negative Reinforcement Lesson).

## 3. Khung Đào Tạo Và Tăng Tiến (Curriculum Matrix)

```
Level 1 (Dành cho Giai đoạn Mồi - 5 Tasks Cơ sở)
  T-001: Khởi tạo Struct 5 thông số.
  T-002: Lập trình Logic cơ bản qua các dạng hàm Logic tuyến tính.

Level 2 (Dành cho Giai đoạn Rèn - 8 Tasks Nâng cao)
  T-006: Khởi chạy Controller / Driver Component.
  T-007: Khắc phục lỗi tương thích kiến trúc Type Mismatches Error.

Level 3 (Dành cho Khảo sát Self-play - 7 Tasks Hệ thống)
  T-014: Thiết kế Network Architecture (Ví dụ: CAN Stack với MCAL + BSW + Service layers).
  T-015: Khởi lập Logic Điều khiển trung tâm (Vehicle Control Unit / Safety Control Machine).
  T-016: Refactor lại Cấu trúc mã sang phân cấp Layers độc lập.
```

## 4. Quản Trị Cổng Chặn Filter Dữ Liệu (Data Quality Gateways)

```python
class DataQualityChecker:
    def validate_episode(self, episode: Episode) -> bool:
        # Gateway 1: Kiểm tra State Context có đủ Payload
        # Gateway 2: Action Logging hợp lệ (Nằm trong 45 Allowed Actions)
        # Gateway 3: Chỉ định Điểm Outcome phải liên kết thành công với Trạng thái Compile
        # Gateway 4: Root-cause Diagnosis bắt buộc đi kèm nếu trạng thái là Bại (Failed)
        return True
    
    def validate_dataset(self, dataset: list[Episode]) -> DatasetReport:
        # Cân bằng Dữ liệu (Class Balance Threshold):
        # - Đảm bảo không Action nào chiếm ưu thế tuyệt đối (>30%) hay bị bỏ sót (<1%).
        # - Hệ số Phân Cực Outcomes: Duy trì tỉ lệ Success/Failure trong ngưỡng dung sai 60/40.
        pass
```

## 5. Tổ Chức Lớp Lưu Trữ Dữ Liệu (Storage Schema)

```sql
CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    timestamp REAL NOT NULL,
    
    -- Lưu trữ khối Data JSON
    state_json TEXT NOT NULL,
    action_json TEXT NOT NULL,
    outcome_json TEXT NOT NULL,
    
    -- Truy vấn Index Cao Cấp
    action_type TEXT NOT NULL,
    outcome_class TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    ...
);
```
