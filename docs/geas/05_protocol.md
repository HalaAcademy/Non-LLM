# Đặc tả Giao thức Tin nhắn (GEAS Message Protocol Specification)
## Chuẩn Hóa Giao Tiếp Hệ Thống & Event-Driven Modularity 

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Nguyên Lý Giao Tiếp Hướng Sự Kiện (Message-Driven Architecture)

Hệ thống GEAS có cốt lõi gồm 12 Module độc lập phân tầng. Để bảo đảm tính tương thích, chịu lỗi (fault-tolerant) và dễ theo vết lập trình rẽ hướng (replay-ability), các trạng thái liên lạc được đóng gói chặt theo chuỗi `Typed Message Data Classes`, thay vì chia sẻ chung Memory Bus.

## 2. Thông Cấu Cú Pháp Tin Nhắn (Standard Message Definitions)

### 2.1 Cấu Trúc Khối Nhận Yêu Cầu Goal (Goal Interpreter Msg)

```python
@dataclass
class GoalParsedMsg:
    """Message Trả Về Sau Khi Phân Tích Thông Số Người Dùng Task Yêu Cầu Mồi."""
    task_id: str
    requirement_graph: list[dict] # Node Graph Dịch Lý Yêu Cầu Context Text
    constraints: list[str]        # Hệ Thống Biên Ràng Cản User Rules Domain
    missing_info: list[str]       # Warning Nếu NLP Trích Lục File Chưa Hoàn Toàn Rõ
```

### 2.2 Cấu Trúc Giao Thức Quản Trị Memort Retrival (Memory Msg)

```python
@dataclass
class MemoryRetrievedMsg:
    """Message Giao Khối Payload Của Rương Kiến Thức Data Base."""
    query_id: str
    relevant_episodes: list[Episode]    # Khay Vector Mapping Chắn Episode Tương Đồng
    lessons: list[Lesson]               # Thẻ Rule System Fix Pattern Extract Traced
    procedures: list[Procedure]         # Flow Chiến Thuật Workflow Chuyển Cấp System 
    confidence_scale: float             # Điểm Phóng Dự Toán Accuracy Trả Tìm Data Base
```

### 2.3 Cấu Trúc Báo Biên Độ Sinh Mạng (World Model Message)

```python
@dataclass
class WorldModelUpdatedMsg:
    """Báo Cáo Tracking Dải Sự Chuyển Biến Code Architecture Nodes Cấu Trúc Của Dự Án Copl Cored."""
    project_graph: ProjectStateNode
    changes_since_last: list[ChangeDelta]
    sync_hash: str 
```

### 2.4 Khối Lập Kế Hoạch Pipeline & Phase (Plan Message)

```python
@dataclass
class PlanCreatedMsg:
    """Kênh Truyền Tải Node Hành Trình Lập Graph Planner Strategy."""
    plan_id: str
    phases: list[PhaseNode]             # Block Phân Lớp Milestone Chiến Lược WorkFlow.
    current_step: TaskStep              # Vệt Thao Tác Kích Lệnh Now Target Call.
    estimated_completion_time: float
```

### 2.5 Cấu Lệnh Thông Biến Cự Ly Cổng Chính Sách Hành Vi (Action Msg)

```python
@dataclass
class ActionSelectedMsg:
    """Dẫn Mạch Code Thông Cáo Action System Lấy Token Select."""
    action: ActionDef                   # Target Object Mapping Dịch Parameter Execute IO Target CLI Call Function File
    confidence: float                   # Output Accuracy Lớp Action Forward Network Value
    reasoning: str                      # Trace Log Lời Điểm Lời Bào Chữa Hệ AI Suy Diễn.
```

### 2.6 Khay Dữ Đầu Ra Từ Mã (Execution Result Msg)

```python
@dataclass
class ExecutionResultMsg:
    """Trả Trạng Thái CLI IO File Node Event Bật Xong Bước Nã Action Executor Cổng."""
    outcome: OutputCodeString       # Raw CLI System StdOut/StdErr Dump Trace
    artifacts_changed: list[str]    # Files Bị Cập Nhật Patch Mới.
    duration: float                 # System Latency Track Timing Node Limits
```

### 2.7 Báo Bệnh Hệ System Cầu Đoán (Diagnosis Complete Msg)

```python
@dataclass
class DiagnosisCompleteMsg:
    """Phiến Phán Cấu Trục Phá Rễ Log Trạng Lỗi Failed Error Error Root System Bounds Error"""
    root_cause: str                     # Object Nhóm Bệnh Đánh Nhóm System Categories.
    affected_modules: list[str]         # Cụm Cơn Chùm Gãy Mạng Lây Dây Chuyền Affected.
    fix_strategy: OptimizationRoute     # Bê Đỡ Khối Khảo Lệnh Solution Plan Policy Đỡ Gập Failed States Route
```

## 3. Quản Trị Hệ Thông Luân Điển Message Event-Bus

Sự điều chuyển Msg Tương tác sẽ được Quản lý Bởi Mô Đun Trung Tâm (Agent Engine Loop), các Object Message sẽ được Đẩy Qua Nguồn Truyền Lưu Trữ DB Storage Gắn Log Trace Event Loop System Trace nhằm phục vụ chức năng Debug Agent Code: `Timeline Message Event Logger System Tracking`.
