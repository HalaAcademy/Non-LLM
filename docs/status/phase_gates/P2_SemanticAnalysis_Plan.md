# Phase 2: Semantic Analysis & Type Checking Plan
**Date**: 2026-04-04
**Target Duration**: Sprint 3 & Sprint 4

## 1. Mục Tiêu (Objective)
Đầu vào của Phase 2 là Cây Cú Pháp (AST) đã được sinh ra từ Phase 1 (100% hợp lệ về ngữ pháp text).
Mục tiêu là biến AST này thành một **Typed AST** hoặc **Semantically Validated AST**, trong đó mọi biến, tên hàm, toán tử đều được gắn kiểu dữ liệu hợp lệ (Type Binding) và mọi quy tắc ràng buộc logic (Context, Contract, Type Safety) đều được thực thi chặt chẽ.

## 2. Các Thành Phần Cốt Lõi Cần Xây Dựng

### 2.1. Symbol Table & Scope Management (Quản Lý Tầm Vực)
- **Cấu trúc dữ liệu**: Xây dựng mảng lưới `Scope` kiểu Tree (mỗi block sinh ra 1 scope con chứa Local variables).
- **Phân giải định danh (Name Resolution)**:
  - Khi gặp `let x = 5;`, lưu `x` vào Scope hiện tại.
  - Khi sử dụng biến `x`, tra ngược từ nhánh Scope lá lên Global Scope.
  - Phân giải Qualified Names (`CanStatus::Ok`, `std::vec::Vec`) đến đúng Enum Variant hoặc Module Declaration.

### 2.2. Type System & Type Checking (Hệ Thống Kiểu)
- **Type Representation**: Chuyển đổi ASTType (các node Type String thuần) thành các Model Type thực sự trong Python (`PrimitiveType`, `StructType`, `EnumType`, `PointerType`, `ArrayType`).
- **Type Inference (Suy diễn kiểu)**: 
  - Suy luận logic từ `let x = 5` => Kiểu `U32` hoặc `I32` (hoặc Inference Default Type).
- **Expression Evaluation**:
  - Binary Operators chỉ được thực hiện trên cùng Type (`U8` + `U8`). 
  - Assign Ops phải khớp biến bên trái (L-Value) và phải có tính khả biến `mut` nếu L-Value là LetStmt.

### 2.3. System Context & Hardware Effects Enforcer
- **Contract Checker**: Verify `pre`, `post`, `invariants` block bên trong Function. Đảm bảo chúng phải là các Expression trả về `Bool`.
- **Effects Tracker**: Ghi nhận và kiểm tra vi phạm `@effects [register]`. Chẳng hạn: Nếu gọi hàm có `@effects [register]` từ một hàm không có quyền hardware, văng Semantic Error!
- **Target Verification**: Xác nhận các `lower @target c` chỉ chạy nếu Platform có hỗ trợ profile nhúng cấp thấp (VD: embedded/C).

## 3. Kiến Trúc Mã Nguồn (Dự Kiến)
Hệ thống Phase 2 sẽ được code tại `src/copl/semantics/`:
1. `types.py`: Khai báo các class lưu trữ trạng thái kiểu tĩnh.
2. `scope.py`: Trình quản lý Symbol / Tầm vực.
3. `analyzer.py` / `type_checker.py`: Module chính dùng mô hình **Visitor Pattern (Tree-Walker)** để duyệt qua mọi node AST.
4. `diagnostics.py`: Kế thừa `DiagnosticBag` để sinh Semantic Error Type (Vd: "Undefined variable", "Type mismatch: expected U32 but got Bool").

## 4. Các Bước Thi Công Chinh Phục (Milestones)
- [ ] **Milestone 1**: Dựng khung `Type` dataclass và `Scope / SymbolTable`.
- [ ] **Milestone 2**: Dựng `ASTVisitor` đi duyệt thô qua AST.
- [ ] **Milestone 3**: Name Resolution (Cắm các Define vào SymbolTable và Link Identifier vào SymbolTable).
- [ ] **Milestone 4**: Type Binding (Kiểm tra Phép Toán Toán Học và Return Type).
- [ ] **Milestone 5**: Hardware & COPL Context Verification.
- [ ] **Milestone 6**: Pass 100% test semantic cho các code lỗi (Bắt được lỗi gán sai Type, biến chưa khai báo...).
