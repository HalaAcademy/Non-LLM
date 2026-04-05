# GEAS — Hệ thống Thích ứng qua Mục tiêu & Kinh nghiệm
## Tổng Quan Dự Án

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. GEAS Là Gì?

GEAS (Goal-Experience Adaptive System) là một **AI Engineering Agent** được thiết kế theo hướng hậu-LLM:

> **Thay vì sinh văn bản tự do, GEAS tự tính toán và chọn lựa hành động tối ưu dựa trên mục tiêu (goal), trạng thái dự án (state), bộ nhớ (memory) và chính sách (policy) — rồi học hỏi từ kết quả.**

Khác biệt giữa LLM truyền thống và GEAS:

| Khía cạnh | LLM Truyền thống | GEAS |
|---|---|---|
| **Đơn vị học** | Token | Episode (mục tiêu + hành động + kết quả + bài học) |
| **Mục tiêu tối ưu** | Đoán token tiếp theo | Chất lượng quyết định + kết quả thành công |
| **Bộ nhớ** | Context window (mất sau session) | Cơ sở dữ liệu ngoài (bền vững theo năm tháng) |
| **Hành vi** | Sinh văn bản (text) | Chọn hành động → chạy → quan sát → rút kinh nghiệm |
| **Cải thiện** | Offline (fine-tuning) | Học hỏi liên tục (Online learning) qua mỗi dự án |

## 2. Triết Lý Cốt Lõi

### "Trí thông minh không hoàn toàn nằm ở trọng số (weights)"

Trí thông minh phân bổ qua:

```
┌──────────────────────────────────────────┐
│           Trí Tuệ Của GEAS               │
│                                          │
│  20% Mô hình Lõi (neural weights)        │
│       → hiểu ngôn ngữ, tính trừu tượng   │
│                                          │
│  25% Hệ thống Bộ nhớ (external database) │
│       → ghi bài học, quy trình, tác vụ   │
│                                          │
│  20% Mô hình Thế giới (COPL SIR)         │
│       → giữ trạng thái dự án, phụ thuộc  │
│                                          │
│  20% Bộ Lập Kế Hoạch + Chính sách        │
│       → chiến lược, phân bổ công việc    │
│                                          │
│  15% Phản hồi từ Môi trường (compiler)   │
│       → kết quả build, kết quả test      │
└──────────────────────────────────────────┘
```

## 3. Kiến Trúc 12 Module

```
┌─────────────────────────────────────────────┐
│              GEAS AGENT                      │
│                                              │
│  ┌─────────────┐    ┌──────────────────┐     │
│  │ 1. Diễn dịch│    │ 2. Quản lý       │     │
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
│  │8. Chẩn  │    │ 9. Động cơ    │             │
│  │ đoán lỗi│───►│ Tự Suy Ngẫm   │             │
│  └─────────┘    └───────┬───────┘             │
│                  ┌──────▼───────┐             │
│                  │ 10. Rút tỉa  │             │
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
Kiến trúc: Encoder-Decoder Hybrid (~150M tham số)

Đầu vào: [token_mục_tiêu, token_trạng_thái, token_bộ_nhớ, token_kế_hoạch]
                             ↓
        Transformer Encoder (6 lớp, d=512, 8 heads)
                             ↓
         Tính Đại Diện Chia Sẻ (Shared Representation)
                             ↓
       ┌─────────────────────┼─────────────────────┐
       ▼                     ▼                     ▼
Đầu Hành động          Đầu Kết quả           Đầu Chẩn đoán
(Action Head)        (Outcome Head)        (Diagnosis Head)
```

- **Đầu Hành động**: Chọn thao tác tiếp theo.
- **Đầu Kết quả**: Dự đoán mức độ thành công.
- **Đầu Chẩn đoán**: Phân loại nguyên nhân gốc rễ nếu bị code lỗi.

## 5. Hệ thống Bộ nhớ 4 Tầng

