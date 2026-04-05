# Đặc tả Mạch Vận hành GEAS (Runtime Pipeline)
## Vòng Lặp Đi Điều Tác Vụ Đặc Vụ + Bộ Rút Rỉa Cặn Lọc Bài Học — Cú Khắc phuc Lỗi Cắm G8+G9

> **Version**: 1.0 | **Status**: Giai đoạn Đặc tả | **Cập nhật lần cuối**: 2026-04-03

---

## 1. Mạch Tua Vành Lặp Diễn Tiệm (Runtime Loop)

```python
class GEASRuntime:
    """Khối Động Hệ Đẩy Điều Lực Đại Tàng Máy Vận (Main agent runtime)"""
    
    def run(self, task: Task) -> TaskResult:
        # Bóp Dây Nạp Điện Vào (Initialize)
        goal = self.goal_interpreter.parse(task)
        memory_ctx = self.memory.retrieve(MemoryQuery.from_goal(goal))
        world = self.world_model.build(self.copl.get_sir())
        plan = self.planner.create(goal, world, memory_ctx)
        
        # Mạch Xoáy Tời Trống Dội Dùi Cúa Vòng Lặp Agent loop
        step_count = 0
        max_steps = 500  # Rặn chặn thắt bụng quá 500 nấc cuốc tịt văng nghỉ
        consecutive_failures = 0
        max_consecutive_failures = 10 # Gập Gãy Nọc Bu Liên Liếp Rịt 10 phát Nát Cọc là buông Cờ 
        
        while not self.is_goal_satisfied(goal, world):
            # Cần Trọc Check Chặn Lố Vượt Nấc Móc Đu Càng Hay Ép Vòng Tròn Gấp Tịt Tắc Vái Lay Văng Hạt Nẩy Tạch Tù Nhịp
            
            # Khúc 1. Trốc Đầu Nỏ Rút Đuốt Chọn Vịnh Action Hành Vi
            state = AgentState(goal, world, memory_ctx, plan, self.history)
            action_msg = self.policy.select(state)
            
            # Khúc 2. Gác Chắn Anti-loop Cản Vô Nhịp Sáo Lập Bài Tật Ngu Rập 1 Dại Rác
            if self.loop_detector.is_loop(action_msg, self.history):
                action_msg = self.policy.select_alternative(state, exclude=self.recent_actions())
            
            # Khúc 3. Nhấp Phím Đập Cần Cáp Trúng Thực Chạy Lệnh (Execute)
            exec_result = self.executor.execute(action_msg)
            
            # Khúc 4. Quăng Lưới Nháp Trỏ Hốt Mảng Mắt Kết (Observe)
            outcome = self.observer.observe(exec_result)
            
            # Khúc 5. Nhào Nặn Thay Tướng Mã Bọc World Model Mạng
            # Khúc 6. Bóp Óc Trích Xẻ Dịch Nghĩa Outcome
            # Vít Nhịp Thành Tựu Mở Khóa Đậu: Tống Phanh Hưởng Thưởng Lưu Gấm Vàng
            # Loạng Quạng Đứt Xích Fail Oạch: Gọi Phái Điểm Viện Đào Chẩn Hút Dãn Mầm Dọng Trầm Process Failure
            
            # Bơm Nút Xả Kẻ Cuối Report Trạm
```

## 2. Đường Ống Quản Tế Soi So Xoáy Gãy Lỗi (Failure Processing)

