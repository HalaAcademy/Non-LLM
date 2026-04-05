# Hệ thống Quản lý Dự án COPL — Project Governance
## Quy trình Làm việc, Báo cáo Tiến độ và Bàn giao

> **Version**: 1.0 | **Cập nhật lần cuối**: 2026-04-03
> **Áp dụng cho**: Mọi thành viên team và AI agent làm việc trên dự án COPL/Cortex

---

## 1. Nguyên tắc Nền tảng

### 1.1 Single Source of Truth (SSOT)

```
docs/                          ← Root của toàn bộ knowledge base
│
├── copl/                      ← SPEC ngôn ngữ COPL (13 files)
│   ├── 00_overview.md
│   ├── 01_grammar_spec.md
│   └── ...
│
├── geas/                      ← SPEC AI agent GEAS (11 files)
│   ├── 00_overview.md
│   └── ...
│
├── cortex/                    ← Quản lý TOÀN DỰ ÁN (7 files)
│   ├── 00_unified_vision.md
│   ├── 01_integration_contracts.md
│   ├── 02_project_management.md
│   ├── 03_work_rules.md
│   ├── 04_ai_handoff.md
│   ├── 05_risk_mitigation.md
│   └── 06_project_governance.md  ← file này
│
└── status/                    ← TRẠNG THÁI THỰC TẾ (cập nhật thường xuyên)
    ├── shared/
    │   ├── project_overview.md    ← Dashboard tổng toàn dự án
    │   ├── decisions/             ← Quyết định ảnh hưởng cả 2 team
    │   └── weekly_reports/        ← Báo cáo cấp platform (cross-team)
    │
    ├── copl/                      ← Status riêng của COPL team
    │   ├── current_sprint.md      ← Cập nhật HÀNG NGÀY
    │   ├── weekly_reports/
    │   ├── phase_gates/
    │   ├── open_questions/        ← Ambiguity về COPL spec
    │   └── spec_issues/           ← Bug/vấn đề trong COPL spec
    │
    └── geas/                      ← Status riêng của GEAS team
        ├── current_sprint.md      ← Cập nhật HÀNG NGÀY (khi active)
        ├── weekly_reports/
        ├── phase_gates/
        └── open_questions/        ← Ambiguity về GEAS spec
```

**Nguyên tắc phân chia:**
- `docs/copl/` + `docs/geas/` + `docs/cortex/` = **Spec** (thay đổi ít, cần review)
- `docs/status/copl/` + `docs/status/geas/` = **Progress** (thay đổi hàng ngày, không cần review)
- `docs/status/shared/` = **Cross-team** (ảnh hưởng cả 2 team, cần cả 2 đọc)

> [!IMPORTANT]
> **Quy tắc số 1**: Nếu thông tin không có trong SSOT, nó KHÔNG TỒN TẠI với project.
> Mọi quyết định kỹ thuật, thay đổi spec, blocker — đều phải ghi vào docs/.


---

## 2. Git Workflow

### 2.1 Cấu trúc Branch

```
main
│   ← Chỉ nhận merge từ release branches
│   ← Mỗi commit trên main = 1 Phase Gate đã pass
│
├── release/phase-1         ← Compiler Phase 1 (lexer + parser)
├── release/phase-2         ← Compiler Phase 2 (type checker + SIR)
├── release/phase-3         ← Compiler Phase 3 (codegen)
│
├── dev/copl-parser         ← Feature branch (max 1 tuần)
├── dev/type-checker
├── dev/c-codegen
│
└── fix/parser-bug-001      ← Hotfix từ main
```

### 2.2 Commit Convention

```
Format: [scope] message (#issue)

Scopes:
  [lexer]    → thay đổi lexer
  [parser]   → thay đổi parser
  [types]    → type system
  [effects]  → effect system
  [sir]      → SIR generation
  [codegen]  → C code generation
  [artifact] → artifact engine
  [test]     → thêm test
  [spec]     → cập nhật docs/spec
  [fix]      → bug fix
  [ci]       → CI/CD changes

Ví dụ:
  [parser] Thêm lower_struct_decl production (#42)
  [types] Fix type inference cho fn type với generic params (#47)
  [spec] Cập nhật grammar với 8 production rules mới (#51)
```

### 2.3 Pull Request Rules

