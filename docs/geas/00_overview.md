# GEAS — Hệ thống Thích ứng qua Mục tiêu & Kinh nghiệm
## Tổng Quan Dự Án

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. GEAS Là Gì?

GEAS (Goal-Experience Adaptive System) là một **AI Engineering Agent** được thiết kế theo hướng hậu-LLM:

> **Thay vì sinh văn bản tự do, GEAS tự tính toán và chọn lựa hành động tối ưu dựa trên mục tiêu (goal), trạng thái dự án (state), bộ nhớ (memory) và chính sách (policy) — sau đó học hỏi từ kết quả thực thi.**

Khác biệt giữa LLM truyền thống và GEAS:

| Khía cạnh | LLM Truyền thống | GEAS |
|---|---|---|
| **Đơn vị học** | Token (Từ/Ký tự) | Episode (Mục tiêu + Hành động + Kết quả + Bài học) |
| **Mục tiêu tối ưu** | Đoán token tiếp theo | Chất lượng quyết định + Số lượng kết quả thành công |
| **Bộ nhớ** | Context window (Sẽ bị xóa sau mỗi phiên làm việc) | Cơ sở dữ liệu ngoài (Lưu trữ bền vững) |
| **Hành vi** | Sinh văn bản (Text generation) | Chọn hành động → Thực thi → Quan sát → Rút kinh nghiệm |
| **Cải thiện** | Cập nhật ngoại tuyến (Fine-tuning) | Học hỏi liên tục (Online learning) qua mỗi dự án |

## 2. Triết Lý Cốt Lõi

### "Trí thông minh không hoàn toàn nằm ở trọng số (weights)"

Trí thông minh của hệ thống được phân bổ qua:

```
┌──────────────────────────────────────────┐
│           Trí Tuệ Của GEAS               │
│                                          │
│  20% Mô hình Lõi (Neural weights)        │
│       → Hiểu ngôn ngữ, phân tích ngữ nghĩa│
│                                          │
│  25% Hệ thống Bộ nhớ (External database) │
│       → Ghi nhận bài học, quy trình      │
│                                          │
│  20% Mô hình Thế giới (COPL SIR)         │
│       → Lưu trữ trạng thái dự án         │
│                                          │
│  20% Bộ Lập Kế Hoạch + Chính sách        │
│       → Chiến lược, phân bổ công việc    │
│                                          │
│  15% Phản hồi từ Môi trường (Compiler)   │
│       → Kết quả build, kết quả chạy test │
└──────────────────────────────────────────┘
```

## 3. Kiến Trúc 12 Module Lõi

```
┌─────────────────────────────────────────────┐
│                 GEAS AGENT                   │
│                                              │
│  ┌─────────────┐    ┌──────────────────┐     │
│  │ 1. Phân tích│    │ 2. Quản lý       │     │
│  │ Mục tiêu    │◄──►│ Bộ Nhớ (Memory)  │     │
│  └──────┬───────┘    └──────┬───────────┘     │
│         │                   │                 │
│  ┌──────▼───────┐    ┌──────▼───────────┐     │
│  │ 3. Xây dựng  │    │ 4. Lập kế hoạch  │     │
│  │ World Model  │◄──►│ Phân cấp         │     │
│  └──────┬───────┘    └──────┬───────────┘     │
│         │                   │                 │
│         └───────┬───────────┘                 │
│          ┌──────▼───────┐                     │
│          │ 5. Động cơ   │                     │
│          │ Chính sách   │                     │
│          └──────┬───────┘                     │
│          ┌──────▼───────┐                     │
│          │ 6. Thực thi  │──► Nền tảng COPL    │
│          │ Hành động    │                     │
│          └──────┬───────┘                     │
│          ┌──────▼───────┐                     │
│          │ 7. Quan sát  │◄── Kết quả Compiler │
│          │ Kết quả      │                     │
│          └──────┬───────┘                     │
│         ┌───────┴────────┐                    │
│  ┌──────▼──┐    ┌────────▼──────┐             │
│  │ 8. Chẩn │    │ 9. Động cơ    │             │
│  │ đoán lỗi│───►│ Tự Đánh giá   │             │
│  └─────────┘    └───────┬───────┘             │
│                  ┌──────▼───────┐             │
│                  │ 10. Trích xuất│             │
│                  │ Bài học      │             │
│                  └──────┬───────┘             │
│                  ┌──────▼───────┐             │
│                  │ 11. Hợp nhất │             │
│                  │ Bộ Nhớ       │             │
│                  └──────┬───────┘             │
│                  ┌──────▼───────┐             │
│                  │ 12. Sinh     │             │
│                  │ Báo Cáo      │             │
│                  └──────────────┘             │
└──────────────────────────────────────────────┘
```

