import cv2
import numpy as np
import os
import shutil

class SudokuRecognizer:
    def __init__(self, model_path=None, target_size=(28, 28)):
        self.target_size = target_size
        self.net = None
        
        if model_path and os.path.exists(model_path):
            try:
                self.net = cv2.dnn.readNetFromONNX(model_path)
                print(f"[INFO] Đã nạp mô hình nhận diện thành công từ: {model_path}")
            except Exception as e:
                print(f"[WARNING] Lỗi nạp mô hình ONNX: {e}. Chạy chế độ giả lập.")
        else:
            print("[INFO] Chạy chế độ giả lập (Mock Mode) do chưa có file model thực tế.")

    def clean_and_center_digit(self, cell_img, pad=8):
        """
        Dọn sạch viền lưới bám mép và căn giữa chữ số.
        Đã tích hợp bộ lọc phân loại chữ số thực tế (Solved Digit) và chữ số ứng viên (Pencil Marks).
        """
        if len(cell_img.shape) == 3:
            gray_orig = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
        else:
            gray_orig = cell_img.copy()

        # 1. BỘ LỌC BẢO VỆ ĐỘ TƯƠNG PHẢN (Contrast Guard)
        min_val, max_val, _, _ = cv2.minMaxLoc(gray_orig)
        contrast_range = max_val - min_val
        _, std_dev = cv2.meanStdDev(gray_orig)
        std_val = std_dev[0][0]

        if contrast_range < 30 or std_val < 5.0:
            return np.ones((50, 50), dtype=np.uint8) * 255

        # 2. KHỬ MỜ ĐỘNG CHUYÊN SÂU (Adaptive Unsharp Masking)
        laplacian_var = cv2.Laplacian(gray_orig, cv2.CV_64F).var()
        
        if laplacian_var < 180.0:
            blurred = cv2.GaussianBlur(gray_orig, (3, 3), 0)
            gray = cv2.addWeighted(gray_orig, 1.8, blurred, -0.8, 0)
        else:
            gray = gray_orig.copy()

        # 3. PHÂN NGƯỠNG THÍCH ỨNG TỐI ƯU (Block_size = 13, C = 6)
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 13, 6
        )
        
        # 4. CẮT BIÊN CÔ LẬP TỐI ƯU (Margin Severing)
        margin = 2
        thresh[0:margin, :] = 0
        thresh[-margin:, :] = 0
        thresh[:, 0:margin] = 0
        thresh[:, -margin:] = 0
                
        # 5. TÌM CONTOUR VÀ PHÂN LOẠI CHỮ SỐ (Pencil Mark Filter)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        large_digits = []
        
        for c in contours:
            area = cv2.contourArea(c)
            x, y, dw, dh = cv2.boundingRect(c)
            
            # --- MÀNG LỌC HÌNH HỌC NGĂN CHẶN ĐƯỜNG LƯỚI & GÓC GIAO ---
            if dw > 36 or dh > 36:
                continue
            
            # Loại bỏ nhiễu vụn cực nhỏ
            if area < 10 or dh < 6:
                continue
                
            # Loại bỏ nét kẻ dẹt dọc hoặc ngang
            if dw > 1.6 * dh or dh > 4.5 * dw:
                continue
                
            # Loại bỏ nét bám sạt mép đứng dẹt
            if x <= 1 or (x + dw) >= (thresh.shape[1] - 1):
                if dh > 2.2 * dw:
                    continue
            # --------------------------------------------------------
            
            # PHÂN LOẠI: Chỉ những nét vẽ có kích thước đủ lớn mới được coi là CHỮ SỐ CHÍNH (Solved Digit)
            # Chữ số ứng viên nhỏ (Pencil Marks) thường có chiều cao dh < 14px trên lưới 50x50 px
            if dh >= 14 and dw >= 7:
                large_digits.append((c, area, x, y, dw, dh))
                
        # Nếu không tìm thấy bất kỳ chữ số lớn nào, kết luận đây là ô trống (chỉ chứa ứng viên hoặc nhiễu)
        if not large_digits:
            return np.ones((50, 50), dtype=np.uint8) * 255
            
        # Chọn chữ số lớn tốt nhất (gần tâm hình học của ảnh nhất)
        best_contour = None
        min_dist_to_center = 999.0
        
        for c, area, x, y, dw, dh in large_digits:
            cx = x + dw / 2.0
            cy = y + dh / 2.0
            dist = np.sqrt((cx - (thresh.shape[1]/2.0)) ** 2 + (cy - (thresh.shape[0]/2.0)) ** 2)
            
            if dist < min_dist_to_center:
                min_dist_to_center = dist
                best_contour = c
                
        if best_contour is None:
            return np.ones((50, 50), dtype=np.uint8) * 255
            
        # 6. TRÍCH XUẤT, CO GIÃN VÀ CĂN GIỮA NÉT CHỮ CHÍNH
        # (Ở bước này, chúng ta chỉ lấy đúng bounding box của best_contour, 
        # loại bỏ hoàn toàn các chữ số ứng viên nhỏ nằm xung quanh ra khỏi ảnh cắt)
        x, y, dw, dh = cv2.boundingRect(best_contour)
        digit_crop = thresh[y:y+dh, x:x+dw]
        
        canvas = np.zeros((50, 50), dtype=np.uint8)
        max_size = 50 - 2 * pad
        scale = min(max_size / dw, max_size / dh)
        new_w, new_h = int(dw * scale), int(dh * scale)
        
        if new_w > 0 and new_h > 0:
            digit_resized = cv2.resize(digit_crop, (new_w, new_h), interpolation=cv2.INTER_AREA)
            start_x = (50 - new_w) // 2
            start_y = (50 - new_h) // 2
            canvas[start_y:start_y+new_h, start_x:start_x+new_w] = digit_resized
            
        final_cell = cv2.bitwise_not(canvas)
        return final_cell
         
    def is_blank_cell(self, cleaned_cell, threshold_ratio=0.008):
        """Kiểm tra ô trống dựa trên tỷ lệ điểm ảnh nét vẽ tối màu"""
        black_pixels = np.sum(cleaned_cell < 127)
        total_pixels = cleaned_cell.shape[0] * cleaned_cell.shape[1]
        ratio = black_pixels / total_pixels
        return ratio < threshold_ratio

    def predict_digit_from_cleaned(self, cleaned_cell):
        """Thực hiện dự đoán chữ số trên ảnh đã được dọn sạch và căn giữa"""
        if self.net is None:
            # Chế độ giả lập an toàn
            import random
            return random.randint(1, 9)
            
        try:
            # 1. Chuyển đổi định dạng tương tự tập huấn luyện (chữ trắng trên nền đen)
            digit_input = cv2.bitwise_not(cleaned_cell)
            
            # 2. Resize về kích thước đầu vào của mô hình (28x28)
            resized = cv2.resize(digit_input, self.target_size, interpolation=cv2.INTER_AREA)
            
            # 3. Tạo blob chuẩn hóa dữ liệu trực tiếp bằng OpenCV DNN (Đồng bộ tuyệt đối với verify_onnx.py)
            blob = cv2.dnn.blobFromImage(resized, scalefactor=1.0/255.0, size=self.target_size)
            
            # 4. Thực hiện suy luận
            self.net.setInput(blob)
            preds = self.net.forward()
            
            # 5. Lấy vị trí nhãn và cộng thêm 1 (Sửa lỗi lệch nhãn nhầm sang ô trống)
            predicted_class = np.argmax(preds[0])
            predicted_digit = predicted_class + 1
            
            return int(predicted_digit)
        except Exception as e:
            print(f"[ERROR] Lỗi suy luận mạng DNN: {e}")
            return 0

    def predict_digit(self, cell_img):
        """Hàm dự đoán thô tiện ích"""
        cleaned = self.clean_and_center_digit(cell_img)
        if self.is_blank_cell(cleaned):
            return 0
        return self.predict_digit_from_cleaned(cleaned)

    def recognize_grid(self, grid_cells_9x9, debug_dir=None):
        """
        Nhận diện lưới 9x9 và tự động lưu ảnh đối chiếu của từng ô để phục vụ phân tích lỗi.
        """
        result_board = []
        
        # Nếu được truyền debug_dir, tạo thư mục cleaned_cells riêng biệt bên trong
        cleaned_cells_dir = None
        if debug_dir:
            cleaned_cells_dir = os.path.join(debug_dir, "cleaned_cells")
            if os.path.exists(cleaned_cells_dir):
                shutil.rmtree(cleaned_cells_dir)
            os.makedirs(cleaned_cells_dir, exist_ok=True)
            
        for r in range(9):
            row_results = []
            for c in range(9):
                cell_img = grid_cells_9x9[r][c]
                
                # 1. Thực hiện dọn viền căn giữa
                cleaned = self.clean_and_center_digit(cell_img)
                
                # 2. Ghi ảnh ra đĩa để phân tích lỗi nếu ở chế độ debug
                if cleaned_cells_dir is not None:
                    # Lưu ảnh thô nhận từ detector
                    cv2.imwrite(os.path.join(cleaned_cells_dir, f"cell_{r}_{c}_0_raw.jpg"), cell_img)
                    # Lưu ảnh sau khi dọn viền căn giữa
                    cv2.imwrite(os.path.join(cleaned_cells_dir, f"cell_{r}_{c}_1_cleaned.jpg"), cleaned)
                
                # 3. Tiến hành phân loại ô trống và dự đoán chữ số
                if self.is_blank_cell(cleaned):
                    digit = 0
                else:
                    digit = self.predict_digit_from_cleaned(cleaned)
                    
                row_results.append(digit)
            result_board.append(row_results)
            
        return result_board