```
TRƯỚC KHI MỞ PR:
  □ Self-review diff — đọc lại từng dòng thay đổi
  □ Tests pass locally: make test
  □ Lint pass: make lint
  □ Docs cập nhật nếu thay đổi behavior

PR TEMPLATE (tự động điền):
---
## Thay đổi gì?
[mô tả ngắn gọn]

## Lý do?
[vấn đề gì đang giải quyết]

## Kiểm tra thế nào?
- Chạy: [lệnh cụ thể]
- Kết quả mong đợi: [output]

## Spec reference
- File spec liên quan: docs/copl/[file].md Section [N]

## Checklist
□ Tests thêm mới cho behavior mới
□ Breaking change? Nếu có: describe migration
□ Docs cập nhật

## Ảnh hưởng đến Phase Gate?
□ Không  □ Có — Gate checkpoint: [tên]
---

MERGE CONDITIONS:
  □ CI xanh (tất cả test pass)
  □ Ít nhất 1 reviewer approve
  □ Tất cả comment resolved
```

---

## 3. Vòng Lặp Làm Việc Hàng Ngày (Daily Loop)

### 3.1 Cho Developer / AI Agent

```
MỖI NGÀY LÀM VIỆC:

Sáng (5 phút):
  1. Đọc docs/status/current_sprint.md
  2. Chọn task đang được assign (status: in_progress)
  3. Kiểm tra có blocker nào không
  4. Update task status → in_progress

Trong ngày:
  - Code theo spec trong docs/
  - Viết test TRƯỚC khi code (TDD preferred)  
  - Commit nhỏ, thường xuyên (mỗi 1-2 giờ)
  - Nếu gặp ambiguity trong spec → raise question ngay, đừng assume

Cuối ngày (5 phút):
  1. Update docs/status/current_sprint.md:
     - Task nào xong → done
     - Task nào đang làm → progress %
     - Blocker mới nếu có
  2. Push commits lên branch
  3. Note: "Tomorrow: [làm gì tiếp]"
```

### 3.2 `current_sprint.md` Format

```markdown
# Sprint [N] — Week [W] of Phase [P]
**Updated**: 2026-MM-DD HH:MM
**Phase**: P1 — Lexer + Parser
**Sprint goal**: [1 câu mô tả mục tiêu sprint này]

## Status: 🟢 ON TRACK | 🟡 AT RISK | 🔴 BLOCKED

## Tasks

### Đang làm (In Progress)
| Task | Assignee | Progress | Deadline |
|------|----------|----------|----------|
| Implement if_let_stmt parser | @person | 60% | Tue |
| Write 20 parser test cases | @person | 80% | Wed |

### Xong (Done this sprint)
- [x] Lexer: tất cả keywords (#commit abc123)
- [x] Lexer: string literals với escape sequences (#commit def456)

### Tồn đọng (Blocked)
| Task | Blocked by | Since |
|------|------------|-------|
| lower_struct parsing | Chờ decision về volatile keyword rules | Mon |

## Metrics hôm nay
- Tests passing: 127/200 (63%)
- Coverage: 71%
- Open PRs: 2

## Blockers cần giải quyết
1. [BLOCKER] volatile keyword: có cần strict @volatile annotation không?
   - Owner: @lead
   - Deadline để quyết định: Thứ 3

## Notes
[Bất kỳ thứ gì quan trọng cần team biết]
```

---

## 4. Báo Cáo Tiến Độ (Progress Reporting)

### 4.1 Báo Cáo Hàng Tuần

**File**: `docs/status/weekly_reports/week_YYYY-WW.md`

```markdown
# Báo Cáo Tuần [N] — Phase [P]
**Period**: 2026-MM-DD đến 2026-MM-DD
**Report by**: [người/AI viết báo cáo]

---

## 1. Tóm tắt (Executive Summary)
- Phase hiện tại: **P1 — Lexer + Parser**
- Tiến độ phase: **45%** (target: 50% vào cuối tuần này)
- Trạng thái: 🟡 **AT RISK** — parser bị chậm 3 ngày do issue X
- Dự kiến Phase Gate: **2026-MM-DD** (nguyên kế hoạch: 2026-MM-DD)

---

## 2. Hoàn thành Tuần này
| Task | Result | Evidence |
|------|--------|----------|
| Lexer hoàn chỉnh | ✅ DONE | 200/200 lexer tests pass |
| Parser: module, struct, enum | ✅ DONE | 45/45 test cases pass |
| Parser: function declarations | ✅ DONE | 30/30 tests pass |

## 3. Đang Làm / Chưa Xong
| Task | Progress | Issue |
|------|----------|-------|
| Parser: statements (if/while/match) | 70% | Đang debug while_let desugaring |
| Parser: expression precedence | 30% | Chưa bắt đầu postfix_op |
| Test suite expansion | 40% | Cần thêm 60 test cases |

## 4. Rủi ro & Blockers
| Vấn đề | Mức độ | Hành động | Owner | Deadline |
|--------|--------|-----------|-------|----------|
| while_let desugaring phức tạp hơn dự kiến | MEDIUM | Simplify: chỉ support `while let Some(x) = e` | @dev1 | Thứ 2 |
| Test coverage < 80% | LOW | Thêm 30 test cases cho edge cases | @dev2 | Thứ 4 |

## 5. Metrics

```
Tests:
  Lexer:   200/200 ✅ (100%)
  Parser:  75/200  ⚠️  (37.5%) — target tuần sau: 150/200
  Types:   0/0     ⏳  (chưa bắt đầu)
  
