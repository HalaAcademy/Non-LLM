# Đặc tả Lược đồ SIR của COPL
## Semantic Intermediate Representation (Biểu diễn trung gian ngữ nghĩa) — Khắc phục C4: "SIR chỉ là các tên gọi"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. SIR là gì?

SIR (Semantic IR) là **biểu diễn trung tâm** của dự án COPL sau khi qua bước phân tích ngữ nghĩa (semantic analysis). Nó chứa:
- Tất cả ngữ nghĩa mã code (kiểu, hàm, luồng điều khiển)
- Toàn bộ context (mục đích, người sở hữu, trạng thái, an toàn)
- Toàn bộ các liên kết dấu vết (yêu cầu → code → test → quyết định)
- Toàn bộ siêu dữ liệu (metadata) được tính toán (hiệu ứng, phụ thuộc, điểm số rủi ro)

SIR chính là thứ khiến COPL trở nên độc đáo: **compiler hiểu toàn bộ dự án của bạn, không chỉ hiểu giới hạn ở mã code.**

## 2. Mô hình Đối tượng SIR (Object Model)

### 2.1 Workspace (Cốc rễ)

```yaml
SIRWorkspace:
  id: WorkspaceId (UUID)
  name: String
  version: String
  packages: List<SIRPackage>
  global_requirements: List<SIRRequirement>
  global_decisions: List<SIRDecision>
  profiles_used: Set<ProfileType>
  targets_used: Set<TargetType>
  dependency_graph: SIRDependencyGraph
  trace_matrix: SIRTraceMatrix
  computed:
    total_modules: U32
    total_functions: U32
    total_loc: U32
    trace_coverage: F64 (0.0-1.0)
    overall_risk_score: F64
  metadata:
    created_at: Timestamp
    last_compiled: Timestamp
    compiler_version: String
    branch: String (nhánh git nếu có)
```

### 2.2 Package (Gói)

```yaml
SIRPackage:
  id: PackageId
  name: String                    # "mcal", "bsw", "services", "app"
  modules: List<SIRModule>
  dependencies: List<PackageRef>
  computed:
    module_count: U32
    risk_score: F64
```

### 2.3 Module (Đơn vị Lõi)

```yaml
SIRModule:
  id: ModuleId
  qualified_name: String          # "mcal.stm32f407.can"
  package: PackageRef
  context:                        # từ khối @context
    purpose: String
    owner: String
    status: Status                # draft|in_progress|review|stable|deprecated
    safety_class: SafetyClass     # QM|ASIL_A|ASIL_B|ASIL_C|ASIL_D
    known_debts: List<String>
    assumptions: List<String>
    risks: List<String>
  platform:                       # từ khối @platform
    profile: ProfileType
    targets: Set<TargetType>
    memory_mode: MemoryMode
    concurrency_mode: ConcurrencyMode
  trace:                          # từ khối @trace
    implements_traits: List<TraitRef>
    trace_to: List<RequirementRef>
    decided_by: List<DecisionRef>
    verified_by: List<TestRef>
    depends_on: List<ModuleRef>
  content:
    imports: List<ImportDecl>
    functions: List<SIRFunction>
    structs: List<SIRStruct>
    enums: List<SIREnum>
    traits: List<SIRTrait>
    impls: List<SIRImpl>
    constants: List<SIRConst>
    type_aliases: List<SIRTypeAlias>
    state_machines: List<SIRStateMachine>
    lower_blocks: List<SIRLowerBlock>
  context_entities:
    requirements: List<SIRRequirement>
    decisions: List<SIRDecision>
    workitems: List<SIRWorkItem>
    tests: List<SIRTest>
    risks: List<SIRRisk>
  computed:                       # được tính toán tự động bởi compiler
    effect_set: Set<Effect>       # sự hợp nhất của mọi hiệu ứng hàm
    dependency_depth: U32         # độ sâu tối đa trong đồ thị phụ thuộc
    exported_symbols: Set<SymbolId>
    imported_symbols: Set<SymbolId>
    risk_score: F64               # f(status, debt, safety, missing_tests)
    trace_coverage: F64           # % tỷ lệ yêu cầu có code + test cover
    loc: U32                      # số dòng code
    complexity: F64               # số đo cyclomatic hoặc tương đương
  source_location:
    file: String
    start_line: U32
    end_line: U32
```

### 2.4 Function (Hàm)

