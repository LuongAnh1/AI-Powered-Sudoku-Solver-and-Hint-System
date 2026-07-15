import os
import cv2
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from cv.detector import find_sudoku_grid, extract_cells_smart
from cv.recognizer import SudokuRecognizer

def print_sudoku_grid(matrix):
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 25)
        row_str = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str.append("|")
            val = matrix[r][c]
            row_str.append(str(val) if val != 0 else ".")
        print(" ".join(row_str))

def run_integration_test(image_name="image1049.jpg"):
    test_image_dir = os.path.abspath(os.path.join(current_dir, "test_images"))
    image_path = os.path.join(test_image_dir, image_name)
    
    if not os.path.exists(image_path):
        print(f"[ERROR] Không tìm thấy ảnh tại: {image_path}")
        return
        
    print(f"\n[BƯỚC 1] Trích xuất khung lưới từ ảnh: {image_name}")
    debug_dir = os.path.join(test_image_dir, f"debug_{image_name.split('.')[0]}")
    warped_grid = find_sudoku_grid(image_path, output_size=450, debug_dir=debug_dir)
    
    if warped_grid is None:
        print("[FAIL] Trích xuất lưới thất bại.")
        return
        
    print("\n[BƯỚC 2] Cắt 81 ô bằng Smart Slicing")
    cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4, debug_dir=debug_dir)
    
    print("\n[BƯỚC 3] Khởi tạo mô hình nhận diện")
    model_dir = os.path.abspath(os.path.join(current_dir, "models"))
    onnx_path = os.path.join(model_dir, "digit_model.onnx")
    recognizer = SudokuRecognizer(model_path=onnx_path, target_size=(28, 28))
    
    if recognizer.net is None:
        print("\n[CẢNH BÁO MOCK MODE] Chưa nạp file ONNX thực tế. Các số dự đoán ngẫu nhiên sẽ không chính xác!")

    print("\n[BƯỚC 4] Nhận diện ma trận và lưu ảnh đối sánh ô")
    # Truyền debug_dir vào đây để yêu cầu lưu ảnh 81 ô con
    sudoku_matrix = recognizer.recognize_grid(cells_9x9, debug_dir=debug_dir)
    
    print("\n" + "=" * 30)
    print(" KẾT QUẢ MA TRẬN SUDOKU DỰ ĐOÁN")
    print("=" * 30)
    print_sudoku_grid(sudoku_matrix)
    print("=" * 30)
    print(f"[THÀNH CÔNG] Đã lưu 81 cặp ảnh đối sánh (Thô vs Đã dọn sạch) vào thư mục:")
    print(f" -> {os.path.join(debug_dir, 'cleaned_cells')}")

if __name__ == "__main__":
    run_integration_test("image1067.jpg")