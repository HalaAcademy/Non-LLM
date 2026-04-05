# Đặc tả Artifact Engine của COPL
## Động cơ Phân xuất và Quản trị Tài sản Thông tin Dự án

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Các Thể loại Artifact (Thông tin Phái sinh)

| Kiểu Artifact | Định dạng | Người dùng mục tiêu | Mục đích áp dụng |
|---|---|---|---|
| Bảng tóm tắt (Summary Card) | JSON | AI Agent, Dashboard | Tính toán và hiển thị thông tin rút gọn cho từng module |
| Sơ đồ Phụ thuộc (Dependency Graph) | JSON | AI Agent, Visualizer | Biểu diễn mối quan hệ ràng buộc giữa các module |
| Ma trận Dấu vết (Trace Matrix) | JSON | AI Agent, Reports | Truy xuất liên kết: Requirement → Code → Test coverage |
| Tình trạng Công việc (Workitem Status) | JSON | Dashboard, PM Tools | Theo dõi tiến độ cập nhật mã nguồn dự án |
| Báo cáo Rủi ro (Risk Report) | JSON/MD | Team Lead, AI Agent | Đánh giá và báo cáo mức độ rủi ro hệ thống |
| Báo cáo Kiến trúc (Architecture Report) | Markdown | Developer | Cung cấp tài liệu mô tả kết cấu kiến trúc dự án |
| Gói Kiến thức AI (AI Bundle) | Thư mục | AI Agent | Tổng hợp toàn bộ dữ liệu cần thiết để AI phân tích dự án |

## 2. Bố cục Mẫu cho Bảng tóm tắt Module (Summary Card Schema)

```json
{
  "$schema": "copl-summary-card-v1",
  "module_name": "mcal.stm32f407.can",
  "purpose": "Hạ tầng lõi điều khiển CAN cho vi điều khiển STM32F407",
  "owner": "team.mcal",
  "status": "stable",
  "safety_class": "QM",
  "profile": "embedded",
  "targets": ["c"],
  "memory_mode": "static",
  
  "metrics": {
    "function_count": 6,
    "struct_count": 3,
    "enum_count": 2,
    "loc": 180,
    "complexity": 12.5
  },
  
  "quality": {
    "trace_coverage": 1.0,
    "test_count": 4,
    "contract_count": 3,
    "risk_score": 0.1,
    "known_debts": ["Chỉ hỗ trợ CAN1, chưa triển khai mã nguồn cho CAN2"],
    "unresolved_items": []
  },
  
  "effects": ["register", "interrupt"],
  
  "dependencies": {
    "imports_from": ["types.can_types"],
    "imported_by": ["bsw.can_interface", "bsw.pdu_router"]
  },
  
  "trace": {
    "implements": ["CanDriver"],
    "requirements": ["REQ-EVCU-002", "REQ-EVCU-006"],
    "decisions": ["D-EVCU-001"],
    "tests": ["T-CAN-001", "T-CAN-002", "T-CAN-003", "T-CAN-004"]
  },
  
  "generated_at": "2026-04-03T10:00:00Z",
  "compiler_version": "copc-0.1.0"
}
```

## 3. Lược Đồ Phụ Thuộc (Dependency Graph Schema)

```json
{
  "$schema": "copl-dependency-graph-v1",
  "nodes": [
    {"id": "mcal.can", "type": "module", "layer": "mcal", "status": "stable", "risk": 0.1},
    {"id": "bsw.canif", "type": "module", "layer": "bsw", "status": "stable", "risk": 0.15},
    {"id": "services.vcu", "type": "module", "layer": "services", "status": "in_progress", "risk": 0.4}
  ],
  "edges": [
    {"from": "bsw.canif", "to": "mcal.can", "type": "imports"},
    {"from": "services.vcu", "to": "bsw.canif", "type": "imports"}
  ],
  "computed": {
    "layers": [["mcal.can", "mcal.gpio"], ["bsw.canif"], ["services.vcu"]],
    "topological_order": ["mcal.can", "mcal.gpio", "bsw.canif", "services.vcu"],
    "cycles": []
  }
}
```

