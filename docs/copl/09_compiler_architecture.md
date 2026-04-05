# Kiến trúc Trình Biên Dịch (Compiler Architecture) của COPL
## Đường ống dẫn Pipeline Xử lý Biên Dịch Hỗ trợ Đa Nhóm Công cụ (Multi-Target) — Khắc phục C10: "Lỗ hổng Ngữ Nghĩa giữa Đa Cấu Hình Cốt Build"

> **Trạng thái**: Bản nháp | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Phương Thức Vận Động (Pipeline) của Compiler

```
                    COPL Compiler Trình Tổng biên (copc)
                    
Source Code (.copl)  ──►  Từ Vựng Lexer  ──►  Phân tách Cấu Trúc Parser  ──►  Cây Cấu Trúc Trừu Tượng AST
                                                 │
                                     ┌───────────▼───────────┐
                                     │ Phân Tích Ngữ Nghĩa   │
                                     │ Semantic Analysis     │
                                     │  ├─ Tìm phân dải Name │
                                     │  ├─ Bộ chẩn Type      │
                                     │  ├─ Rà soát Effect    │
                                     │  ├─ Nắn Profile       │
                                     │  ├─ Kiểm tra Contract │
                                     │  └─ Dò Trace Linker   │
                                     └───────────┬───────────┘
                                                 │
                                     ┌───────────▼───────────┐
                                     │ Bộ Đúc Khuôn SIR      │
                                     │  (Semantic IR)        │
                                     └───────────┬───────────┘
                                                 │
                           ┌─────────────────────┼─────────────────────┐
                           │                     │                     │
                   ┌───────▼──────┐   ┌──────────▼──────┐   ┌─────────▼──────┐
                   │  C Lowering  │   │  Rust Lowering  │   │   Go Lowering  │
                   │  SIR → C-TIR │   │  SIR → Rust-TIR │   │   SIR → Go-TIR │
                   └───────┬──────┘   └──────────┬──────┘   └─────────┬──────┘
                           │                     │                     │
                   ┌───────▼──────┐   ┌──────────▼──────┐   ┌─────────▼──────┐
                   │  C Codegen   │   │  Rust Codegen   │   │  Go Codegen    │
                   └───────┬──────┘   └──────────┬──────┘   └─────────┬──────┘
                           │                     │                     │
                       Tệp .h + .c        Thư mục .rs          File .go
                           │                     │                     │
                    arm-none-eabi-gcc       rustc / cargo         go build
```

## 2. Diễn tiến các Giai Đoạn (Phase Details)

### Giai Đoạn 1: Lexer (Tạo chuỗi ngắt dòng Tín Hiệu Nguồn Source → Tokens)

```python
class Lexer:
    """Biến mã ký tự thô trong tệp source code text về một nguồn nhả ra tín hiệu token stream.
    
    Yêu cầu Tốc độc tiêu chuẩn: Quét quét ngốn 1M tokens/sec
    Yêu cầu Mốc RAM: chạy Streaming tuần hoàn liên tiếp (Sài ít tốn hạn O(1) memory trên từng block mã file)
    """
    
    def tokenize(self, source: str, filename: str) -> Iterator[Token]:
        pos = 0
        line = 1
        col = 1
        while pos < len(source):
            token = self.next_token(source, pos, line, col)
            yield token
        yield Token(TokenType.EOF, "", line, col)
```

### Giai Đoạn 2: Parser (Cuộn ghép dòng Từ vựng cắt Tokens → Thành Cây dữ liệu AST)

