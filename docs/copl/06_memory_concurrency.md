# Đặc tả Mô hình Bộ nhớ & Đồng thời (Concurrency) của COPL
## Khắc phục C7: "Không có định nghĩa nào về thứ tự xử lý trên Memory"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Các Chế độ Cấu hình Bộ nhớ (Memory Modes)

COPL định nghĩa rõ 4 mode giới hạn cho vấn đề Cấp phát (Allocation) Bộ nhớ có đi kèm cấu hình hồ sơ profile liên kết:

| Chế độ | Thực hiện Cấp phát | Giải phóng Vùng nhớ (Deallocation) | Các Profile liên quan |
|---|---|---|---|
| `static` | Chỉ lúc Build Compile-time | Không bao giờ | embedded, kernel |
| `owned` | Tường minh, do lập trình viên ấn định pool/arena | Phá hủy Explicit gốc rễ | kernel, backend |
| `managed` | Logic tự quản Runtime (GC, Cơ chế Dem/Refcount) | Giải phóng cực quang (Tự động hóa tuyệt đối) | backend, scripting |
| `region` | Dựa vào Vùng quản lý logic con (Region-based) | Thoát ra / Mất con trỏ (Region Exit) | backend |

### 1.1 Chế độ Static (Cho Embedded / Kernel)

```copl
module mcal.buffer {
  @platform { memory_mode: static }
  
  // Toàn bộ cơ chế xin cấp phát phân tán kích thước cố định là Bắt buộc ngay từ biên dịch
  const BUFFER_SIZE: USize = 256;
  
  struct RxBuffer {
    data: [U8; 256],     // ← kích cỡ cứng array chuẩn đặt lên stack hoặc BSS → OK
    head: USize,
    tail: USize
  }
  
  // COMPILE ERROR CODE (Lỗi rào chặn Compile): Hàm Vec là gọi Xin cấp phát Heap động Runtime → bị CẤM trong chế độ Static mode do thiếu RAM
  // let buffer = Vec::new();  // ❌ ERROR E401
  
  // Trạng thái Static global (Dữ liệu tĩnh để đưa vô block BSS)
  static rx_buf: RxBuffer = RxBuffer { 
    data: [0; 256], head: 0, tail: 0 
  };
}
```

**Qui tắc biên dịch cấm chặn (Compile enforcement)**:
```
(MEMORY-STATIC-CHECK)
    module M có memory_mode = static
    biểu thức e ép xin đòi vùng cấp phát heap nhạy cảm
    ─────────────────────────────────
    COMPILE ERROR E401: "Khởi tạo Heap qua lại cấm tuyệt đối tại bộ nhớ mức Tĩnh (Static memory mode)."
```

### 1.2 Chế độ Owned (Quản lý Vòng đời Tường minh)

```copl
module services.logger {
  @platform { memory_mode: owned }
  
  // Xin Cấp phát bộ nhớ cục bộ từ hồ chứa dạng cấp bậc pool do lập trình lệnh
  fn create_log_entry(pool: Pool, msg: String) -> Owned<LogEntry> {
    let entry = pool.alloc::<LogEntry>();  // lệnh gọi trực diện explicit allocation
    entry.message = msg;
    return entry;
  }
  
  // Xin cấp thu hồi (Giải phóng giải phóng rác bằng lệnh code tay
  fn discard_entry(entry: Owned<LogEntry>) {
    entry.dealloc();  // xin explicit free — ngăn chốt bắt mã rác xài lại use-after-free (bộ biên dịch găm chốt xác minh được)
  }
}
```

### 1.3 Chế độ Managed (Tự động Hóa Cơ Cơ Mức Quản lý Cao Tầng)

```copl
module app.web_handler {
  @platform { memory_mode: managed }
  
  // Tự quản RunTime — Thu gom Dọn bộ nhớ rác GC thả phanh hoặc đếm liên kết tham chiếu (Refcount).
  fn handle_request(req: Request) -> Response {
    let data = Vec::new();       // ← HOÀN TOÀN HỢP LỆ VỚI managed mode
    data.push(parse(req.body));  // XIN Phân bổ Array Cấp phát động
    return Response { body: data.to_json() };
    // Mảng nhớ Data sẽ tự được Tẩy Hủy dọn Rác xóa bộ Nhớ khi ngắt kết nối vòng Scope ra khối Return (kích hoạt Dọn GC âm)
  }
}
```

