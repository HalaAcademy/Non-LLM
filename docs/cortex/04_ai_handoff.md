# Giao thức Chuyển giao Tác nhân AI Cortex (AI Handoff Protocol)
## Hướng Dẫn Kế Khảo Nạp Context Cho Các Phiên AI Mới

> **Phiên bản**: 2.0 | **Cập nhật**: 2026-04-03

---

## ⚡ Bắt Đầu Nhanh (TL;DR) — Quy trình khởi tạo trong 60 giây

```
Bước 1: Nắm bắt bức tranh tổng thể qua file README.md ở thư mục gốc (Non-LLM/)
Bước 2: Nạp dữ liệu hiện trạng mạng lưới thông qua docs/status/shared/project_overview.md
Bước 3: Tải cấu hình dữ liệu Sprint tương thích: docs/status/copl/current_sprint.md (Khối COPL)
         hoặc docs/status/geas/current_sprint.md (Khối GEAS)
Bước 4: Trích xuất các tham số kỹ thuật Spec tương quan (Tham khảo Section 3 trong README.md)
→ Chính thức cấp quyền thực thi thuật toán
```

---

## 1. Điểm Tích Hợp Thông Tin Khởi Nguyên (Entry Point) Duy Nhất

> [!IMPORTANT]
> **Tệp `README.md` tại vị trí Thư mục Gốc được xem định dạng là Tệp Root Duy Nhất để nắm mọi ngữ cảnh dự án!**
> Nơi đây cung ứng chi tiết: Project overview, tài liệu Hierarchy tree map, quy chuẩn Framework rules, và tiến trình Onboarding khởi tạo.

---

## 2. Mã Mẫu Mớm Bồi Trí Trí (Context Prompt Template) - Triển Khai Cho Từng Session Mới

Mỗi khi cấu hình tạo phiên Context làm việc cho Engine Tác Nhân, yêu cầu nạp chuỗi tham chiếu mã sau để thiết đặt Base Model:

```
# Project Context: Thiết lập Hệ sinh thái Cortex (COPL + GEAS Platform)

## Kiến Trúc Nền Tảng Dự Án (Architecture Summary)
Cortex đóng lưới kết hợp giữa 2 khối = COPL compiler (Dòng code ngôn ngữ lập trình cho mảng hệ thống vi nhúng cực đoan an toàn safety-critical) + GEAS (Siêu Tác Nhân Thông minh tự đọc, đánh giá và viết lại code thông qua Machine learning).
Flow chuẩn: Tác nhân GEAS lập trình mô-đun COPL Code → Compiler làm Tester gắt để kiểm chứng dọn rác lỗi → GEAS thu thông tin Audit để tối ưu trải nghiệm đúc kết.

## Chỉ Lệnh Nạp Cội Entry point (Base Navigation Point)
Ưu cầu rà soát cấu hình lõi bằng file README.md (Tại thư mục root local environment).

## Bảng Cập Nhật Thông Số Hoàn Thành Trực Tuyến (Live Tracking Dashboard)
- docs/status/shared/project_overview.md  → Luân chuyển toàn phần tiến độ Core Project Status.
- docs/status/copl/current_sprint.md      → Trạm cấp tiến COPL Sprint
- docs/status/geas/current_sprint.md      → Trạm cập GEAS Sprint

## Mục Tiêu Phát Động Nhiệm Vụ Tức Thời [Điền Task Cụ Thể]
Phân Luồng Hệ Vận Hành (Component): [COPL / GEAS]
Biên Dịch Mục Task (Task Definition): [Mô tả cụm Task Cụ thể]
Đường Viền Tham Chiếu Kỹ thuật (Spec Reference Target): [docs/copl/XX_file.md Section N]
Dấu Hiệu Thoát Exit Condition (Acceptance criteria):
  1. [...]
  2. [...]
  3. [...]

## Bộ Luật Khung "Hardcore" Ngăn Ngăn Chặn Thao Tác Sai Lêch Của Model (Absolute Invariants)
1. Grammar Parsing System bắt buộc tuân theo hệ thức chuẩn LL(1)/LL(2)
2. Không phép phá Cấu Kiến Trúc Spec Nếu chưa được hệ Censor Approval Xác Nhận
3. Mọi phiên viết Code đều đồng thời sinh Test Code (TDD Focus)
4. Mọi task hoàn tất bắt buộc trigger Update lên tệp current_sprint.md 
5. Trong Quá trình Parsing mà sinh Exception do Spec gây ambiguity (Chồng chéo mờ ảo) → Không Assumption Cứ thế bạo Code. BẮT BUỘC ĐƯA VĂN BẢN RAISE VẤN ĐỀ RA `open_questions` file.
```

