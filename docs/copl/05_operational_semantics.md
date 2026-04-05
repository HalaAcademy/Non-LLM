# Ngữ nghĩa Động COPL (Operational Semantics)
## Mô hình Thực thi Hình thức — Khắc phục C6: "Không có operational semantics"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Tổng quan

COPL sử dụng loại **ngữ nghĩa động bước nhỏ (small-step operational semantics)** — nhằm định nghĩa cụ thể mọi quy trình cắt giảm biểu thức diễn ra ở bước nhỏ nhất ra sao. Với mô hình xử lý hình thức này:
- Chứng minh tính chuẩn xác về kiểu an toàn (type soundness) (giúp cho các tiến trình kiểm soát đánh giá kiểu không bị khựng cứng)
- Định nghĩa các phương pháp thực thi đảm bảo Hợp đồng - contract (điều kiện kiện quyết pre/post conditions)
- Định nghĩa kiểm soát hiệu ứng (effect tracking) khi đang kích hoạt ở trạng thái Runtime
- Định nghĩa xác định vi phạm quy tắc Profile ngay ở lúc compile-time (biên dịch) thay vì đợi đến khi chạy Runtime lỗi mới lộ

## 2. Ký hiệu (Notation)

```
⟨e, σ⟩ → ⟨e', σ'⟩     Biểu thức e lưu ở store σ phát sinh ra 1 bước xử lý về hàm e' trong store σ'
v                       Value (giá trị — đã ở dạng tinh giản không thể thu nhỏ hơn)
σ                       Store: Bản đồ ánh xạ từ biến → giá trị
Γ                       Context định hình kiểu (Type context)
E                       Tập hợp effects được thu thập trong suốt quá trình evaluation

(* Tín hiệu luồng điều khiển — Control Flow Signals *)
Return(v)               Tín hiệu thoát hàm sớm mang giá trị v
Break                   Tín hiệu thoát vòng lặp
Continue                Tín hiệu nhảy lên đầu vòng lặp tiếp theo
```

## 3. Các giá trị khả dụng (Values)

```
v ::= n                            (* Hằng số kiểu số nguyên âm/dương *)
    | f                            (* Hằng số kiểu số thực dấu phẩy động *)
    | true | false                 (* Giá trị bool - boolean *)
    | c                            (* Số hạng Ký tự - char *)
    | s                            (* Dòng string *)
    | Unit                         (* Cột unit không giá trị (Void) *)
    | [v₁, ..., vₙ]              (* Biến kiểu mảng Array *)
    | (v₁, ..., vₙ)              (* Định dạng nhóm dữ liệu tuple *)
    | S { f₁: v₁, ..., fₙ: vₙ } (* Đối tượng thuộc dạng Struct *)
    | E::V(v₁, ..., vₙ)          (* Cột giá trị thay đổi variant cho định dạng Enum *)
    | Some(v)                      (* optional khi có value *)
    | None                         (* optional khi trống rỗng *)
    | Ok(v)                        (* Trả về value của kết quả hợp lệ *)
    | Err(v)                       (* Trả về value biểu tình có lỗi của Hàm *)
    | closure(env, params, body)   (* Cột giá trị Closure (bao trùm khối cục bộ) *)
```

## 4. Các quy tắc Đánh giá Cốt lõi (Core Evaluation Rules)

### 4.1 Biến và Let (Bindings)

```
(E-VAR)
    x ↦ v ∈ σ
    ────────────────────────
    ⟨x, σ⟩ → ⟨v, σ⟩

(E-LET)
    ⟨e, σ⟩ → ⟨v, σ'⟩
    ────────────────────────
    ⟨let x: τ = e; rest, σ⟩ → ⟨rest[x ↦ v], σ'[x ↦ v]⟩

(E-ASSIGN)
    ⟨e, σ⟩ → ⟨v, σ'⟩
    x đã được định danh biến mut (cho phép ghi đè/thay đổi)
    ────────────────────────
    ⟨x = e, σ⟩ → ⟨Unit, σ'[x ↦ v]⟩
```

### 4.2 Tính toán Số học (Arithmetic) & Sự So sánh (Comparison)

