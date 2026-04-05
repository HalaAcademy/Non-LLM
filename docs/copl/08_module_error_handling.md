# Hệ thống Module & Cơ chế Bắt Lỗi COPL
## Khắc phục C8+C9: "Không có định nghĩa xử lý lỗi" + "Hệ thống module chỉ là hàng test ví dụ"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Hệ thống Phân bổ Module (Module System)

### 1.1 Cấu trúc Phân cấp (Module Hierarchy)

```
Workspace (root - Mức độ gốc)
└── Package (Gói directory)
    └── Module (Tập tin code hoặc khối lệnh block ngầm)
        └── Định dạng Items (Các khai báo hàm/structs/enums/traits...)
```

COPL tuân thủ **một module là đi liền với quy luật mỗi một phân vùng file** như một cơ chế mặc định default, với khối file/module lồng lặp nếu cần.

### 1.2 Hiển thị Đường dẫn Liên kết Module Paths

```
File lưu: mcal/can_driver.copl → truy xuất code thành: module mcal.can_driver
File lưu: services/vcu/state_machine.copl → module trỏ tới: services.vcu.state_machine
```

Tên của 1 Module = Sẽ lấy path phân cấp thư mục đổi chỗ `/` thành dấu chấm `.` con trỏ và cắt bỏ cụm `.copl`.

### 1.3 Cơ chế Cấp quyền Truy xuất Public/Private (Visibility)

```copl
module mcal.can {
  // Public — Bật cơ chế ngoại vi, cho các hệ Module bên ngoài quyền để móc code
  pub struct CanPdu { ... }
  pub fn init(config: CanConfig) -> CanStatus { ... }
  
  // Private (Riêng tư) — Chỉ những ai đứng trong khối logic block của module hiện tại mới chạm tay được vào nó (Tính default)
  fn find_empty_mailbox() -> Option<U8> { ... }
  struct InternalState { ... }
}
```

Quy tắc truy cập:
```
(VISIBILITY-PUB)
    có nhãn dán cho khối quy luật biến item là khóa 'pub'
    ─────────────────────────────
    Quyền Truy cập mở toang cửa có thể đọc từ bất cứ Module nào import đến nó 

(VISIBILITY-PRIVATE)
    Item gán không cung cấp tag 'pub'
    ─────────────────────────────
    Chỉ cho giao thức xử lý khép mình ở nội vi khối nội hàm Module sở tại

(VISIBILITY-IMPORT)
    Đội Code ở Block Module A import nhầm cái Item khối ngoại có cờ khóa đóng kín (private) từ Block mã B
    ─────────────────────────────
    BẬT KÍCH LỖI BIÊN DỊCH COMPILE ERROR E501: "Quyền bảo mật kích hoạt! Cấm việc móc lốp xài riêng 'x' chôm code từ Module cấp ngoài 'B'"
```

### 1.4 Lệnh cấu hình nhập Use (Import System)

```copl
// Tải vào Single item trọn nguyên kiện 
use mcal.can.CanPdu;

// Kéo thả Đa truy nạp Multiple items
use mcal.can.{CanPdu, CanStatus, init};

// Cài lệnh Alias thay thế cho gọn code
use mcal.stm32f407.can as hw_can;

// Đả càn khôn trọn bộ hằng số Item dạng public (Nhà sản xuất chê, KHÔNG KHUYẾN KHÍCH xài loạn xạ)
use mcal.can.*;
```

### 1.5 Cấm Đoán Mối quan hệ xoắn vặn (Module Dependencies)

```
Logic cho phép (Allowed):  Mở cờ đi từ Layer lớp cao → Gọi ngược dần về Lower
          app → services → bsw → mcal

Nghiêm Cấm Tuyệt (Forbidden): Trò tung hứng Dependencies xoay quẩn (Circular)
           mcal.can → bsw.canif → mcal.can  // ❌ CYCLE VÒNG LẶP CHẾT

Cách Rà Soát (Detection):
  Bảng mạch Compiler đánh giáp lá cà build chéo toàn bộ dependency graph khi lên nền tảng SIR construction.
  Hễ thấy quẩn quanh chu kỳ nhầm dòng → COMPILE ERROR E502: "Phát hiện Mối gọi Xoắn quẩy vòng cung: A → B → A"
```