---

## 3. Bản đồ Liên Kết Nhanh Phục Vụ Tận Răng (Quick Reference Map)

| Mục Đích Tìm Kiếm Cơ Sở Dữ Liệu | Luồng File Đích Quy chiếu |
|-----------|-------------|
| Tổng quan Cấu Trúc Toàn Hình Dự án (Overview) | `README.md` |
| Tiến Độ Báo Cáo Tracking Trạng Thái Bức Tranh Tổng (Status Map)| `docs/status/shared/project_overview.md` |
| Đặc Tả Ngữ Pháp Cú Pháp Ngôn Của Lõi COPL | `docs/copl/01_grammar_spec.md` |
| Bảng Cốt Kiểu Dữ Liệu Bộ Nhớ COPL (Type Systems) | `docs/copl/02_type_system.md` |
| Đặc tả Phương Trúc Ngữ Cảnh Hiệu Chuẩn Báo Hệ Types (Effects Space)| `docs/copl/03_effect_system.md` |
| Bảng Tóm Lược SIR Thông Biểu (Semantic Intermediate Representation) | `docs/copl/04_sir_schema.md` |
| Ý Thức Học Biểu Cảm Hoàn Động Hệ Vận Hành Compiler (Semantics) | `docs/copl/05_operational_semantics.md` |
| Kế cấu Hoạt Vận Bộ Nhớ và Concurrency Thần đồng COPL | `docs/copl/06_memory_concurrency.md` |
| Chuyển Đặc Tả Cơ Sở Mã Kình Hệ Nhỏ Codegen (C System Lowering) | `docs/copl/07_lowering_spec.md` |
| Tính Phối Lệnh Lỗi Cấu Chuyển Biến (Module/Diagnostics Rules) | `docs/copl/08_module_error_handling.md` |
| Bản Vẽ Chuyên Kiến Trúc Lát Cắt Architecture Của Cả Compiler | `docs/copl/09_compiler_architecture.md` |
| Bản Đồ Nhận Não Cảm Đặc Cấu Trúc GEAS model/arch | `docs/geas/01_architecture.md` + `02_core_model.md` |
| Ràng Buộc Cơ Sở SQL Database Cho Phân Khối Nhớ GEAS| `docs/geas/04_memory_system.md` |
| Chuỗi Tiêu Chuẩn Truy Cập Message Network GEAS protocol | `docs/geas/05_protocol.md` |
| Giáp Cạnh Nhau: Bổ Kết Node Cột Interface COPL↔GEAS | `docs/cortex/01_integration_contracts.md` |
| Nội Thiết Tổ Điều Hành Và Trình Tự Bệnh Tuần Cấu Vận (Workflow) | `docs/cortex/06_project_governance.md` |
| Dàn Sắc Tiêu Cấu Xây Kênh Mới Lập Trình (Coding standards) | `docs/cortex/03_work_rules.md` |

---

## 4. Những Thao Tác Chống Chỉ Định Tuyệt Đối Vi Phạm Cho Engine AI (Black-list Actions)

```
❌ Không vận dụng thuật toán Nội Suy Đán Chừng khi bộ Spec không clear (Ambiguity Issue) → Chỉ được đặt cờ Phản Viện Report vào thẻ cấu trúc file `open_questions`.
❌ Tuyệt đối cấm thao túng (Override) tệp tin nội hành trong phân dĩa docs/copl/ hoặc docs/geas/ nếu Không Sở hữu Chứng thực Chuyển Phê Chuẩn Approval.
❌ Cấm rọc hay phân đoạn can thiệp code đã được bảo chứng nhãn Tag Label "DONE — do not touch".
❌ Chống hành động Remove Xóa đi mảng dữ liệu Field tồn tại trong SIR Schema Framework (Lựa chọn nguyên tắt Đồng Thuận Lắp Ráp Nâng Cấp Tịnh Tiến Backward compat bắt buộc).
❌ Chặn lệnh Commit Merge Code nhánh nếu không đi kèm kịch bản Test System.
❌ Dừng cấp khởi Tạo Run File Code Nếu Không Scan Review Trọn Đặc Đặc Cấu Tệp Source Của Spec file định đính.
```

---

## 5. Các Hành Vi Kỹ Thuật AI Phải Đảm Bảo Liên Tuất Hiện Diện (White-list Invariants)