```
(E-ARITH)
    ⟨e₁, σ⟩ → ⟨n₁, σ'⟩
    ⟨e₂, σ'⟩ → ⟨n₂, σ''⟩
    n₃ = n₁ op n₂    (toán tử op ∈ {+, -, *, /, %})
    không có hiện tượng tràn bộ nhớ số (no overflow)
    ────────────────────────
    ⟨e₁ op e₂, σ⟩ → ⟨n₃, σ''⟩

(E-ARITH-OVERFLOW)
    ⟨e₁, σ⟩ → ⟨n₁, σ'⟩
    ⟨e₂, σ'⟩ → ⟨n₂, σ''⟩
    n₁ op n₂ tạo ra tràn giới hạn hệ lưu trữ đối với biến τ
    ────────────────────────
    ⟨e₁ op e₂, σ⟩ → ⟨RuntimeError("overflow"), σ''⟩

(E-COMPARE)
    ⟨e₁, σ⟩ → ⟨v₁, σ'⟩
    ⟨e₂, σ'⟩ → ⟨v₂, σ''⟩
    b = v₁ cmp v₂    (toán tử so sánh cmp ∈ {==, !=, <, >, <=, >=})
    ────────────────────────
    ⟨e₁ cmp e₂, σ⟩ → ⟨b, σ''⟩

(E-LOGICAL-AND)
    ⟨e₁, σ⟩ → ⟨false, σ'⟩
    ────────────────────────
    ⟨e₁ && e₂, σ⟩ → ⟨false, σ'⟩        (* Xử lý đoản mạch / Cắt ngắn luồng đánh giá - short-circuit *)

    ⟨e₁, σ⟩ → ⟨true, σ'⟩
    ⟨e₂, σ'⟩ → ⟨b, σ''⟩
    ────────────────────────
    ⟨e₁ && e₂, σ⟩ → ⟨b, σ''⟩

(E-LOGICAL-OR)         (* Luận lý giống AND, kích hoạt đoản mạch trên điều kiện true đầu tiên *)
```

### 4.3 Gọi Hàm (Function Call)

```
(E-CALL)
    ⟨f, σ⟩ → ⟨closure(env, [x₁,...,xₙ], body), σ₁⟩
    ⟨eᵢ, σᵢ⟩ → ⟨vᵢ, σᵢ₊₁⟩  (đánh giá áp dụng cho từng đối tượng i ∈ 1..n)
    σ_body = env ∪ {x₁ ↦ v₁, ..., xₙ ↦ vₙ}
    ⟨body, σ_body⟩ → ⟨v_result, σ_final⟩
    ────────────────────────
    ⟨f(e₁, ..., eₙ), σ⟩ → ⟨v_result, σ_final⟩

(E-CALL-WITH-CONTRACT)
    (* Các bước duyệt Điều kiện Pre-contract *)
    ⟨eᵢ, σᵢ⟩ → ⟨vᵢ, σᵢ₊₁⟩  (cho từng biến tham số i)
    σ_args = {x₁ ↦ v₁, ..., xₙ ↦ vₙ}
    ⟨pre_condition, σ_args⟩ → ⟨true, σ'⟩
    
    (* Các bước duyệt Thân Hàm *)
    ⟨body, σ_args⟩ → ⟨v_result, σ''⟩
    
    (* Các bước duyệt Mệnh lệnh Post-contract (Logic Hợp đồng Đích trả về) *)
    σ_post = σ'' ∪ {result ↦ v_result}
    ⟨post_condition, σ_post⟩ → ⟨true, σ'''⟩
    ────────────────────────
    ⟨f(e₁,...,eₙ), σ⟩ → ⟨v_result, σ'''⟩

(E-CONTRACT-VIOLATION-PRE)
    ⟨pre_condition, σ_args⟩ → ⟨false, σ'⟩
    ────────────────────────
    ⟨f(e₁,...,eₙ), σ⟩ → ⟨ContractViolation("precondition failed"), σ'⟩

(E-CONTRACT-VIOLATION-POST)
    ⟨post_condition, σ_post⟩ → ⟨false, σ'⟩
    ────────────────────────
    ⟨f(e₁,...,eₙ), σ⟩ → ⟨ContractViolation("postcondition failed"), σ'⟩
```

