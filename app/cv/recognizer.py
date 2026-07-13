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
                print(f"[INFO] Đã nạp mô hình nhận diện: {model_path}")
            except Exception as e:
                print(f"[WARNING] Lỗi nạp mô hình ONNX: {e}. Chạy chế độ giả lập.")
        else:
            print("[INFO] Chạy chế độ giả lập (Mock Mode) do chưa có file model thực tế.")

    def clean_and_center_digit(self, cell_img, pad=8):
        """
        Dọn sạch viền lưới bám mép và căn giữa chữ số.
        Đã tích hợp thêm Max Size Guard để triệt tiêu góc lưới chữ L và nhiễu lấm chấm ở ô trống.
        """
        if len(cell_img.shape) == 3:
            gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
        else:
            gray = cell_img.copy()

        # 1. BỘ LỌC BẢO VỆ ĐỘ TƯƠNG PHẢN (Contrast Guard)
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        contrast_range = max_val - min_val
        _, std_dev = cv2.meanStdDev(gray)
        std_val = std_dev[0][0]

        if contrast_range < 30 or std_val < 5.0:
            return np.ones((50, 50), dtype=np.uint8) * 255

        # 2. PHÂN NGƯỠNG THÍCH ỨNG
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 19, 8
        )
        
        # 3. CẮT BIÊN CÔ LẬP TỐI ƯU (Margin Severing)
        margin = 2
        thresh[0:margin, :] = 0
        thresh[-margin:, :] = 0
        thresh[:, 0:margin] = 0
        thresh[:, -margin:] = 0
                
        # 4. TÌM CONTOUR CHỮ SỐ CHUẨN HÌNH HỌC (Geometry Contours Filter)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        best_contour = None
        min_dist_to_center = 999.0
        
        for c in contours:
            area = cv2.contourArea(c)
            x, y, dw, dh = cv2.boundingRect(c)
            
            # --- MÀNG LỌC HÌNH HỌC NGĂN CHẶN ĐƯỜNG LƯỚI & GÓC GIAO ---
            # A. Max Size Guard: Chữ số in Sudoku thật không bao giờ chiếm quá 36px rộng/cao trong ô 50x50.
            # Lọc bỏ hoàn toàn đường lưới dọc, ngang dài và các góc giao chữ L.
            if dw > 36 or dh > 36:
                continue
            
            # B. Scale Guard: Lọc nhiễu hạt nhỏ, bụi bẩn lấm chấm
            if area < 15 or dh < 8:
                continue
                
            # C. Lọc đường kẻ ngang dẹt (Nếp gấp ngang dẹt)
            if dw > 1.6 * dh:
                continue
                
            # D. Lọc đường lưới dọc dẹt thẳng đứng
            if dh > 4.5 * dw:
                continue
                
            # E. Edge Touch Guard: Lọc nét dọc bám sát sạt mép ảnh tuyệt đối
            if x <= 1 or (x + dw) >= (thresh.shape[1] - 1):
                if dh > 2.2 * dw:
                    continue
            # --------------------------------------------------------
                
            # Tính toán khoảng cách tới tâm hình học của ảnh
            cx = x + dw / 2.0
            cy = y + dh / 2.0
            dist = np.sqrt((cx - (thresh.shape[1]/2.0)) ** 2 + (cy - (thresh.shape[0]/2.0)) ** 2)
            
            if dist < min_dist_to_center:
                min_dist_to_center = dist
                best_contour = c
                
        if best_contour is None:
            # Nếu không có contour nào vượt qua được hệ thống màng lọc -> Kết luận ô trống
            return np.ones((50, 50), dtype=np.uint8) * 255
            
        # 5. TRÍCH XUẤT, CO GIÃN VÀ CĂN GIỮA NÉT CHỮ
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
            # Chuyển đổi định dạng phù hợp với MNIST (chữ trắng nền đen)
            digit_input = cv2.bitwise_not(cleaned_cell)
            resized = cv2.resize(digit_input, self.target_size, interpolation=cv2.INTER_AREA)
            normalized = resized.astype("float32") / 255.0
            blob = cv2.dnn.blobFromImage(normalized)
            
            self.net.setInput(blob)
            preds = self.net.forward()
            return int(np.argmax(preds[0]))
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