### 1.6 Xác thực Khước Từ/Kích hoạt Giao Thức Interface thông qua Trait (Trait Enforcement)

```copl
// Khai pháo khởi tạo mẫu giao diện interface logic
pub trait CanDriver {
  fn init(config: CanConfig) -> CanStatus;
  fn write(pdu: CanPdu) -> CanStatus;
  fn read() -> Result<CanPdu, CanStatus>;
}

// Module code xử lý phải hiện thực hóa toàn bộ interface đã rào 
module mcal.stm32f407.can {
  @trace { implements: [CanDriver] }
  
  // Compiler check soi kỹ lại logic: 100% tất thảy Methods đóng chốt tại CanDriver đều phải gõ lệnh cài code (impl)
  // có mang trọn bộ signatures khai mạc trùng lặp
  impl CanDriver for McalCan {
    fn init(config: CanConfig) -> CanStatus { ... }
    fn write(pdu: CanPdu) -> CanStatus { ... }
    fn read() -> Result<CanPdu, CanStatus> { ... }
  }
}
```

## 2. Hệ Thông Quản Trị Bắt Bug / Xử Lý Lỗi (Error Handling)

### 2.1 Triết lý Code Check Lỗi

COPL kế thừa con đường tư duy chuẩn chỉ từ Rust: **Bug/Lỗi được đánh giá như một giá trị thông tin, Tuyệt đối nghiêm cấm kiểu ném ngoại lệ quăng ném exception lung tung**.

| Cơ chế Xử Lý | Cách sử dụng / Use Case | Khai báo Profile |
|---|---|---|
| `Result<T, E>` | Các nhóm Code Bug / Lỗi có giải thuật vãn hồi đập bù qua (Recoverable errors) | Khắp toàn dự phòng Tất Cả profile |
| `Option<T>` (T?) | Khai biến Value Tùy biến tùy chọn chờ bắt Null rỗng | Khắp tất Cả profile |
| `panic` | Các Lỗi đớn đau hủy diệt, phá tan hệ thống không thể hồi cứu (Unrecoverable bugs) | Chỉ cấp phép qua khối kernel, backend, scripting |
| Contract violations | Vi phạm Lập luận logic toán / quy tắc nghiệp vụ điều kiện trước & sau | Mức bảo hộ phụ thuộc thiết lập chế độ lúc biên dịch |

### 2.2 Kiểu Dữ liệu Định Vị kết quả Output Result

```copl
enum Result<T, E> {
  Ok(T),
  Err(E)
}

// Logic dùng mẫu:
fn divide(a: I32, b: I32) -> Result<I32, MathError> {
  if b == 0 {
    return Err(MathError::DivisionByZero);
  }
  return Ok(a / b);
}

// Mảng truy vấn gọi hàm Call:
fn caller() -> Result<I32, MathError> {
  let result = divide(10, 0)?;  // Toán tử dấu chấm ? sẽ Auto Propagation trích ra rào chắn cho lỗi Err mà pass đi nếu an toàn
  return Ok(result * 2);
}
```

### 2.3 Phép Tính Đẩy Tràn Lỗi Propagation (Toán Tử Dấu Hỏi ?)

```
(TRY-PROPAGATE)
    Ký tự biểu thức 'e' chứa kết cấu hệ định chuẩn type Result<T, E>
    Đoạn Hàm đùm kín báo kết toán return trả lại Result<_, E> (E phải giống chung rễ với E cục bộ)
    
    e? 
      = if hệ tính e mang biến Ok(v) → Ném xuất giá trị v chạy trơn chu
      = if hệ thống bắt ngắt cờ e là thẻ báo lỗi Err(err) → Hủy chạy và out luồng ép gọi hàm mẹ ném thẳng return Err(err) (Lệnh bắt rút quân đóng cửa sớm)
```

