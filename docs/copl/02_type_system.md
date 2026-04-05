# Đặc tả Hệ thống Kiểu COPL
## Kiểm tra Kiểu Hai chiều (Bidirectional) — Khắc phục C2: "Không có quy tắc gán kiểu"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Tổng quan

COPL sử dụng **hệ thống kiểu hai chiều (bidirectional type system)** bao gồm:
- **Tổng hợp kiểu (Type synthesis - ⇒)**: suy luận kiểu từ biểu thức
- **Kiểm tra kiểu (Type checking - ⇐)**: xác minh biểu thức khớp với kiểu mong đợi
- **Kiểm tra kiểu nhận thức Profile (Profile-aware typing)**: các kiểu dữ liệu bị giới hạn bởi profile (ví dụ: không được dùng heap trong profile `embedded`)
- **Kiểm tra kiểu nhận thức Hiệu ứng (Effect-aware typing)**: kiểu của hàm mang theo thông tin hiệu ứng (effects)

## 2. Hệ thống Không gian Kiểu dữ liệu (Type Universe)

### 2.1 Các Kiểu Nguyên thủy (Primitive Types)

```
τ ::= Bool                            (* boolean *)
    | U8 | U16 | U32 | U64 | USize    (* số nguyên không dấu *)
    | I8 | I16 | I32 | I64 | ISize    (* số nguyên có dấu *)
    | F32 | F64                        (* số thực dấu phẩy động *)
    | Char                             (* ký tự unicode scalar *)
    | String                           (* Chuỗi UTF-8 — không dùng trong embedded *)
    | Unit                             (* tương đương void / không có giá trị *)
```

### 2.2 Các Kiểu Phức hợp (Compound Types)

```
τ ::= ...
    | [τ; n]                           (* mảng kích thước cố định, n: hằng số nguyên *)
    | [τ]                              (* slice — chỉ tham chiếu *)
    | (τ₁, τ₂, ..., τₙ)               (* tuple *)
    | τ?                               (* tùy chọn = Some(τ) | None *)
    | Result<τ, ε>                     (* kết quả = Ok(τ) | Err(ε) *)
    | S                                (* kiểu struct định danh *)
    | E                                (* kiểu enum định danh *)
    | fn(τ₁, ..., τₙ) -> τᵣ @E        (* kiểu hàm đi kèm với danh sách hiệu ứng E *)
```

### 2.3 Độ Tương thích Kiểu (Type Compatibility)

```
Ép kiểu mở rộng kích thước số (ngầm định):
  U8 → U16 → U32 → U64
  I8 → I16 → I32 → I64
  F32 → F64

Không có chuyển đổi ngầm định giữa số có dấu ↔ không dấu.
Không có chuyển đổi ngầm định giữa số ↔ bool.
```

## 3. Quy tắc Phán đoán Kiểu (Typing Judgments)

### Ký hiệu

```
Γ         Context (Ngữ cảnh): Bản đồ ánh xạ từ tên biến sang kiểu dữ liệu
Γ ⊢ e ⇒ τ Tổng hợp (Synthesize): Trong ngữ cảnh Γ, biểu thức e được suy luận có kiểu τ
Γ ⊢ e ⇐ τ Kiểm tra (Check): Trong ngữ cảnh Γ, biểu thức e được kiểm tra khớp với kiểu τ
Σ         Signature (Chữ ký): Bản đồ ánh xạ từ tên module/function/struct sang định nghĩa
P         Profile hiện tại
```

### 3.1 Quy tắc Cốt lõi (Core Rules)

#### Biến số (Variables)

```
(VAR)
    x: τ ∈ Γ
    ─────────────
    Γ ⊢ x ⇒ τ
```

#### Hằng số giá trị (Literals)

