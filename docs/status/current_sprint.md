# Sprint 4 — Phase P3 (Code Generation / IR)
**Updated**: 2026-04-04
**Phase**: P3 → IR & C Code Generation
**Sprint goal**: Xây dựng hệ thống Code Generator, biến Typed-AST (đã qua Semantic Rule Check) thành các tệp tin header và source C (.h/.c) có khả năng biên dịch thẳng trên trình biên dịch nhúng (GCC/Clang/Arm-GCC).

## Status: 🟢 ON TRACK

---

## Tasks

### Hoàn thành (Done)
- [x] Toàn bộ thiết kế Spec 10/10 đã xong (Phase P0).
- [x] Phase 1 (Frontend): Lexer & Pratt Parser ổn định. Xuất lỗi chi tiết mảng Parsing.
- [x] Phase 2 (Semantic): Hệ thống gán Type (Type Inference, Checking).
- [x] Phase 2 (Semantic): Quản lý Scope, SymbolTable, Name Resolution, Constraints Immutability (`mut`).
- [x] Đạt 100% Passed Test Cases với 72% Coverage. Báo cáo nghiệm thu `P2_SemanticAnalysis_Report.md`.

### Đang Làm (In Progress)
- [/] (Init P3) Cấu trúc bộ Generator cho vòng đời Emit Code ra `.c`/`.h`.
- [/] Dựng khung Translation Layer biến COPL Structs thành C Structs.

### Chưa Bắt Đầu (Backlog)
- [ ] Chuyển đổi COPL `fn` thành mã code nhúng C an toàn, có bọc macro theo kiến trúc AUTOSAR.
- [ ] Tích hợp Hardware Rules (`lower @target c`).
- [ ] Xây dựng test suite so sánh text C đầu ra.

---

## Metrics hôm nay
- Code: Vừa khởi động Phase 3 (0%).
- Phase 1 & Phase 2: Coverage Test >71%, ổn định hoàn toàn.

## Blockers
Không có.

## Notes
Hệ thống Frontend đã đạt 100% sức mạnh mong đợi, nay được trang bị cả lá chắn Semantic. 
**Bước tiếp theo quan trọng nhất**: Cần thiết lập mô hình Dịch C (C-Transpiler Model) cho phép parse AST thẳng ra Text Stream dạng mảng C Structs. Có thể sử dụng Module Visitor độc lập để thăm trực tiếp các Node đã được đóng dấu bằng Symbol Table.
