# Đặc tả Chiến Binh Cày Dữ liệu Nền GEAS (Data Bootstrap Strategy)
## Đường Ống Huấn Luyện 3 Giai Đoạn DAgger — Khắc phục G4: "Bài toán Con gà - Quả trứng dữ liệu"

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Nan giải Cuộc Chiến Trứng và Gà Khởi Lập

```
Muốn nắn não cày đào huấn luyện Đặc Vụ GEAS → Buộc phải cạy đống phễu data từ các Lượt ván Chuyên gia Trải Ngoặc xịn (expert episodes)
Muốn bốc lôi moi tay Nhặt Đống ván tập chuyên gia → Lại ngặt nghẽo cần Con Người chĩa mõ mõm nhảy vào rã mồ hôi gõ code quất Task
Chưa nhú Ai Ra Đời Gánh Tạ AI → Nên Trắng xóa sạch trơn ván Episode
Rỗng Không Lịch Sử Tập Ván → Không Mồi Thuốc Kích Dậy Nổi Lưới Nhện của Thằng AI

→ DÍNH LỖ LÚNG LẦY BOOTSTRAPPING QUẨN LỐI BÀI TOÁN CON GÀ QUẢ TRỨNG
```

## 2. Diệu Phép Giải Lưới: Cố Máy Đường Ống Mồi 3 Tầng DAgger (Dataset Aggregation)

### Nhịp Thở Oai Chóp Tầng 1: Móc Túi Hành Vi Trí Lực Con Người Trình Diễn (Tháng 1-2)

```
Cao Nhân Chuyên gia cởi trần lăn xả Xúc Tiên giải mã Vô Số Mảng code project Đích thân xài hệ COPL.
Từng Cú Bóp Chóp Tay Nút Nã Đều Bị Cái Camera Lùa Hốt Bắn Gọn Hết Thành Episode Cứng.

Ma Trận Tóm: Bày cỗ rải 20 chóp móc Task Trạc Lừa được bóp chọn căng đét:
  - Đáy Đu Nhẹ: Nặn 1 mụn module thôi, nặn nhẹ nhõm nhít enum định tuyến, vuốt struct.
  - Oằn Giữa Tầng Cao: Dũi Xọc Dệt một Nền tảng Nhánh đa tấc modules, Rũ sạch diệt lỗi rễ types, cày gắm bọc ranh giới xích mốc.
  - Lũ Cao Đỉnh Khét: Mảng Layered bự khủng, Đan chéo Tơ Lưới Phủ Khắc Trace băm Test trịch hệ thống.

Thu Hoạch:
  1 Kèo Task ngốn ~30-100 Lượt Action múa chiêu = Túm cổ vắt nước rớt được ~30-100 episodes
  Tổng Sưu Tập Gom Được Xô: 20 bài tasks × băm nát nhặt ~60 lượt/cục episodes = Tính Rạc Tầm ~1,200 hạt Mầm Lõi Episodes Xịn Thơm.
```

### Nhịp Thở Đi Đoạn Xoáy Tầng 2: Váy Áo Cùng Học - Đặc Vụ Nặn Đạn Và Tiên Nhân Vác Bay Vá Sửa Cầm Tay Trỏ (Tháng 3-4)

```
1. Lôi Cái Bọc 1,200 hạt Episodes Xịn Thơm đó Ra, Cho Đổ Đúc Ép Não Thằng Model Sơ Sinh Tươi.
2. Thả Cọp Trổ Tài Tự Rút Thử Xà Khúc Quất Task Độc Lập tự nhú.
3. Khi Nào Tên Ngốc AI đánh Võ Mồm Quất Bậy Tung Lạc Bước → Trưởng xưởng Con Người xách Thước Đập Tay Phạt ÉP NẮN SỬA LỖI Hành Vi Vết Tội.
4. Mảnh Khúc Vá Sửa Từ Vết Sẹo Lỗi Kia Cứa Nặng Bọc Sinh Làm Một Cái Bọc Bài Học Trải Nghiệm Tập Training Mới Toe Nóng Hổi Chói Nhạy.
5. Cuộn Gom Nhồi Rải Trả Ngược Đống Cơm Ép Đó Đút Lại Vọng Retrain Đổ Dồn Model Quắt Qué Lại Lên Phiên Khởi Kiền Lượt mới với bụng Mập Data.

Vòng Lọng Tuần Hoàn DAgger Bóp Đầu:
  Lặp Xoáy vòng quay Kép:
    Nhón Kép Lỗ agent_data = agent cất tay tự trổ(món task mới chưa nhìn bao giờ)
    Bàn Tay Tiên Nhân Cọ Sẹo Chữa Chỉnh expert_corrections = con_người.nghiền_soi(agent_data)
    dữ_liệu_gốc.đớp(expert_corrections)
    model.vuốt_tới_nái_tái_đóng(dữ_liệu_gốc)

Rụng Quả Rớt Sau 5 Chặng Rèn Chua Trát:
  Kho data bụng mỡ tăng rọt: Vọt đỉnh lên ~4,200 hạt chóp episodes xịn giòn
  Điểm Độ Bén Của Quỷ Đặc Vụ Khôn Rột: Chèo qua đỉnh 65% bách thắng (Quẫy lên từ mức 20% ngu đặc ngày đầu tiên dính tạ).
```

