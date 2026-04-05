# Project Status — Cortex Platform (COPL + GEAS)
**Updated**: 2026-04-03
**Tổng quan toàn dự án**

---

## Trạng thái Tổng thể

| Component | Phase | Spec | Implementation | Ghi chú |
|-----------|-------|------|----------------|---------|
| **COPL Compiler** | P0 → sắp P1 | ✅ 100% (10/10) | ⏳ Chưa bắt đầu | Bắt đầu tuần tới |
| **GEAS Agent** | P0 (waiting) | ✅ 100% | ⏸️ Chờ COPL P3 | Design only |
| **Integration** | — | ✅ 5 contracts | ⏸️ Chờ cả 2 | Sau tuần 22 |

---

## Tiến độ COPL (Compiler)

```
P0 Spec    ████████████████████ 100% ✅ DONE
P1 Lexer   ░░░░░░░░░░░░░░░░░░░░   0% → bắt đầu
P2 Types   ░░░░░░░░░░░░░░░░░░░░   0%
P3 Codegen ░░░░░░░░░░░░░░░░░░░░   0%
P4 CLI     ░░░░░░░░░░░░░░░░░░░░   0%
```

## Tiến độ GEAS (Agent)

```
P0 Spec    ████████████████████ 100% ✅ DONE
P4 Core    ░░░░░░░░░░░░░░░░░░░░   0% → sau COPL P3
P5 Integ   ░░░░░░░░░░░░░░░░░░░░   0%
P6 Train   ░░░░░░░░░░░░░░░░░░░░   0%
```

---

## Quyết định Chung (Shared Decisions)

1. COPL phát triển trước, GEAS chờ đến COPL P3 Gate
2. Integration contracts (5 hợp đồng) là ranh giới cứng giữa 2 team
3. SIR là trung tâm — mọi artifact sinh từ SIR
4. Target đầu tiên: C codegen cho embedded/STM32

---

## Links Nhanh

- COPL sprint: `docs/status/copl/current_sprint.md`
- GEAS sprint: `docs/status/geas/current_sprint.md`
- Governance: `docs/cortex/06_project_governance.md`
- AI handoff: `docs/cortex/04_ai_handoff.md`
- Spec COPL: `docs/copl/`
- Spec GEAS: `docs/geas/`