### 4.4 Luồng Điều khiển (Control Flow)

```
(E-IF-TRUE)
    ⟨cond, σ⟩ → ⟨true, σ'⟩
    ⟨then_block, σ'⟩ → ⟨v, σ''⟩
    ────────────────────────
    ⟨if cond { then_block } else { else_block }, σ⟩ → ⟨v, σ''⟩

(E-IF-FALSE)
    ⟨cond, σ⟩ → ⟨false, σ'⟩
    ⟨else_block, σ'⟩ → ⟨v, σ''⟩
    ────────────────────────
    ⟨if cond { then_block } else { else_block }, σ⟩ → ⟨v, σ''⟩

(E-WHILE-TRUE)
    ⟨cond, σ⟩ → ⟨true, σ'⟩
    ⟨body, σ'⟩ → ⟨_, σ''⟩
    ⟨while cond { body }, σ''⟩ → ⟨v, σ'''⟩
    ────────────────────────
    ⟨while cond { body }, σ⟩ → ⟨v, σ'''⟩

(E-WHILE-FALSE)
    ⟨cond, σ⟩ → ⟨false, σ'⟩
    ────────────────────────
    ⟨while cond { body }, σ⟩ → ⟨Unit, σ'⟩

(E-FOR)
    ⟨iter, σ⟩ → ⟨[v₁,...,vₙ], σ'⟩
    đi từng i: ⟨body[x ↦ vᵢ], σᵢ⟩ → ⟨_, σᵢ₊₁⟩
    ────────────────────────
    ⟨for x in iter { body }, σ⟩ → ⟨Unit, σₙ₊₁⟩

(E-MATCH)
    ⟨scrutinee, σ⟩ → ⟨v, σ'⟩
    tìm vòng lặp pattern pᵢ nếu nó khớp với v
    bindings = match_bindings(pᵢ, v)
    ⟨eᵢ, σ' ∪ bindings⟩ → ⟨v_result, σ''⟩
    ────────────────────────
    ⟨match scrutinee { p₁=>e₁, ..., pₙ=>eₙ }, σ⟩ → ⟨v_result, σ''⟩

(E-MATCH-NO-ARM)    (* Không có pattern nào khớp → runtime error *)
    ⟨scrutinee, σ⟩ → ⟨v, σ'⟩
    không có pᵢ nào khớp với v
    ────────────────────────
    ⟨match scrutinee { ... }, σ⟩ → ⟨RuntimeError("non-exhaustive match"), σ'⟩
```

### 4.5 Cú pháp liên kết cho Struct và Enum

```
(E-STRUCT-CONSTRUCT)
    ⟨eᵢ, σᵢ⟩ → ⟨vᵢ, σᵢ₊₁⟩  áp dụng đối với mọi thành tố trường i
    ────────────────────────
    ⟨S { f₁:e₁, ..., fₙ:eₙ }, σ⟩ → ⟨S { f₁:v₁, ..., fₙ:vₙ }, σₙ₊₁⟩

(E-FIELD-ACCESS)
    ⟨e, σ⟩ → ⟨S { ..., f:v, ... }, σ'⟩
    ────────────────────────
    ⟨e.f, σ⟩ → ⟨v, σ'⟩

(E-ENUM-CONSTRUCT)
    ⟨eᵢ, σᵢ⟩ → ⟨vᵢ, σᵢ₊₁⟩
    ────────────────────────
    ⟨E::V(e₁,...,eₙ), σ⟩ → ⟨E::V(v₁,...,vₙ), σₙ₊₁⟩
```

### 4.6 Logic liên kết của Optional (Tùy chọn biến trống) và Result (Mệnh lệnh điều khiển trả về)

```
(E-TRY-OK)
    ⟨e, σ⟩ → ⟨Ok(v), σ'⟩
    ────────────────────────
    ⟨e?, σ⟩ → ⟨v, σ'⟩

(E-TRY-ERR)
    ⟨e, σ⟩ → ⟨Err(v_err), σ'⟩
    ────────────────────────
    ⟨e?, σ⟩ → ⟨Return(Err(v_err)), σ'⟩   (* Hồi biến / Ngắt hàm thoát sớm *)

(E-SOME)
    ⟨e, σ⟩ → ⟨v, σ'⟩
    ────────────────────────
    ⟨Some(e), σ⟩ → ⟨Some(v), σ'⟩
```