```python
class Parser:
    """Máy cuộn Đệ quy (LL(1) recursive descent parser).
    
    Tiêu chuẩn Bảng Ngữ Pháp: Tổng bộ 152 Mẫu Định Tuyến Production rules (Hãy ghé lại nhánh đọc bài viết tài liệu số 01_grammar_spec.md)
    Biện pháp Trục Vớt Khủng Cố khi rớt mảng lỗi (Error recovery): Tính năng Panic mode bỏ qua khúc nghẽo lỗi — trượt luồng Skip để vượt qua hố cạn mà nhắm tới điểm tụ sync mốc tiếp theo token nhảy ra
    """
    
    def parse_module(self) -> ASTModule:
        self.expect(TokenType.MODULE)
        name = self.parse_qualified_name()
        self.expect(TokenType.LBRACE)
        items = self.parse_module_items()
        self.expect(TokenType.RBRACE)
        return ASTModule(name=name, items=items)
    
    def parse_module_items(self) -> list[ASTItem]:
        items = []
        while self.current.type != TokenType.RBRACE:
            # LL(1): Phân trích bằng hệ quy nạp nhắm mắt báo trước nhìn cờ hiệu (lookahead token)
            match self.current.type:
                case TokenType.AT:      items.append(self.parse_annotation_block())
                case TokenType.PUB:     items.append(self.parse_pub_item())
                case TokenType.FN:      items.append(self.parse_function())
                case TokenType.STRUCT:  items.append(self.parse_struct())
                case TokenType.ENUM:    items.append(self.parse_enum())
                case TokenType.TRAIT:   items.append(self.parse_trait())
                case TokenType.IMPL:    items.append(self.parse_impl())
                case TokenType.USE:     items.append(self.parse_use())
                case TokenType.CONST:   items.append(self.parse_const())
                case TokenType.TYPE:    items.append(self.parse_type_alias())
                case TokenType.LOWER:   items.append(self.parse_lower())
                case TokenType.STATE_MACHINE: items.append(self.parse_state_machine())
                case TokenType.REQUIREMENT: items.append(self.parse_requirement())
                case TokenType.DECISION: items.append(self.parse_decision())
                case TokenType.WORKITEM: items.append(self.parse_workitem())
                case TokenType.TEST:    items.append(self.parse_test())
                case TokenType.RISK:    items.append(self.parse_risk())
                case _:                 self.error_recovery()
        return items
```

### Giai Đoạn 3: Semantic Analysis (Phân Tích Ngữ Nghĩa Từ Vựng Nội Hàm)

```python
class SemanticAnalyzer:
    """Máy Mổ Xẻ Nội Hàm chắt lọc tầng phân đoạn đa điểm qua đường multi-pass semantic analysis.
    
    Lưới Chải Lần 1: Lược giản định danh Name resolution — Cắt khóa gộp dời móc thông suốt giải quyết toàn bộ định vị (resolve all identifiers)
    Lưới Chải Lần 2: Check Soát Cấu Trúc Kiểu Type checking — Rà check thuật toán hai chiều quy nạp (bidirectional type inference)
    Lưới Chải Lần 3: Moi thông tin Rà Cảm Xúc Biến Tính Effect inference — Thu nhặt thông tin tính nhẩm gán Mác Effects ra hết tất thảy khai báo func
    Lưới Chải Lần 4: Đo ép khuôn Profile checking — Cắt lớp lọc vi phạm cấm vận không do giới hạn profile
    Lưới Chải Lần 5: Xét Duyệt tính Đồng Thuận Giao Kèo Contract checking — Đo xét khối Logic code Expression ghi vào cờ Hợp Đồng có chuẩn đánh kiểu dán Typed xôi hỏng bỏng không.
    Lưới Chải Lần 6: Khới Link Trace linking — Thiết lập cấu nối găm chân trỏ Mũi Tên yêu cầu requirements ↔ hàm thực thi code ↔ bộ mảng đánh test
    """
    
    def analyze(self, ast: ASTModule) -> AnalysisResult:
        # Pass 1: Xây Bảng Mã Ánh Xạ Symbol table
        symbols = self.name_resolver.resolve(ast)
        
        # Pass 2: Khẩu trừ Type check
        type_errors = self.type_checker.check(ast, symbols)
        
        # Pass 3: Áp đoán Infer effects
        effects = self.effect_checker.infer(ast, symbols)
        
        # Pass 4: Nắn Chuẩn Khuôn Độ Profile compliance
        profile_errors = self.profile_checker.check(ast, effects)
        
        # Pass 5: Bắt Lỗi Mốc Thỏa Định Contract types
        contract_errors = self.contract_checker.check(ast, symbols)
        
        # Pass 6: Nối Rễ Mã Hóa Link Trace links
        trace_info = self.trace_linker.link(ast)
        
        all_errors = type_errors + profile_errors + contract_errors
        return AnalysisResult(
            symbols=symbols,
            effects=effects,
            traces=trace_info,
            diagnostics=all_errors
        )
```

### Giai Đoạn 4: Bộ Đúc Lắp Kiến Tạo SIR (SIR Builder)