```
SIRFunction
├── id: FunctionId
├── name: String
├── module: ModuleRef
├── visibility: Visibility          (* pub | private *)
│
├── signature:
│   ├── params: List<SIRParam>
│   │   └── SIRParam { name: String, type: SIRType, mutable: Bool }
│   ├── return_type: SIRType
│   └── generic_params: List<SIRGenericParam>
│
├── effects:
│   ├── declared: Set<Effect>       (* từ chú giải @effects *)
│   ├── inferred: Set<Effect>       (* suy luận ra hiệu ứng *)
│   └── is_pure: Bool
│
├── contract:                       (* từ khối @contract *)
│   ├── preconditions: List<SIRExpr>
│   ├── postconditions: List<SIRExpr>
│   ├── invariants: List<String>
│   ├── latency_budget: Option<Duration>
│   ├── memory_budget: Option<Size>
│   └── safety_notes: Option<String>
│
├── body: SIRBlock                  (* AST giản lược hóa *)
│
├── trace:
│   ├── trace_to: List<RequirementRef>
│   └── verified_by: List<TestRef>
│
├── computed:
│   ├── calls: List<FunctionRef>    (* hàm này gọi hàm nào *)
│   ├── called_by: List<FunctionRef>(* ai gọi đến hàm này *)
│   ├── memory_behavior: MemoryBehavior (* stack_only|heap_alloc|static_only *)
│   ├── is_recursive: Bool
│   ├── complexity: F64
│   └── loc: U32
│
└── source_location: SourceLocation
```

### 2.5 Định nghĩa các Kiểu (Type Definitions)

```
SIRStruct
├── id: StructId
├── name: String
├── generic_params: List<SIRGenericParam>
├── fields: List<SIRField>
│   └── SIRField { name: String, type: SIRType, visibility: Visibility }
├── size_bytes: Option<U32>         (* tính toán tự động nếu code mang tính đơn định *)
└── derives: List<String>

SIREnum
├── id: EnumId
├── name: String
├── generic_params: List<SIRGenericParam>
├── variants: List<SIRVariant>
│   └── SIRVariant { name: String, fields: List<SIRField> }
└── has_associated_data: Bool

SIRTrait
├── id: TraitId
├── name: String
├── generic_params: List<SIRGenericParam>
├── super_traits: List<TraitRef>
├── methods: List<SIRFunction>      (* chỉ có phần signatures hàm *)
└── associated_types: List<SIRTypeAlias>

SIRImpl
├── id: ImplId
├── trait_ref: Option<TraitRef>
├── target_type: SIRType
├── methods: List<SIRFunction>      (* có chứa code block logic *)
└── generic_params: List<SIRGenericParam>
```

### 2.6 Biểu diễn Kiểu SIR (SIR Type Representation)

```
SIRType
├── kind:
│   ├── Primitive(PrimitiveType)
│   ├── Named(TypeId)                       (* tham chiếu vào struct/enum *)
│   ├── Array(element: SIRType, size: U32)
│   ├── Slice(element: SIRType)
│   ├── Optional(inner: SIRType)
│   ├── Result(ok: SIRType, err: SIRType)
│   ├── Tuple(elements: List<SIRType>)
│   ├── Function(params: List<SIRType>, ret: SIRType, effects: Set<Effect>)
│   ├── Generic(name: String, bounds: List<TraitRef>)
│   └── Unit
├── size_bytes: Option<U32>
├── alignment: Option<U32>
└── profile_allowed: Set<ProfileType>
```

### 2.7 Các Thực thể Ngữ cảnh (Context Entities)

```
SIRRequirement
├── id: RequirementId               (* "REQ-EVCU-001" *)
├── title: String
├── statement: String
├── priority: Priority
├── verification: VerificationMethod
├── safety_class: Option<SafetyClass>
├── status: EntityStatus
├── parent: Option<RequirementRef>
├── computed:
│   ├── implemented_by: List<FunctionRef>
│   ├── tested_by: List<TestRef>
│   └── coverage: F64              (* 0.0 = không gì cả, 1.0 = code + test *)

SIRDecision
├── id: DecisionId
├── title: String
├── context: String
├── alternatives: List<String>
├── chosen: String
├── because: List<String>
├── tradeoffs: List<String>
├── affects: List<String>
├── status: DecisionStatus

SIRWorkItem
├── id: WorkItemId
├── title: String
├── assignee: Option<String>
├── priority: Priority
├── status: WorkItemStatus
├── blocked_by: List<WorkItemRef>
├── estimate: Option<Duration>

SIRTest
├── id: TestId
├── title: String
├── verifies: RequirementRef
├── method: TestMethod
├── pass_condition: String
├── status: TestStatus
├── last_run: Option<Timestamp>

SIRRisk
├── id: RiskId
├── title: String
├── likelihood: RiskLevel
├── impact: RiskLevel
├── mitigation: String
├── status: RiskStatus
├── computed_score: F64             (* likelihood × impact *)
```

