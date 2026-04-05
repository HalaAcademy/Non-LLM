# Cortex Risk Mitigation
## Risk Matrix and Contingency Plans

> **Status**: Draft | **Last Updated**: 2026-04-03

---

## 1. Risk Matrix

| ID | Risk | Likelihood | Impact | Score | Mitigation |
|---|---|:---:|:---:|:---:|---|
| R1 | COPL grammar too complex for LL(1) | Medium | High | 🔴 | Drop to LL(k) or PEG if needed |
| R2 | Type system undecidable | Low | Critical | 🔴 | Limit generics, add inference bounds |
| R3 | C codegen produces incorrect code | Medium | Critical | 🔴 | Extensive test suite, compare with reference |
| R4 | GEAS model doesn't converge | Medium | High | 🔴 | Simplify model, more Phase 1 data |
| R5 | Training data insufficient | High | High | 🔴 | DAgger + synthetic generation |
| R6 | Catastrophic forgetting despite EWC | Medium | Medium | 🟠 | Add Progressive Neural Networks |
| R7 | Memory retrieval quality degrades | Medium | Medium | 🟠 | Hierarchical retrieval + compaction |
| R8 | Integration contracts break silently | Low | High | 🟠 | CI enforcement, never skip |
| R9 | Scope creep | High | Medium | 🟠 | Strict phase gates, MVP mindset |
| R10 | Single point of failure (key person) | Medium | High | 🟠 | Documentation-first approach |
| R11 | Performance: compilation too slow | Medium | Medium | 🟡 | Incremental compilation from day 1 |
| R12 | COPL syntax bikeshedding | High | Low | 🟡 | Freeze grammar at P1 gate |

## 2. Contingency Plans

### R1: Grammar Complexity

```
Trigger: Cannot resolve grammar ambiguity with LL(1)

Option A: Use LL(k) lookahead (k=2 or k=3)
  Pro: Simple extension, recursive descent still works
  Con: Slightly more complex parser

Option B: Use PEG (Parsing Expression Grammar)
  Pro: No ambiguity by definition
  Con: Different error recovery, left-recursion issues

Option C: Simplify syntax
  Pro: Simpler language
  Con: May lose expressiveness

Decision: Try Option A first, then C. Avoid B.
```

### R4: Model Doesn't Converge

```
Trigger: Loss doesn't decrease after 50 epochs

Option A: Reduce model size (512→256, 6→4 layers)
  → Smaller model converges faster, may be sufficient

Option B: Increase data (more DAgger rounds)
  → More expert demonstrations usually helps

Option C: Use pretrained backbone (distill from GPT-2)
  → Transfer learning from language model

Option D: Simplify to rule-based agent first
  → No neural model, pure heuristics
  → Prove system works, add learning later

Decision: Try A → B → C → D in order.
```

### R5: Insufficient Training Data

```
Trigger: < 1000 quality episodes after Phase 1

Option A: Generate synthetic tasks
  → Programmatically create COPL projects + expected solutions
  → Use template-based generation

Option B: Invite beta testers
  → 5-10 engineers use COPL normally
  → Record their sessions as expert demonstrations

Option C: Use LLM to generate demonstrations
  → GPT-4 solves tasks, human verifies
  → Only verified solutions used as training data

Decision: Start with A (cheapest), add B if A insufficient.
```

### R9: Scope Creep

```
Trigger: Phase takes >150% estimated time

Actions:
  1. Review and cut non-essential features for this phase
  2. Move "nice-to-have" to next phase
  3. Focus on quality gate requirements only
  4. If still over: extend timeline, do NOT cut quality

MVP definition:
  - COPL MVP: Lexer + Parser + Type Checker + C Codegen (no Rust/Go)
  - GEAS MVP: 3 heads model + SQLite memory + basic loop (no MAML)
  - Cortex MVP: GEAS creates module + builds + fixes type error + learns
```

## 3. Monitoring

```python
class RiskMonitor:
    """Weekly risk assessment."""
    
    def assess(self) -> list[RiskAlert]:
        alerts = []
        
        # R4: Check model convergence
        if self.training_active:
            recent_loss = self.get_recent_loss(window=10)
            if self.is_plateau(recent_loss):
                alerts.append(RiskAlert("R4", "Model convergence plateau detected"))
        
        # R9: Check phase timeline
        current_phase = self.get_current_phase()
        elapsed = current_phase.elapsed_days
        planned = current_phase.planned_days
        if elapsed > planned * 1.2:
            alerts.append(RiskAlert("R9", f"Phase {current_phase.name} at {elapsed/planned:.0%} of planned time"))
        
        # R7: Check memory retrieval quality
        precision = self.sample_retrieval_precision(n=50)
        if precision < 0.6:
            alerts.append(RiskAlert("R7", f"Memory retrieval precision: {precision:.1%}"))
        
        # R8: Check contract test status
        contract_results = self.run_contract_tests()
        if not contract_results.all_passed:
            alerts.append(RiskAlert("R8", "Contract tests failing!"))
        
        return alerts
```
