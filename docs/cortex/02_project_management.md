# Quản trị Dự án Cortex (Project Management)
## Các Cột mốc, Cổng Kiểm tra Chất lượng và Theo dõi Tiến độ

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Các Giai Đoạn Phát Triển Dự Án (Project Phases)

| Phase | Trọng tâm Phát triển (Focus) | Thời gian triển khai | Điều Kiện Vượt Ải (Exit Criteria) |
|---|---|---|---|
| P1 | Thiết lập Bộ phân tích Cú pháp (COPL Grammar + Parser) | 4 tuần | Parser xuất sắc vượt qua 100% grammar tests |
| P2 | Tích hợp Type + Effect + SIR của COPL | 4 tuần | Vượt qua bài đo mảng Type checker với 3 test projects |
| P3 | Kích phát Trình Sinh Mã COPL (Codegen + Artifacts) | 4 tuần | Mã C (C code) biên dịch mượt mà thông qua trình chuẩn gcc |
| P4 | Cài đặt Bộ nhớ và Nền tảng Nhận thức (GEAS Core Model + Memory) | 4 tuần | Mô hình hoàn tất training, hệ CRUD memory hoạt động chuẩn |
| P5 | Quy trình Tích hợp (Integration) | 4 tuần | Tác nhân giả lập (Mock agent) chạy hoàn thiện luồng EVCU demo trọn chu kỳ |
| P6 | Quá trình Huấn luyện & Đánh giá (Training + Evaluation) | 8 tuần | Độ hoàn chỉnh Task Success Rate (TSR) ≥ 50% tính trên bộ COPL-Bench-20 |
| P7 | Hiệu chỉnh Cuối & Đóng gói Phân phối (Polish + Release) | 4 tuần | Đóng gói Toàn bộ tài liệu Đặc tả (docs), Benchmarks, Publishing packaging |

## 2. Các Mốc Chốt Kiểm Soát Kiểm Định Chất lượng (Quality Gates)

Mỗi giai đoạn (Phase) bắt buộc phải vượt qua mốc chuẩn (Quality gate) trước khi kích hoạt chuyển đổi sang giai đoạn kế tiếp:

### P1 Gate: Đóng Băng Đặc tả Khung Cú Pháp (Grammar Lock)
```
□ Cả 152 hàm biểu thức EBNF productions được kích chạy thành công trong Parser
□ Parser test suite: Mật độ quét kiểm thử chạm ngưỡng 200+ test cases với tỷ lệ Pass là 100%
□ Module Lexer thao tác chuẩn xác toàn phần thẻ Token types hiện hữu (đặc biệt chuẩn COPL-specific)
□ Trục xuất Lỗi an toàn (Error recovery): Tính năng parser tiếp diễn an toàn ngay cả khi chặnSyntax errors.
□ Vượt Bài Ktra (Parse) 3 dự án thử nghiệm mà không có tín hiệu vỡ hệ thống (crash)
```

### P2 Gate: Tính Định Chế Ngữ Nghĩa (Semantic Stability)
```
□ Module Type Checker: Cover toàn bộ quy chuẩn đặc tả typing rules trong tài liệu 02_type_system.md
□ Module Effect Checker: Ràng buộc ma trận tương thích 9 effects × 5 profiles matrix
□ Hệ thiết kế SIR Builder: Đồng nhất tuyệt đối định dạng Output với chuẩn 04_sir_schema.md
□ Các Hợp đồng tích hợp định tuyến (Integration Contracts): Đặc tả Contract #1 (SIR Query) xác nhận Pass.
□ 3 test projects đáp ứng tính tương thích trong 2 môi trường type-check và effect-check clean.
```

### P3 Gate: Sinh Biên Dịch Mã Đích Toàn Quy Trình (End-to-End Compile)
```
□ Luồng C codegen: Bao phủ Toàn cảnh type mappings định sẵn tại `07_lowering_spec.md`
□ State machine lowering: Lập bảng tương quan sinh mã tự động Code (transition table codegen)
□ Contract lowering: Nâng thẩm quyền kiểm định pre/post checks hoạt động trong debug mode
□ Luồng biên dịch C đáp ứng chặt với tập compiler `arm-none-eabi-gcc -Wall -Werror`
□ Kích phát Artifact engine: Khởi tạo module summary cards + dữ liệu trace matrix được đánh dấu.
□ Các hợp đồng tích hợp định tuyến: #2, #3, #4 đạt tiêu chuẩn Pass
```

### P4 Gate: Hiện Thực Nền Tảng AI GEAS (GEAS Foundation)
```
□ Cốt lõi Mô hình: Cơ chế truyền xuôi hoạt động (Forward pass works), với 3 heads kết nối ra Output.
□ Hoàn thành Hệ Cấu Trúc Data SQL SQLite CRUD cho đối tượng episodes + lessons (Memory system)
□ Hoạt xuất Memory retrieval: Trả về chính xác relevant lessons (Thẩm định qua Manual check)
□ Kỹ nghệ Giao thức Message Protocol: Chốt xuất bản 15 Message types đạt chuẩn serializable
□ Định tuyến Data pipeline: Thu thập episode recording and storage hoạt động trơn tru
□ Hệ quy chiếu Hợp đồng tích hợp: Mã #5 (Episode Schema) thông báo Pass.
```