Code:
  LOC compiler: 1,247
  LOC tests:    834
  Coverage:     68% (target: 80%)
  
CI:
  Build: GREEN ✅
  Last failure: 2026-MM-DD (fixed in commit abc123)
```

## 6. Kế Hoạch Tuần Tới
| Task | Owner | Deadline |
|------|-------|----------|
| Complete statement parser | @dev1 | Thứ 4 |
| Complete expression parser | @dev1 | Thứ 6 |
| Write 60 more test cases | @dev2 | Thứ 5 |
| Parser error recovery | @dev2 | Thứ 6 |
| Phase Gate self-check list | @lead | Thứ 6 |

## 7. Dự Báo Phase Gate
- **Target**: [Date]
- **Current forecast**: [Date +/- N days]
- **Confidence**: HIGH / MEDIUM / LOW
- **Lý do nếu lệch**: [giải thích]
```

### 4.2 Phase Gate Review

**File**: `docs/status/phase_gates/gate_P1_result.md`

```markdown
# Phase Gate Review: P1 — Lexer + Parser
**Review date**: 2026-MM-DD
**Reviewer(s)**: [names]
**Decision**: ✅ PASS | ❌ FAIL | ⚠️ CONDITIONAL PASS

---

## Checklist kết quả

### Mandatory (tất cả phải PASS):
- [x] 168 EBNF productions implemented ← đếm cụ thể
- [x] Parser test suite: 250 test cases / 250 pass (100%)
- [x] Lexer: tất cả token types hoạt động
- [x] Error recovery: parser tiếp tục sau syntax error
- [x] Parse 3 example projects không crash
- [x] Parse benchmark file < 10ms

### Evidence (kèm link commit/test):
- Lexer tests: tests/lexer/ [commit hash]
- Parser tests: tests/parser/ [commit hash]
- Benchmark: scripts/bench.sh output [log file]
- Example projects: examples/ [commit hash]

---

## Metrics tại Gate

```
Test Results:
  Total: 250
  Pass:  250 (100%) ✅
  Fail:  0

Performance:
  Benchmark file (500 lines): 6ms ✅ (target < 10ms)
  
Coverage:
  Parser: 94% ✅ (target ≥ 80%)
  
Code quality:
  Lint: 0 warnings ✅
  Complexity: avg cyclomatic 3.2 ✅ (target < 5)
```

---

## Quyết định

**DECISION**: ✅ PASS

**Ghi chú**: while_let được implement đầy đủ (không cần simplify).
Parser test coverage 94% vượt target 80%.

**Bước tiếp theo**: Bắt đầu Phase 2 — Type Checker
- Start date: [Date]
- Owner: [name]
- First milestone: [description by Date]

---
*Signed off by*: [Lead name] — [Date]
```

---

## 5. Quy Trình Bàn Giao (Handoff Protocol)

### 5.1 Bàn Giao Sang Người / Team Khác

**Khi nào cần bàn giao**: member mới join, team member nghỉ, rotate assignment, kết thúc phase.

