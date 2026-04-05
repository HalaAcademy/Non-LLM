# Cortex AI Handoff Protocol
## Hướng Dẫn Chuyển Giao Context Cho AI Mới

> **Version**: 2.0 | **Cập nhật**: 2026-04-03

---

## ⚡ TL;DR — Bắt đầu ngay trong 60 giây

```
Bước 1: Đọc README.md ở thư mục gốc (Non-LLM/)
Bước 2: Đọc docs/status/shared/project_overview.md
Bước 3: Đọc docs/status/copl/current_sprint.md (nếu làm COPL)
         hoặc docs/status/geas/current_sprint.md (nếu làm GEAS)
Bước 4: Đọc file spec cụ thể cho task (xem Section 3 trong README.md)
→ Bắt đầu làm việc
```

---

## 1. Entry Point Duy Nhất

> [!IMPORTANT]
> **`README.md` ở thư mục gốc là file duy nhất cần đọc đầu tiên.**
> File đó chứa: project overview, bản đồ tài liệu, quy tắc, structure, và cách bắt đầu.

---

## 2. Context Prompt Template (Dán vào session mới)

Khi bắt đầu session AI mới, dán prompt sau:

```
# Project Context: Cortex (COPL + GEAS)

## Dự án là gì?
Cortex = COPL compiler (ngôn ngữ nhúng safety-critical) + GEAS (AI agent học viết code).
GEAS viết code COPL → compiler verify → GEAS học từ kết quả.

## Entry point
Đọc README.md tại thư mục gốc của project để nắm toàn bộ context.

## Trạng thái hiện tại
- docs/status/shared/project_overview.md  → Dashboard tổng
- docs/status/copl/current_sprint.md      → COPL sprint
- docs/status/geas/current_sprint.md      → GEAS sprint

## Task cần làm [ĐIỀN VÀO ĐÂY]
Component: [COPL / GEAS]
Task: [mô tả task]
Spec reference: [docs/copl/XX_file.md Section N]
Acceptance criteria:
  1. [...]
  2. [...]
  3. [...]

## Quy tắc bất di bất dịch
1. Grammar phải LL(1)/LL(2)
2. Không thay đổi spec không có approval
3. Viết test cùng hoặc trước code
4. Cập nhật current_sprint.md sau mỗi task
5. Gặp ambiguity → tạo open_questions file, không assume
```

---

## 3. Bản đồ Tài liệu Nhanh

| Tôi cần... | Đọc file này |
|-----------|-------------|
| Hiểu dự án tổng thể | `README.md` |
| Biết đang làm gì | `docs/status/shared/project_overview.md` |
| COPL grammar/syntax | `docs/copl/01_grammar_spec.md` |
| COPL types | `docs/copl/02_type_system.md` |
| COPL effects | `docs/copl/03_effect_system.md` |
| COPL SIR format | `docs/copl/04_sir_schema.md` |
| COPL semantics | `docs/copl/05_operational_semantics.md` |
| COPL memory | `docs/copl/06_memory_concurrency.md` |
| COPL C codegen | `docs/copl/07_lowering_spec.md` |
| COPL errors/modules | `docs/copl/08_module_error_handling.md` |
| COPL compiler arch | `docs/copl/09_compiler_architecture.md` |
| GEAS model/arch | `docs/geas/01_architecture.md` + `02_core_model.md` |
| GEAS memory | `docs/geas/04_memory_system.md` |
| GEAS protocol | `docs/geas/05_protocol.md` |
| Interface COPL↔GEAS | `docs/cortex/01_integration_contracts.md` |
| Workflow hàng ngày | `docs/cortex/06_project_governance.md` |
| Coding standards | `docs/cortex/03_work_rules.md` |

---

## 4. Những Điều AI Không Được Làm

```
❌ Không tự assume khi spec không rõ → tạo open_questions file
❌ Không thay đổi file trong docs/copl/ hoặc docs/geas/ mà không có approval
❌ Không thay đổi code đã đánh dấu "DONE — do not touch"
❌ Không xóa field trong SIR schema (backward compat bắt buộc)
❌ Không merge code mà không viết test tương ứng
❌ Không code nếu chưa đọc spec file tương ứng
```

---

## 5. Những Điều AI Luôn Phải Làm

```
✅ Đọc current_sprint.md trước khi bắt đầu
✅ Update current_sprint.md sau khi xong task
✅ Commit message theo convention: [scope] message
✅ Tạo open_questions file khi gặp ambiguity
✅ Reference spec section trong commit message và PR
✅ Chạy make test trước khi submit PR
```

---

## 6. Invariants — Không Bao Giờ Được Phá Vỡ

```
1. COPL grammar: LL(1)/LL(2) — FIRST sets disjoint
2. Integration contracts: pytest tests/contracts/ phải green
3. Generated C: compile được với -Wall -Werror
4. SIR: backward compatible — chỉ thêm field, không xóa
5. Effect system: conservative — reject false positive OK, accept undeclared effect KHÔNG OK
6. Spec > Code: nếu mâu thuẫn → fix code, không tự ý fix spec
```

---

## 7. Cách Verify Sau Khi Làm Xong

```bash
make check        # < 30s: lint + type check
make test         # < 5m: tất cả unit tests
make contracts    # < 2m: integration contract tests
make ci           # < 30m: full CI pipeline
```

---

## 8. Escalation

| Vấn đề | Hành động |
|--------|-----------|
| Spec ambiguous | `docs/status/[project]/open_questions/YYYY-MM-DD_topic.md` |
| Spec có bug | `docs/status/[project]/spec_issues/name.md` + DỪNG implement |
| Block > 2 ngày | Escalate ngay, ghi trong current_sprint.md |
| Muốn thay đổi architecture | `docs/status/shared/decisions/` + cần approval |
