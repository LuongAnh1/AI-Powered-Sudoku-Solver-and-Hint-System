import cv2
import numpy as np

model_path = "app/models/digit_model.onnx"

try:
    # 1. Tải mô hình bằng module DNN của OpenCV
    net = cv2.dnn.readNetFromONNX(model_path)
    print("✅ Tải mô hình ONNX bằng OpenCV thành công!")
    
    # 2. Tạo một ảnh giả lập (dummy input) 28x28 px
    dummy_img = np.random.randint(0, 255, (28, 28), dtype=np.uint8)
    
    # 3. Chuyển đổi ảnh thành blob đầu vào (Đã sửa từ scale sang scalefactor)
    blob = cv2.dnn.blobFromImage(dummy_img, scalefactor=1.0/255.0, size=(28, 28))
    
    # 4. Chạy thử nghiệm suy luận
    net.setInput(blob)
    output = net.forward()
    
    print("✅ Chạy thử nghiệm suy luận thành công!")
    print(f"Kích thước đầu ra: {output.shape} (Mong muốn: 1x9)")
    print(f"Kết quả dự đoán mẫu: {output}")
    
except Exception as e:
    print(f"❌ Có lỗi xảy ra khi kiểm tra mô hình: {e}")