```markdown
# Handoff Document — [Component] — [Date]

## Người bàn giao
- Name: [...]
- Role: [...]
- Thời gian làm: [bao lâu]

## Người nhận
- Name: [...]
- Bắt đầu: [date]

---

## Trạng thái hiện tại

**Component**: COPL Parser
**Phase**: P1 — 80% hoàn thành
**Tiếp theo phải làm**: Hoàn thiện expression Pratt parser

## Kiến trúc code hiện tại

```
src/copl/
├── lexer.py          ← HOÀN THÀNH — đừng sửa trừ khi có bug
├── parser.py         ← ĐANG LÀM — main file cần tiếp tục
│   ├── parse_module()    ← DONE
│   ├── parse_function()  ← DONE
│   ├── parse_statement() ← 70% DONE — thiếu while_let, critical_section
│   └── parse_expr()      ← 30% DONE — Pratt parser chưa xong postfix
├── ast.py            ← HOÀN THÀNH — schema cho toàn bộ AST nodes
└── errors.py         ← HOÀN THÀNH — error codes E001-E502
```

## Những quyết định đã chốt (ĐỪNG thay đổi)

1. **Pratt parser cho expressions** — đã chọn, không dùng recursive descent pure
   - Lý do: operator precedence table dễ mở rộng
   - File: parser.py line 340-410
   
2. **Desugaring `if let` → `match`** — xảy ra TRONG parser, không phải semantic phase
   - Lý do: đơn giản hơn, không cần thêm AST node riêng
   - Documented trong: docs/copl/01_grammar_spec.md Section 6

3. **Error recovery**: tiếp tục sau `}` sync token
   - Lý do: cho phép báo nhiều lỗi cùng lúc
   - File: parser.py line 85, method `synchronize()`

## Những thứ còn dở

1. **CHƯA XONG**: `parse_expr()` — Pratt parser thiếu:
   - postfix: `()` function call
   - postfix: `[]` index
   - postfix: `?` try operator
   - Ước tính: 2 ngày nữa
   
2. **CHƯA XONG**: `parse_statement()` thiếu:
   - `critical_section` statement  
   - `while let` desugaring
   - Ước tính: 1 ngày

3. **TỒN TẠI BUG**: parser.py line 234 — struct literal ambiguous với block trong some edge cases
   - Documented: issue #67
   - Workaround hiện tại: require explicit type annotation

## Cách chạy và test

```bash
# Chạy tất cả tests
pytest tests/

# Chạy chỉ parser tests
pytest tests/test_parser.py -v

# Parse một file cụ thể
python -m copl parse examples/can_driver.copl

# Benchmark
python scripts/bench.py examples/
```

## Liên hệ nếu cần hỏi thêm

- Slack: [channel] hoặc DM @[sender]
- Office hours: [time]
- Emergency: [contact]

---
*Handoff completed*: [Date and time]
*Acknowledged by receiver*: [signature/date]
```

---

### 5.2 Bàn Giao Cho AI Agent (AI Handoff)

**Đây là phần quan trọng nhất** — để AI mới có thể tiếp tục mà không cần đọc toàn bộ docs.

**File**: `docs/status/ai_context_bundle.json` (tự động generate)

```json
{
  "version": "1.0",
  "generated_at": "2026-04-03T12:00:00Z",
  "project": {
    "name": "COPL Compiler + Cortex Platform",
    "tagline": "Context-oriented language for safety-critical embedded systems",
    "repo": "github.com/[user]/copl"
  },
  
  "current_state": {
    "phase": "P1",
    "phase_name": "Lexer + Parser",
    "phase_progress_pct": 80,
    "sprint": 3,
    "status": "AT_RISK",
    "status_reason": "Expression parser 30% behind schedule"
  },
  
  "immediate_task": {
    "description": "Complete Pratt parser for expression parsing",
    "file": "src/copl/parser.py",
    "start_at_line": 340,
    "spec_reference": "docs/copl/01_grammar_spec.md Section 7",
    "acceptance_criteria": [
      "Function call: f() syntax works",
      "Index access: arr[i] syntax works",
      "Try operator: expr? syntax works",
      "All 42 expression test cases pass"
    ],
    "estimated_hours": 8
  },
  
  "critical_context": {
    "key_decisions": [
      {
        "decision": "Pratt parser for expressions",
        "rationale": "Operator precedence table extensible",
        "impl_location": "parser.py:340-410"
      },
      {
        "decision": "if_let desugars to match in parser phase",
        "rationale": "No extra AST node",
        "spec": "docs/copl/01_grammar_spec.md:Section 6"
      }
    ],
    "known_bugs": [
      {
        "id": "#67",
        "description": "Struct literal ambiguous with block",
        "workaround": "Require explicit type annotation",
        "priority": "LOW"
      }
    ],
    "do_not_change": [
      "lexer.py — complete, do not touch",
      "ast.py — schema frozen until Phase Gate",
      "errors.py — error codes must match spec"
    ]
  },
  
  "how_to_verify": {
    "quick_check": "pytest tests/ (< 60s)",
    "full_verify": "make ci (< 5min)",
    "run_benchmarks": "python scripts/bench.py"
  },
  
  "spec_map": {
    "grammar": "docs/copl/01_grammar_spec.md",
    "types": "docs/copl/02_type_system.md",
    "effects": "docs/copl/03_effect_system.md",
    "sir": "docs/copl/04_sir_schema.md",
    "semantics": "docs/copl/05_operational_semantics.md",
    "memory": "docs/copl/06_memory_concurrency.md",
    "lowering": "docs/copl/07_lowering_spec.md",
    "modules_errors": "docs/copl/08_module_error_handling.md",
    "compiler_arch": "docs/copl/09_compiler_architecture.md"
  },
  
  "next_phase_preview": {
    "phase": "P2",
    "name": "Type Checker + Effect Checker + SIR",
    "starts_when": "P1 Gate passes",
    "first_task": "Implement symbol resolution for module imports"
  }
}
```