## 4. Cấu trúc Ma trận Dấu vết (Trace Matrix Schema)

```json
{
  "$schema": "copl-trace-matrix-v1",
  "entries": [
    {
      "requirement_id": "REQ-EVCU-001",
      "requirement_title": "Bộ Máy Trạng thái Vận Hành Thiết Bị Xe Điện (Vehicle State Machine)",
      "priority": "high",
      "status": "implemented",
      "implemented_by": [
        {"module": "services.vcu.state_machine", "functions": ["process_event", "prepare_drive"]}
      ],
      "tested_by": [
        {"test_id": "T-SM-001", "title": "Giả lập chuyển đổi trạng thái từ Park → Ready", "status": "pass"},
        {"test_id": "T-SM-002", "title": "Giả lập kiểm tra lỗi an toàn từ Drive → Chế độ Khẩn cấp (Fault emergency)", "status": "pass"}
      ],
      "decided_by": ["D-EVCU-002"],
      "coverage": 1.0,
      "trace_status": "complete"
    }
  ],
  "summary": {
    "total_requirements": 9,
    "fully_traced": 8,
    "partially_traced": 1,
    "untraced": 0,
    "overall_coverage": 0.94
  }
}
```

## 5. Tổ Chức Thư Mục AI Bundle (AI Bundle Directory)

```yaml
ai_bundle/:
  manifest.json:           # Chứa metadata tổng quan về AI Bundle
  summary_cards/:
    - mcal.can.json
    - bsw.canif.json
    - services.vcu.json
    - ...                  # File Summary JSON độc lập cho từng module
  dependency_graph.json:   # Sơ đồ phụ thuộc (Dependency Graph)
  trace_matrix.json:       # Ma trận dấu vết (Trace Matrix)
  workitem_status.json:    # Trạng thái công việc (Workitem Status)
  risk_report.json:        # Báo cáo rủi ro (Risk Report)
  project_summary.json:    # Thống kê tổng quan dự án (Project summary)
  episode_schema.json:     # Định dạng quy định cho việc phần rã task
```

Ví dụ `manifest.json`:
```json
{
  "bundle_version": "1.0",
  "project_name": "evcu_project",
  "generated_at": "2026-04-03T10:00:00Z",
  "compiler_version": "copc-0.1.0",
  "module_count": 23,
  "total_loc": 4500,
  "trace_coverage": 0.94,
  "overall_risk": 0.25,
  "build_status": "pass"
}
```

## 6. Quy Tắc Tạo Artifact (Generation Rules)

```python
class ArtifactEngine:
    def generate(self, sir: SIRWorkspace, output_dir: str):
        # Nguyên tắc 1: Tạo duy nhất một Summary Card định dạng chuẩn cho mỗi module
        for module in sir.all_modules():
            card = self.build_summary_card(module)
            self.save_json(f"{output_dir}/summary_cards/{module.name}.json", card)
        
        # Nguyên tắc 2: Cấu trúc biểu đồ Dependency bao quát toàn bộ Workspace
        graph = self.build_dependency_graph(sir)
        self.save_json(f"{output_dir}/dependency_graph.json", graph)
        
        # Nguyên tắc 3: Ma Trận Truy Vết bao gồm 100% tất cả các Requirement
        matrix = self.build_trace_matrix(sir)
        self.save_json(f"{output_dir}/trace_matrix.json", matrix)
        
        # Nguyên tắc 4: Tính đơn định cấp thiết (Deterministic Artifacts)
        # Nếu Dữ liệu SIR không đổi, kết quả Artifacts khởi tạo giống nhau 100%.
        # Cấm thêm timestamp vào dữ liệu nội dung content (chỉ lưu tại tệp metadata).
        # Không sử dụng ID ngẫu nhiên không khả đoán trong nội dung.
        
        # Nguyên tắc 5: Cơ chế cập nhật cấu hình thân thiện với Biên Dịch Gia Số (Incremental-Friendly)
        # Các tệp JSON được tổ chức rời rạc dạng file riêng lẻ để tối ưu tốc độ cập nhật dựa theo thay đổi code.
```
