# Đặc tả Chiến Lược Mồi Dữ Liệu GEAS (Data Bootstrap Strategy)
## Đường Ống Huấn Luyện 3 Pha DAgger — Khắc phục G4: "Bài toán Con gà - Quả trứng dữ liệu"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Bài Toán Con Gà Và Quả Trứng

```
Muốn tự động vắt óc huấn luyện Đặc Vụ GEAS → Phải có sẵn núi dữ liệu (các ván cày của Cố vấn Chuyên gia)
Mà MUỐN CÓ đống ván cày Chuyên gia → Thì lại bắt buộc phải TÌM RA NGƯỜI chịu trận múa code
Ai chưa mọc cánh → Thế nên chưa nôn ra được Ván Code
Sạch bách Ván Code → Rỗng ruột khỏi luyện AI

→ KHÚC MẮC TUYỆT PHONG: CHẾT THEO VÒNG LUẨN QUẨN BOOTSTRAPPING
```

## 2. Diệu Kế Nắn Dây: DAgger (Dataset Aggregation) Ép 3 Giai Đoạn

### Pha 1: Trí Tuệ Con Người Mồi Mẫu (Tháng 1-2)

```
Siêu sao Kỹ sư Code Trực tiếp Đóng Phim Nhả Tay bằng ngôn ngữ nền COPL.
Từng Nút Phím, Từng Lựa Chọn Action sẽ bị camera Rình Ghi Nén Lại Thành Các Khối Episode Tuyệt Đỉnh.

Chia Ngạch: Chọn Lọc Trích Bắn vào đúng 20 Cục Task xịn:
  - Khúc Nhẹ Ký: Mở Trắng 1 module lẻ, Dệt thử mã struct, Khởi nắn 1 mảnh func
  - Khúc Cứng Tay: Vát khối dự án đẻ chùm module, Mổ Chữa lệch Kiểu type, Kẹp Nọc Hợp Đồng Contract Contract
  - Khúc Nhằn Cực Khét: Xây Lắp Cấu Trúc Khủng layered, Lên Rạp Hệ Chạy Máy Trạng thái State Machine, Siết Đai Vạch Trace.

Quy Chuẩn Đo Đếm:
  Mỗi 1 Task quất cần bóp ~30-100 vòng nhịp Action = Vắt ra cỡ 30-100 episodes
  Xé Rào Tổng Vụ: Chơi Mướt Trọn 20 tasks × băm nát nhặt ~60 episodes = Thả Vô Chậu Khoảng ~1,200 episodes Đỏ Loét.
```

### Pha 2: Chấp Cánh AI Kẹp Lời Chuyên Gia Chỉnh Đường (Tháng 3-4)

```
1. Lấy rổ 1,200 hạt Mầm Episodes Pha 1 rắc Mồi Não múa Training lót nền Tinh Khôi.
2. Nới Xích Cho Đặc vụ cắn thử Task, Nằm đó run Tự Giác Nhả Lệnh
3. Đụng Trạm Thằng AI Cãi Bướng Đâm Lạc Nhịp Cù Cù Lộn Bước Quyết Định Trượt Quỹ Đạo → Dùng Búa Tiên Nhân Gõ Đầu Chỉnh Nắn ÉP Nhận Tay Sửa action lại (human corrects)
4. Cái Cú Nẹp Lỗi Sửa Kia Sẽ Quết Tròn Ép Mãnh Mới Vô Data Điểm Béo Sụn Mới
5. Vòng Xoáy Lặp Đổ Bồi Bếp Xới Model lại Để Quện Vào Não (Retrain).
```

### Pha 3: Cuộc Tỉ Thí Tự Do Solo (Self-Play Tháng 5+)

```
Lúc này Đặc Vụ Bung lụa Cất Cánh, Miễn Trực Ca Quản Giáo.
Chiếc Thước Kẻ Đo Tính Chính Danh Chốt Hạ Giờ Nằm Trong Tay Bộ Trình Biên Cấu COPL Compiler:
  - Máy Báo Build lọt khe Thơm Phức → Thẻ Xanh Tín Niệm Rót Bài Đỉnh
  - Máy Báo Rớt Xệ Trượt Sập → Điểm Méo Tiêu Cực → Gọi Nhảy Cây Phân Chẩn Lỗi diagnosis → Nắn Sửa Kéo correction.
```

## 3. Khung Nấc Dùi Luyện Tập Curriculum

```
Vòng Gửi Xe Lớp 1 (Siêu Dễ): Gồm 5 tasks mẫu
  T-001: Ép Cấu Mảng struct vát 5 núm fields
  ... (Các task đơn lẻ ráp mã)

Vòng Đấu Khu Cấp 2 (Ngọt Vừa): Gồm 8 Khúc xương
  T-006: Tháp Lòng Nhạc Driver CAN cắm rễ 3 mạch function function
  T-007: Vục Sửa lỗi Lệch Nhịp Cấu Hình type mismatches bẻ gãy dự án
  ...

Vòng Lên Tháp Tử Địa 3 (Mạng Lưới Chằng Chéo): Gồm 7 Quả Lớn
  T-014: Gầy Trọn Ổ Già CAN stack (Chồng Đủ các khe MCAL + BSW + Tầng dịch vụ)
  T-015: Trấn Giữ Lõi VCU Phân Mã Mạch Cỗ Máy state machine Có Viền bọng lướt safety
  T-016: Đập Lỗ Ban refactor Cấu Vịn Phẳng Sang Tầng Layer Chéo...
```

## 4. Rào Chắn Lọc Nước Đục Kiểm Đảm Data Đục/Sạch (Data Quality Gates)

```python
class DataQualityChecker:
    def validate_episode(self, episode: Episode) -> bool:
        # Cửa Điểm 1: Màng Trạng thái State Không Bị lũng lỗ thiếu hụt
        # Cửa Điểm 2: Nước Cờ Lựa Action phải Móng Mặt Đều Trong Gọn Vành Vực 45 Action
        # Cửa Điểm 3: Thẻ Outcome Phải Được Đoán Phán Đóng Nẹp Chắc Nịch
        # Cửa Điểm 4: Gáy Rớt Fail Thì Khối Rễ Diagnosis Đi Kèm Phải Chắc Không Trống Đỡ
        return True
    
    def validate_dataset(self, dataset: list[Episode]) -> DatasetReport:
        # Check Cân Cân Tỷ Đóng Lực (No action >30% or <1%)
        # Cân Nhíp Rớt/Tồn Không Quá Đà Ngọt, Rơi Chệch Luồng 60/40 thì Bóp
        pass
```

## 5. Tổ Cất Nén Kho Episodes

```sql
-- Dàn Lên Khuôn SQLite nén mảng Màng tập Training Episodes
CREATE TABLE episodes (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    branch TEXT DEFAULT 'main',
    timestamp REAL NOT NULL,
    
    -- Gói Kín JSON
    state_json TEXT NOT NULL,
    action_json TEXT NOT NULL,
    outcome_json TEXT NOT NULL,
    
    -- Chỉ vạch Truy Ngợc (Fast query)
    action_type TEXT NOT NULL,
    outcome_class TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    ...
);
```