**Script generate tự động** — chạy mỗi ngày:

```python
# scripts/generate_ai_context.py

def generate_ai_context():
    """Tự động build ai_context_bundle.json từ git + test state."""
    return {
        "current_state": read_current_sprint_status(),
        "immediate_task": get_next_unfinished_task(),
        "critical_context": read_key_decisions(),
        "metrics": run_test_suite_and_collect_metrics(),
        "recent_commits": get_last_10_commits_summary(),
    }

# Chạy trong CI mỗi ngày:
# 0 9 * * * python scripts/generate_ai_context.py > docs/status/ai_context_bundle.json
```

---

## 6. Quy trình Giải quyết Xung đột / Ambiguity

### 6.1 Khi Spec Không Rõ

```
Developer / AI gặp vấn đề không rõ trong spec:

1. STOP — không tự assume, không code theo instinct

2. Tạo file: docs/status/open_questions/YYYY-MM-DD_[topic].md
   Format:
   ---
   ## Question
   [Câu hỏi cụ thể, reference đến spec section]
   
   ## Context
   [Đang implement cái gì, dòng code nào bị affected]
   
   ## Options
   A. [Cách hiểu 1] — Consequence: [...]
   B. [Cách hiểu 2] — Consequence: [...]
   
   ## Recommendation
   [Nên chọn option nào và tại sao]
   
   ## Urgency
   BLOCKING | HIGH | MEDIUM | LOW
   ---

3. Tag @lead trong PR / Slack với link file

4. Lead quyết định trong 24h (nếu BLOCKING) hoặc 48h (nếu HIGH)

5. Khi có quyết định → update spec ngay, commit vào docs/
```

### 6.2 Khi Phát Hiện Spec Sai

```
Nếu implementation reveal spec có vấn đề:

1. Ghi rõ: docs/status/spec_issues/[issue_name].md
   - Spec section bị affected
   - Tại sao spec không đúng / không khả thi
   - Proposed fix
   
2. Không sửa spec unilaterally mà không có review

3. Lead review và approve spec change

4. Sau khi approve: cập nhật spec + cập nhật relevant tests
```

---

## 7. Checklist Nhận Việc (Onboarding Checklist)

### Dành cho Developer Mới

```markdown
# Onboarding Checklist — COPL Project

## Ngày 1: Setup
□ Clone repo
□ Đọc docs/cortex/00_unified_vision.md (30 phút)
□ Đọc docs/copl/00_overview.md (20 phút)  
□ Đọc docs/cortex/03_work_rules.md (15 phút)
□ Chạy: make setup && make test → tất cả xanh
□ Join Slack channel #copl-dev

## Ngày 2: Hiểu Spec
□ Đọc spec file liên quan đến task đầu tiên
□ Chạy ví dụ trong examples/ và hiểu output
□ Đọc 10 test case để hiểu behavior expected

## Ngày 3: Làm Task Đầu Tiên
□ Chọn 1 task "good first issue" từ current_sprint.md
□ Tạo branch dev/[tên-task]
□ Implement + test + submit PR
□ Pair review với 1 member khác

## Done khi:
□ 1 PR merged thành công
□ Hiểu rõ git workflow
□ Biết cách update current_sprint.md
```

### Dành cho AI Agent Mới