### 4.7 Array Operations (Vận Hành Mảng Array)

```
(E-INDEX)
    ⟨arr, σ⟩ → ⟨[v₀,...,vₙ₋₁], σ'⟩
    ⟨idx, σ'⟩ → ⟨i, σ''⟩
    0 ≤ i < n
    ────────────────────────
    ⟨arr[idx], σ⟩ → ⟨vᵢ, σ''⟩

(E-INDEX-OUT-OF-BOUNDS)
    ⟨arr, σ⟩ → ⟨[v₀,...,vₙ₋₁], σ'⟩
    ⟨idx, σ'⟩ → ⟨i, σ''⟩
    i < 0 hoặc i ≥ n
    ────────────────────────
    ⟨arr[idx], σ⟩ → ⟨RuntimeError("index out of bounds"), σ''⟩
```

### 4.8 Luồng Điều khiển Sớm (Early Control Flow) — **[MỚI]**

*Đây là phần bổ sung so với phiên bản trước — các rules này sử dụng tín hiệu `Return(v)`, `Break`, `Continue` được định nghĩa trong Section 2.*

```
(* ─── RETURN ─── *)

(E-RETURN)              (* return e; → đánh giá e rồi phát tín hiệu Return *)
    ⟨e, σ⟩ → ⟨v, σ'⟩
    ────────────────────────
    ⟨return e; rest, σ⟩ → ⟨Return(v), σ'⟩

(E-RETURN-VOID)         (* return; → Return Unit *)
    ────────────────────────
    ⟨return; rest, σ⟩ → ⟨Return(Unit), σ⟩

(E-RETURN-PROPAGATE)    (* Return(v) lan truyền qua các câu lệnh tiếp theo *)
    ⟨stmt, σ⟩ → ⟨Return(v), σ'⟩
    ────────────────────────
    ⟨stmt; rest, σ⟩ → ⟨Return(v), σ'⟩

(E-CALL-RETURN)         (* Hàm gọi: bắt Return(v) từ body và trả về v *)
    ⟨body, σ_body⟩ → ⟨Return(v), σ'⟩
    ────────────────────────
    ⟨f(e₁,...,eₙ), σ⟩ → ⟨v, σ'⟩

(* ─── BREAK ─── *)

(E-BREAK)               (* break; → phát tín hiệu Break *)
    ────────────────────────
    ⟨break; rest, σ⟩ → ⟨Break, σ⟩

(E-WHILE-BREAK)         (* while loop bắt tín hiệu Break từ body → kết thúc loop *)
    ⟨cond, σ⟩ → ⟨true, σ'⟩
    ⟨body, σ'⟩ → ⟨Break, σ''⟩
    ────────────────────────
    ⟨while cond { body }, σ⟩ → ⟨Unit, σ''⟩

(E-FOR-BREAK)           (* for loop bắt tín hiệu Break *)
    ⟨body[x ↦ vᵢ], σᵢ⟩ → ⟨Break, σᵢ₊₁⟩
    ────────────────────────
    ⟨for x in iter { body }, σ⟩ → ⟨Unit, σᵢ₊₁⟩

(* ─── CONTINUE ─── *)

(E-CONTINUE)            (* continue; → phát tín hiệu Continue *)
    ────────────────────────
    ⟨continue; rest, σ⟩ → ⟨Continue, σ⟩

(E-WHILE-CONTINUE)      (* while loop bắt Continue → bỏ qua phần còn lại body, lặp lại từ đầu *)
    ⟨cond, σ⟩ → ⟨true, σ'⟩
    ⟨body, σ'⟩ → ⟨Continue, σ''⟩
    ⟨while cond { body }, σ''⟩ → ⟨v, σ'''⟩
    ────────────────────────
    ⟨while cond { body }, σ⟩ → ⟨v, σ'''⟩
```

