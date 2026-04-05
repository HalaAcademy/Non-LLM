# Đặc tả Tiêu Chuẩn Kiểm Thử COPL (Test Framework)
## Hệ thống Phối Hợp Đa Module (Multi-Type Test Orchestration)

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Phân Loại Cấu Trúc Các Khối Kiểm Thử của COPL

| Thể Loại Kiểm thử (Test Type) | Trình Môi trường (Runner) | Tốc độ (Speed) | Mục đích (Purpose) |
|---|---|---|---|
| Unit Test (Kiểm thử chức năng nền) | Cấp Host System (Môi trường PC gốc) | Nhanh (< 1s) | Kiểm thử cục bộ chức năng hoặc cấu trúc riêng biệt (Single function). |
| Contract Test (Kiểm thử hợp đồng) | Trình Compiler COPL | Cực nhanh (~0ms) | Phân tích tính hợp lệ tiền/hậu quyết của thuật toán tại thời điểm Compile-time. |
| Integration Test (Kiểm thử tích hợp) | Trình Mô Phỏng QEMU / Simulator | Dao động (< 30s) | Kiểm tra quá trình tương tác hoạt động qua lại trực tiếp của mô-đun. |
| System Test (Kiểm thử hệ thống toàn vẹn) | Phân cấp Target Hardware (MCU Board đích) | Chậm (< 5 phút) | Triển khai mô hình test toàn hệ thống khi hoạt động thực tế trên phần cứng. |
| HIL Test (Hardware-in-the-loop Test) | Thiết bị Kiểm giả tín hiệu môi trường gốc | Rất chậm (< 10 phút) | Xây dựng bài đo chức năng tương tác mức độ hệ quy chiếu môi trường tín hiệu nhiễu và board điện. |

## 2. Phương Pháp Khởi Tạo Khối Kiểm Thử

### 2.1 Cú pháp Test Khối Thực Thể Gắn Nội (Inline Test Entities)

```copl
module services.safety {
  fn check_safety(voltage: U32, limit: U32) -> Bool {
    return voltage <= limit;
  }
  
  // Khai báo Test entity — Đóng vai trò là metadata (Trình biên dịch ghi nhận thông tin quản lý, không chạy lệnh thực thi)
  test T-SAFETY-001 {
    title: "Overvoltage detection"
    verifies: REQ-EVCU-003a
    method: unit_test
    pass_condition: "check_safety(420001, 420000) trả về output false"
    status: pass
  }
}
```

### 2.2 Module Test Thực Thi Riêng Biệt (Executable Test Module)

```copl
module tests.safety_tests {
  @context { purpose: "Bảng chốt tập hợp file Unit tests bảo lưu độ trong sạch khối cấu trúc cho logic safety monitor" }
  @platform { profile: portable, target: c }
  
  use services.safety.{check_safety, SafetyLimits, SafetyStatus};
  
  test_fn test_overvoltage() {
    let limits = SafetyLimits { max_voltage_mv: 420000, max_current_ma: 300000, max_temp_degc: 85 };
    let result = check_safety(limits, 420001, 100000, 25);
    assert_true(result.overvoltage);
    assert_true(result.fault_active);
  }
  
  test_fn test_normal_voltage() {
    let limits = SafetyLimits { max_voltage_mv: 420000, max_current_ma: 300000, max_temp_degc: 85 };
    let result = check_safety(limits, 380000, 100000, 25);
    assert_false(result.overvoltage);
    assert_false(result.fault_active);
  }
  
  test_fn test_overcurrent() {
    let limits = SafetyLimits { max_voltage_mv: 420000, max_current_ma: 300000, max_temp_degc: 85 };
    let result = check_safety(limits, 380000, 350000, 25);
    assert_true(result.overcurrent);
    assert_true(result.fault_active);
  }
}
```

## 3. Khai Báo Bộ Tập Hợp Test (Test Suite Definition)

```copl
// Cấu hình quy mô kiểm thử cấp Dự án (Project-level test)
test_suite evcu_unit_tests {
  type: unit_test
  runner: native                    // Executable trên hệ máy PC local (Host)
  timeout_per_test: 5s
  parallel: true                    // Hỗ trợ đánh luồng Test Test đồng thời (Multi-threading)
  includes: [tests.safety_tests, tests.can_tests, tests.vcu_sm_tests]
  fail_fast: false                  // Thực thi trọn bộ test mặc dù xuất hiện các nhánh bị thất bại (Fail)
}

test_suite evcu_integration_tests {
  type: integration_test
  runner: qemu_stm32               // Gắn module trực tiếp giả lập QEMU
  timeout_per_test: 30s
  parallel: false
  depends_on: [evcu_unit_tests]    // Yêu cầu: Bắt buộc vượt qua hàng test `evcu_unit_tests` mới tiếp tục kích hoạt suite hiện thời
  includes: [tests.integration.*]
}

test_suite evcu_system_tests {
  type: system_test
  runner: hardware                  // Khảo nghiệm kiểm thử trên STM32F407 hardware board
  timeout_per_test: 120s
  depends_on: [evcu_integration_tests]
  includes: [tests.system.*]
  hardware_required: "STM32F407_EVCU_v2"
}
```