## 2. Các Chế độ Concurrency (Đồng thời hóa luồng tính toán)

| Chế độ | Cấu trúc Logic Xử lý | Các Profile áp dụng |
|---|---|---|
| `none` | Duy nhất 1 luồng xử lý không tranh đoạt | portable, embedded (bare-metal trực máy) |
| `cooperative` | Phân cấp Task/Đồng nhiệm rẽ nhóm Coroutines, loại bỏ luồng ngắt preemption | embedded (RTOS), backend |
| `preemptive` | Tạo Threads qua HĐH (OS threads), Preemption mức độ mạnh full nhất | kernel, backend, scripting |

### 2.1 Mode None (Không Đồng thời / Luồng đơn) 

```
Mọi hệ thống chạy tuần tự hoàn toàn. Không có hàm Interrupt handlers chuyên rẽ lối báo ngắt / Không chia tác vụ Tasks. 
Hệ điều phối compiler đảm bảo: không bao giờ có Lỗi tranh đoạt ghi Data Race conditions. (Do logic máy vận chuyển bằng sự hiển nhiên).
```

### 2.2 Mode Cooperative (Nhiệm Vụ Hợp Tác Giao Quyền Ở HĐH Nhúng qua RTOS)

```copl
module app.task_manager {
  @platform { concurrency_mode: cooperative }
  
  // Hàm tạo khai báo Task (Phong cách điều phối qua RTOS truyền thống)
  task safety_task {
    priority: highest,
    period: 10ms,
    stack_size: 1KB
  }
  
  task main_task {
    priority: normal,
    period: 50ms,
    stack_size: 2KB
  }
}
```

### 2.3 Mode Preemptive (Chạy Tiến trình Đa luồng Giao quyền Mạnh Ngắt)

```copl
module backend.worker {
  @platform { concurrency_mode: preemptive }
  
  fn process_requests(queue: SharedQueue<Request>) -> Unit
    @effects [async, heap]
  {
    // Kiểm chéo điều phối cho luồng xử lý An toàn hàng chờ Queues an toàn luồng Thread
    while let Some(req) = queue.pop() {
      spawn || {
        handle(req);
      };
    }
  }
}
```

## 3. Quy ước Thứ tự Đọc/Ghi qua Không Gian Bộ Nhớ Dữ liệu Dùng chung 

### 3.1 Quy tắc Truy Cập Bộ Nhớ Chia sẻ State

```
(SHARED-ACCESS-NONE)
    concurrency_mode = none
    ─────────────────────────────
    Không cần thiết chế ngự giới hạn Order (Ordering constraints). Sự nhất quán tuần tự thực thi theo đường truyền mặc yếu và đúng quy chuẩn gốc.

(SHARED-ACCESS-COOPERATIVE)
    concurrency_mode = cooperative
    Giá trị chia sẻ biến variable bị khai thác bởi vài phân vùng tác vụ multi-tasks
    ─────────────────────────────
    BẮT BUỘC (REQUIRES): Sử dụng lệnh khối critical_section { ... } bao bọc lấy quá trình gọi quyền
    Compiler ép: toàn bộ dữ liệu gọi dùng chung cho quá trình access buộc đặt trong chuồng an toàn critical sections.

(SHARED-ACCESS-PREEMPTIVE)
    concurrency_mode = preemptive
    Dữ liệu dùng biên mảng Data chung bị tróc rút ở mức độ cấp tốc qua Multil-thread
    ─────────────────────────────
    BẮT BUỘC XÀI 1 TRONG CÁC KHUNG DƯỚI ĐÂY:
      - Block dùng khóa chặn Mutex { ... } 
      - Chỉ dùng toán nguyên tử Atomic operation
      - Vận chuyển bằng Ký kết Thông tin liên giao Channel-based communication
    Compiler chốt khóa (Enforces): cấm toàn bộ tính trạng truy xuất cập nhật dùng trần (unprotected shared).
```

### 3.2 Tác Động Giao Thức Điện Tín Volatile (Giành phần cứng Hardware Registers)