```python
def process_failure(self, state, action, outcome, world):
    """Cụm Vành Máy Cửa Rịt Phân Hóa Đậu Gãy: Bác Nghe Diagnose → Phọt Ngẫm Reflect → Gắp Tóp Ruột Lesson Learn → Lẻ Lưới Cuộn Nảy Đớp Thân Adapt."""
    
    # Khoáy Đoạn 1: Lược Bác Bắt Tay Căn Nguyên Lỗi
    diagnosis = self.diagnoser.diagnose(outcome, world, self.history)
    
    # Khoáy Đoạn 2: Trầm Mặc Ghì Trực Xét Nhìn Tội 
    reflection = self.reflector.reflect(diagnosis, self.history)
    
    # Khoáy Đoạn 3: Moi Sạch Bóp Ép Bài Học Rút Dạ 
    lessons = self.learner.extract(diagnosis, outcome, reflection)
    
    # Khoáy Đoạn 4: Gí Trọn Nuốt Mớm Nhập Kho Đồng Hóa memory Tẩy Lọc Đẩy Assimi 
    
    # Khoáy Mạn 5: Húc Nếp Vá Tường Bồi Policy Mới Coong Phản Ưng Cuộn Từ Bài Bài Sóc Đọc Online Đẩy Vào 
    if any(l.confidence > 0.7 for l in lessons):
        self.policy.online_update(lessons)
    
    # Vướng Loạn Quần Cuốn 6: Nếu Toang Xé Bái Lại Vũng Lún Plan → Đẩy Gỡ Xé Ngược Nặn Lại Quy Replan Kế Đồ 
    if reflection.plan_quality == "needs_revision":
        self.planner.replan(world, diagnosis, reflection)
```

## 3. Khâu Kẹp Khuôn Oằn Cắt Điểm Ép Kỹ Điết Rút Gọng Bài Học Lesson (Sửa Gãy Cụt Máy G8)

```python
class LessonExtractor:
    """Dao Kéo Vắt Ruột Giải Vũng Ép Vàng Mực Xịn Kẹp Vào Dòng Cấu Trút Từ Vách Cứt Ép Episodes Lụi Tàn Thất Bại.
    
    Xiết Quăng Gồng Nghì Vào Thế Rọ Constrained:
    - Rác Rưởi Móc Vòng Text Lảm Nhảm Bay Tịt, Từng Dòng Lesson ép vô Format nín Thóp Cứng Khuôn Gờ Đổ Cấu Cốp Đóng Chặt structured
    - Tạp Trát Bộ Nháp Giáp Bọc Rìa Khuôn Đúc Biền Template-based gò nếp ngọn
    """
    
    LESSON_TEMPLATES = {
        "type_mismatch": LessonTemplate(
            context="Đang Đụng Ở cái Module {module} Kẹp vào giò Nhấn kiểu {type_a} tạt kiểu lại đụng vách {type_b}",
            problem="Đứt Cầu Nối Khống Cụp Lệch Khía: Ngó Mong Đám {expected}, Trúng Quả Nhấn Bọc Rác được {found}",
            root_cause="{root_cause_analysis}",
            recommendation="Đắp Thuốc Lại Lấy Liền Ngay Kẹo Phím Mõm Trích xài đúng {correct_type} đổ vô cái lỗ hố điền field chỏ danh mục {field_name} bởi vì {reason}"
        ),
        # .... Đủ Mớ Ép Cho Đủ Bọc Các Cánh Cứa Ngầm 15 Nguyên Do Mối Lỗi
    }
```

## 4. Khuôn Ém Gọt Ngọn Xé Loạn Vát Nhánh Mảng Lực Phổ Tung Trúc Đòn Không Gian Rải Hành Động Action (Giải Bug Cụt Điếc Não Phi Tuyến G9)

