# Cortex — Unified GEAS + COPL Platform
## Tầm Nhìn Hợp Nhất

> **Version**: 1.0 | **Status**: Planning Phase | **Last Updated**: 2026-04-03

---

## 1. Cortex Là Gì?

**Cortex** là sản phẩm hợp nhất của hai dự án:
- **GEAS** — AI Agent biết lập kế hoạch, thực thi, và học từ kinh nghiệm
- **COPL** — Ngôn ngữ lập trình có trí nhớ dự án, compiler hiểu cả kiến trúc

Kết hợp tạo ra:

> **Một AI kỹ sư có ngôn ngữ riêng — viết code bằng COPL, compiler verify, tự học qua mỗi dự án, và trở nên giỏi hơn theo thời gian.**

```
Cortex = GEAS (Brain) + COPL (Language + Compiler)

Input:  "Build EVCU firmware for STM32F407"
Output: Complete COPL project → C code → artifacts → lessons learned
```

## 2. Tại Sao Kết Hợp?

### GEAS cần COPL

| GEAS cần | COPL cung cấp |
|---|---|
| World model có cấu trúc | SIR — biểu diễn dự án có ngữ nghĩa |
| Structured error feedback | Compiler diagnostics 5 loại, có phân loại |
| Training data tự nhiên | Mỗi compile cycle = 1 structured episode |
| Verify code chất lượng | Type checker + effect checker + profile checker |

### COPL cần GEAS

| COPL cần | GEAS cung cấp |
|---|---|
| AI agent hiểu artifacts | Goal Interpreter + Memory Manager |
| Tự động viết code + debug | Action Executor + Diagnoser |
| Lập kế hoạch dự án | Hierarchical Planner |
| Liên tục cải thiện | Lesson Learner + Policy Adapter |

### Flywheel Effect

```
GEAS viết COPL → Compiler sinh artifacts → Artifacts = training data
→ GEAS học từ data → Viết COPL TỐT HƠN → ... (positive feedback loop)
```

## 3. Product Positioning

```
GitHub Copilot:   Human viết code → AI gợi ý
Devin:            Human đưa task → AI viết code (ngôn ngữ cũ)
Cortex:           Human đưa goal → AI engineer CẢ DỰ ÁN
                  bằng ngôn ngữ native → compiler verify
                  → sinh target code + artifacts + lessons
```

**Competitive moat**: Không ai khác có cả ngôn ngữ lẫn AI agent tích hợp.

## 4. Kiến Trúc Hợp Nhất

```
┌──────────────────────────────────────────────────────┐
│                     CORTEX                            │
│                                                       │
│  ┌──────────────────┐    ┌──────────────────────┐    │
│  │    GEAS BRAIN     │    │   COPL PLATFORM      │    │
│  │                   │    │                      │    │
│  │ Goal Interpreter  │    │ Lexer/Parser         │    │
│  │ Memory Manager ◄──┼────┤ Type Checker         │    │
│  │ World Model    ◄──┼────┤ Effect Checker       │    │
│  │ Planner           │    │ SIR Builder     ─────┼──► SIR
│  │ Policy Engine     │    │ Target Lowering      │    │
│  │ Action Executor──►┼────┤ C/Rust/Go Codegen    │    │
│  │ Diagnoser     ◄───┼────┤ Diagnostics     ─────┼──► Errors
│  │ Reflection        │    │ Artifact Engine ─────┼──► AI Bundle
│  │ Lesson Learner    │    │                      │    │
│  └──────────────────┘    └──────────────────────┘    │
│                                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │             INTEGRATION CONTRACTS                 │ │
│  │  1. SIR Query Interface                           │ │
│  │  2. Diagnostic Output Format                      │ │
│  │  3. Artifact Output Format                        │ │
│  │  4. COPL Action Interface                         │ │
│  │  5. Feedback Loop Data Schema                     │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 5. Development Strategy

### COPL First — GEAS Design Parallel, Code After

```
Tháng 1-4:   COPL compiler hoàn chỉnh
             GEAS thiết kế (chỉ docs, không code)
             Mock GEAS Agent validate contracts trong CI