```copl
// Tệp nhúng Profile được cấy phép đặt mức gọi qua Hardware là Volatile tự mặc định bật lên
lower read_register(addr: U32) -> U32 @target c {
  // Biên dịch thành Output dóng C: *(volatile uint32_t*)addr
  // Quy ước định hướng Memory Ordering (Bộ nhớ): Cán mốc Sequentially consistent tương hộ mọi thiết lập volatile chung hàng Ops
  return volatile_read(addr);
}

lower write_register(addr: U32, value: U32) @target c {
  // Hạ gầm Biên Dịch Code thành Output C language: *(volatile uint32_t*)addr = value
  volatile_write(addr, value);
}
```

### 3.3 Hàng Rào Chắn Memory Barriers 

```copl
// Các Hàm tích hợp sẵn tường minh xây Ranh Giói Barrier tương tác Tần Mạch Vật lý CPU.
intrinsic memory_barrier() @effects [register];
intrinsic data_sync_barrier() @effects [register];
intrinsic instruction_sync_barrier() @effects [register];
```

## 4. Các Vành đai Độ An Toàn (Safety Properties) — Phân Tầng Phạm Vi

> [!IMPORTANT]
> Phần này phân tầng rõ giữa **Guarantee hiện tại** (có formal rule) và **Future Guarantee** (mục tiêu thiết kế chưa có formal proof).

### 4.1 Data Race Freedom (Chỉ Với `none` Mode) — *Guarantee hiện tại*

```
(RACE-FREE-NONE)
    concurrency_mode = none
    ──────────────────────────────────
    Không có data race (trivially: chỉ 1 execution context)
    Compiler không cần enforcement — đúng theo definition.
```

> **Phạm vi**: CHỈ với `concurrency_mode = none`. Với `cooperative` và `preemptive`, data race freedom phụ thuộc vào việc developer dùng đúng `critical_section`/`Mutex`/`Atomic` — compiler hiện tại **cảnh báo** nhưng chưa **chứng minh** hoàn toàn.

### 4.2 Critical Section Semantics — *Guarantee hiện tại với embedded*

```
(E-CRITICAL-SECTION)
    profile ∈ {embedded, kernel}
    ──────────────────────────────────
    ⟨critical_section { body }, σ⟩:
        1. disable_interrupt()          (* effect: {interrupt} *)
        2. ⟨body, σ⟩ → ⟨v, σ'⟩
        3. restore_interrupt()
        → ⟨v, σ'⟩

(EFFECT-CRITICAL-SECTION)
    critical_section block → effect {interrupt} bắt buộc
    Compiler check: critical_section chỉ hợp lệ trong profile=embedded hoặc profile=kernel
    Xuất hiện trong profile={backend, scripting} → COMPILE ERROR E503 (Critical section outside embedded/kernel)
```

### 4.3 Static Memory Safety — *Guarantee hiện tại*

> Xem `05_operational_semantics.md` Section 8.4 cho formal statement.
> - **`memory_mode = static`**: Không có heap allocation → không có use-after-free → guaranteed.
> - **`memory_mode = owned`**: Tracking tại boundary function call — partial guarantee.

### 4.4 Use-After-Free Prevention cho `owned` mode — *Future Guarantee*

> [!WARNING]
> **Future Guarantee**: Claim "compiler prevents use-after-free trong `owned` mode" là **mục tiêu thiết kế**, chưa có formal ownership calculus.
>
> Để đạt được guarantee này cần thêm:
> - Linear typing rule cho `Owned<T>`: khi `x: Owned<T>` được pass vào `f(x)`, `x` bị consume khỏi scope
> - Compiler tracking: sau `dealloc(x)`, mọi use của `x` → COMPILE ERROR E402
>
> **Hiện tại (v1.0)**: Compiler phát E402 dựa trên heuristic, không phải linear type system đầy đủ.

### 4.5 Race-Freedom cho `cooperative` và `preemptive` — *Future Guarantee*

> [!WARNING]
> **Future Guarantee**: Race-freedom cho `cooperative`/`preemptive` mode cần formal access discipline.
>
> **Hiện tại**: Compiler kiểm tra shared variable có được bọc trong `critical_section`/`Mutex` không dựa trên annotation, không phải static analysis đầy đủ.

### 4.6 Buffer Overflow Prevention — *Một phần Guarantee*

> - Constant index: Bounds check tại compile-time → **Guarantee**.
> - Dynamic index: Runtime bounds check (E-INDEX-OUT-OF-BOUNDS rule trong semantics) → **Guarantee** với overhead runtime.
> - `unchecked` mode: Bỏ runtime check → **Không có guarantee** — trách nhiệm hoàn toàn của developer.