### 2.4 Quản trị Mảng Phân Loại Error Types

```copl
// Tự phát lệnh Khai biến mã Loại lỗi cấu trúc chuyên biệt (domain-specific error types)
enum CanError {
  Timeout,
  BusOff,
  MailboxFull,
  InvalidDlc(U8),
  HardwareError { code: U16, register: U32 }
}

// Từng mảnh Functions tuyên bố danh hiệu lỗi cụ thể mà nó có thể cấn tạo
fn can_write(pdu: CanPdu) -> Result<Unit, CanError> {
  if !is_initialized() { return Err(CanError::BusOff); }
  if pdu.dlc > 8 { return Err(CanError::InvalidDlc(pdu.dlc)); }
  // ...
}
```

### 2.5 Logic Hạn Chế Error Tại Embedded (Lệnh Tước bỏ Panic)

```copl
module mcal.can {
  @platform { profile: embedded }
  
  // Tại môi trường khắt khe hệ nhúng embedded: CẤM TẠO LỖI VĂNG panic, CẤM móc ruột unwrap, CẤM hàm logic expect.
  // Nhất quán dùng cách thức Tường minh explicit bằng thẻ cờ quy kết mã Result handling.
  
  fn safe_read() -> Result<CanPdu, CanError> {
    let mailbox = find_empty_mailbox();
    match mailbox {
      Some(mb) => { ... return Ok(pdu); },
      None => { return Err(CanError::MailboxFull); }
    }
    // Những hàm chọc lỗi trực diện sau KHÔNG BAO GIỜ CHO PHÉP áp dụng biên dịch trót lọt tại môi trường chuẩn profile embedded:
    // let mb = mailbox.unwrap();  // ❌ LỖI VĂNG KIỂU BẤT NGỜ panic! bị quy là sai phạm
  }
}
```

Màn hình Compiler sẽ bật rào rát (enforcement):
```
(NO-PANIC-EMBEDDED)
    Mảng Module code quy chứa nhãn hồ sơ profile = embedded
    Logic rà trúng từ code bị nhiễm cụm hàm cấm địa: unwrap(), expect(), panic!(), assert!()
    ─────────────────────────────
    LẬP TỨC PHÁT KÊU COMPILE ERROR E601: "Các câu lệnh gây đứt luồng nhúng dở dang 'panic-inducing' như thế bị hệ thống thẳng thừng loại bỏ quyền sinh thiết đối với profile 'embedded'"
```

### 2.6 Khối Logic Nắn Luồng Đổi Kiểu Lỗi Mượt Mà (Error Conversion)

```copl
// Áp khuôn giao thức triết lý Trait mẫu From để biến thế quy kết thông số mã tự động thông qua toán tử vát dấu tự hành ?
impl From<CanError> for SystemError {
  fn from(e: CanError) -> SystemError {
    match e {
      CanError::Timeout => SystemError::CommTimeout("CAN"),
      CanError::BusOff => SystemError::HardwareFault("CAN bus off"),
      _ => SystemError::Unknown
    }
  }
}

// Giải pháp đền bù trọn vẹn để múa toán tử dấu hỏi vọt qua các bảng error types sai khác:
fn system_init() -> Result<Unit, SystemError> {
  can_init(config)?;  // Logic CanError rà tự động trượt hóa giải nâng lên mác lỗi bự SystemError bằng đường cầu From
  gpio_init()?;
  return Ok(Unit);
}
```

### 2.7 Kiểu bắt Null (Lỗ hổng trống của giá trị) thông qua Option Type

```copl
// T? Là ngôn từ Sugar/cú pháp đường viền gọi vắn tắt thay cho cụm mẫu Option<T>

fn find_module(name: String) -> ModuleInfo? {
  for m in modules {
    if m.name == name { return Some(m); }
  }
  return None;
}

fn caller() {
  let info = find_module("mcal.can");
  match info {
    Some(m) => { use_module(m); },
    None => { log("module not found"); }
  }
  
  // Hay dùng mẹo Ràng Buộc Cú pháp mẫu if-let pattern gộp nhánh:
  if let Some(m) = find_module("mcal.can") {
    use_module(m);
  }
}
```

