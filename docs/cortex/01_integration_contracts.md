# Cortex Integration Contracts
## 5 Formal Interface Contracts — Fixes X1-X5

> **Status**: Draft | **Last Updated**: 2026-04-03

---

## 1. Why Contracts

COPL develops before GEAS. Contracts guarantee they will integrate:

```
COPL (provider) ──── Contracts ──── GEAS (consumer)
                     5 interfaces
                     validated by Mock Agent in CI
```

## 2. Contract #1: SIR Query Interface

**Provider**: COPL Compiler | **Consumer**: GEAS World Model Builder

```python
class SIRQueryContract:
    """GEAS World Model calls these methods. COPL must implement."""
    
    def get_workspace(self) -> SIRWorkspace:
        """Return full SIR representation."""
    
    def get_module(self, name: str) -> SIRModule:
        """Return SIR for a single module."""
    
    def get_modules_by_status(self, status: str) -> list[SIRModule]:
        """All modules with given status."""
    
    def get_dependencies(self, module: str) -> list[DependencyEdge]:
        """Direct dependencies of a module."""
    
    def get_trace_coverage(self) -> TraceMatrix:
        """Full trace matrix with coverage percentages."""
    
    def get_unimplemented_requirements(self) -> list[SIRRequirement]:
        """Requirements without code trace."""
    
    def get_untested_requirements(self) -> list[SIRRequirement]:
        """Requirements without test coverage."""
    
    def get_module_risk(self, module: str) -> float:
        """Risk score 0.0-1.0."""
    
    def search(self, query: str) -> list[SIRModule]:
        """Full-text search across module names and purposes."""

# Validation test
def test_sir_query_contract(compiler, test_project):
    result = compiler.compile(test_project)
    query = SIRQueryContract(result.sir)
    
    ws = query.get_workspace()
    assert ws.name is not None
    assert ws.computed.total_modules > 0
    
    modules = query.get_modules_by_status("stable")
    for m in modules:
        assert m.context.purpose is not None
        assert m.context.status == "stable"
        assert m.computed.risk_score >= 0.0
    
    coverage = query.get_trace_coverage()
    assert 0.0 <= coverage.computed.overall_coverage <= 1.0
```

## 3. Contract #2: Diagnostic Output Format

**Provider**: COPL Compiler | **Consumer**: GEAS Diagnoser

```python
@dataclass
class DiagnosticContract:
    """Every diagnostic MUST have these fields. No exceptions."""
    
    category: str      # "syntax"|"semantic"|"profile"|"lowering"|"architecture"
    severity: str      # "error"|"warning"|"info"
    code: str          # Stable code: "E001", "W023"
    message: str       # Human-readable description
    file: str          # File path
    line: int          # Line number (1-indexed)
    column: int        # Column number (1-indexed)
    suggested_fix: str # Optional hint for fixing
    related: list[str] # Related entities (REQ-xxx, module.name)

# Validation test
def test_diagnostic_contract(compiler):
    result = compiler.compile("test_data/errors/type_mismatch.copl")
    assert not result.success
    
    for diag in result.diagnostics:
        assert diag.category in ["syntax", "semantic", "profile", "lowering", "architecture"]
        assert diag.severity in ["error", "warning", "info"]
        assert diag.code.startswith(("E", "W"))
        assert len(diag.code) >= 4
        assert len(diag.message) > 0
        assert diag.line > 0
        assert diag.column > 0
```

## 4. Contract #3: Artifact Output Format

**Provider**: COPL Artifact Engine | **Consumer**: GEAS Memory Manager

```python
class ArtifactContract:
    """Artifact schemas GEAS depends on. Changes require version bump."""
    
    SUMMARY_CARD_REQUIRED_FIELDS = [
        "module_name", "purpose", "owner", "status", "profile",
        "metrics.function_count", "metrics.loc",
        "quality.trace_coverage", "quality.risk_score",
        "effects", "dependencies", "trace"
    ]
    
    DEP_GRAPH_REQUIRED_FIELDS = [
        "nodes[].id", "nodes[].type", "nodes[].status",
        "edges[].from", "edges[].to", "edges[].type"
    ]
    
    TRACE_MATRIX_REQUIRED_FIELDS = [
        "entries[].requirement_id", "entries[].implemented_by",
        "entries[].tested_by", "entries[].coverage",
        "summary.overall_coverage"
    ]

# Validation test
def test_artifact_contract(compiler, test_project):
    result = compiler.compile(test_project)
    artifacts = result.artifacts
    
    for card in artifacts.summary_cards:
        for field in ArtifactContract.SUMMARY_CARD_REQUIRED_FIELDS:
            assert get_nested(card, field) is not None, f"Missing field: {field}"
    
    graph = artifacts.dependency_graph
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) >= 0
    
    matrix = artifacts.trace_matrix
    assert 0.0 <= matrix["summary"]["overall_coverage"] <= 1.0
```

