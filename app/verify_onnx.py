import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

model_path = "app/models/digit_model.onnx"

try:
    net = cv2.dnn.readNetFromONNX(model_path)
    print("--- BẮT ĐẦU KIỂM TRA ĐỘ CHÍNH XÁC ---")
    
    # Chúng ta sẽ thử nghiệm vẽ lần lượt từ số 1 đến số 9
    for test_digit in range(1, 10):
        # 1. Tạo một ảnh đen 28x28 px
        img = Image.new('L', (28, 28), color=0)
        draw = ImageDraw.Draw(img)
        
        # Sử dụng font mặc định để vẽ chữ số
        font = ImageFont.load_default()
        text = str(test_digit)
        
        # Tính toán căn giữa chữ số
        text_box = draw.textbbox((0, 0), text, font=font)
        text_w = text_box[2] - text_box[0]
        text_h = text_box[3] - text_box[1]
        pos_x = (28 - text_w) // 2
        pos_y = (28 - text_h) // 2 - 2
        
        # Vẽ chữ số màu trắng (255) lên nền đen (0)
        draw.text((pos_x, pos_y), text, fill=255, font=font)
        
        # Chuyển đổi sang mảng numpy để đưa vào OpenCV
        img_np = np.array(img, dtype=np.uint8)
        
        # 2. Tạo blob đầu vào và thực hiện suy luận
        blob = cv2.dnn.blobFromImage(img_np, scalefactor=1.0/255.0, size=(28, 28))
        net.setInput(blob)
        output = net.forward()
        
        # 3. Lấy ra chữ số dự đoán
        predicted_class = np.argmax(output[0])
        predicted_digit = predicted_class + 1
        
        # 4. Đối chiếu kết quả
        is_correct = (predicted_digit == test_digit)
        status = "✅ ĐÚNG" if is_correct else "❌ SAI"
        
        print(f"Ảnh vẽ số: {test_digit} | Mô hình dự đoán: {predicted_digit} -> {status}")
        
except Exception as e:
    print(f"Lỗi khi thực hiện kiểm tra: {e}")