### P5 Gate: Tích Hợp Đa Phân Hệ (Integration)
```
□ GEAS đã nắm đặc quyền thông qua Action Interface để chế khởi modules file .copl tự động
□ Tác nhân GEAS nhận thức hoàn hảo đọc mã Compiler diagnostics
□ Nạp mã SIR reading để nhận diện phân tích logic bản vẽ World model
□ Tác nhân GEAS thu thập lượng lớn artifacts làm nguồn sống bộ nhớ
□ Xác minh luồng vòng cung tuần hoàn: write → build → diagnose → fix works hoạt động tự trị 100%
□ Phiên Mock GEAS agent hoàn tất bộ 3 Level-1 benchmark tasks.
```

### P6 Gate: Bàn Giao Mô Hình ML Training (Training Complete)
```
□ Dữ liệu Training Phân bổ 1-3 training complete (tập tính imitation → outcome → diagnosis)
□ Ghi nhận Tỷ lệ TSR ≥ 50% thao tác thử nhiệm theo trục COPL-Bench-20
□ Độ tin cậy tính năng Hành động Action accuracy ≥ 70%
□ Rà soát tính xác thực của luồng Chẩn đoán Diagnosis accuracy ≥ 60%
□ Gia tốc biểu đồ Học Machine Learning Learning curve show rõ mức độ tiến hóa cải thiện dự án.
□ EWC phát huy tác dụng cản phá sự cố suy giảm chức năng bộ nhớ Catastrophic forgetting (kiểm định 3 bài liên tiếp)
```

## 3. Hệ Thống Tra Cứu Tiến Độ (Progress Tracking)

### 3.1 Mẫu Báo Cáo Định Kỳ Hàng Tuần (Weekly Status Report Template)

```markdown
# Báo Cáo Cường Độ Tuần (Week N Status Report)

## Tóm Lược Cơ Sở (Summary)
- Giai đoạn dự án: Phase P{n}
- Tiến trình triển khai: {pct}%
- Trạng thái kế hoạch: On Track/ At Risk

## Luồng Công Việc Hoàn Thành (Completed This Week)
- [x] Item 1
- [x] Item 2

## Các Đầu Việc Trong Quá Trình Thi Công (In Progress)
- [/] Item 3 (50%)
- [/] Item 4 (20%)

## Cảnh Báo Treo Dự Án (Blocked)
- [ ] Item 5 — Cản trở bởi lý do: {reason}

## Đo Đạt Số Liệu Thống Kê (Metrics)
- Số Lượng Test thành công: {n}/{total}
- Hợp đồng Contract tests hoàn tất: {pass}/{total}
- Độ bao phủ Code coverage báo cáo: {pct}%

## Biện Pháp Phân Tích Rủi Ro (Risks)
- Cảnh báo số 1: {description} — Hướng khắc phục: {action}

## Lịch Trình Cam Kết Tuần Tới (Next Week Plan)
- [ ] Item 6
- [ ] Item 7
```

### 3.2 Bảng Điều Khiển Tự Động Chỉ Số (Automated Metrics Dashboard)

```python
class ProjectDashboard:
    def generate(self) -> DashboardData:
        return DashboardData(
            # Tín hiệu sức khỏe quá trình Built (Build health)
            parser_tests=run_tests("tests/parser/"),
            type_checker_tests=run_tests("tests/types/"),
            codegen_tests=run_tests("tests/codegen/"),
            contract_tests=run_tests("tests/contracts/"),
            
            # Đo lường Mảng Source Code metrics
            loc_copl_compiler=count_loc("src/copc/"),
            loc_geas_agent=count_loc("src/geas/"),
            loc_tests=count_loc("tests/"),
            test_coverage=measure_coverage(),
            
            # Cấu hình tính điểm Quality
            open_issues=count_issues(status="open"),
            lint_warnings=run_linter(),
        )
```

## 4. Bố Trí Phân Hạng Nhân Sự Tiêu Chuẩn (Resource Allocation)

```
Dự Án COPL Team (Giai đoạn Tháng 1-4):
  1 Trưởng Nhóm: Đảm trách Thiết kế Ngôn ngữ (Language design) + Cấu hình Grammar
  1 Chuyên Viên Phân Tích:  Tạo lập Parser + Tối ưu Type checker
  1 Chuyên Viên Xây Dựng: Tác dụng hóa Codegen + Mô hình Lowering
  0.5 Chuyên Viên Tester: Giữ vững Tests + cấu trúc CI

Dự Án Lõi AI GEAS Team (Giai đoạn Tháng 1-4): Ưu Tiên Design Only
  1 Lãnh Đạo Trưởng: Gọt rũa Architecture + specifications
  0.5 Kỹ sư Trí tuệ Ảo: Vẽ khối Memory system prototype
  0.5 Chuyên Gia Kỹ thuật: Setup Tooling lưu chuyển Data collection

Quá Trình Tích Hợp Cấu Trúc Toàn Hệ (Months 5+):
  Kiến Tạo Khối Luồng Thỏa Thuận Liên Minh 100% thành viên (Full team converges)
```