## 4. Mô hình Cốt lõi — Decision Transformer Lai

```
Kiến trúc: Encoder-Decoder Hybrid (~150 triệu tham số)

Đầu vào: [token_mục_tiêu, token_trạng_thái, token_bộ_nhớ, token_kế_hoạch]
                             ↓
        Transformer Encoder (6 lớp, d=512, 8 attention heads)
                             ↓
          Đại Lượng Biểu Diễn Dữ Liệu (Shared Representation)
                             ↓
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
Cổng Hành động         Cổng Kết quả          Cổng Chẩn đoán
(Action Head)         (Outcome Head)        (Diagnosis Head)
```

- **Cổng Hành động**: Dự đoán và chọn thao tác tiếp theo.
- **Cổng Kết quả**: Dự đoán xác suất hoàn thành luồng công việc.
- **Cổng Chẩn đoán**: Phân loại theo cấu trúc lỗi (Root cause) nếu gặp lỗi mã.

## 5. Hệ thống Bộ nhớ 4 Tầng

| Tầng Phân Lớp | Cấu trúc Lưu trữ | Nền Tảng Lưu Trữ | Mục Đích Sử Dụng |
|---|---|---|---|
| **Working Memory (Hiện hành)** | Task hiện tại, dòng kế hoạch, lỗi hiện hữu | RAM Memory | Hỗ trợ trong cùng phiên làm việc (Session) |
| **Episodic Memory (Trải nghiệm)**| Log Lịch sử: Trạng thái→Hành động→Kết quả | SQLite Database | Dò phân tích khi xuất hiện Task tương tự |
| **Semantic Memory (Ngữ nghĩa)**| Kho Bài học, Quy luật đúc kết, Kiến trúc mã | SQLite Database | Tham chiếu kiến thức xử lý vấn đề tổng quát |
| **Procedural Memory (Quy trình)**| Chu trình quy tắc vòng đời, Workflow | SQLite Database | Lựa chọn phương hướng chiến thuật cốt lõi |

Quy định vòng đời hệ bộ nhớ:
Áp dụng tiêu chuẩn AGM (AGM Belief Revision) khi giải quyết xung đột thông tin. Thống nhất cơ chế dọn dẹp (Garbage collection) đối với metadata không tương tác lớn hơn 6 tháng.

## 6. Hàm Mất Mát Điểm Hồi Quy Bộ Trí Học (Loss Function)

```
L_total = Σᵢ (1/(2σᵢ²)) L_termᵢ + log(σᵢ)

Mô hình 5 cấu phần riêng biệt:
L_decision  = Đối soát học qua mẫu (Behavioral Cloning Loss)
L_outcome   = Hàm đánh giá giá trị thành bại của lệnh (Outcome Prediction)
L_diagnosis = Tìm nguyên nhân gốc chẩn đoán phân rã cấu trúc (Root Cause Diagnosis)
L_lesson    = Thang đo lường tinh chỉnh bài học rút ra (Lesson Quality Contrastive)
L_adapt     = Cơ chế học siêu thích nghi nhạy bén (Fast Adaptation MAML loss)
```
*Tài liệu tham chiếu chi tiết: `docs/geas/03_loss_functions.md`*

## 7. Quy Trình Hoạt Động (Runtime Pipeline)