Tháng 5-7:   GEAS code bắt đầu (COPL grammar đã đóng băng)
             COPL maintenance + bug fixes

Tháng 8-10:  Integration GEAS ↔ COPL
             End-to-end demos

Tháng 11-14: Polish, training at scale, release
```

Lý do COPL trước:
1. Grammar instability sẽ phá hủy GEAS training data nếu làm song song
2. COPL có giá trị độc lập (con người dùng được), GEAS phụ thuộc COPL
3. Con người phải validate compiler trước AI
4. Mọi ngôn ngữ thành công đều build platform trước

### 5 Integration Contracts

Viết TRƯỚC cả COPL và GEAS để đảm bảo tương thích:

1. **SIR Query Contract** — GEAS World Model đọc SIR
2. **Diagnostic Contract** — GEAS Diagnoser parse compiler errors
3. **Artifact Contract** — GEAS Memory nạp summary cards, trace matrix
4. **Action Contract** — GEAS Executor điều khiển COPL compiler
5. **Episode Schema Contract** — GEAS tạo training data từ compile results

Mock GEAS Agent chạy trong CI suốt quá trình phát triển COPL → validate contracts daily.

## 6. Scale Considerations

| Vấn đề | Giải pháp |
|---|---|
| 30GB project | SIR index (~150MB) → query thay vì load toàn bộ |
| Nhớ qua nhiều tháng | External memory (SQLite) persistent |
| Nhiều git branches | Branch-aware memory (lesson tagged by branch) |
| Nhiều loại tests | Test orchestration layer (unit → integration → HIL) |
| Memory degradation | Hierarchical retrieval + compaction |
| Incremental build | Dependency-aware incremental compilation |

## 7. Target Market

**Primary**: Embedded / Automotive / Safety-critical (ISO 26262)
- Traceability bắt buộc → COPL native
- Complex codegen → COPL multi-target
- Long-lived projects → GEAS memory
- AI-assisted development → Cortex full package

**Secondary**: Backend systems engineering, multi-team projects

## 8. Bản Đồ Tài Liệu

```
docs/
├── copl/                    ← 13 files — Ngôn ngữ COPL
│   ├── 00_overview.md       ← COPL là gì, tại sao, architecture
│   ├── 01-12 ...            ← Specs chi tiết
│
├── geas/                    ← 11 files — AI Agent GEAS
│   ├── 00_overview.md       ← GEAS là gì, 12 modules, model
│   ├── 01-10 ...            ← Specs chi tiết
│
└── cortex/                  ← 6 files — Hợp nhất + Quản lý
    ├── 00_unified_vision.md ← BẠN ĐANG ĐỌC FILE NÀY
    ├── 01_integration_contracts.md ← 5 formal interface contracts
    ├── 02_project_management.md    ← Phases, milestones, quality gates
    ├── 03_work_rules.md            ← Coding standards, reporting
    ├── 04_ai_handoff.md            ← Protocol bàn giao cho AI khác
    └── 05_risk_mitigation.md       ← Risk matrix + contingency plans
```

## 9. Glossary Hợp Nhất

| Thuật ngữ | Nguồn | Định nghĩa |
|---|---|---|
| **Cortex** | Combined | Sản phẩm hợp nhất GEAS + COPL |
| **SIR** | COPL | Semantic IR — biểu diễn project có cấu trúc |
| **Episode** | GEAS | 1 đơn vị kinh nghiệm của agent |
| **Integration Contract** | Cortex | Interface giữa GEAS và COPL |
| **Mock Agent** | Cortex | Agent giả validate contracts trong CI |
| **Flywheel** | Cortex | Positive feedback loop: viết → learn → viết tốt hơn |
| **Proto-COPL** | Cortex | JSON bridge trước khi compiler sẵn sàng |