### 2.8 Máy Trạng thái (State Machine)

```
SIRStateMachine
├── id: StateMachineId
├── name: String
├── state_type: SIRType             (* kiểu enum dành cho việc set state *)
├── event_type: SIRType             (* kiểu enum cấu hình cho event *)
├── initial_state: String
├── transitions: List<SIRTransition>
│   └── SIRTransition
│       ├── from_state: String
│       ├── events: List<String>     (* compound event = AND *)
│       ├── to_state: String
│       ├── action: FunctionRef
│       └── guard: Option<SIRExpr>
├── computed:
│   ├── reachable_states: Set<String>
│   ├── unreachable_states: Set<String>
│   ├── deadlock_states: Set<String> (* các trạng thái bị khóa cứng, không có cầu nối chuyển trang *)
│   └── is_deterministic: Bool
```

### 2.9 Đồ thị Phụ thuộc (Dependency Graph)

```
SIRDependencyGraph
├── nodes: List<SIRDependencyNode>
│   └── SIRDependencyNode
│       ├── id: String              (* chuỗi qualified name của module *)
│       ├── type: NodeType          (* module|package|function *)
│       ├── status: Status
│       └── risk_score: F64
├── edges: List<SIRDependencyEdge>
│   └── SIRDependencyEdge
│       ├── from: String
│       ├── to: String
│       └── type: DependencyType    (* imports|calls|implements|trace_to *)
├── computed:
│   ├── topological_order: List<String>
│   ├── cycles: List<List<String>>  (* sự phụ thuộc vòng / quẩn *)
│   └── layers: List<List<String>>  (* đánh giá phân chia theo mảng/layer *)
```

### 2.10 Ma trận Dấu vết (Trace Matrix)

```
SIRTraceMatrix
├── entries: List<SIRTraceEntry>
│   └── SIRTraceEntry
│       ├── requirement_id: RequirementId
│       ├── requirement_title: String
│       ├── requirement_status: EntityStatus
│       ├── implemented_by: List<FunctionRef>
│       ├── tested_by: List<TestRef>
│       ├── decided_by: List<DecisionRef>
│       ├── coverage: F64           (* 0.0 - 1.0 *)
│       └── status: TraceStatus     (* complete|partial|missing *)
├── computed:
│   ├── total_requirements: U32
│   ├── fully_traced: U32
│   ├── partially_traced: U32
│   ├── untraced: U32
│   └── overall_coverage: F64
```

## 3. Định dạng Tuần tự hóa (Serialization Format)

SIR sử dụng file JSON là định dạng tuần tự hóa quy chiếu chính:

```json
{
  "sir_version": "1.0",
  "workspace": {
    "id": "ws_evcu_001",
    "name": "evcu_project",
    "packages": [
      {
        "name": "mcal",
        "modules": [
          {
            "qualified_name": "mcal.stm32f407.can",
            "context": {
              "purpose": "CAN driver for STM32F407 bxCAN",
              "owner": "team.mcal",
              "status": "stable",
              "safety_class": "QM"
            },
            "platform": {
              "profile": "embedded",
              "targets": ["c"],
              "memory_mode": "static"
            },
            "functions": [...],
            "computed": {
              "effect_set": ["register", "interrupt"],
              "risk_score": 0.1,
              "trace_coverage": 1.0
            }
          }
        ]
      }
    ],
    "trace_matrix": {
      "overall_coverage": 0.87,
      "entries": [...]
    }
  }
}
```

Có hỗ trợ Protocol Buffers dành cho các dự án cực lớn (>100MB SIR) để tăng hiệu năng xử lý.

## 4. Giao diện Query SIR (SIR Query API)

Các lệnh gọi Hàm được cấp phép để bất kỳ công cụ bên ngoài nào có thể truy vấn:

```
get_module(name: String) -> SIRModule
get_function(module: String, name: String) -> SIRFunction
get_dependencies(module: String) -> List<SIRDependencyEdge>
get_dependents(module: String) -> List<SIRDependencyEdge>
get_unimplemented_requirements() -> List<SIRRequirement>
get_untested_requirements() -> List<SIRRequirement>
get_trace_coverage() -> SIRTraceMatrix
get_modules_by_status(status: Status) -> List<SIRModule>
get_modules_by_risk(min_risk: F64) -> List<SIRModule>
get_effect_violations(profile: ProfileType) -> List<Violation>
get_workitems_by_status(status: WorkItemStatus) -> List<SIRWorkItem>
get_state_machine(name: String) -> SIRStateMachine
search_modules(query: String) -> List<SIRModule>
get_cycle_warnings() -> List<List<String>>
```