```
(LIT-INT)
    n là số nguyên hằng số
    n vừa vặn trong I32
    ─────────────────
    Γ ⊢ n ⇒ I32

(LIT-UINT)
    n là số nguyên hằng số có hậu tố 'u'
    n vừa vặn trong U32
    ─────────────────
    Γ ⊢ n ⇒ U32

(LIT-FLOAT)
    f là số thực hằng số
    ─────────────────
    Γ ⊢ f ⇒ F64

(LIT-BOOL)
    ─────────────────
    Γ ⊢ true ⇒ Bool
    Γ ⊢ false ⇒ Bool

(LIT-STRING)
    s là chuỗi string hằng số
    String ∈ allowed_types(P)
    ─────────────────
    Γ ⊢ s ⇒ String

(LIT-CHAR)
    c là ký tự hằng số
    ─────────────────
    Γ ⊢ c ⇒ Char
```

#### Bao hàm Kiểu (Subsumption - Quy tắc Nới lỏng)

```
(SUB)
    Γ ⊢ e ⇒ τ₁    τ₁ <: τ₂
    ──────────────────────────
    Γ ⊢ e ⇐ τ₂

(ANNOT)
    Γ ⊢ e ⇐ τ
    ──────────────────────────
    Γ ⊢ (e : τ) ⇒ τ
```

### 3.2 Quy tắc Hàm (Function Rules)

```
(FN-DECL)
    Γ, x₁:τ₁, ..., xₙ:τₙ ⊢ body ⇐ τᵣ
    effects(body) ⊆ E
    E ⊆ allowed_effects(P)
    ──────────────────────────────────────────
    Γ ⊢ fn f(x₁:τ₁, ..., xₙ:τₙ) -> τᵣ @E ⇒ (τ₁,...,τₙ) -> τᵣ @E

(APP)
    Γ ⊢ f ⇒ (τ₁,...,τₙ) -> τᵣ @E
    Γ ⊢ eᵢ ⇐ τᵢ   cho mỗi i ∈ 1..n
    ──────────────────────────────────────────
    Γ ⊢ f(e₁,...,eₙ) ⇒ τᵣ    với hiệu ứng E

(METHOD-CALL)
    Γ ⊢ receiver ⇒ T
    T có phương thức m: (T, τ₁,...,τₙ) -> τᵣ @E
    Γ ⊢ eᵢ ⇐ τᵢ   cho mỗi i
    ──────────────────────────────────────────
    Γ ⊢ receiver.m(e₁,...,eₙ) ⇒ τᵣ    với hiệu ứng E

(CLOSURE)
    Γ, x₁:τ₁, ..., xₙ:τₙ ⊢ body ⇒ τᵣ
    ──────────────────────────────────────────
    Γ ⊢ |x₁:τ₁, ..., xₙ:τₙ| body ⇒ fn(τ₁,...,τₙ) -> τᵣ @E
```

### 3.3 Quy tắc Luồng Điều khiển (Control Flow)

```
(IF-EXPR)
    Γ ⊢ cond ⇐ Bool
    Γ ⊢ then_branch ⇒ τ
    Γ ⊢ else_branch ⇐ τ
    ──────────────────────────────
    Γ ⊢ if cond { then_branch } else { else_branch } ⇒ τ

(IF-STMT)  (* không có else — trả về Unit *)
    Γ ⊢ cond ⇐ Bool
    Γ ⊢ then_branch ⇐ Unit
    ──────────────────────────────
    Γ ⊢ if cond { then_branch } ⇒ Unit

(WHILE)
    Γ ⊢ cond ⇐ Bool
    Γ ⊢ body ⇐ Unit
    ──────────────────────────────
    Γ ⊢ while cond { body } ⇒ Unit

(FOR)
    Γ ⊢ iter ⇒ Iterable<τ>
    Γ, x:τ ⊢ body ⇐ Unit
    ──────────────────────────────
    Γ ⊢ for x in iter { body } ⇒ Unit

(MATCH)
    Γ ⊢ scrutinee ⇒ τₛ
    cho mỗi nhánh (pᵢ => eᵢ):
        Γ, bindings(pᵢ, τₛ) ⊢ eᵢ ⇒ τᵣ    (* mọi nhánh đều trả về cùng kiểu *)
    các p₁...pₙ bao phủ đầy đủ biểu thức (exhaustive) cho τₛ
    ──────────────────────────────────────────
    Γ ⊢ match scrutinee { p₁ => e₁, ..., pₙ => eₙ } ⇒ τᵣ
```

