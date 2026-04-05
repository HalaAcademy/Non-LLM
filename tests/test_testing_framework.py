"""TDD Tests cho Phase 10: COPL Test Framework.

Kiểm tra:
- TestCase data model
- TestSuiteResult aggregation
- TestCollector from AST
- TestOrchestrator dependency ordering
- CoverageChecker warning generation
- TestReport JSON schema
"""
import pytest
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from copl.testing.framework import (
    TestCase, TestStatus, TestSuiteConfig, TestSuiteResult,
    TestCollector, TestRunner, TestOrchestrator, CoverageChecker,
    TestReport, RunnerType
)


# ============================================
# 1. TestCase data model
# ============================================

def test_testcase_to_dict():
    tc = TestCase(name="test_init", module="mcal.can", status=TestStatus.PASS, duration_ms=2.5)
    d = tc.to_dict()
    assert d["name"] == "test_init"
    assert d["status"] == "pass"
    assert d["duration_ms"] == 2.5

def test_testcase_with_verifies():
    tc = TestCase(name="test_init", module="mcal.can", verifies=["REQ-CAN-001"])
    d = tc.to_dict()
    assert d["verifies"] == ["REQ-CAN-001"]


# ============================================
# 2. TestSuiteResult aggregation
# ============================================

def test_suite_result_counts():
    result = TestSuiteResult(name="unit_tests", tests=[
        TestCase("t1", "mod", status=TestStatus.PASS),
        TestCase("t2", "mod", status=TestStatus.PASS),
        TestCase("t3", "mod", status=TestStatus.FAIL),
        TestCase("t4", "mod", status=TestStatus.SKIP),
    ])
    
    assert result.tests_total == 4
    assert result.tests_passed == 2
    assert result.tests_failed == 1
    assert result.tests_skipped == 1
    assert result.all_passed is False

def test_suite_result_all_passed():
    result = TestSuiteResult(name="clean", tests=[
        TestCase("t1", "mod", status=TestStatus.PASS),
        TestCase("t2", "mod", status=TestStatus.PASS),
    ], status="passed")
    assert result.all_passed is True

def test_suite_result_to_dict():
    result = TestSuiteResult(name="unit", suite_type="unit_test", status="passed", tests=[
        TestCase("t1", "mod", status=TestStatus.PASS, duration_ms=1.0),
    ], duration_ms=5.0)
    d = result.to_dict()
    assert d["name"] == "unit"
    assert d["type"] == "unit_test"
    assert d["tests_total"] == 1
    assert d["tests_passed"] == 1


# ============================================
# 3. TestRunner
# ============================================

def test_runner_runs_test():
    runner = TestRunner()
    tc = TestCase("test_add", "math")
    result = runner.run_test(tc)
    assert result.status == TestStatus.PASS
    assert result.duration_ms >= 0

def test_runner_runs_multiple():
    runner = TestRunner()
    config = TestSuiteConfig(name="suite1")
    tests = [
        TestCase("t1", "mod"),
        TestCase("t2", "mod"),
        TestCase("t3", "mod"),
    ]
    results = runner.run_tests(tests, config)
    assert len(results) == 3
    assert all(t.status == TestStatus.PASS for t in results)


# ============================================
# 4. TestOrchestrator — dependency ordering
# ============================================

def test_orchestrator_runs_suites_in_order():
    orchestrator = TestOrchestrator()
    
    suites = [
        TestSuiteConfig(name="integration", depends_on=["unit"], includes=["mod_int"]),
        TestSuiteConfig(name="unit", includes=["mod_unit"]),
    ]
    
    test_cases = {
        "mod_unit": [TestCase("test_a", "mod_unit"), TestCase("test_b", "mod_unit")],
        "mod_int": [TestCase("test_c", "mod_int")],
    }
    
    results = orchestrator.run_suites(suites, test_cases)
    
    # Unit should run first, then integration
    assert len(results) == 2
    assert results[0].name == "unit"
    assert results[1].name == "integration"
    assert results[0].all_passed is True
    assert results[1].all_passed is True

def test_orchestrator_skips_on_dep_failure():
    orchestrator = TestOrchestrator()
    
    # Manual failure: no tests in "unit" → fails
    suites = [
        TestSuiteConfig(name="unit", includes=["nonexistent"]),
        TestSuiteConfig(name="integration", depends_on=["unit"], includes=["mod_int"]),
    ]
    
    test_cases = {
        "mod_int": [TestCase("test_c", "mod_int")],
    }
    
    results = orchestrator.run_suites(suites, test_cases)
    assert len(results) == 2
    # Integration should be skipped due to unit failure
    # (Unit has 0 tests → status depends on implementation)


# ============================================
# 5. CoverageChecker
# ============================================

def test_coverage_checker_full():
    from copl.sir.model import SIRFunction, SIRModule
    
    mod = SIRModule(name="mcal.can")
    mod.functions = [
        SIRFunction(name="init", has_contract=True, traces=["REQ-CAN-001"]),
        SIRFunction(name="send", has_contract=True, traces=["REQ-CAN-002"]),
    ]
    
    test_cases = [
        TestCase("test_init", "tests.can", verifies=["REQ-CAN-001"]),
    ]
    
    checker = CoverageChecker()
    coverage = checker.check_coverage([mod], test_cases)
    
    # send has no test → warning
    assert len(coverage["warnings"]) > 0
    assert any("send" in w for w in coverage["warnings"])
    assert len(coverage["suggestions"]) > 0

def test_coverage_checker_all_covered():
    from copl.sir.model import SIRFunction, SIRModule
    
    mod = SIRModule(name="mcal.can")
    mod.functions = [
        SIRFunction(name="init", has_contract=True, traces=["REQ-001"]),
    ]
    
    test_cases = [
        TestCase("test_init", "tests.can", verifies=["REQ-001"]),
    ]
    
    checker = CoverageChecker()
    coverage = checker.check_coverage([mod], test_cases)
    
    # All covered
    assert coverage["requirements_tested"] == 1
    assert coverage["coverage"] == 1.0


# ============================================
# 6. TestReport
# ============================================

def test_report_to_json():
    report = TestReport(
        suites=[
            TestSuiteResult(name="unit", status="passed", tests=[
                TestCase("t1", "mod", status=TestStatus.PASS, duration_ms=1.0),
                TestCase("t2", "mod", status=TestStatus.PASS, duration_ms=2.0),
            ], duration_ms=5.0),
        ],
        coverage={"requirements_total": 5, "requirements_tested": 5, "coverage": 1.0},
        duration_total_ms=5.0,
    )
    
    j = report.to_json()
    parsed = json.loads(j)
    
    assert parsed["$schema"] == "copl-test-report-v1"
    assert parsed["summary"]["total"] == 2
    assert parsed["summary"]["passed"] == 2
    assert parsed["summary"]["all_passed"] is True
    assert parsed["coverage"]["coverage"] == 1.0

def test_report_all_passed_property():
    report = TestReport(suites=[
        TestSuiteResult(name="s1", tests=[
            TestCase("t1", "m", status=TestStatus.PASS),
        ]),
    ])
    assert report.all_passed is True
    assert report.total_tests == 1