| Tầng | Lưu nội dung gì | Ở đâu | Khi nào dùng |
|---|---|---|---|
| **Working (Hiện hành)** | Task hiện tại, kế hoạch, lỗi | RAM | Trong phiên (session) |
| **Episodic (Trải nghiệm)**| Chuỗi: trạng thái→action→kết quả | SQLite | Khi đụng task tương tự |
| **Semantic (Ngữ nghĩa)**| Các bài học thiết kế tổng quát hóa | SQLite | Khi cần phương hướng giải quyết |
| **Procedural (Quy trình)**| Chiến lược, cấu trúc workflow | SQLite | Khi cần chọn hướng đi mấu chốt |

Vòng đời bộ nhớ:
Vá xung đột thông qua chuẩn AGM. Dọn rác khi không dùng sau 6 tháng.

## 6. Hàm Mất Mát (Loss Function)

```
L_tổng = Σᵢ (1/(2σᵢ²)) L_cụmᵢ + log(σᵢ)

L_decision  = Behavioral cloning (Học theo mẫu)
L_outcome   = Dự đoán mức thành công của lệnh
L_diagnosis = Tìm nguyên nhân gốc
L_lesson    = So sánh thang chất lượng bài học
L_adapt     = Nhạy bén qua Fast adaptation MAML
```
*Chi tiết: `docs/geas/03_loss_functions.md`*

## 7. Cách GEAS Vận hành Runtime

1. **Hiểu (Understand)**: Phân tích mục tiêu, tra bộ nhớ định vị trạng thái.
2. **Lên Kế hoạch (Plan)**: Rải phân cấp kế hoạch.
3. **Hành động (Act)**: Trực tiếp quăng lệnh xuống COPL xử lý code.
4. **Quan sát (Observe)**: Bắt tin nhắn báo lỗi hoặc thành công từ Compiler.
5. **Học hỏi (Learn - Nếu thất bại)**: Chẩn đoán, suy ngẫm, rút ra bài học rồi tích vào bộ nhớ. Replay lại kế hoạch.

## 8. Mối liên hệ với COPL

GEAS điều khiển và nhờ COPL compiler cung cấp:
- Đọc Sơ đồ SIR sinh ra World Model.
- Đọc bảng Diagnostics để Chẩn đoán bắt lỗi.
- Đọc Artifact cards để Cấy thêm vào Memory Manager.
- Đọc Trace matrix để Planner dò lọt khe Test.

## 9. Bản đồ Tài liệu GEAS

```
docs/geas/
├── 00_overview.md               ← BẠN ĐANG ĐỌC FILE NÀY
├── 01_architecture.md           ← Tơ Đồ 12 modules rành mạch
├── 02_core_model.md             ← Trụ Não Model architecture + embeddings
├── 03_loss_functions.md         ← Hàm tính mất mát (5 loss terms)
├── 04_memory_system.md          ← Chi Giai 4 chóp tầng phân cõi bộ nhớ memory
├── 05_protocol.md               ← Cáp giao tiếp giữa các mô-đun Inter-module
├── 06_data_strategy.md          ← Chiến lược mồi Data bootstrapping DAgger
├── 07_training_pipeline.md      ← Móc Phễu huấn luyện 6 phase training
├── 08_runtime_pipeline.md       ← Trục lặp Runtime loop thực tiễn
├── 09_branch_memory.md          ← Xử lý phân nhánh Nhớ branch-aware memory
└── 10_evaluation.md             ← Chuẩn mốc đánh giá Benchmarks
```

## 10. Kho Từ Vựng

| Định danh | Giải nghĩa |
|---|---|
| **Episode** | Khối kinh nghiệm: mục tiêu, tình hình, thao tác, kết quả, bài học. |
| **Trajectory** | Một chuỗi episodes cho chung 1 task. |
| **Lesson** | Bài học tóm chứa Nguyên nhân do đâu, xử trí cách nào. |
| **Policy** | Chính sách xác định hành vi chọn bước kế tiếp. |
| **World Model**| Khối tái hiện trạng thái sinh động mã SIR của dự án. |
| **EWC** | Cơ chế chống lãng quên (Catastrophic forgetting). |
| **AGM** | Định luật dỡ bỏ xung đột cấn cá của bộ nhớ niềm tin. |
| **DAgger** | Mạng nhồi đẩy luyện data (Dataset Aggregation). |
| **MAML** | Đo lường bắt xu hướng nhanh Model-Agnostic Meta-Learning. |