### 3.4 Quy tắc cho Kiểu Phức hợp

```
(STRUCT-LIT)
    S có các trường f₁:τ₁, ..., fₙ:τₙ
    Γ ⊢ eᵢ ⇐ τᵢ   cho mỗi i
    ──────────────────────────────
    Γ ⊢ S { f₁: e₁, ..., fₙ: eₙ } ⇒ S

(FIELD-ACCESS)
    Γ ⊢ e ⇒ S
    S có trường f: τ
    ──────────────────────────────
    Γ ⊢ e.f ⇒ τ

(ENUM-CONSTRUCT)
    E có biến thể V(τ₁, ..., τₙ)
    Γ ⊢ eᵢ ⇐ τᵢ   cho mỗi i
    ──────────────────────────────
    Γ ⊢ E::V(e₁, ..., eₙ) ⇒ E

(ARRAY-LIT)
    Γ ⊢ eᵢ ⇐ τ   cho mỗi i ∈ 1..n
    ──────────────────────────────
    Γ ⊢ [e₁, ..., eₙ] ⇒ [τ; n]

(INDEX)
    Γ ⊢ e ⇒ [τ; n]    (hoặc [τ])
    Γ ⊢ idx ⇐ USize
    ──────────────────────────────
    Γ ⊢ e[idx] ⇒ τ
```

### 3.5 Quy tắc Optional và Result

```
(OPTIONAL-SOME)
    Γ ⊢ e ⇒ τ
    ──────────────────────────────
    Γ ⊢ Some(e) ⇒ τ?

(OPTIONAL-NONE)
    ──────────────────────────────
    Γ ⊢ None ⇐ τ?

(RESULT-OK)
    Γ ⊢ e ⇒ τ
    ──────────────────────────────
    Γ ⊢ Ok(e) ⇒ Result<τ, ε>     (* ε được suy luận từ ngữ cảnh *)

(RESULT-ERR)
    Γ ⊢ e ⇒ ε
    ──────────────────────────────
    Γ ⊢ Err(e) ⇒ Result<τ, ε>    (* τ được suy luận từ ngữ cảnh *)

(TRY-OPERATOR)
    Γ ⊢ e ⇒ Result<τ, ε>
    hàm bao bọc bên ngoài trả về Result<_, ε>
    ──────────────────────────────
    Γ ⊢ e? ⇒ τ                   (* tự động lan truyền (propagate) Err(ε) lên trên *)
```

### 3.6 Quy tắc Toán tử Nhị phân

```
(ARITH)
    Γ ⊢ e₁ ⇒ τ    τ ∈ {U8..U64, I8..I64, F32, F64}
    Γ ⊢ e₂ ⇐ τ
    op ∈ {+, -, *, /, %}
    ──────────────────────────────
    Γ ⊢ e₁ op e₂ ⇒ τ

(COMPARE)
    Γ ⊢ e₁ ⇒ τ    τ có triển khai Ord hoặc Eq
    Γ ⊢ e₂ ⇐ τ
    op ∈ {==, !=, <, >, <=, >=}
    ──────────────────────────────
    Γ ⊢ e₁ op e₂ ⇒ Bool

(LOGICAL)
    Γ ⊢ e₁ ⇐ Bool
    Γ ⊢ e₂ ⇐ Bool
    op ∈ {&&, ||}
    ──────────────────────────────
    Γ ⊢ e₁ op e₂ ⇒ Bool

(BITWISE)
    Γ ⊢ e₁ ⇒ τ    τ ∈ {U8..U64, I8..I64}
    Γ ⊢ e₂ ⇐ τ
    op ∈ {&, |, ^, <<, >>}
    ──────────────────────────────
    Γ ⊢ e₁ op e₂ ⇒ τ
```

## 4. Kiểm tra Kiểu cho Hợp đồng (Contract)