### Nhịp Thở Vương Mệnh Đại Càn Tầng 3: Tự Lăn Tự Xé Sóng Giương Buồm Gióng Chèo (Self-Play Tháng 5+)

```
Trưởng Thành Vung Đao Mặc Giáp Hoạt Động Tự Chủ Miễn Cần Vú Em Con người Bọc Khung Bú Sữa Chéo.
Treo Lọng Chóp Điểm Xác Trúng Phán Cuối Vẫn Do Lão Quản Giáo Đạo Tạc Lời Của Bộ Compiler Trả Điểm Tín Cứ.

Chuỗi Rà Luồn Túm Bóng Xoáy Trọn Tự Soi Lỗi Chống Vỡ Tự Nhú Bám Self-play:
  Xáp Vồ lấy bài Cày task = quàng quất 1 bài chưa thấy nốt
  Tua màng quăng tay móc action:
    Hành vi được bốc chọn action = agent.rải_bát_quái(state)
    Kết Cục rọc gáy rụng result = lão_cộp_COPL.Búa_Lệnh_Nhả(action)
    Kết Điểm phán chóp outcome = ngáo_kẹt_mắt_rình.soi_trĩ(result)
    
    If Ngọt (Trúng Mốc Chín múp success):
      Khuôn Vào Hồ Sơ Chạm Thắng Khỏa Nước positive
    Else (Nắn Oằn Thọt Lên Tảng Băng failure):
      Lôi Đầu Quỷ Rễ diagnosis ra Mổ Bụng Cạo Lỗi
      Vắt Nước Tiết Chưng Thấm lesson Rút Ranh Rập Mạch Kẹp Ngốc
      Nhào Nặn Đóng Cái Của Nợ Sập Ruột negative_episode Tống Cấm
      
      # Tiên Chước Khôn Dồn Tự Chữa Vết Mẻ (Self-correction): 
      Hành Vi Ké alt_action = policy.chỉ_nhích_ra_nhấn_đường_khác(state, cấm_nhại_đồ_cũ)
      Bắn Đạn Lại Ké alt_result... Nếu lọt Cửa → Mừng! Lưu Cú Gỡ Hoàn Mỹ correction_episode đó Lập Đáy Cốt Vàng.
```

## 3. Khung Đạo Giáo Phù Cấp Bậc Luyện Task Curriculum

```
Ngạch Môn Nấc 1 (Vô Môn Ngẩn Rập Ngốc): 5 Khúc bài
  T-001: Đẻ khuôn đúc gạch struct đủ 5 ổ fields
  T-002: Đắp Rãnh Mạch liệt enum chia ngóc 4 lối thoát
  T-003: Chải lượn hàm nhúng nhão cạo gọt ruột struct A xả qua B
  ...

Ngạch Chạm Nấc 2 (Gia Truyền Sức Rặn Trung Cấp): 8 Khúc Bài
  T-006: Tháp mạch rặn đúc Phễu CAN driver thông 3 rãnh function hút hàm
  T-007: Giải hố ngáp cắn bẫy hụt lụn type mismatch lỗi dọc dự án
  ...

Tột Đỉnh Chóp Phá Đảo Tuyệt Môn Nấc 3: 7 Trận Chiến Giành Ngôi
  T-014: Gầy Móng Nốc trọn Vòm Kiến TRúc Tàng Phá CAN stack đủ ngóc MCAL+BSW
  T-015: Trấn Lập Cõi Máy VCU nhay nuốt bọc khối safety monitor cắn lồi đo rờ test rên gáy
  T-016: Vát Tạc Núi Xé refactor dẹp bỏ dự án nhão bung bằng phẳng sang Nếp Rẽ Tầng layered ngon ơ
```

## 4. Chốt Vòm Trạm Chắn Đoạt Kiểm Định An Toàn Mực Data Gỉ

```python
class DataQualityChecker:
    def validate_episode(self, episode: Episode) -> bool:
        # Cửa Điểm 1: Màng State phải không cụt rỗng
        # Cửa Điểm 2: Action Đòi Vượt mảng có nằm trong cõi 45 ô lọng hay là trót đâm tít dở hơi gí
        # Cửa Điểm 3: Bộ Outcome Đo phải ôm ngọn lớp đúng cọc điểm số
        # Cửa Điểm 4: Gáy Oằn Rớt thì Rễ Diagnosis gỉ gốc lỗi thối Phải Có Chắn
        # Cửa Trạm 5: Đáy trace Vết ko lũng trôi
        return True
    
    def validate_dataset(self, dataset: list[Episode]) -> DatasetReport:
        # Chốt Rà San San Không Lún Cân Phân Biểu Balance Check:
        # Tỷ Lệ Không một phím Võ Nào Cấm vượt trần Lạm mặt trên bàn tiệc >30% hay Khẽ Ngất xỉu tóp mất tiêu <1% bọt bèo.
        # Ràng Phán Tự Động Rẽ Trắng Đen Lên Đỉnh Mảng Phấn Tỷ số: Rạch ranh dao động Thắng Khỏi phải Nằm Ngáng đà trong Cầu ngập lộn Nhào ~60/40.
```