## 3. Hệ Thông Bảng Diagnostic Codes Báo Trục trặc Của Compiler

Chấn chỉnh Mã/Mã Nhúng Lỗi với định danh chuẩn ổn định để robot AI thông minh GEAS agent dễ tiêu hóa bắt code rà quy mã chuẩn:

```
Giới báo lỗi theo Cú pháp Syntax:       E001-E099
Xác định Trục Trặc lệch Kiểu gán Type:         E100-E199
Sự Cố văng đạn Vi phạm Effect:   E300-E399
Lỗi truy vấn sai Memory:   E400-E499
Nhóm Module bóc phốt chéo sai sót:       E500-E599
Bảng mốc sai lệch báo hỏng Error handling:      E600-E699
Kiểu check Hợp đồng Contract chối nhận:     E700-E799
Sai do vướng lệnh tầng thập Lowering:     E800-E899
Từ khối Context entity:      E900-E999

Các Bảng Cảnh báo Warning (đỏ cờ check nhẹ không gãy luồng):            W001-W999
```

### Những Ký Bộ Code Quan Trọng Bắt Bug Cốt Lõi

| Code Dấu Nhận | Định Danh Category | Dòng chữ Mẫu System Template Xuất Phát |
|---|---|---|
| E001 | syntax | Unexpected token (Nhận diện mã bất ngờ) '{tok}', đáng lẽ chỗ đó phải là '{expected}' |
| E002 | syntax | Unterminated string literal (Chuỗi định biên chưa được chốt dấu kết thúc) |
| E101 | type | Type mismatch: expected (Hai vế râu ông nọ cắm cằm bà kia) '{expected}', nhưng nhận lại hàng '{found}' |
| E102 | type | Cannot apply operator (Không thể chốt giao thương toán tử logic) '{op}' lên đầu cái loại type ngớ ngẩn như '{lhs}' và vế tréo '{rhs}' |
| E103 | type | Unknown type (Tuyệt giao mã gốc) '{name}' |
| E104 | type | Missing return type annotation (Lạc quẻ thẻ định tuyến giá trị gốc) |
| E301 | effect | Effect '{effect}' bị cấm kị đối với khuỷu config mang thẻ định vị profile '{profile}' |
| E302 | effect | Function trỏ họng gắn mác cực tinh khiết @effects [pure] thế nhưng lại vô tư chêm rác tác vụ đâm xén ngoại effect '{effect}' |
| E401 | memory | Heap allocation không có quy quyền ở lại hệ static memory mode |
| E402 | memory | Gây bug gọi trích trỏ Use sau khi đã phang lệnh tẩy thẻ giải phóng deallocation dành cho Owned<{type}> |
| E501 | module | Ngăn thủng luồng! Cấm truy quyền cờ chặn item khóa cứng '{item}' khi nhìn lén bằng mã code từ chuồng khảm module '{module}' |
| E502 | module | Đứt gãy luồng quẩn xoắn não vòng lặp (Circular dependency detected): {cycle} |
| E503 | module | Tịt ngòi Mảng code tìm Module không ra tung tích '{name}' |
| E601 | error | Cấm văng code kích cầu nhảy màn panic-inducing vào cõi khép kín nhúng lập biên chuẩn embedded profile |
| E701 | contract | Khước từ Tiền tố Precondition (Mệnh điều Tiên quyết): {condition} |
| E901 | context | Nhập lệnh thẻ Requirement bị treo mốc reference '{id}' vào hố đen chưa được cắt đặt defined |

Mỗi dòng thông điệp báo Bug qua chẩn đoán diagnostic Diagnostic bao hàm gồm: code, mảng category, tính chất trầm trọng severity, vị trí File file, đánh cọc dòng số thứ line, định vị chi chít chữ cái cột column, chuỗi text càm ràm mắng mỏ message, và một lời khuyên gỡ rối suggested_fix do AI dọn giúp.

---

