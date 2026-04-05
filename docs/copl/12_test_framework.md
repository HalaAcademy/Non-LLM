# Đặc tả Framework Kiểm thử Test của COPL
## Hệ thống Chỉ huy Soạn Nhạc Gọi Lệnh Kiểm thử Đa Chủng Loại Bộ Test (Multi-Type Test Orchestration) — Khắc phục Vấn đề Scale#5

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Hệ Phả Khảo Các Loạt Nhóm Nhánh Tests của COPL

| Thể Loại Soi Rọi Tests | Đội Xung Phong Gọi Runner chạy Còi | Khoảng Chờ (Speed) | Sứ mệnh và Trách nhiệm (Purpose) |
|---|---|---|---|
| Mã Đánh Unit Test | Test chay môi trường PC cá nhân Host Mệ Host native | Rẻ nhanh <1s | Sục cọ Đánh độc cô cầu bại Test single chuyên 1 cọng Hàm func riêng tư |
| Cọ Nhịp Bắt Lỗi Mạch Test Hợp Đồng (Contract Test) | Bộ Bóc Compiler | Tiệm cận 0ms | Tước Quyền Tra check cắm mọt lỗi Vi Sát Logic (Ngay từ ở bước Compile-time) |
| Giao Đấu Tính Tuần Hợp Integration Test | Thông qua Cổng Máy Giả Lập Simulator/QEMU | Dao động <30s | Chuyên Tét test điểm móc nối tương quan độ hòa hợp của cấu thành mô đun liên kết module interaction |
| Đưa Toàn Giáp Test Mã Máy System Test | Chạy Tích Trực Trên Bản Đồ Chíp đích Target hardware | Băng mốc <5min | Giải lệnh Đẩy Nện Test căng 100% full hệ trần system |
| Gõ Trực Châm Điện Dòng HIL Test (Phần Mềm Móc Nối Vòng Đo Hệ Hardware) | Thiết bị gõ xung nãy nhịp đo mồi Hardware-in-the-loop | Chiếm tới <10min | Buông Xích Thả Lòi Cỏ Code Lái Hệ Để Ép Chọi Thử Nhận Test múa trực diện Bằng Xung Nẩy Sóng với mạch board tín hiệu thực hardware signals |

## 2. Giao Cách Viết Khai Cáo Biện Đánh Test Vào COPL

### 2.1 Viết Các Khối Lồng Test Chỉ Đường Thực Thể Tĩnh Gắn Theo Cú Pháp Ngầm Nội (Inline Test Entities)

```copl
module services.safety {
  fn check_safety(voltage: U32, limit: U32) -> Bool {
    return voltage <= limit;
  }
  
  // Góc tạo Điểu Hình Test Thực thể (Test entity) — Ở đây là kiểu Dán chắp giấy biên chú metadata purely only (COPL thu lưới ghi sổ quản, chứ ko bấm nút dội chạy cạch cạch code run executes)
  test T-SAFETY-001 {
    title: "Overvoltage detection"
    verifies: REQ-EVCU-003a
    method: unit_test
    pass_condition: "check_safety(420001, 420000) trả về output false"
    status: pass
  }
}
```

### 2.2 Cuộn File Module Test Riêng Chống Hành Động Xưng Trận Xé Mạch Cài Đặt Mã Thực Thi (Executable Test Module)

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

## 3. Khai Cọc Dựng Tuyến Điểm Suite Bộ Tập Hợp Bảng Mạch Test Chuỗi (Test Suite Definition)

```copl
// Quy mô Lập Bảng điều binh khiển tướng cấu hình Project-level test
test_suite evcu_unit_tests {
  type: unit_test
  runner: native                    // Cho chạy lướt build nóng trên chính vòm máy của host
  timeout_per_test: 5s
  parallel: true                    // Giục máy dắt đạn đánh Đa Hướng chạy song song
  includes: [tests.safety_tests, tests.can_tests, tests.vcu_sm_tests]
  fail_fast: false                  // Cho dập búa thử càn quét chọc lỗi toàn luồng run all ngay cả khi trong đám test đang xài có tèo một số lính fail
}

test_suite evcu_integration_tests {
  type: integration_test
  runner: qemu_stm32               // Kẹp vô lòng Máy Giả Lập QEMU simulator
  timeout_per_test: 30s
  parallel: false
  depends_on: [evcu_unit_tests]    // Treo điều kiện: Bắt Buộc Vượt Luân xa qua mảng bóc tách test unit tests đầu mối cho trót mới được gọi cọc chạy tiếp tới cọc tests này
  includes: [tests.integration.*]
}

test_suite evcu_system_tests {
  type: system_test
  runner: hardware                  // Khảo thẳng Cột Gạch Chip Bo real STM32F407 board
  timeout_per_test: 120s
  depends_on: [evcu_integration_tests]
  includes: [tests.system.*]
  hardware_required: "STM32F407_EVCU_v2"
}
```