```python
class ActionSpacePruner:
    """Búa Cưa Tỉa Cành Cắt Ngọn ActionSpace Tóm Rụng Thu Hẹp từ Mẻ Chống 45 Nhịp Đòn action Mỏi Rũ Sang Ngắt Kéo Giật Khí Thành Bọt Rễ Thích Đáng Nhất Đợi Đớp Phân Cực Bề Quãng Hiện Lọt Nghĩa Mới State Đầu Đấu .
    
    Nhắm So Đong Cân Tạ:
    Vớ Rụng Trơn Nếu Mà Để Y Vậy Đổ Không Vuốt Trọng Rìa Lọc Tỉa Cứa: Mớ Rác Xả 45 actions vung vãi tung bưng × Ép Lòi trẹo 500 bước gõ đi dạo nát nước = Oằn Tạ Rớt 22,500 Lượt Sóng Cân Đong Tính Toán nhức nhối Đau Não Chói Chết Lòi Dã Cục .
    
    Xén Xoáy Nếu Mà Lắp Dao Phay Tỉa Mấy Quả Chuẩn Form: Chít Đuôi Bóp Rẽo Ép Chỉ Lòi Trỏ Vòng Thu Ráp Nhòe Lọt Nhõn Trong Tầm Tích Phân Cuộc Rải Dao Động Chỉ Cỡ ~8-15 actions Lệnh Phợp Bối Cảnh Lót Xịn × Cuộn vòng 500 nấc gõ nhịp điệp = Nát Đỡ Ra Xíu Khỏe Re Nhẹ Óc Nhất Khoảng Lều Điệu Rơi Ráng Chỉ Còn ~5,000 nhịp Quyết Chọn Ép Quả (decisions) Phăng Đều Điếu Thoải Lên Óc Nhỉ.
    
    Lọt Lỗ Dút Rát Hạn Mức Triệt Ngáo Không Gian Ngớp Phẳng Cuộn Loanh Quanh Đi Đảo Cuồng Vọng: Vót Dẽ Rớt Văng Khoảng Cỡ Áp Trúc Chọc Được Cứu Tầm Gần Xong Ế Đỡ Phả Cỡ Tới ~70% Áp Quát Não Nhảo Gọn!
    """
    
    # Luật Tỉa 1: Trảm Cái Đòn Vuốt Bấm Bóp Build Code Nếu Nhác Không Khảy Thấy Module Ráo Rống Mảng Ko Có Lòi Ra Cục Nào
    # Luật Tỉa 2: Không Cò Lôi Bác Vá Cấu Kéo Fix Gỡ Cứu Nếu Đời Ráo Nước Trơn Tru Xoẹt Không Có Tíu Tí Tì Tì Bám Cụt Nùi Lỗi Error Mảng Nào
    # Luật Tỉa 4: Cấm Nhấn Nút Chéo Vách Đỉnh Niêm Phong Chung Kết Task finalize Nếu Điển Phạch Mạch Trace Mép Đuổi Trốn Quét Kém Điểm Tỉ Phối < 80% Lực Nén Che Chắn
    # Luật Tỉa 5: Khóa Lánh Đường Cấm Tung Chưởng Múa Phím Quay Đi Đánh Chập Lại Y Hút Bài Cũ Móp Đã Chết Ngoẻm Rỉ Máu Đứa Cố Hét (Nhại Cũ Rích Xưa Khắc Nhai Arg)
```

## 5. Mạch Máy Cảm Khử Vòng Luẩn Quẩn Căng Loát (Anti-Loop Detection)

```python
class LoopDetector:
    """Phi Tiêu Rạch Mảng Gỗ Phát Điểm Nhại Lặp Cóng Dòng Giật Trơn Nhấn Đít (action loops)."""
    
    # Cuộn Đo Pattern Cụm Nhạc 1: Vong Ngáy Sủa Dội Tung Toang Đục 1 Lệnh y boong vỗ nấp dập lặp lại sủa vang > 3 lần
    # Khúc Gậy Pattern Mảng Luồng Tái 2: Bấm chớp Chớp Nhát A-B-A-B quay tròn giật cục vướng nhay oscillation
    # Chuỗi Ghềnh Dao Pattern Chập Đầu Nhai Mầm 3: Y chốc Ngã Nọc Khục Lấy Cùng Sát 1 Đám Rễ Lỗi Đu Trật Mãi (Bói Lỗi fix→Ép Bọt build→Loi Y Lại Cục Lỗi Cũ rích Xưa Nhỉ Cấp Đó→Căng Véo Đúp Nhót Fix lại vắt→Ép Bám build→Văng Mép Tòi Lại Nó same error). Ngơ Quanh Đi Cùm Kẹt 
```