## 4. Cơ Cấu Tổ Chức Hệ Điều Phối Hệ Thống Đo Test Runner

```python
class TestOrchestrator:
    """Trình Điều phối Hệ Thống: Cấu trúc lộ trình thực thi luân chuyển tập kiểm thử thông minh dựa trên Phả hệ Phụ thuộc (Dependencies Order)."""
    
    def run_all(self, project: str) -> TestReport:
        suites = self.load_suites(project)
        
        # Sắp xếp tuyến lịch thực thi Dựa trên Dependency Order 
        ordered = self.topological_sort(suites)
        
        results = {}
        for suite in ordered:
            # Rà soát điều kiện xác nhận các chùm đội Dependencies trước đó gặp Fail hay không
            for dep in suite.depends_on:
                if not results.get(dep, TestSuiteResult()).all_passed:
                    results[suite.name] = TestSuiteResult(
                        status="skipped",
                        reason=f"Bộ Dependent báo lỗi sập nguồn ở '{dep}'"
                    )
                    continue
            
            # Khởi động Run Suite
            result = self.run_suite(suite)
            results[suite.name] = result
            
            # Cấu hình Fast Fail: Tắt chức năng build nếu tầng Critical System xảy ra củi lỗi
            if not result.all_passed and suite.type == "system_test":
                break
        
        return TestReport(results)
    
    def run_suite(self, suite: TestSuite) -> TestSuiteResult:
        match suite.runner:
            case "native":
                return self.run_native(suite)
            case "qemu_stm32":
                return self.run_qemu(suite)
            case "hardware":
                return self.run_hardware(suite)
    
    def run_native(self, suite: TestSuite) -> TestSuiteResult:
        """Thúc đẩy COPL hạ hệ test C → GCC compiler → Biên chạy tiến trình nhị phân nhấp lệnh Native Build Runtime."""
        # 1. Hạ định dạng (Lowering) Test COPL Module qua nền C System File 
        c_files = self.copl_compiler.compile(suite.includes, target="c")
        
        # 2. Compile COPL C-output test module dùng Host GCC Native Compiler
        binary = self.gcc.compile(c_files, output="test_binary")
        
        # 3. Kích chạy phân khúc Execute Data output qua bộ theo thời giới Timeout quy chiếu
        result = self.execute(binary, timeout=suite.timeout_per_test)
        
        return self.parse_test_output(result)
```

## 5. Tổ Chức Định Dạng Dữ Liệu Báo Cáo Đo Đạt (Test Results Reporting)

```json
{
  "$schema": "copl-test-report-v1",
  "project": "evcu_project",
  "run_at": "2026-04-03T10:30:00Z",
  "duration_total_ms": 4500,
  "suites": [
    {
      "name": "evcu_unit_tests",
      "type": "unit_test",
      "status": "passed",
      "tests_total": 18,
      "tests_passed": 18,
      "tests_failed": 0,
      "tests_skipped": 0,
      "duration_ms": 850,
      "details": [
        {"name": "test_overvoltage", "status": "pass", "duration_ms": 2},
        {"name": "test_normal_voltage", "status": "pass", "duration_ms": 1}
      ]
    },
    {
      "name": "evcu_integration_tests",
      "type": "integration_test",
      "status": "passed",
      "tests_total": 8,
      "tests_passed": 8,
      "duration_ms": 3200
    }
  ],
  "coverage": {
    "requirements_tested": 9,
    "requirements_total": 9,
    "coverage": 1.0
  }
}
```

## 6. Tiện Ích Đề Xuất Bổ Sung Kiểm Thử (Auto-Suggestions)

Hệ trợ lực thông minh của Trình biên dịch COPL tự rà soát và gợi ý những khoản ngách thiếu Test-cases (Test Coverage Gap):

```
copc test --check-coverage

Hệ xuất Kết Báo Output:
  ⚠️ Cảnh báo: Hàm 'can_write' bao gồm block @contract ràng buộc nghiêm ngặt nhưng không tìm thấy module test phủ lệnh này. 
  ⚠️ Lỗ hổng: Requirement REQ-EVCU-002b chưa xác định được dữ liệu Verified Validation thông qua module tests.
  ⚠️ Khoảng trống: Chuyển đổi Trạng thái (State Machine) từ `Park` → `Charging` hoàn toàn khuyết Test.
  
  Suggestion (Khuyến nghị khai báo hàm kiểm thử tự động bổ trợ mới):
    - test_can_write_success
    - test_can_write_mailbox_full
    - test_park_to_charging_transition
```

## 7. Các Phương Thức Toán Tử Asserts Tích Hợp (Assert Macros)

```copl
// Tệp Code quản lý Logic Assert Framework Test tích hợp sẵn (Built-in Assertions)
intrinsic assert_true(condition: Bool);
intrinsic assert_false(condition: Bool);
intrinsic assert_eq<T: Eq>(expected: T, actual: T);
intrinsic assert_ne<T: Eq>(a: T, b: T);
intrinsic assert_some<T>(opt: T?);
intrinsic assert_none<T>(opt: T?);
intrinsic assert_ok<T, E>(result: Result<T, E>);
intrinsic assert_err<T, E>(result: Result<T, E>);
```
