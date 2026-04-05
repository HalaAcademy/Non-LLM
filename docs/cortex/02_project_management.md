# Cortex Project Management
## Milestones, Quality Gates, and Progress Tracking

> **Status**: Draft | **Last Updated**: 2026-04-03

---

## 1. Project Phases

| Phase | Focus | Duration | Exit Criteria |
|---|---|---|---|
| P1 | COPL Grammar + Parser | 4 weeks | Parser passes 100% grammar tests |
| P2 | COPL Type + Effect + SIR | 4 weeks | Type checker + 3 test projects pass |
| P3 | COPL Codegen + Artifacts | 4 weeks | C code compiles with gcc |
| P4 | GEAS Core Model + Memory | 4 weeks | Model trains, memory CRUD works |
| P5 | Integration | 4 weeks | Mock agent runs full EVCU demo |
| P6 | Training + Evaluation | 8 weeks | TSR ≥ 50% on COPL-Bench-20 |
| P7 | Polish + Release | 4 weeks | All docs, benchmarks, packaging |

## 2. Quality Gates

Each phase must pass quality gate before next phase begins:

### P1 Gate: Grammar Lock
```
□ All 152 EBNF productions implemented in parser
□ Parser test suite: 200+ test cases, 100% pass
□ Lexer handles all token types including COPL-specific
□ Error recovery: parser continues after syntax errors
□ Parse 3 example projects without crash
```

### P2 Gate: Semantic Stability
```
□ Type checker: all typing rules from 02_type_system.md
□ Effect checker: 9 effects × 5 profiles matrix enforced
□ SIR builder: output matches 04_sir_schema.md
□ Integration contracts: Contract #1 (SIR Query) passes
□ 3 test projects type-check and effect-check clean
```

### P3 Gate: End-to-End Compile
```
□ C codegen: all type mappings from 07_lowering_spec.md
□ State machine lowering: transition table codegen
□ Contract lowering: pre/post checks in debug mode
□ Generated C compiles with arm-none-eabi-gcc -Wall -Werror
□ Artifact engine: summary cards + trace matrix generated
□ Integration contracts: #2, #3, #4 pass
```

### P4 Gate: GEAS Foundation
```
□ Core model: forward pass works, 3 heads produce output
□ Memory system: SQLite CRUD for episodes + lessons
□ Memory retrieval: returns relevant lessons (manual check)
□ Message protocol: 15 message types serializable
□ Data pipeline: episode recording and storage works
□ Integration contract: #5 (Episode Schema) passes
```

### P5 Gate: Integration
```
□ GEAS creates COPL module via Action Interface
□ GEAS reads compiler diagnostics correctly
□ GEAS reads SIR and builds world model
□ GEAS reads artifacts and populates memory
□ Full loop: write → build → diagnose → fix works
□ Mock GEAS agent completes 3 Level-1 benchmark tasks
```

### P6 Gate: Training Complete
```
□ Phase 1-3 training complete (imitation → outcome → diagnosis)
□ TSR ≥ 50% on COPL-Bench-20
□ Action accuracy ≥ 70%
□ Diagnosis accuracy ≥ 60%
□ Learning curve shows improvement across projects
□ EWC prevents catastrophic forgetting (test with 3 sequential projects)
```

## 3. Progress Tracking

### 3.1 Weekly Status Report Template

```markdown
# Week N Status Report

## Summary
- Phase: P{n}
- Progress: {pct}%
- On Track: Yes/No/At Risk

## Completed This Week
- [x] Item 1
- [x] Item 2

## In Progress
- [/] Item 3 (50%)
- [/] Item 4 (20%)

## Blocked
- [ ] Item 5 — blocked by: {reason}

## Metrics
- Tests passing: {n}/{total}
- Contract tests: {pass}/{total}
- Code coverage: {pct}%

## Risks
- Risk 1: {description} — Mitigation: {action}

## Next Week Plan
- [ ] Item 6
- [ ] Item 7
```

### 3.2 Automated Metrics Dashboard

```python
class ProjectDashboard:
    def generate(self) -> DashboardData:
        return DashboardData(
            # Build health
            parser_tests=run_tests("tests/parser/"),
            type_checker_tests=run_tests("tests/types/"),
            codegen_tests=run_tests("tests/codegen/"),
            contract_tests=run_tests("tests/contracts/"),
            
            # Code metrics
            loc_copl_compiler=count_loc("src/copc/"),
            loc_geas_agent=count_loc("src/geas/"),
            loc_tests=count_loc("tests/"),
            test_coverage=measure_coverage(),
            
            # Quality
            open_issues=count_issues(status="open"),
            lint_warnings=run_linter(),
        )
```

## 4. Resource Allocation

```
COPL Team (Months 1-4):
  1 Lead: Language design + grammar
  1 Dev:  Parser + type checker
  1 Dev:  Codegen + lowering
  0.5 Dev: Tests + CI

GEAS Team (Months 1-4): Design Only
  1 Lead: Architecture + specifications
  0.5 Dev: Memory system prototype
  0.5 Dev: Data collection tooling

Integration (Months 5+):
  Full team converges
```
