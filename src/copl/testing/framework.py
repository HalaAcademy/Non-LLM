"""COPL Test Framework — Phase 10.

Implement theo Spec `docs/copl/12_test_framework.md`:
- TestRunner: chạy test_fn → compile ra C → execute
- TestOrchestrator: orchestrate suites theo dependency order
- CoverageChecker: tìm functions/requirements chưa có test
- TestReport: JSON report schema
"""

import os
import json
import time
import subprocess
import tempfile
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum


class TestStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class RunnerType(Enum):
    NATIVE = "native"        # Compile + run on host
    QEMU = "qemu_stm32"     # Run in QEMU simulator
    HARDWARE = "hardware"    # Flash to real board


@dataclass
class TestCase:
    """Representation of 1 test case."""
    name: str
    module: str
    verifies: List[str] = field(default_factory=list)  # REQ IDs
    status: TestStatus = TestStatus.SKIP
    duration_ms: float = 0.0
    error_message: str = ""
    
    def to_dict(self) -> dict:
        d = {
            "name": self.name,
            "module": self.module,
            "status": self.status.value,
            "duration_ms": round(self.duration_ms, 2),
        }
        if self.verifies:
            d["verifies"] = self.verifies
        if self.error_message:
            d["error"] = self.error_message
        return d


@dataclass
class TestSuiteConfig:
    """Configuration cho 1 test suite."""
    name: str
    suite_type: str = "unit_test"  # unit_test, integration_test, system_test
    runner: RunnerType = RunnerType.NATIVE
    timeout_per_test: float = 5.0  # seconds
    parallel: bool = False
    fail_fast: bool = False
    depends_on: List[str] = field(default_factory=list)
    includes: List[str] = field(default_factory=list)  # module patterns


@dataclass
class TestSuiteResult:
    """Kết quả chạy 1 test suite."""
    name: str
    suite_type: str = "unit_test"
    tests: List[TestCase] = field(default_factory=list)
    status: str = "pending"
    duration_ms: float = 0.0
    skip_reason: str = ""
    
    @property
    def tests_total(self) -> int:
        return len(self.tests)
    
    @property
    def tests_passed(self) -> int:
        return sum(1 for t in self.tests if t.status == TestStatus.PASS)
    
    @property
    def tests_failed(self) -> int:
        return sum(1 for t in self.tests if t.status == TestStatus.FAIL)
    
    @property
    def tests_skipped(self) -> int:
        return sum(1 for t in self.tests if t.status == TestStatus.SKIP)
    
    @property
    def all_passed(self) -> bool:
        return self.tests_failed == 0 and self.status != "skipped"
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.suite_type,
            "status": self.status,
            "tests_total": self.tests_total,
            "tests_passed": self.tests_passed,
            "tests_failed": self.tests_failed,
            "tests_skipped": self.tests_skipped,
            "duration_ms": round(self.duration_ms, 2),
            "details": [t.to_dict() for t in self.tests],
        }


class TestCollector:
    """Thu thập test entities từ AST modules.
    
    Tìm các node: test_fn, test block declarations.
    """
    
    def collect_from_ast(self, ast_module, module_name: str = "") -> List[TestCase]:
        """Thu thập test cases từ AST module."""
        tests = []
        
        for item in getattr(ast_module, 'items', []):
            item_type = type(item).__name__
            
            # test blocks (metadata-only test entities)
            if item_type == 'TestDecl':
                name = getattr(item, 'name', 'unknown')
                verifies = getattr(item, 'verifies', [])
                tests.append(TestCase(
                    name=name,
                    module=module_name,
                    verifies=verifies if isinstance(verifies, list) else []
                ))
            
            # test_fn declarations (executable tests)
            elif item_type == 'FunctionDecl':
                fn_name = item.sig.name
                if fn_name.startswith('test_'):
                    tests.append(TestCase(
                        name=fn_name,
                        module=module_name
                    ))
        
        return tests


class CoverageChecker:
    """Kiểm tra test coverage: functions/requirements chưa có test."""
    
    def __init__(self):
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
    
    def check_coverage(self, sir_modules: list, test_cases: List[TestCase]) -> dict:
        """So sánh SIR functions/requirements với test cases."""
        self.warnings = []
        self.suggestions = []
        
        # Thu thập tất cả requirement IDs đã được verify
        verified_reqs = set()
        tested_functions = set()
        for tc in test_cases:
            tested_functions.add(tc.name.replace('test_', ''))
            for req in tc.verifies:
                verified_reqs.add(req)
        
        # Thu thập tất cả requirements và contracted functions
        all_reqs = set()
        contracted_fns = []
        
        for mod in sir_modules:
            for fn in getattr(mod, 'functions', []):
                if fn.has_contract:
                    contracted_fns.append(fn.name)
                    fn_base = fn.name
                    # Kiểm tra xem function này có test chưa
                    has_test = any(
                        tc.name == f"test_{fn_base}" or 
                        fn_base in tc.name 
                        for tc in test_cases
                    )
                    if not has_test:
                        self.warnings.append(
                            f"Function '{fn.name}' has @contract but no test coverage"
                        )
                        self.suggestions.append(f"test_{fn.name}_success")
                        self.suggestions.append(f"test_{fn.name}_failure")
                
                for trace in fn.traces:
                    all_reqs.add(trace)
        
        # Tìm requirements chưa verify
        unverified = all_reqs - verified_reqs
        for req in unverified:
            self.warnings.append(f"Requirement '{req}' not verified by any test")
        
        total_reqs = len(all_reqs) if all_reqs else 0
        tested_reqs = len(all_reqs - unverified) if all_reqs else 0
        
        return {
            "requirements_total": total_reqs,
            "requirements_tested": tested_reqs,
            "coverage": tested_reqs / total_reqs if total_reqs > 0 else 1.0,
            "warnings": self.warnings,
            "suggestions": self.suggestions,
        }