```markdown
# AI Onboarding — COPL Project

## Bước 1: Đọc context (Bắt buộc, THEO THỨ TỰ)
1. docs/status/ai_context_bundle.json ← ĐỌC ĐÂY TRƯỚC TIÊN
2. docs/cortex/04_ai_handoff.md
3. docs/copl/00_overview.md
4. File spec cụ thể cho task được assign

## Bước 2: Verify môi trường
- Chạy: make test → expect xanh
- Đọc: docs/status/current_sprint.md

## Bước 3: Verify hiểu đúng trước khi code
- Tóm tắt task trong 2-3 câu
- List 3 acceptance criteria
- Xác nhận với human trước khi bắt đầu

## Quy tắc bất di bất dịch cho AI:
1. KHÔNG thay đổi những gì đã đánh dấu "DONE — do not touch"
2. KHÔNG thay đổi spec mà không có explicit approval
3. LUÔN viết test trước hoặc cùng lúc với code
4. LUÔN update current_sprint.md sau khi xong task
5. Báo cáo bất kỳ ambiguity → tạo open_questions file, đừng assume
```

---

## 8. Metrics & Dashbboard Tự Động

### 8.1 Makefile targets

```makefile
# Makefile

setup:       ## Setup dev environment
    pip install -r requirements.txt
    
test:        ## Run all tests
    pytest tests/ -v --tb=short
    
test-fast:   ## Run only fast tests (< 30s)
    pytest tests/ -v -m "not slow"
    
coverage:    ## Run tests with coverage report
    pytest tests/ --cov=src/ --cov-report=html
    
lint:        ## Check code style
    ruff check src/ tests/
    
check:       ## Type check + lint
    mypy src/
    ruff check src/
    
ci:          ## Full CI pipeline (runs in GitHub Actions)
    make lint && make check && make test && make coverage

bench:       ## Run COPL-Bench-20
    python scripts/run_benchmarks.py

status:      ## Print current project status
    python scripts/project_status.py

handoff:     ## Generate AI context bundle for handoff
    python scripts/generate_ai_context.py > docs/status/ai_context_bundle.json
    echo "AI context bundle updated"

sprint-close:  ## Close current sprint, generate weekly report
    python scripts/close_sprint.py
```

### 8.2 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: COPL CI

on:
  push:
    branches: [main, dev/*, release/*]
  pull_request:
    branches: [main, release/*]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install -r requirements.txt
      - name: Lint
        run: make lint
      - name: Type Check
        run: make check
      - name: Tests
        run: make test
      - name: Coverage
        run: make coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
      
      # Tự động update AI context bundle mỗi ngày
      - name: Update AI context
        if: github.ref == 'refs/heads/main'
        run: make handoff && git add docs/status/ai_context_bundle.json && git commit -m "[ci] Update AI context bundle" || true
```

---

## 9. Escalation & Decision Tree

```
Khi gặp vấn đề:

Vấn đề nhỏ (< 2h để giải quyết):
  → Tự quyết, comment trong code, ghi trong commit message

Vấn đề trung bình (ảnh hưởng đến task của mình):
  → Tạo issue GitHub + update current_sprint.md
  → Mention @teammate trong issue
  → Expect response trong 4h trong giờ làm việc

Vấn đề lớn (ảnh hưởng đến Phase Gate hoặc architecture):
  → Tạo docs/status/open_questions/[date]_[topic].md
  → Tag @lead
  → Tổ chức meeting nếu cần (không giả sử đồng ý một chiều)
  → Ghi quyết định vào docs/ ngay sau meeting

Spec conflict (implementation mâu thuẫn với spec):
  → DỪNG implementation
  → Tạo docs/status/spec_issues/[name].md
  → Không code theo assume
  → Chờ spec được update và approve

Blocker (không thể tiến nếu không có external input):
  → Escalate ngay trong ngày phát hiện
  → Ghi trong current_sprint.md với deadline cần giải quyết
  → Nếu block ≥ 2 ngày → notify toàn team
```

---

## 10. Tổng Quan Các File Cần Duy Trì

| File | Update tần suất | Ai cập nhật | Nội dung |
|------|----------------|-------------|---------|
| `docs/status/current_sprint.md` | Hàng ngày | Mọi người | Task status, blockers |
| `docs/status/ai_context_bundle.json` | Tự động (CI daily) | Script | AI handoff context |
| `docs/status/weekly_reports/` | Hàng tuần (Thứ 6) | Lead | Weekly summary |
| `docs/status/phase_gates/` | Mỗi phase | Lead | Gate review results |
| `docs/status/open_questions/` | Khi phát sinh | Mọi người | Câu hỏi cần giải quyết |
| `docs/status/spec_issues/` | Khi phát hiện | Developer | Spec problems |
| `docs/copl/*.md` | Khi có change request | Lead approval | Source of truth |
