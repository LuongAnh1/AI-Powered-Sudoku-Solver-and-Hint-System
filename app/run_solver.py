import os
import sys
import time

# Thêm đường dẫn để Python nạp đúng các module trong thư mục app/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 1. Thử nghiệm nạp Module C++ cầu nối
try:
    import sudoku_solver_cpp
    print("✅ [INFO] Nạp thành công module giải Sudoku viết bằng C++!")
except ImportError as e:
    print(f"❌ [ERROR] Không thể nạp module C++: {e}")
    print("Vui lòng kiểm tra xem tệp .pyd đã được đặt đúng trong thư mục 'app/' chưa.")
    sys.exit(1)

from cv.detector import find_sudoku_grid, extract_cells_smart
from cv.recognizer import SudokuRecognizer

def print_grid(matrix, title="GRID"):
    print(f"\n--- {title} ---")
    for r in range(9):
        if r % 3 == 0 and r != 0:
            print("-" * 21)
        row_str = []
        for c in range(9):
            if c % 3 == 0 and c != 0:
                row_str.append("|")
            val = matrix[r][c]
            row_str.append(str(val) if val != 0 else ".")
        print(" ".join(row_str))

def main(image_name="image1062.jpg"):
    test_image_dir = os.path.join(current_dir, "test_images")
    image_path = os.path.join(test_image_dir, image_name)
    
    if not os.path.exists(image_path):
        print(f"❌ [ERROR] Không tìm thấy ảnh test tại: {image_path}")
        return

    # =========================================================
    # PHẦN 1: XỬ LÝ ẢNH & NHẬN DIỆN CHỮ SỐ (PYTHON COMPUTER VISION)
    # =========================================================
    print(f"\n[BƯỚC 1] Trích xuất lưới từ ảnh: {image_name}")
    warped_grid = find_sudoku_grid(image_path, output_size=450)
    if warped_grid is None:
        print("❌ [FAIL] Trích xuất khung lưới thất bại.")
        return

    print("[BƯỚC 2] Cắt 81 ô số bằng Smart Slicing")
    cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4)

    print("[BƯỚC 3] Nhận dạng chữ số sử dụng mô hình AI ONNX")
    onnx_path = os.path.join(current_dir, "models", "digit_model.onnx")
    recognizer = SudokuRecognizer(model_path=onnx_path)
    
    # Thực hiện nhận diện ma trận đề bài từ 81 ảnh ô con
    detected_matrix = recognizer.recognize_grid(cells_9x9)
    print_grid(detected_matrix, "MA TRẬN ĐỀ BÀI NHẬN DIỆN ĐƯỢC")

    # =========================================================
    # PHẦN 2: GIẢI SUDOKU BẰNG LÕI HIỆU NĂNG CAO (C++ ENGINE)
    # =========================================================
    print("\n[BƯỚC 4] Khởi tạo C++ Solver Engine...")
    engine = sudoku_solver_cpp.SolverEngine()
    
    print("[BƯỚC 5] Nạp ma trận đề bài vào C++ Engine...")
    engine.load_grid(detected_matrix)
    
    print("[BƯỚC 6] Thực hiện giải toàn bộ bài toán bằng C++...")
    start_time = time.perf_counter()
    engine.solve_full()
    end_time = time.perf_counter()
    
    # Trích xuất kết quả đã giải từ C++ về Python
    solved_matrix = engine.get_grid()
    
    print_grid(solved_matrix, "KẾT QUẢ GIẢI BẰNG LÕI C++ ENGINE")
    print(f"\n[THÀNH CÔNG] Thời gian giải của lõi C++: {(end_time - start_time) * 1000:.3f} ms")

if __name__ == "__main__":
    # Bạn có thể thay đổi tên ảnh kiểm thử tại đây
    main("image_web3.png")