```python
class SIRBuilder:
    """Cụm Dồn Gộp Xây Trấn lên Khối Tinh Phôi SIR (Từ Cây Trừu Tượng được Xâu Chuỗi Rà Xé phân tách đã tinh lọc AST)
    
    SIR = Nguồn IR Dành Riêng cho mặt Ngữ Nghĩa Ý Niệm Logic (Khẳng định thông tin đọc qua file số 04_sir_schema.md)
    Giá Trị Của Nó đại diện cho Nền Móng TRUNG TÂM TUYỆT PHẨM đóng chóp ngự trị (CENTRAL representation) ứng với các khối như:
      - Thiết Bộ Target lowering (cấp mã luân chuyển hạ tầng hardware nhằm xõa tung ra khối thông dịch code generation)
      - Máy In Phân Kênh Kết Tính Artifact engine (Lập khung Trả số liệu ghi biên bản Báo Cáo cho Reports)
      - Chuyên Vụ Tương Quan Dốc Não Đại Diện GEAS agent (Đọc Lại Toàn Văn Dịch Tư Duy nhằm Phân tích Hấp thụ Ý Chí Lập Trình Về Trọn Bộ cho project)
    """
    
    def build(self, modules: list[AnalyzedModule]) -> SIRWorkspace:
        workspace = SIRWorkspace()
        
        for module in modules:
            sir_module = self.build_module(module)
            workspace.add_module(sir_module)
        
        # Vắt Lực Tính Toán Toàn Thể Độ Dung Hòa Liên Lớp Cụm module (cross-module properties)
        workspace.dependency_graph = self.build_dependency_graph(workspace)
        workspace.trace_matrix = self.build_trace_matrix(workspace)
        workspace.computed.overall_risk = self.compute_risk(workspace)
        workspace.computed.trace_coverage = self.compute_coverage(workspace)
        
        return workspace
```

### Giai Đoạn 5: Biến Dịch Hạ Tầng Cho Nền Target Cụ Thể (SIR → TIR)

```python
class CLowering:
    """Tua Ráp Chuẩn Biến Hóa Đầu Đích hạ nguồn về thành khung sương mã C chuyên chóp C-TIR (Hạ phanh SIR thành C-TIR)."""
    
    def lower(self, sir: SIRWorkspace) -> CTIR:
        tir = CTIR()
        
        for module in sir.topological_order():
            # Định Khúc Bản Khuôn Generate header
            header = self.generate_header(module)
            tir.add_header(module.name, header)
            
            # Định Khúc Lõi Body Ngầm Generate source file content
            source = self.generate_source(module)
            tir.add_source(module.name, source)
        
        return tir
    
    def lower_type(self, sir_type: SIRType) -> CType:
        """Đắp nặn Nếp Type (Móc chéo COPL type để lột thay đổi map dính thành chuẩn C type)."""
        match sir_type.kind:
            case Primitive("U32"):   return CType("uint32_t")
            case Primitive("Bool"):  return CType("bool")
            case Array(elem, size):  return CType(f"{self.lower_type(elem)}[{size}]")
            case Optional(inner):    return self.generate_optional_struct(inner)
            case Result(ok, err):    return self.generate_result_struct(ok, err)
            case Named(id):          return CType(sir_type.name)
```

### Giai Đoạn 6: Code Generation (Hệ Trưởng Gõ Mã Trục Xuất Mã Ngôn ngữ Cuối TIR → C/Rust/Go Target Source)

```python
class CCodegen:
    """Hệ Thông Soát Xuất Build Mã Text Source C (Generate C source files) lấy thông số lồng từ khuôn C-TIR."""
    
    def generate(self, tir: CTIR, output_dir: str) -> list[str]:
        generated = []
        
        for module_name, header in tir.headers.items():
            path = f"{output_dir}/{module_name}.h"
            self.write_header_file(path, header)
            generated.append(path)
        
        for module_name, source in tir.sources.items():
            path = f"{output_dir}/{module_name}.c"
            self.write_source_file(path, source)
            generated.append(path)
        
        # Bồi thêm Bộ Ráp Kịch Bản Build Generate Makefile
        self.generate_makefile(output_dir, tir)
        
        return generated
```

## 3. Guồng Máy Chuyên Xuất Cốt Thành Thục Kết Tinh Sự Kiện Hướng Đích (Artifact Engine)

