# Cortex Work Rules
## Coding Standards, Reporting, and Review Processes

> **Status**: Draft | **Last Updated**: 2026-04-03

---

## 1. Code Standards

### 1.1 COPL Compiler (Rust/Python)

```
- Language: Rust preferred for compiler, Python for tooling
- Formatting: rustfmt / black (automated in CI)
- Naming: snake_case for functions and variables, PascalCase for types
- Documentation: Every public function has docstring
- Tests: Every module has corresponding test file
- Error handling: Result/Option, no unwrap() in library code
- Max function length: 50 lines (extract if longer)
- Max file length: 500 lines (split if longer)
```

### 1.2 GEAS Agent (Python)

```
- Language: Python 3.11+
- Formatting: black + isort (automated)
- Type hints: Required for all public functions
- Naming: snake_case for functions, PascalCase for classes
- Documentation: Google-style docstrings
- Tests: pytest, minimum 80% coverage
- Dependencies: Pinned versions in requirements.txt
- Model code: PyTorch, type-annotated tensors
```

### 1.3 Documentation

```
- Format: Markdown
- Naming: NN_descriptive_name.md (e.g., 01_grammar_spec.md)
- Headers: Include version, status, last updated
- Code examples: Every specification must include at least 1 example
- Cross-references: Link to other docs using relative paths
```

## 2. Git Workflow

```
main ────────────────────────────────────────────→
  │
  ├── develop ──────────────────────────────────→
  │     │
  │     ├── feature/copl-parser ──→ merge ──→
  │     ├── feature/copl-type-checker ──→ merge ──→
  │     ├── feature/geas-memory ──→ merge ──→
  │     └── fix/parser-recovery ──→ merge ──→
  │
  ├── release/v0.1 ──→ tag ──→
  └── release/v0.2 ──→ tag ──→
```

### Branch Naming

```
feature/copl-{component}     Feature development
feature/geas-{component}     Feature development
fix/{short-description}      Bug fixes
docs/{area}                  Documentation updates
test/{area}                  Test additions
```

### Commit Messages

```
Format: [{component}] {verb} {description}

Examples:
  [copl-parser] Add state machine grammar rules
  [copl-types] Fix bidirectional inference for closures
  [geas-memory] Implement EWC regularization
  [contracts] Add SIR query contract validation tests
  [docs] Update lowering spec with enum codegen
```

## 3. Review Process

### Pull Request Template

```markdown
## Summary
Brief description of changes.

## Type
- [ ] Feature
- [ ] Bug fix
- [ ] Documentation
- [ ] Test
- [ ] Refactor

## Related
- Fixes #{issue}
- Related to #{issue}
- Weakness addressed: {C1/G3/X5/...}

## Testing
- [ ] Unit tests added/updated
- [ ] Contract tests pass
- [ ] Manual testing done

## Checklist
- [ ] Code formatted (rustfmt/black)
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Breaking changes documented
```

### Review Criteria

```
Required for merge:
  □ At least 1 approval
  □ CI passes (all tests green)
  □ Contract tests pass
  □ No unresolved comments
  □ Documentation updated if API changed
```

## 4. Testing Requirements

```
Every PR must include:
  - Unit tests for new code
  - Contract tests if interface changes
  - Integration test for cross-module changes

Coverage requirements:
  - Parser: ≥ 90% line coverage
  - Type checker: ≥ 85% line coverage
  - Codegen: ≥ 80% line coverage
  - GEAS modules: ≥ 80% line coverage
  - Overall: ≥ 85%
```

## 5. Communication

### Daily Standup (15 min)

```
Each person reports:
  1. What I did yesterday
  2. What I'll do today
  3. Blockers (if any)
```

### Weekly Review (1 hour)

```
Agenda:
  1. Demo of completed work (10 min per person)
  2. Review metrics dashboard (10 min)
  3. Discuss blockers and risks (15 min)
  4. Plan next week (15 min)
```
