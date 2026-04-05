# Đặc tả guồng máy Artifact Engine của COPL
## Động cơ Phân xuất và Quản trị Tài sản Thông tin Dự án

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Các Thể loại Artifact (Thông tin Phái sinh)

| Kiểu Artifact | Định dạng | Phục vụ người dùng | Mục đích áp dụng |
|---|---|---|---|
| Bảng tóm tắt Summary Card | JSON | Phục vụ Đặc vụ AI Agent, Bảng màu Dashboard | Chấm điểm hiển thị khung tóm tắt cực nhanh cho từng module |
| Sơ đồ Phụ Thuộc Dependency Graph | JSON | Trợ lực AI Agent, Màn hình trực quan Visualizer | Mối quan hệ luân chuyển ràng buộc giữa các module |
| Ma trận Dấu vết Trace Matrix | JSON | Nuôi AI Agent, Lập bảng Reports | Soát chéo theo vết Cầu: Req (Yêu cầu) → Code → Test coverage |
| Tình hình Khối lượng việc Workitem Status | JSON | Đẩy lên Dashboard, Công cụ PM Tools | Theo sát tiến độ gõ code dự án |
| Báo cáo đánh giá Mức nguy hiểm Risk Report | JSON/MD | Cho Trưởng nhóm Team Lead, AI Agent | Đong đếm và Cáo báo thẩm định Risk assessment |
| Báo cáo Tổng quan Kiến trúc Architecture Report | Markdown | Cho Con người đọc | Thư viện tài liệu miêu tả kết cấu kiến trúc dự án |
| Thùng Rương Phân Bón AI Bundle | Nhóm Directory | Dâng tặng riêng AI Agent | Gom trọn vẹn tất thảy những gì AI cần xơi để thấu hiểu dự án |

## 2. Bố cục Mẫu cho Bảng tóm tắt nội dung Module (Summary Card Schema)

```json
{
  "$schema": "copl-summary-card-v1",
  "module_name": "mcal.stm32f407.can",
  "purpose": "Hạ Tầng Lõi lập trình mã Driver kết nối cụm phụ trợ CAN cho chíp bxCAN loại STM32F407",
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
    "known_debts": ["Bộ logic chỉ mới cống hiến cho CAN1, luồng đường cho CAN2 đang đợi trống (Chưa viết)"],
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

## 3. Lược Đồ Sơ đồ Phụ Thuộc (Dependency Graph Schema)

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

## 4. Khuôn mẫu Cấu tạo Ma trận Dấu vết Truy vết (Trace Matrix Schema)

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
        {"test_id": "T-SM-001", "title": "Giả lập nhảy trang thay trạng thái từ Park (đỗ xe) → Ready (vận hành)", "status": "pass"},
        {"test_id": "T-SM-002", "title": "Dìm hệ thống test bắt lỗi từ Drive → Chế độ Khẩn cấp báo lỗi an toàn (Fault emergency)", "status": "pass"}
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

## 5. Tổ Chức Thùng Lưu Trữ Kiến Thức Bơm Cho AI (AI Bundle Directory)

```yaml
ai_bundle/:
  manifest.json:           # Hồ sơ thẻ định danh mô tả metadata tổng kho bundle
  summary_cards/:
    - mcal.can.json
    - bsw.canif.json
    - services.vcu.json
    - ...                  # Sẽ xả nén riêng rẽ từng tờ biên lai cho mỗi một module
  dependency_graph.json:   # Sơ đồ phụ thuộc
  trace_matrix.json:       # Ma trận dấu vết
  workitem_status.json:    # Trạng thái công việc
  risk_report.json:        # Báo cáo rủi ro
  project_summary.json:    # Báo cáo sức khỏe tổng thể Project health
  episode_schema.json:     # Sổ sách luật tạo dựng kịch bản chia tasks
```

Nội soi `manifest.json`:
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

## 6. Định Tuyến Sinh Bản Gợi Ý Mẫu (Generation Rules)

```python
class ArtifactEngine:
    def generate(self, sir: SIRWorkspace, output_dir: str):
        # Kỷ luật Hành động 1: Cung phụng duy nhất đúng 1 tấm tóm tắt Summary card quy chuẩn cho 1 block module
        for module in sir.all_modules():
            card = self.build_summary_card(module)
            self.save_json(f"{output_dir}/summary_cards/{module.name}.json", card)
        
        # Kỷ luật Hành động 2: Một biểu đồ Mạng Ràng buộc Phụ thuộc bao quát Trọn vẹn Workspace Đơn tuyến
        graph = self.build_dependency_graph(sir)
        self.save_json(f"{output_dir}/dependency_graph.json", graph)
        
        # Kỷ luật Hành động 3: Bảng Ma Trận Soi Chiếu Truy lùng Bọc trọn 100% các Nhánh Requirements rải rác
        matrix = self.build_trace_matrix(sir)
        self.save_json(f"{output_dir}/trace_matrix.json", matrix)
        
        # Kỷ luật Hành động 4: Sản phẩm chắt lọc Artifacts bị khoá cứng bằng TÍNH ĐƠN ĐỊNH CẤP THIẾT (DETERMINISTIC) — Dữ liệu SIR giữ nguyên gốc = Kết quả Artifacts tạo lập Giống hệt 100% không suy suyển
        # Cấm gắn timestamp trộn xen vào phần nội hàm content (chỉ cho ghi lịch trích xuất ẩn tại bảng metadata)
        # Bác bỏ trò nặn random văng mã ID rác
        
        # Kỷ luật Hành động 5: Kiến trúc Artifact PHỤ TRỢ TỐI ƯU CƠ CHẾ GIA SỐ LẺ (INCREMENTAL-FRIENDLY)
        # Mỗi một bản card module nằm ngang tự do cá nhân độc lập → Tức Chỉ cập nhật dập lại file card mới đối với các module chịu sức ép sửa đổi, cái nào Không sửa Code KHÔNG In Lại File Json Card
```
