# Sprint GEAS — Phase P0 (Design Only)
**Updated**: 2026-04-03
**Phase**: P0 → Đặc tả thiết kế hoàn chỉnh — chờ COPL compiler xong
**Sprint goal**: GEAS không implement cho đến khi COPL Phase 3 Gate pass

## Status: ⏸️ WAITING (blocked by COPL P1–P3)

### Xong
- [x] 11 file spec GEAS hoàn chỉnh (architecture, core model, loss, memory, protocol, training, runtime, evaluation...)

### Blocked
- [ ] GEAS implementation — **blocked by**: COPL compiler chưa xong
  - GEAS cần SIR output từ COPL compiler
  - GEAS cần artifact bundle từ COPL
  - Bắt đầu khi: COPL Phase 3 Gate pass (~tuần 22)

### Có thể làm song song (không cần COPL):
- [ ] Setup Python ML environment (PyTorch, SQLite)
- [ ] Prototype Episode data schema (SQLite)
- [ ] Prototype Memory retrieval logic