> **Ghi chú thiết kế**: `Return(v)`, `Break`, `Continue` không phải là giá trị thông thường — đây là **tín hiệu** (signals) chỉ có thể bị bắt bởi các cấu trúc điều khiển tương ứng:
> - `Return(v)` chỉ bị bắt bởi `E-CALL-RETURN`
> - `Break` chỉ bị bắt bởi `E-WHILE-BREAK` và `E-FOR-BREAK`
> - `Continue` chỉ bị bắt bởi `E-WHILE-CONTINUE`
>
> Nếu tín hiệu lan ra ngoài context hợp lệ (ví dụ `break` ngoài vòng lặp) → **COMPILE ERROR** phát hiện tĩnh lúc semantic analysis.

## 5. Ngữ nghĩa Hợp đồng (Contract Semantics)


### 5.1 Các Chế độ Thực thi/Thực thi Hợp đồng

| Chế độ | Pre-condition (Tiền điều kiện) | Post-condition (Hậu điều kiện) | Trường hợp áp dụng |
|---|---|---|---|
| `debug` | Kiểm tra Runtime → báo lỗi panic nếu vi phạm | Kiểm tra ở runtime | Giai đoạn Phát triển (Development) |
| `release` | Kiểm tra Runtime → báo lỗi panic | Bỏ qua (tối ưu tốc độ) | Phát hành hệ thống sử dụng (Production) |
| `verified` | Được phân tích / chứng minh tĩnh tại Pre-compilation | Chứng minh tĩnh trước khi biên dịch | Dự án Tối cao An toàn (Safety-critical) |
| `unchecked` | Tước / lược đi / Bỏ hết | Bỏ hết các logic kiểm tra | Ép cấu trúc hoạt động Tối đa hiệu năng máy |

### 5.2 Quy tắc Hợp đồng Lớp cao (Formal Contract Rule)

```
(CONTRACT-ENFORCE)
    mode = current_compilation_mode
    mode ∈ {debug, release}
    ⟨pre, σ_args⟩ → ⟨true, σ'⟩
    ⟨body, σ'⟩ → ⟨v, σ''⟩
    mode = debug → ⟨post, σ'' ∪ {result: v}⟩ → ⟨true, σ'''⟩
    ────────────────────────
    Kết xuất hệ thống phát hành thành function trả về giá trị là v

(CONTRACT-SKIP)
    mode = unchecked
    ⟨body, σ⟩ → ⟨v, σ'⟩
    ────────────────────────
    function trả về là v (hủy toàn bộ contract evaluation)
```

## 6. Lớp Ngữ nghĩa Khối lệnh Lower (Lowering)

```
(E-LOWER-BLOCK)
    module hiện thời khai báo biên dịch Target đích danh thiết bị là loại T
    các khối lower_block lập ra đặc quyền dành cho T
    ⟨lower_body, σ⟩ →_T ⟨v, σ'⟩     (* thực thi tập lệnh cấu hình thiết bị cấp thiết *)
    ────────────────────────
    ⟨lower_call(), σ⟩ → ⟨v, σ'⟩

(E-LOWER-REGISTER-WRITE)
    target = C
    ⟨value, σ⟩ → ⟨v, σ'⟩
    ────────────────────────
    ⟨REG.FIELD = value, σ⟩ →_C ⟨Unit, σ'[REG.FIELD ↦ v]⟩
    effect: {register}
```

## 7. Lớp Ngữ nghĩa Máy Trạng thái (State Machine Semantics)

```
(E-SM-TRANSITION)
    sm khởi tranh ở phân mục/hệ trạng thái S₁
    Sự kiện/Event hiệu lện nhận tín hiệu thông báo E
    Hàm cầu nối chuyển trang (transition) từ (S₁, E) → (S₂, action/logic gán mốc chức năng) đã xuất hiện trong bảng table
    ⟨action(context), σ⟩ → ⟨_, σ'⟩
    ────────────────────────
    sm đổi mode trạng thái của nó để lùi qua/nhảy sang trang hiển thị S₂, σ'

(E-SM-NO-TRANSITION)
    sm khởi tranh ở khu vực trạng thái gốc S₁
    Event cấp báo lỗi / logic E cất tiếng gọi  
    Chưa/Không có tồn tại bảng (S₁, E) transition bắc cầu để nối đi xa
    ────────────────────────
    sm vẫn mắc kẹt ở phân mục cũ S₁, hệ thống bất di bất dịch đóng cửa không thực thi bất kỳ logic gán/hành động action nào thêm.
```

