# SỔ TAY HƯỚNG DẪN SỬ DỤNG COPL COMPILER (v0.3.0)

*(COPL - Component-Oriented Programming Language)*

Tài liệu này hướng dẫn cách soạn thảo mã nguồn ngôn ngữ COPL, các quy tắc an toàn hệ thống, và cách sử dụng Giao diện dòng lệnh của Trình biên dịch (COPL Compiler CLI).

---

## 1. Sử dụng Bộ Công Cụ Dòng Lệnh (CLI)

Lệnh chính để điều khiển COPL là `copc` (hoặc script `coplc.py`).

### 1.1 `check` (Kiểm tra lỗi phân tích tĩnh 6-vòng)
```bash
copc check <file.copl>
```
- **Tác dụng**: Chạy qua các bước: Parser -> Phân loại dữ liệu (Type Inference) -> Suy luận hiệu ứng (Effect Inference) -> Kiểm tra tính an toàn theo cấu hình (Profile checking) -> Phân tích hợp đồng (Contract checking).
- **Trường hợp sử dụng**: Dùng khi đang viết code, hỗ trợ phát hiện lỗi nhanh tương tự như công cụ linter.

### 1.2 `build` (Biên dịch trực tiếp sang C/Rust/Go)
```bash
copc build <file.copl> -o <thư_mục_đích>
```
- **Tác dụng**: Nếu mã nguồn vượt qua trình kiểm tra tĩnh (check pass), hệ thống sẽ chuyển giao cho bộ phận Dịch chuyển mã (Transpiler) để sinh ra mã đích (ví dụ nền tảng C sẽ sinh ra 1 File Header `.h` và 1 File Source `.c`).
- Các khối lệnh hạ cấp phần cứng (`lower`) sẽ được dịch trực tiếp thành các cấu trúc tương ứng trong mã đích.

### 1.3 `artifacts` (Xuất dữ liệu hệ thống cho AI/Agent)
```bash
copc sir <file.copl> -o <file.json>
copc artifacts <file.copl> -o <thư_mục_bundle>
```
- **Tác dụng**: Phục vụ cho kiến trúc AI tạo sinh. Trình biên dịch ngoại suy cấu trúc COPL thành một cơ sở dữ liệu dạng Cây Ngữ nghĩa (SIR - Semantic IR), giúp các Tác tử AI (AI Agents) dễ dàng đọc hiểu bối cảnh dự án thay vì phải phân tích mã nguồn thô.

---

## 2. Ngôn Ngữ COPL - Cú Pháp Cơ Bản

### 2.1 Module & Cú pháp Import
Mọi file COPL đều phải nằm trong một khối định nghĩa `module`.
```rust
module mcal.uart {
    use bsw.rcc.{enable_clock, clock_status};

    // ...
}
```

### 2.2 Biến biến thiên (Let) và Kiểu dữ liệu
Mặc định các biến trong COPL là bất biến (Immutable). Để thay đổi giá trị, cần phải khai báo với từ khoá `mut` (mutable):
```rust
let is_active: Bool = true;
let mut counter: U32 = 0;
counter = counter + 1;
```

### 2.3 Struct & Enum
```rust
pub struct Point {
    x: U32,
    y: U32
}

pub enum Direction {
    Up, Down, Left, Right
}
```

### 2.4 Luồng điều khiển (Control Flow)
```rust
if counter > 10 {
    return true;
} else if counter == 0 {
    break;
}

while is_active {
    counter = counter + 1;
}

match dir {
    Direction::Up => counter = counter + 1,
    Direction::Down => counter = counter - 1,
    _ => return false,
}
```

---

## 3. Lập Trình Hệ Thống Cấp Thấp (Hardware Lowering)

COPL là ngôn ngữ mạnh mẽ cho phát triển Firmware nhờ khả năng can thiệp trực tiếp vào phần cứng (`lower`). Khối `lower` sẽ vô hiệu hoá các tính năng trừu tượng bậc cao để chèn trực tiếp các mã nền tảng (ví dụ C struct/macro) vào phần cứng.

