# SỔ TAY HƯỚNG DẪN SỬ DỤNG COPL COMPILER (v0.3.0)

*(COPL - Component-Oriented Programming Language)*

Tài liệu này bao quát cách soạn thảo mã ngôn ngữ COPL, các luật an toàn hệ thống, và cách điều khiển Trình biên dịch (COPL Compiler).

---

## 1. Sử dụng Bộ Công Cụ Dòng Lệnh (The CLI)

Command chính để điều khiển COPL là `coplc.py`.

### 1.1 `check` (Kiểm tra lỗi tĩnh 6-pass)
`python coplc.py check <file.copl>`
- **Tác dụng**: Chạy qua Parser -> Phân loại Type -> Suy luận Effect -> Check Profile an toàn -> Phóng soát Contract.
- **Dùng khi nào**: Đang code, muốn bắt lỗi cực nhanh hoặc linter.

### 1.2 `build` (Biên dịch ra C)
`python coplc.py build <file.copl> -o <thư_mục_đích>`
- **Tác dụng**: Nếu code không có lỗi tĩnh (check pass), tự động đẩy qua C-Transpiler và sinh ra 2 file: 1 Header `(.h)` và 1 Source code `(.c)`.
- Các khối lệnh `lower` sẽ được nhả trực quan thẳng vào source C sinh ra.

### 1.3 `sir` và `artifacts` (Tạo dữ liệu cho AI/Agent)
`python coplc.py sir <file.copl> -o <file.json>`  
`python coplc.py artifacts <file.copl> -o <thư_mục_bundle>`
- **Tác dụng**: Phục vụ kiến trúc Gen-AI. Ép COPL Code ra một bộ CSDL cây Ngữ nghĩa (SIR) giúp Tác tử AI đọc dễ hiểu thay vì đọc raw Code.

---

## 2. Ngôn Ngữ COPL - Cú Pháp Cơ Bản

### 2.1 Module & Import
Mọi file COPL đều bắt đầu chung trong một khối `module`.
```rust
module mcal.uart {
    use bsw.rcc.{enable_clock, clock_status};

    // ...
}
```

### 2.2 Biến (Let) và Kiểu
Mặc định biến trong COPL là Immutable (Không đổi). Phải thêm `mut` để sửa đổi:
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

### 2.4 Control Flow (If / While / Match)
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

COPL cực mạnh cho lập trình Firmware nhờ khả năng xuyên suốt chạm vi mạch (`lower`). Khối `lower` sẽ chặn đứng các hiệu ứng trừu tượng và inject C macro thẳng xuống Hardware:

**1. Khai báo Hardware Struct:**
```rust
lower_struct UART_TypeDef @target c {
    SR: volatile U32 @offset 0x00,
    DR: volatile U32 @offset 0x04,
}
```

**2. Trỏ Map Hardware Pointer:**
```rust
lower_const UART1: *UART_TypeDef @target c = 0x40011000;
```

**3. Khối gọi thực thi ép nhúng Hardware:**
```rust
fn send_byte(data: U8) {
    lower @target c {
        while ((UART1->SR & 0x80) == 0) {}  // Chờ cho TX flag rỗng
        UART1->DR = data;
    }
}
```

---

## 4. Hệ Thống Luật & Ràng Buộc (An Toàn)

Vì là ngôn ngữ nhúng an toàn, COPL quản trị bằng Profile, Effect và Contract.

### 4.1 Khai Báo Cấu Hình File
```rust
module mcal.can {
    @platform {
        profile: embedded,   // Mức chặn gắt: Không Heap, Cấm String, Cấm panic()
    }
    @context {
        safety_class: ASIL-B,
    }
    //...
}
```

### 4.2 Effects (Hiệu ứng phụ)
COPL theo dõi hàm của bạn làm gì. Nếu dùng phần cứng, nó sẽ dính mark `[register]`, nếu đọc ghi sẽ dính `[io]`. Compiler sẽ tự suy luận (Inference), TUY NHIÊN có thể chủ động đánh dấu để compiler check:

```rust
// Trình biên dịch sẽ báo Lỗi (Error) nếu ở trong hàm này mà bạn dám gọi `lower` hay can thiệp thiết bị IO
fn calculate_checksum(data: [U8; 8]) -> U32 
    @effects [pure] 
{
    // ...
}
```

### 4.3 Contract (Hợp đồng bảo mật & Budget)
Khai báo Điều Kiện Tiên Quyết (Pre), Hậu Quyết (Post), và giới hạn chi phí.
```rust
fn process_signal(voltage_mv: U32) -> Result<U32, Error>
    @contract {
        pre: [voltage_mv <= 3300],          // Dữ liệu đầu vào không vượt 3.3V
        latency_budget: "10ms",             // Chống treo lặp
        memory_budget: "256B",
    }
{
    // logic
}
```

---

## 5. Viết Code Kiểm Thử (Testing)
Tích hợp thẳng bộ Test bên trong mà không rác Code lõi qua cơ chế `test_fn` (Tương tự `#[test]` của Rust).

```rust
module tests.uart_tests {
    use mcal.uart.{send_byte};

    test_fn test_send_byte() {
        let result = send_byte(0xFF);
        assert_eq(result, true);
    }
}
```
**Chạy Test Cảnh Báo Coverage:**
Sau này gọi `coplc test --check-coverage`, Trình biên dịch sẽ nhắc nhắc xem những hàm nào bạn từng viết có chứa `@contract` nhưng vô duyên lười nhác chưa có file `test_fn` kiểm chứng!