## 7. Quy tắc Gọi Qua Ranh Giới Profile (Cross-Profile Call Rules) — **[MỚI]**

### 7.1 Ma Trận Cho Phép Gọi Qua Profile

| Caller Profile | Callee Profile | Điều kiện | Kết quả |
|---|---|---|---|
| `embedded` | `portable` | effects của callee ⊆ {pure, register} | ✅ Hợp lệ |
| `embedded` | `embedded` | same profile | ✅ Hợp lệ |
| `embedded` | `kernel` | — | ❌ E510 |
| `embedded` | `backend` | — | ❌ E510 |
| `kernel` | `embedded` | effects ⊆ {pure, register, interrupt} | ✅ Hợp lệ (supervisor call) |
| `backend` | `portable` | effects ⊆ {pure, heap, io} | ✅ Hợp lệ |
| `backend` | `embedded` | — | ❌ E510 |

### 7.2 Formal Rule (Cross-Profile Call Typing)

```
(CROSS-PROFILE-CALL-ALLOWED)
    module A: profile=P_A
    module B: profile=P_B
    B.f : fn(params) -> τ  [effects: E_B]
    E_B ⊆ allowed_effects(P_A)      (* B's effects không vượt quá những gì A được phép *)
    ────────────────────────
    A được phép gọi B.f
    Resulting call effect = E_B ∪ current_effects(A)

(CROSS-PROFILE-CALL-FORBIDDEN)
    module A: profile=P_A
    module B: profile=P_B
    E_B ⊄ allowed_effects(P_A)      (* B có effects mà A không được phép *)
    ────────────────────────
    COMPILE ERROR E510: Cross-profile call effect violation:
    "Profile '{P_A}' không được phép gọi hàm có effect '{E_B - allowed_effects(P_A)}'"
```

### 7.3 Bảng `allowed_effects(profile)`

```
embedded:  {pure, register, interrupt}
kernel:    {pure, register, interrupt, heap}     (kernel có quyền alloc cho kernel objects)
portable:  {pure}                                (portable = không có side effect gì cả)
backend:   {pure, heap, io, network, fs, async}
scripting: {pure, heap, io, network, fs, async, panic}
```

---

## 8. Ngữ nghĩa Wildcard Import (Wildcard Import Semantics) — **[MỚI]**

```
(USE-WILDCARD)
    module M có public symbols S = {s₁: τ₁, s₂: τ₂, ..., sₙ: τₙ}
    'use M.*' được khai báo trong module A
    ────────────────────────
    Tất cả sᵢ ∈ S được thêm vào scope của A như thể khai báo 'use M.sᵢ'

(USE-WILDCARD-CONFLICT)
    'use M.*' đưa sᵢ vào scope
    scope của A đã có symbol sᵢ (từ local def hoặc use khác)
    ────────────────────────
    COMPILE ERROR E301: "Ambiguous import: '{sᵢ}' tồn tại trong cả local scope và 'M.*'"
    Cách giải quyết: dùng 'use M.{sᵢ} as M_sᵢ' để explicit rename

(USE-WILDCARD-DISCOURAGED)
    'use M.*' detected
    ────────────────────────
    WARNING W101: "Wildcard import 'use M.*' có thể gây shadowing không rõ ràng.
    Khuyến nghị: dùng explicit import 'use M.{item1, item2}' để rõ ràng hơn."
    (* Warning không block build — chỉ cảnh báo style *)
```

> **Lý do có WARNING**: Wildcard import được hỗ trợ vì đôi khi cần thiết (ví dụ import toàn bộ HAL functions), nhưng khuyến nghị dùng explicit import để tăng readability và tránh accidental shadowing.

---

### Cập nhật Bảng Error Codes

| Code | Category | Mô tả |
|---|---|---|
| E301 | import | Ambiguous import — wildcard conflict |
| E501 | module | Access violation — private item |
| E501 | pointer | Pointer type outside lower context |
| E502 | module | Circular dependency detected |
| E503 | module | Module not found |
| E503 | effect | critical_section outside embedded/kernel profile |
| E510 | profile | Cross-profile call effect violation |