## 8. Khẳng định Tính đúng đắn (Soundness)

> [!IMPORTANT]
> **Phạm vi áp dụng (Proof Scope)**: Các định lý dưới đây được phát biểu cho **COPL Core Language** — tức là tập con gồm: biểu thức, câu lệnh, hàm, struct, enum, contract, effect checking. **Không bao gồm**: lower blocks (opaque), generics nâng cao (GADT), concurrency primitives.

### 8.1 Tính Tiến hành (Progress)

> **Định lý (Progress)**: Với mọi biểu thức `e` thuộc Core Language, nếu `Γ ⊢ e : τ` và `e` không phải là một giá trị (`v`) hay tín hiệu điều khiển (`Return(v)`, `Break`, `Continue`), thì tồn tại `e'`, `σ'` sao cho `⟨e, σ⟩ → ⟨e', σ'⟩`.
>
> *Diễn giải*: Mọi chương trình well-typed trong Core không bao giờ bị stuck (kẹt không tiến được), ngoại trừ các trường hợp runtime error có định nghĩa (overflow, index out of bounds, contract violation).
>
> **Phạm vi**: Core expressions & statements. **Ngoại trừ**: lower blocks (pass-through), runtime panics (có định nghĩa).

### 8.2 Tính Bảo tồn (Preservation)

> **Định lý (Preservation)**: Với mọi `e` thuộc Core Language, nếu `Γ ⊢ e : τ` và `⟨e, σ⟩ → ⟨e', σ'⟩`, thì tồn tại `Γ' ⊇ Γ` sao cho `Γ' ⊢ e' : τ`.
>
> *Diễn giải*: Một bước reduce không thay đổi type của biểu thức. Type inference tĩnh đảm bảo không có type confusion tại runtime.
>
> **Phạm vi**: Core expressions. **Ngoại trừ**: lower blocks (ta chỉ tin signature, không type-check body).

### 8.3 Độ An Toàn Hợp Đồng (Contract Safety)

> **Định lý (Contract Safety)**: Ở chế độ `debug`, nếu hàm `f` có contract `(pre, post)` và `pre(inputs) = true`, thì:
> - (a) Nếu `f` trả về `v` thì `post(inputs, v) = true`, hoặc
> - (b) `f` phát ra `ContractViolation("postcondition")` — xác nhận có bug trong body của `f`.
>
> **Phạm vi**: Mode `debug` và `release`. **Ngoại trừ**: Mode `unchecked` (bỏ qua hoàn toàn), mode `verified` (yêu cầu static proof bên ngoài — là **Future Guarantee**).

### 8.4 Độ An Toàn Bộ nhớ Tĩnh (Static Memory Safety) — *Phạm vi hạn chế*

> **Định lý (Static Memory Safety)**: Với profile `embedded` có `memory_mode = static`:
> - Không có heap allocation tại runtime (đảm bảo bởi E401 compile check)
> - Không có use-after-free đối với static variables (không có deallocation)
> - Kích thước bộ nhớ được xác định hoàn toàn tại compile-time
>
> **Phạm vi**: Chỉ với `memory_mode = static`. **Ngoại trừ**: `owned`, `managed`, `region` — cần additional machinery chưa được formalize đầy đủ.

> [!WARNING]
> **Future Guarantees (Mục tiêu tương lai — chưa có formal proof)**:
> - **Race-freedom** (absence of data races): Cần formal access discipline cho concurrency primitives
> - **Use-after-free prevention cho `owned` mode**: Cần ownership tracking rules
> - **Soundness cho generics phức tạp**: Cần HM inference proof hoàn chỉnh
> - **Verified mode contract checking**: Cần tích hợp với SMT solver
>
> Những items trên đây **không phải là guarantees hiện tại**. Chúng là mục tiêu thiết kế cho các giai đoạn phát triển tiếp theo của COPL.