Cài Lệnh Nhảy Số Chạy Song Song Đu Bám Tiến Trình Biên Dịch codegen — Cơ sở chốt báo Lõi ra bản tóm gọn nén gỡ rối (generates artifacts from SIR):

```python
class ArtifactEngine:
    """Tự Độ máy móc Thống Kê ghi Bản Văn In human/AI-readable artifacts thu trích ép mật từ nấm gốc SIR."""
    
    def emit(self, sir: SIRWorkspace, output_dir: str) -> ArtifactBundle:
        bundle = ArtifactBundle()
        
        # 1. Khai Chiếu Bản Ngắn File Module (Thẻ summary cards dành ra 1 cái cho 1 module)
        for module in sir.all_modules():
            card = self.generate_summary_card(module)
            bundle.add_card(card)
        
        # 2. Phát Ghi Khai Sơ đồ Phụ Thuộc Dependency graph
        bundle.dependency_graph = sir.dependency_graph.to_json()
        
        # 3. Lập Bảng Thống Tịch Theo Giới Độ Phủ Trace matrix
        bundle.trace_matrix = sir.trace_matrix.to_json()
        
        # 4. Kiểm Kê Mã Bốc Điểm Bảng Đo Công Việc Status / workitems
        bundle.workitems = [wi.to_json() for wi in sir.all_workitems()]
        
        # 5. Phập Mạch Tấu Cáo Hiểm Họa Mức Cảnh Báo Bản Rủi Ro (Risk report)
        bundle.risk_report = self.generate_risk_report(sir)
        
        bundle.save(f"{output_dir}/ai/")
        return bundle
```

## 4. Chiến lược Thao lược Phân Xử Phục Hồi Lỗi Hổng (Error Recovery Strategy)

```python
class ErrorRecovery:
    """Bảng Quy Mạch Cho Hệ Điều Trình Compiler Tiếp Theo Khi Bước Đi Bị Lỗi Dội Ngã Gãy (Khung Cơ Sở Bảo Quản Lượng Truy Vớt Hiển Thị Thượng Đỉnh Cao Nhất maximum useful info)."""
    
    # Synchronization tokens (Tín Hỗ Điều Đồng Phân Phối Trùng Khớp Kệnh Tín) — Cuộn Cặp lệnh Băng qua Cho Bộ Parser Tự Đu Mình Bám Chấm Lành Lặn
    SYNC_TOKENS = {
        TokenType.FN, TokenType.STRUCT, TokenType.ENUM,
        TokenType.MODULE, TokenType.RBRACE, TokenType.SEMICOLON
    }
    
    def recover(self, parser, error):
        """Skip tokens until sync point (Nhảy phước rác không rành rẽ bỏ qua vướt rào để nhấp bờ tìm token ăn sóng sync point)."""
        parser.diagnostics.append(error)
        while parser.current.type not in self.SYNC_TOKENS:
            parser.advance()
        # Vực dậy Lại Nền Trình Bộ Nén Parser Chín Sinh Đạo Parse Resume khôi phục lại tính mạng
```

## 5. Bảng Dòng Lệnh Cú Pháp COPL Compiler Gọi (Compiler CLI)

```bash
# Phóng Biên Dịch Cho Bộ Thiết Bị Target ra mã code chuẩn C target
copc build --target c --profile embedded --output out/c/

# Gọi Mã Kiểm Xét Bug Mọt (Code Chạy Tính Rà Lỗi Thuần check only, Không xuất mã nhúng Build code No codegen)
copc check --profile embedded

# Chỉ chắt bóp kết tủa thành phần văn thư báo cáo Emitted AI / Con người báo Artifacts only
copc artifacts --output out/ai/

# Rà build Đong đưa Build toàn triệt để Build + Đập Artifacts gộp hết mọi lệnh
copc build --target c --profile embedded --output out/ --artifacts

# Mã Lệnh Đào Hầm Truy vấn Tra Thống kÊ Query Hệ Cục SIR
copc query --module mcal.can --field dependencies
copc query --trace-coverage

# Mode Ánh Mắt Quan Sát Ứng Đáp Build Nóng Tần Suất Dựng Chớp Bóng Watch mode (Chỉ build mảng chắp vá gia số cho gọn lẹ incremental)
copc watch --target c --profile embedded
```