1. **Phân tích (Understand)**: Bóc xuất Mục tiêu (Goal parsed), truy vấn cấu trúc thông tin từ Bộ Nhớ định hình Trạng thái (Current state).
2. **Lên Kế hoạch (Plan)**: Khởi tạo lộ trình đa tầng (Multi-level Plan step generation).
3. **Thực thi (Act)**: Kích phát giao diện Action để khởi lệnh thao tác trên nền code COPL.
4. **Quan sát (Observe)**: Phân tích log chuẩn Output ghi nhận thông điệp Diagnostic/Result từ Compiler.
5. **Học hỏi (Learn - Nhanh chóng khôi phục khi Fail)**: Mở Module chẩn đoán phân loại trạng thái, suy ngẫm lỗi (Reflection), trích cặn bài học và đưa vào Memory Database. Auto vòng lại thiết đặt lại thông lộ (Replan).

## 8. Mối liên hệ với Hạ Tầng COPL

Cơ chế điều khiển GEAS phụ thuộc COPL cung ứng:
- Đọc xuất Sơ đồ SIR nhằm mô phỏng mạng World Model.
- Bắt lấy Diagnostic API để cung ứng siêu dữ liệu cho mô đun Chẩn đoán Lỗi.
- Tái sử dụng Code Artifact Cards để làm nguyên liệu nhồi nhét Cấu trúc Memory.
- Duyệt lược biểu Trace Matrix hỗ trợ Module Planner lập chiến lược phủ Test.

## 9. Cấu Trúc Khung Tài Liệu GEAS

```
docs/geas/
├── 00_overview.md               ← FILE HIỆN TẠI ĐANG DUYỆT (TỔNG QUAN)
├── 01_architecture.md           ← Tầng kiến trúc quy mô 12 mô-đun chi tiết
├── 02_core_model.md             ← Trọng tâm Mô hình Model Core Architecture & Trạm Embeddings
├── 03_loss_functions.md         ← Lý thuyết thiết lập hàm Mất Mát Toán học
├── 04_memory_system.md          ← Chi tiết cấu hình Database 4 tầng Memory Layer
├── 05_protocol.md               ← Giao thức tin nhắn (Message Protocol)
├── 06_data_strategy.md          ← Chiến lược Data Bootstrap & kỹ thuật DAgger
├── 07_training_pipeline.md      ← Khái lược 6 phân giai đoạn huấn luyện Training Cycle
├── 08_runtime_pipeline.md       ← Sơ đồ luồng Agent Runtime vòng lặp tác vụ
├── 09_branch_memory.md          ← Kiến trúc bộ Nhớ chia nhánh Branch-aware memory routing
└── 10_evaluation.md             ← Chế tài mảng chấm đánh giá chất lượng hệ theo Benchmark
```

## 10. Kho Từ Vựng Giao Thức (Vocabulary)

| Định danh | Giải nghĩa Kỹ thuật Đại chúng |
|---|---|
| **Episode** | Bản ghi Cấu trúc đơn trị: Trạng thái, Mục tiêu, Hành động chốt, Kết Quả Báo cáo, Bài Học Đi kèm. |
| **Trajectory** | Lộ trình theo tuần tự một cụm Episodes gắn chung cho 1 Session hay Task ID. |
| **Lesson** | Gói quy tắc dữ liệu đóng khối Structured Data (Chứa Cội Rễ căn nguyên lỗi và cách Fixing). |
| **Policy** | Chính sách đưa thuật toán đánh giá Action phù hợp ở bước tiếp sau của Model. |
| **World Model**| Khối Abstract Mạng Trạng Thái Dự Án dựng lại từ bản dịch SIR Code Compiler. |
| **EWC** | Giới luật Cân Bằng Bảo Trì Trọng lượng (Elastic Weight Consolidation) — cản màng xóa dữ liệu mô hình. |
| **AGM** | Thuật toán xử lý Xung đột Belief Networks (AGM Belief Revision). |
| **DAgger** | Nhóm thuật toán tạo hệ Training Set giả lập thông minh (Dataset Aggregation). |
| **MAML** | Khung tư duy Tự Học Không Trói Hệ Mô hình Học (Model-Agnostic Meta-Learning). |