## 4. Giải Trình Tầng Lớp Kiến Trúc Cấu Kết Của Tổng Cơ Đầu Tàu Test Runner

```python
class TestOrchestrator:
    """Kéo dãn màng Đội Chạy Gọi Các Băng Nhóm Các Bộ test suites dầm dập đánh xáp theo cái Phả hệ Lớp Lên lớp trước xuống sau Cấp Dependencies Order."""
    
    def run_all(self, project: str) -> TestReport:
        suites = self.load_suites(project)
        
        # Vuốt lật Nhóm Đội Xếp Bảng Chia Hạng Dựa Trên dependency
        ordered = self.topological_sort(suites)
        
        results = {}
        for suite in ordered:
            # Gài Rà Soát chùm đội Dependencies móc xích Cú Vấp ngã Mảng Náo Động passed chưa
            for dep in suite.depends_on:
                if not results.get(dep, TestSuiteResult()).all_passed:
                    results[suite.name] = TestSuiteResult(
                        status="skipped",
                        reason=f"Đội Phụ Trợ Dependency chốt tuyến '{dep}' failed Thất Bại sập nguồn"
                    )
                    continue
            
            # Quạt Trận Kích đánh Run Bắn cọc của Suite
            result = self.run_suite(suite)
            results[suite.name] = result
            
            # Giật Còi Chặn ngắt Gãy Fast Failed Rút Cầu nếu sập ở cấp đọ cao Tương Đoạn Chốt Critical System
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
        """Thông Tốc Hạ Đèn Cấm COPL test module trượt ra mã lạch C → gọi ép Cục Biên Dịch Gcc → gõ lệnh Đánh Start run."""
        # Bước 1. Luân Hoán Lệnh COPL test module dồn ép ra file ngốn C
        c_files = self.copl_compiler.compile(suite.includes, target="c")
        
        # Bước 2. Nối Chỉ Compiler tệp C bằng Lõi build gốc Tầng hệ thông của host gcc
        binary = self.gcc.compile(c_files, output="test_binary")
        
        # Bước 3. Khều Giây Đề Phóng Chạy Và Tóm mớ Bạc Nhạc Kết Quả Rớt Output
        result = self.execute(binary, timeout=suite.timeout_per_test)
        
        return self.parse_test_output(result)
```

## 5. Tổ Hợp Đúc Hồ Sơ Đóng Sổ Test Results Reporting

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

## 6. Mẹo vặt Phím Dẫn (Hints) Auto-Gợi Ý Trổ Đường Test Phái Sinh

Đại não COPL compiler kiêu sa tự giác gõ bàn cờ phím mớm khôn Gợi Mở Missing Tests Lỗ Hổng Khoang Tối Rỗng Trắng:

```
copc test --check-coverage

Hệ xuất Kết Báo Output:
  ⚠️ Cuộc Lật Tranh Phơi Báo Gọi Hàm 'can_write' dù bệ phong dán ngực Đề bạt @contract uy danh nhưng tủi nhục trơ lì cạn mảng test bao bọc
  ⚠️ Ngáo Cờ: Chuẩn Thiết yết Requirement REQ-EVCU-002b nhởn nhơ không bị kiểm sát verified bằng bất cứ ngài test dũng mãnh nào
  ⚠️ Điểm Chết Dòng Chuyển Động Chuyển Phái Từ Park→Charging Bỏ Trống Vùng Xám Lọt Băng test soi rọi mờ mịt
  
  Mớm Bồi Suggestion (Cố Tình Đẩy Lời Quyên Nên Gõ Code Make tests bổ trợ Mới):
    - test_can_write_success
    - test_can_write_mailbox_full
    - test_park_to_charging_transition
```

## 7. Đảo Ngữ Logic Kiểm Suy Giả Lược Nhâm Bắn (Assert Macros)

```copl
// Tệp Code chắt lọt Chìm sâu Nhánh Built-in test assertions mài khố cản chuẩn test nhanh lẹ
intrinsic assert_true(condition: Bool);
intrinsic assert_false(condition: Bool);
intrinsic assert_eq<T: Eq>(expected: T, actual: T);
intrinsic assert_ne<T: Eq>(a: T, b: T);
intrinsic assert_some<T>(opt: T?);
intrinsic assert_none<T>(opt: T?);
intrinsic assert_ok<T, E>(result: Result<T, E>);
intrinsic assert_err<T, E>(result: Result<T, E>);
```