```
(CONTRACT-PRE)
    Γ, params ⊢ condition ⇐ Bool
    ──────────────────────────────
    pre: [condition] kiểm tra kiểu hợp lệ (well-typed)

(CONTRACT-POST)
    Γ, params, result:τᵣ ⊢ condition ⇐ Bool
    ──────────────────────────────
    post: [condition] kiểm tra kiểu hợp lệ

(CONTRACT-LATENCY)
    duration là DURATION_LIT
    ──────────────────────────────
    latency_budget: duration kiểm tra kiểu hợp lệ

(CONTRACT-MEMORY)
    size là SIZE_LIT
    ──────────────────────────────
    memory_budget: size kiểm tra kiểu hợp lệ
```

## 5. Giới hạn Kiểu Tương thích Theo Cấu hình (Profile Restrictions)

```
Các giới hạn profile cho các kiểu dữ liệu:

  embedded:
    - Cấm kiểu chuỗi String (FORBIDDEN) (dùng [U8; N] thay thế)
    - Cấm các kiểu dùng cấp phát Heap (FORBIDDEN)
    - Cấm mảng động (FORBIDDEN) (dùng mảng tĩnh [T; N])
    
  kernel:
    - Giống embedded nhưng cho phép tính năng panic
    
  portable:
    - Cấm dùng kiểu dữ liệu tuân theo thiết bị/mã máy
    - Cấm các khối low (lower blocks)
    
  backend:
    - Cho phép tất cả các kiểu
    - Có sẵn String, Vec, HashMap
    
  scripting:
    - Cho phép tất cả các kiểu
    - Có hỗ trợ dynamic dispatch
```

```
(PROFILE-TYPE-CHECK)
    kiểu τ sử dụng trong module M
    M có profile P
    τ ∉ forbidden_types(P)
    ──────────────────────────────
    τ được cho phép trong M

(PROFILE-TYPE-VIOLATION)
    kiểu τ sử dụng trong module M
    M có profile P
    τ ∈ forbidden_types(P)
    ──────────────────────────────
    COMPILE ERROR: "Kiểu dữ liệu τ không được phép dùng trong profile P"
```

## 6. Lập trình Tổng quát (Generics)

```
(GENERIC-INST)
    f: ∀T₁...Tₙ where C₁...Cₘ. (τ₁,...,τₖ) -> τᵣ
    σ = [T₁ ↦ σ₁, ..., Tₙ ↦ σₙ]    (* áp dụng thay thế kiểu *)
    σ(Cᵢ) giữ vững tính đúng đắn cho ràng buộc Cᵢ
    Γ ⊢ eᵢ ⇐ σ(τᵢ) cho từng i
    ──────────────────────────────
    Γ ⊢ f::<σ₁,...,σₙ>(e₁,...,eₖ) ⇒ σ(τᵣ)

(TRAIT-BOUND)
    T: Trait có nghĩa là kiểu T bắt buộc cấu hình tất cả phương thức quy định ở Trait
    ──────────────────────────────
    Xác minh đúng ngay tại vị trí khởi tạo (instantiation site)
```

## 7. Khẳng định Tính đúng đắn (Soundness Claim)

> **Định lý Tính đúng đắn của hệ kiểu (Type Soundness Theorem)**:
> Nếu `Γ ⊢ e ⇒ τ` và `e →* v` (e đánh giá/chuyển thành một giá trị v) thì giá trị `v` phải thuộc cấp kiểu `τ` (`v : τ`).
>
> **Phương pháp chứng minh**: Tiến triển (Progress) + Tính bảo toàn (Preservation) (Wright & Felleisen, 1994).
> - **Tiến triển (Progress)**: Một khối biểu thức kiểu hợp lệ luôn là một biến giá trị hoặc có khả năng tiếp tục thực hiện ở các bước máy luân phiên.
> - **Tính bảo toàn (Preservation)**: Các bước đánh giá đi tiếp bảo toàn thiết lập kiểu dữ liệu.
>
> Chứng minh toán học đầy đủ sẽ được hoàn thiện ở bước đánh giá kiểm định chính thức.