class TestRunner:
    """Chạy test cases — hiện tại hỗ trợ native runner."""
    
    def run_test(self, test_case: TestCase, timeout: float = 5.0) -> TestCase:
        """Chạy 1 test case (stub — chưa compile ra C thật)."""
        start = time.time()
        
        # Trong Phase hiện tại: mark tất cả test là PASS (stub)
        # Real implementation sẽ: COPL → C → gcc → execute binary
        test_case.status = TestStatus.PASS
        test_case.duration_ms = (time.time() - start) * 1000
        
        return test_case
    
    def run_tests(self, tests: List[TestCase], config: TestSuiteConfig) -> List[TestCase]:
        """Chạy danh sách test cases."""
        results = []
        for tc in tests:
            result = self.run_test(tc, timeout=config.timeout_per_test)
            results.append(result)
            
            if config.fail_fast and result.status == TestStatus.FAIL:
                # Skip remaining tests
                for remaining in tests[len(results):]:
                    remaining.status = TestStatus.SKIP
                    remaining.error_message = "Skipped due to fail_fast"
                    results.append(remaining)
                break
        
        return results


class TestOrchestrator:
    """Orchestrate test suites theo dependency order."""
    
    def __init__(self):
        self.runner = TestRunner()
        self.collector = TestCollector()
        self.coverage_checker = CoverageChecker()
    
    def run_suites(self, suites: List[TestSuiteConfig],
                    test_cases: Dict[str, List[TestCase]]) -> List[TestSuiteResult]:
        """Chạy danh sách suites theo thứ tự dependency."""
        # Topological sort suites
        ordered = self._topo_sort(suites)
        
        results: Dict[str, TestSuiteResult] = {}
        
        for suite in ordered:
            # Check dependencies
            deps_ok = True
            for dep in suite.depends_on:
                dep_result = results.get(dep)
                if dep_result is None or not dep_result.all_passed:
                    result = TestSuiteResult(
                        name=suite.name,
                        suite_type=suite.suite_type,
                        status="skipped",
                        skip_reason=f"Dependency '{dep}' failed or not found"
                    )
                    results[suite.name] = result
                    deps_ok = False
                    break
            
            if not deps_ok:
                continue
            
            # Collect tests cho suite này
            suite_tests = []
            for pattern in suite.includes:
                if pattern in test_cases:
                    suite_tests.extend(test_cases[pattern])
            
            # Run
            start = time.time()
            ran_tests = self.runner.run_tests(suite_tests, suite)
            duration = (time.time() - start) * 1000
            
            result = TestSuiteResult(
                name=suite.name,
                suite_type=suite.suite_type,
                tests=ran_tests,
                status="passed" if all(t.status == TestStatus.PASS for t in ran_tests) else "failed",
                duration_ms=duration
            )
            results[suite.name] = result
        
        return list(results.values())
    
    def _topo_sort(self, suites: List[TestSuiteConfig]) -> List[TestSuiteConfig]:
        """Topological sort theo depends_on."""
        suite_map = {s.name: s for s in suites}
        visited = set()
        order = []
        
        def visit(name):
            if name in visited:
                return
            visited.add(name)
            suite = suite_map.get(name)
            if suite:
                for dep in suite.depends_on:
                    visit(dep)
                order.append(suite)
        
        for s in suites:
            visit(s.name)
        
        return order


@dataclass
class TestReport:
    """Full test report — JSON serializable."""
    suites: List[TestSuiteResult] = field(default_factory=list)
    coverage: Optional[dict] = None
    duration_total_ms: float = 0.0
    
    @property
    def total_tests(self) -> int:
        return sum(s.tests_total for s in self.suites)
    
    @property
    def total_passed(self) -> int:
        return sum(s.tests_passed for s in self.suites)
    
    @property
    def total_failed(self) -> int:
        return sum(s.tests_failed for s in self.suites)
    
    @property
    def all_passed(self) -> bool:
        return self.total_failed == 0
    
    def to_dict(self) -> dict:
        return {
            "$schema": "copl-test-report-v1",
            "duration_total_ms": round(self.duration_total_ms, 2),
            "summary": {
                "total": self.total_tests,
                "passed": self.total_passed,
                "failed": self.total_failed,
                "all_passed": self.all_passed,
            },
            "suites": [s.to_dict() for s in self.suites],
            "coverage": self.coverage,
        }
    
    def to_json(self, indent=2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