## 5. Contract #4: COPL Action Interface

**Provider**: COPL CLI/API | **Consumer**: GEAS Action Executor

```python
class ActionContract:
    """GEAS executor sends these commands. COPL must accept them."""
    
    def create_module(self, name: str, content: str) -> ActionResult:
        """Create new .copl file."""
    
    def modify_module(self, name: str, patch: str) -> ActionResult:
        """Modify existing .copl file."""
    
    def delete_module(self, name: str) -> ActionResult:
        """Delete .copl file."""
    
    def build(self, target: str = "c") -> BuildResult:
        """Full build: parse → check → codegen."""
    
    def check(self) -> CheckResult:
        """Check only: parse → type check → effect check. No codegen."""
    
    def run_tests(self, suite: str = "all") -> TestResult:
        """Run test suite."""
    
    def emit_artifacts(self) -> ArtifactResult:
        """Generate AI bundle."""
    
    def get_sir(self) -> SIRWorkspace:
        """Get current SIR."""

@dataclass
class BuildResult:
    success: bool
    diagnostics: list[Diagnostic]
    output_files: list[str]
    sir: SIRWorkspace
    artifacts: ArtifactBundle
    duration_ms: int

# Validation test
def test_action_contract():
    api = ActionContract(workspace="test/")
    
    r1 = api.create_module("test.hello", 'module test.hello {}')
    assert r1.success
    
    r2 = api.build(target="c")
    assert isinstance(r2.success, bool)
    assert isinstance(r2.diagnostics, list)
    assert r2.sir is not None
    
    r3 = api.check()
    assert isinstance(r3.success, bool)
```

## 6. Contract #5: Episode Data Schema

**Provider**: COPL compile results | **Consumer**: GEAS training pipeline

```python
@dataclass
class EpisodeSchemaContract:
    """Schema for training episodes. Must be extractable from compile results."""
    
    # Before action
    state_modules: int
    state_functions: int  
    state_errors: int
    state_trace_coverage: float
    state_build_status: str
    
    # Action taken
    action_type: str
    action_args: dict
    
    # After action
    outcome_success: bool
    outcome_class: str
    new_errors: int
    resolved_errors: int
    new_trace_coverage: float

# Validation test
def test_episode_schema(compiler, test_project):
    sir_before = compiler.get_sir()
    state_before = extract_state(sir_before)
    
    compiler.create_module("test.new_module", MODULE_CONTENT)
    result = compiler.build()
    sir_after = compiler.get_sir()
    
    state_after = extract_state(sir_after)
    
    episode = EpisodeSchemaContract(
        state_modules=state_before.module_count,
        state_functions=state_before.function_count,
        state_errors=state_before.error_count,
        state_trace_coverage=state_before.trace_coverage,
        state_build_status=state_before.build_status,
        action_type="create_module",
        action_args={"name": "test.new_module"},
        outcome_success=result.success,
        outcome_class="success" if result.success else "compile_error",
        new_errors=max(0, state_after.error_count - state_before.error_count),
        resolved_errors=max(0, state_before.error_count - state_after.error_count),
        new_trace_coverage=state_after.trace_coverage
    )
    
    # Must be JSON serializable
    json_str = json.dumps(asdict(episode))
    roundtrip = EpisodeSchemaContract(**json.loads(json_str))
    assert roundtrip == episode
```

## 7. CI Integration

```yaml
# .github/workflows/contract_validation.yml
name: GEAS Contract Validation
on: [push, pull_request]

jobs:
  contracts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build COPL compiler
        run: make copc
      - name: Run Contract Tests
        run: |
          pytest tests/contracts/test_sir_query.py
          pytest tests/contracts/test_diagnostics.py
          pytest tests/contracts/test_artifacts.py
          pytest tests/contracts/test_actions.py
          pytest tests/contracts/test_episode.py
      - name: Run Mock GEAS Agent
        run: pytest tests/contracts/test_mock_agent.py
      - name: Fail on contract break
        if: failure()
        run: echo "🔴 GEAS CONTRACTS BROKEN — FIX BEFORE MERGE"
```