**1. Khai báo Cấu trúc phần cứng (Hardware Struct):**
```rust
lower_struct UART_TypeDef @target c {
    SR: volatile U32 @offset 0x00,
    DR: volatile U32 @offset 0x04,
}
```

**2. Trỏ Địa chỉ con trỏ phần cứng (Hardware Pointer):**
```rust
lower_const UART1: *UART_TypeDef @target c = 0x40011000;
```

**3. Khối lệnh thực thi tương tác phần cứng (Hardware action):**
```rust
fn send_byte(data: U8) {
    lower @target c {
        while ((UART1->SR & 0x80) == 0) {}  // Chờ luồng truyền (TX flag) sẵn sàng
        UART1->DR = data;
    }
}
```

---

## 4. Hệ Thống Luật & Ràng Buộc (An Toàn Hệ Thống)

Là một ngôn ngữ thiết kế cho các hệ thống nhúng đòi hỏi an toàn cao, COPL quản lý trạng thái thông qua Profile, Effect và Contract.

### 4.1 Khai Báo Cấu Hình File (Profile Setup)
```rust
module mcal.can {
    @platform {
        profile: embedded,   // Mức hạn chế nghiêm ngặt: Ngăn cấp phát Heap, Cấm kiểu String động, Cấm gọi hàm panic().
    }
    @context {
        safety_class: ASIL_B,
    }
    //...
}
```

### 4.2 Hiệu ứng phụ (Effects)
COPL theo dõi hành vi của các hàm. Nếu hàm thao tác với thanh ghi phần cứng, hệ thống đánh dấu hàm đó mang hiệu ứng `[register]`; nếu thực hiện đọc/ghi dữ liệu, mang hiệu ứng `[io]`. Trình biên dịch có khả năng tự động nội suy (Inference), TUY NHIÊN người lập trình cũng có thể chỉ định rõ ràng bảo vệ tính hợp lệ:

```rust
// Trình biên dịch sẽ báo lỗi nếu trong hàm này chứa khối lệnh `lower` hoặc các can thiệp I/O hệ thống.
fn calculate_checksum(data: [U8; 8]) -> U32 
    @effects [pure] 
{
    // ...
}
```

### 4.3 Hợp đồng phần mềm (Contracts)
Cho phép khai báo Điều Kiện Tiên Quyết (Pre-conditions), Điều Kiện Hậu Quyết (Post-conditions), và giới hạn chi phí phần cứng.
```rust
fn process_signal(voltage_mv: U32) -> Result<U32, Error>
    @contract {
        pre: [voltage_mv <= 3300],          // Yêu cầu bắt buộc: Dữ liệu đầu vào điệp áp không vượt 3.3V
        latency_budget: "10ms",             // Định mức thời gian tối đa để tránh lỗi lặp vô hạn
        memory_budget: "256B",
    }
{
    // logic xử lý
}
```

---

## 5. Viết Mã Kiểm Thử (Testing)
Tích hợp trực tiếp các đoạn mã kiểm thử vào trong tệp tin gốc thông qua cơ chế `test_fn` (Tương đương macro `#[test]` của Rust), trình biên dịch tự động tách không đưa vào mã thực thi cuối cùng.

```rust
module tests.uart_tests {
    use mcal.uart.{send_byte};

    test_fn test_send_byte() {
        let result = send_byte(0xFF);
        assert_eq(result, true);
    }
}
```
**Chẩn đoán Mức độ Tầm phủ Mã kiểm thử (Test Coverage):**
Khi thực hiện lệnh `copc test --check-coverage`, Trình biên dịch sẽ cung cấp báo cáo nếu phát hiện các hàm có sử dụng ràng buộc `@contract` nhưng thiếu các bài kiểm tra `test_fn` tương ứng.
