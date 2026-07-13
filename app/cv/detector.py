import cv2
import numpy as np
import os
import shutil

def order_points(pts):
    pts = pts.reshape(4, 2)
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def perspective_transform(image, pts, output_size=450):
    rect = order_points(pts)
    dst = np.array([
        [0, 0],
        [output_size - 1, 0],
        [output_size - 1, output_size - 1],
        [0, output_size - 1]], dtype="float32")
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (output_size, output_size))
    return warped

def get_four_corners(contour):
    peri = cv2.arcLength(contour, True)
    for eps in np.linspace(0.01, 0.1, 50):
        approx = cv2.approxPolyDP(contour, eps * peri, True)
        if len(approx) == 4:
            if cv2.isContourConvex(approx):
                return approx
                
    hull = cv2.convexHull(contour)
    peri_hull = cv2.arcLength(hull, True)
    for eps in np.linspace(0.01, 0.1, 50):
        approx = cv2.approxPolyDP(hull, eps * peri_hull, True)
        if len(approx) == 4:
            return approx
            
    return None

def find_sudoku_grid(image_path, output_size=450, debug_dir=None):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Lỗi: Không thể đọc ảnh từ đường dẫn: {image_path}")
        return None
    orig = img.copy()
    
    # Bước 1: Chuyển ảnh xám
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if debug_dir:
        os.makedirs(debug_dir, exist_ok=True)
        cv2.imwrite(os.path.join(debug_dir, "step01_gray.jpg"), gray)
        
    # Bước 2: Cân bằng độ tương phản cục bộ (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    gray_enhanced = clahe.apply(gray)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step02_clahe.jpg"), gray_enhanced)
        
    # Bước 3: Làm mịn bằng Gaussian Blur để giảm nhiễu tần số cao
    blur = cv2.GaussianBlur(gray_enhanced, (5, 5), 0)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step03_blur.jpg"), blur)
        
    # Bước 4: Nhị phân hóa thích ứng
    thresh = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 19, 5
    )
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step04_thresh.jpg"), thresh)

    # Bước 5: Lọc hạt nhiễu nhỏ bằng toán tử Morphological Opening
    clean_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh_cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, clean_kernel)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step05_thresh_cleaned.jpg"), thresh_cleaned)

    # Tính toán kích thước kernel động dựa trên kích thước ảnh đầu vào
    height, width = thresh.shape
    h_size = max(15, width // 20)
    v_size = max(15, height // 20)
    
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (h_size, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, v_size))
    
    # Bước 6 & 7: Trích xuất các nét thẳng dài nằm ngang và dọc
    h_lines = cv2.morphologyEx(thresh_cleaned, cv2.MORPH_OPEN, h_kernel)
    v_lines = cv2.morphologyEx(thresh_cleaned, cv2.MORPH_OPEN, v_kernel)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step06_h_lines.jpg"), h_lines)
        cv2.imwrite(os.path.join(debug_dir, "step07_v_lines.jpg"), v_lines)
    
    # Bước 8: Ghép thành khung xương của lưới Sudoku
    grid_skeleton = cv2.add(h_lines, v_lines)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step08_skeleton.jpg"), grid_skeleton)
        
    # Bước 9: Giãn nở nhẹ để liên kết các giao điểm bị hở nét
    dilate_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    grid_skeleton_dilated = cv2.dilate(grid_skeleton, dilate_kernel, iterations=1)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step09_skeleton_dilated.jpg"), grid_skeleton_dilated)

    # Tìm đường bao lớn nhất trên khung xương
    contours, _ = cv2.findContours(grid_skeleton_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    sudoku_contour = None
    img_area = img.shape[0] * img.shape[1]
    used_fallback = False
    
    if len(contours) > 0 and cv2.contourArea(contours[0]) > (0.10 * img_area):
        sudoku_contour = get_four_corners(contours[0])

    # Cơ chế Dự phòng: Thử tìm góc trên ảnh nhị phân gốc nếu khung xương bị đứt gãy quá nhiều
    if sudoku_contour is None:
        print("Cảnh báo: Không tìm thấy góc trên Grid Skeleton. Chuyển sang tìm trên ảnh nhị phân gốc...")
        contours_orig, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours_orig = sorted(contours_orig, key=cv2.contourArea, reverse=True)
        if len(contours_orig) > 0 and cv2.contourArea(contours_orig[0]) > (0.10 * img_area):
            sudoku_contour = get_four_corners(contours_orig[0])
            used_fallback = True

    if sudoku_contour is None:
        print("Lỗi: Không tìm thấy góc của bảng Sudoku.")
        return None
        
    # Bước 10: Vẽ kết quả các góc tìm được lên ảnh gốc
    if debug_dir:
        debug_img = orig.copy()
        cv2.drawContours(debug_img, [sudoku_contour.astype(int)], -1, (0, 255, 0), 3)
        for point in sudoku_contour.reshape(4, 2):
            cv2.circle(debug_img, tuple(point.astype(int)), 10, (0, 0, 255), -1)
            
        method_str = "Fallback (Orig Thresh)" if used_fallback else "Grid Skeleton"
        cv2.putText(debug_img, f"Method: {method_str}", (15, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        cv2.imwrite(os.path.join(debug_dir, "step10_detected_corners.jpg"), debug_img)

    # Bước 11: Thực hiện biến đổi phối cảnh để nắn thẳng bảng Sudoku
    warped = perspective_transform(orig, sudoku_contour, output_size)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step11_warped_grid.jpg"), warped)
        
    return warped

# def extract_cells_smart(warped_grid, output_size=450, margin=4, debug_dir=None):
def extract_cells_smart(warped_grid, output_size=450, margin=2, debug_dir=None):
    # Thay đổi mặc định margin từ 4 xuống 2 để giữ tối đa nét chữ sát lề
    # Bước 12: Nhị phân hóa cục bộ trên ảnh đã nắn thẳng
    gray = cv2.cvtColor(warped_grid, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step12_warped_thresh.jpg"), thresh)
        
    # Bước 13 & 14: Tìm các đường lưới dọc và ngang cục bộ
    line_length = 15
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (line_length, 1))
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, line_length))
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel)
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step13_warped_h_lines.jpg"), h_lines)
        cv2.imwrite(os.path.join(debug_dir, "step14_warped_v_lines.jpg"), v_lines)
        
    # Bước 15: Tạo mặt nạ lưới và giãn nở để phủ kín các nét
    grid = cv2.add(h_lines, v_lines)
    grid = cv2.dilate(grid, cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)))
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step15_warped_grid_mask.jpg"), grid)
        
    # Bước 16: Đảo ngược ảnh (Vùng các ô vuông sẽ trở thành màu trắng trên nền đen)
    inv_grid = cv2.bitwise_not(grid)
    if debug_dir:
        cv2.imwrite(os.path.join(debug_dir, "step16_warped_inv_grid.jpg"), inv_grid)
        
    contours, _ = cv2.findContours(inv_grid, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    cell_polygons = []
    expected_area = (output_size // 9) ** 2  
    
    # Lọc các contour thỏa mãn diện tích của một ô Sudoku tiêu chuẩn
    for c in contours:
        area = cv2.contourArea(c)
        if (0.3 * expected_area) < area < (2.0 * expected_area):
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            if len(approx) == 4:
                M = cv2.moments(c)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cell_polygons.append({"pts": approx, "cx": cx, "cy": cy})

    # Vẽ sơ đồ các ô đa giác tìm thấy để debug
    if debug_dir:
        contour_debug = warped_grid.copy()
        for idx, cell in enumerate(cell_polygons):
            cv2.drawContours(contour_debug, [cell["pts"]], -1, (0, 255, 0), 2)
            cv2.putText(contour_debug, str(idx+1), (cell["cx"]-10, cell["cy"]+5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        cv2.imwrite(os.path.join(debug_dir, "step17_cell_contours.jpg"), contour_debug)

    if len(cell_polygons) != 81:
        print(f"Chuyển sang cắt lưới toán học (Fallback) do chỉ tìm thấy {len(cell_polygons)}/81 ô đa giác.")
        return fallback_extract_cells(warped_grid, output_size, margin)
        
    print("Sử dụng Transform cục bộ cho 81 ô.")
    # Sắp xếp các ô từ trên xuống dưới, từ trái sang phải
    cell_polygons.sort(key=lambda item: item["cy"])
    sorted_cells = []
    for i in range(0, 81, 9):
        row = cell_polygons[i:i+9]
        row.sort(key=lambda item: item["cx"])
        sorted_cells.extend(row)
        
    grid_cells = []
    idx = 0
    for r in range(9):
        row_cells = []
        for c in range(9):
            cell_pts = sorted_cells[idx]["pts"]
            idx += 1
            cell_warped = perspective_transform(warped_grid, cell_pts, output_size=50)
            cell_clean = cell_warped[margin:50-margin, margin:50-margin]
            row_cells.append(cell_clean)
        grid_cells.append(row_cells)
    return grid_cells

# def fallback_extract_cells(warped_grid, output_size=450, margin=4):
#     safe_margin = margin + 3 
#     cell_size = output_size // 9
#     grid_cells = []
#     for r in range(9):
#         row_cells = []
#         for c in range(9):
#             y1, y2 = r * cell_size, (r + 1) * cell_size
#             x1, x2 = c * cell_size, (c + 1) * cell_size
#             cell = warped_grid[y1:y2, x1:x2]
#             cell_clean = cell[safe_margin:cell_size-safe_margin, safe_margin:cell_size-safe_margin]
#             row_cells.append(cell_clean)
#         grid_cells.append(row_cells)
#     return grid_cells
def fallback_extract_cells(warped_grid, output_size=450, margin=2):
    # Hạ safe_margin xuống bằng đúng margin (2px) thay vì margin + 3 (7px)
    safe_margin = margin 
    cell_size = output_size // 9
    grid_cells = []
    for r in range(9):
        row_cells = []
        for c in range(9):
            y1, y2 = r * cell_size, (r + 1) * cell_size
            x1, x2 = c * cell_size, (c + 1) * cell_size
            cell = warped_grid[y1:y2, x1:x2]
            # Cắt biên thô rất nhẹ (chỉ bỏ 2px sát rìa ngoài cùng chứa lưới thật)
            cell_clean = cell[safe_margin:cell_size-safe_margin, safe_margin:cell_size-safe_margin]
            row_cells.append(cell_clean)
        grid_cells.append(row_cells)
    return grid_cells

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image_dir = os.path.abspath(os.path.join(current_dir, "..", "test_images"))
    
    image_name = "image1.jpg" 
    image_path = os.path.join(test_image_dir, image_name)
    
    # Tạo thư mục debug riêng biệt cho từng ảnh để tránh ghi đè lẫn nhau
    debug_output_dir = os.path.join(test_image_dir, f"debug_{image_name.split('.')[0]}")
    if os.path.exists(debug_output_dir):
        shutil.rmtree(debug_output_dir)
    os.makedirs(debug_output_dir)
    
    print(f"Bắt đầu xử lý ảnh: {image_path}")
    print(f"Toàn bộ tiến trình debug sẽ được ghi tại thư mục: {debug_output_dir}")
    
    warped_grid = find_sudoku_grid(image_path, output_size=450, debug_dir=debug_output_dir)
    
    if warped_grid is not None:
        cells_9x9 = extract_cells_smart(warped_grid, output_size=450, margin=4, debug_dir=debug_output_dir)
        cells_output_dir = os.path.join(test_image_dir, f"cells_{image_name.split('.')[0]}")
        if os.path.exists(cells_output_dir):
            shutil.rmtree(cells_output_dir)
        os.makedirs(cells_output_dir)
        
        for r in range(9):
            for c in range(9):
                cv2.imwrite(os.path.join(cells_output_dir, f"cell_{r}_{c}.jpg"), cells_9x9[r][c])
        print(f"[THÀNH CÔNG] Đã lưu 81 ô vào: {cells_output_dir}")