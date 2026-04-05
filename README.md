# COPL Compiler (copc) v0.3.0
**A Systems Programming Language for Safety-Critical Environments**

COPL (Component-Oriented Programming Language) là ngôn ngữ lập trình hệ thống được thiết kế đặc biệt cho các hệ thống nhúng, xe điện (EVCU), phần mềm hàng không, và tự động hóa - nơi sự an toàn (safety) và hiệu suất biên dịch là trên hết.

Dự án này bao gồm Trình biên dịch COPL sang C (COPL-to-C Transpiler), được trang bị các tính năng phân tích tĩnh (Static Analysis) chuyên sâu và mô hình sinh Artifact cho AI Agent.

---

## Tính Năng Cốt Lõi (Core Features)
COPL Compiler `v0.3.0` hỗ trợ 10 tính năng lõi (Phase 1-10) đầy đủ:

1. **Syntax & Parser Mạnh Mẽ**: Lấy cảm hứng từ Rust, thân thiện và chặt chẽ.
2. **Effect System**: Kiểm soát chặt side-effects (IO, Heap, Register) với 9 effect types và hệ thống Profile (embedded, kernel, portable...).
3. **Profile Enforcement**: Chặn đứng các hành vi lỗi (panic), cấm các kiểu biến động (String, Vec) trên thiết bị nhúng ngay lúc biên dịch.
4. **Contract-Based Design**: Kiểm tra `@contract` (pre/post-conditions) và budgets cấp phát (`latency_budget`, `memory_budget`).
5. **Traceability**: Link trực tiếp các file source code (functions/tests) với Requirements (Mã đặc tả) qua `@trace`.
6. **Hardware Lowering**: Tính năng Native cho phép nhúng trực tiếp code phần cứng cấp thấp `lower_struct`, `lower @target c`. Cực kỳ hữu dụng khi viết Drivers.
7. **Control Flow to C**: Tự động chuyển đổi `if/else`, `while`, `match` (Thành `switch`), `break/continue` ra mã nguồn C sạch nề nếp.
8. **Incremental Compilation**: Phát hiện cache thay đổi (Băm SHA256) giúp luồng dịch nhanh chóng mặt (~10ms) với CSDL SQLite tích hợp. Đóng gọi recompilation set thông minh.
9. **Test Framework Trực Tiếp**: Viết hàm `test_fn` trong chính code của COPL với builtin assertions, coverage checking và auto-orchestrator.
10. **Semantic IR & AI Artifact Engine**: Hỗ trợ xuất Cấu trúc dữ kiện ngữ nghĩa SIR dưới dạng JSON và thẻ "Summary Cards" để các Bot AI (Agent) tiện phân tích ngữ cảnh hệ thống.

---

## Hướng dẫn sử dụng (User Guide)
Tài liệu đầy đủ để thao tác Lập trình và Cấu hình COPL Compiler có thể được tìm thấy tại:  
👉 **[docs/copl/00_USER_GUIDE.md](docs/copl/00_USER_GUIDE.md)**

---

## Cài đặt (Getting Started)

Cài đặt bằng cách tạo Virtual Environment (Yêu cầu Python 3.10+):

```bash
# 1. Khởi tạo môi trường
python3 -m venv venv
source venv/bin/activate

# 2. Chạy thử COPL Compiler CLI
python coplc.py -h
```

---

## Các Dòng Lệnh Cơ Bản (CLI Commands)

1. **Check & Phân Tích (Dry-run)**:
Kiểm tra Lỗi Cú pháp, Kiểu dữ liệu, Hiệu ứng (Effects) mà KHÔNG sinh ra mã.
```bash
python coplc.py check examples/02_can_driver.copl
```

2. **Dịch ra Mã C**:
```bash
python coplc.py build examples/02_can_driver.copl -o build_output/
```

3. **Xuất Phổ hệ Ngữ Nghĩa (SIR JSON)**:
```bash
python coplc.py sir examples/02_can_driver.copl -o build_output/sir.json
```

4. **Kích hoạt Gói tạo Phân Tích Artifact cho AI (AI Bundle)**:
```bash
python coplc.py artifacts examples/02_can_driver.copl -o build_output/ai_bundle/
```

---

## Chạy Test Hồi Quy (Test Suite)

Dự án dùng `pytest` và hiện đang bảo lưu **274 Unit Tests** đảm bảo kiến trúc không gãy vỡ (100% Pass).

```bash
pip install pytest
PYTHONPATH=src pytest tests/ -v
```

---

*COPL Compiler — An open-source project by HalaAcademy.*