```
✅ Khớp cấu trúc Đọc nạp Bảng Update Lệnh `current_sprint.md` trước khi Action Start.
✅ Liên Thông Update Data Báo Cáo `current_sprint.md` tại luồng End Chốt Nhiệm vụ (Task completed).
✅ Cấu trúc Thông Lệnh Commit messages buộc phải đóng theo đúng Convention màng chuẩn: [scope] text_message.
✅ Buộc Sinh Báo Cáo Yêu Cầu Gỡ Định (Thẻ báo ambiguity `open_questions`) bất cứ lúc nào có mâu thuẫn hệ Framework Error Spec.
✅ Bắt Chuỗi Reference section chi tiết trong cấu trúc Commit message và luồng Pull Request.
✅ Yêu Cầu Render `make test` test validation file local check point trước khi kích Submit PR lện GitHub.
```

---

## 6. Tính Bất Biến Của Đồ Thị Hợp Khớp Lõi Hệ Thống (Invariants Architecture)

```
1. COPL grammar rule: Giữ chuẩn LL(1)/LL(2) — FIRST sets disjoint không thể vi phạm.
2. Các đường biên Interface Khớp NỐI system Contracts: Lệnh Report `pytest tests/contracts/` luân chuyển phải Xanh Green báo Pass hệ 100%.
3. Luồng Gỉa Sữ Báo Cáo Biên Mã Gốc Generated C Target: Được thiết lập Biên Dịch trơn 100% bằng command GCC flag: `-Wall -Werror`.
4. Tính Bảo Tồn SIR data: Trực chỉ cho chèn cấu trúc Data schema Field thêm, Kiên Quyết Không Delete Rối Data (Backward Compatibly strictly imposed).
5. Luồng Sinh Thái Khám Tuyến Hiệu Hệ Đo Effects system rules: Bảo Thủ Đoán Thử Conservative — Việc Test bắt Reject false positive OK (Chấp Thuận Error) , Việc Trót Lọt Accept qua ải Tín Hiệu undeclared effect effect lậu là KHÔNG OK! (Cấm Lỗi Thông Nguồn).
6. Sự Cao Thấp Đặc Tả So Với Mã: Spec > Code (Bộ Đặc định nghĩa luôn Cầm Cự Tín Khải Hơn Bộ Máy Test Thực Tiễn) → Vậy nên khi có sai lệch: Vui lòng Chỉnh Mã Code, Không cố Xuyên Thủng Chỉnh Chuẩn Phá Bỏ Bộ Rule của Spec. 
```

---

## 7. Các Thông Lệnh Verify Cầu Cứng Checkpoints (Phê Duyệt Dịch Sau Đóng Coding Tasks)

```bash
make check        # Cường Vận Hành Tốc < 30 giây: Cán kiểm rác Lint check + Trắc type kiểm hiệu chuẩn checker.
make test         # Cường Hệ Thống < 5 phút: Quét mọi ngóc Unit tests data toàn tuyến files.
make contracts    # Cường Biên Mô < 2 phút: Đo hệ Mạch Intergration Testing Tests Khớp hợp đồng Data.
make ci           # Đo Đạt Hàng Hệ Chuyên < 30 phút: Luân Phiên Full CI Pipeline Server Check.
```

---

## 8. Sơ Đồ Định Tuyến Escalation Bổ Túc Truy Trách Nhiệm 

| Báo Cáo Cường Sự Cố/Vấn Đề (Issue Level) | Thủ Thuật Phản Biện Chấn Chỉnh Lên Trên (Escalation Path Action) |
|--------|-----------|
| Gặp Spec Không Clear (Spec ambiguous) | Chỉnh Trọng Data báo lỗi Lưu thẻ `docs/status/[project]/open_questions/YYYY-MM-DD_topic.md` |
| Phát Hiện Bug Logic Cứng Nguồn Của Spec | Đính ngay Thẻ `docs/status/[project]/spec_issues/name.md` + **Kích Đóng Stop Dừng Đóng Code Implementation ngay lập tức.** |
| Công Đoạn Chặn Block bị ngâm Lì quá > 48 Giờ (2 Ngày) | Tạo Trọng Trình Escalate Thông Lệnh Ngay tại `current_sprint.md`. |
| Nếu Xé Đạo Phá Vẽ Trọng Kiến Trúc Architecture | Đẩy Trình `docs/status/shared/decisions/` + Ràng buộc thông suốt Đợi Hệ Lấy Chữ Ký Request Cho Hệ Nhận Approve Mới Được Rục Rịch Khởi Sự Code! |
