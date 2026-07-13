import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import onnx

# ==========================================
# 1. CẤU HÌNH & CHUẨN BỊ FONT CHỮ
# ==========================================
# Khai báo các font chữ phổ biến trên hệ điều hành để sinh dữ liệu.
# Bạn có thể bổ sung thêm các đường dẫn font .ttf khác nếu cần.
SYSTEM_FONTS = []
possible_paths = [
    # Windows
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\times.ttf",
    "C:\\Windows\\Fonts\\calibri.ttf",
    "C:\\Windows\\Fonts\\cour.ttf",
    "C:\\Windows\\Fonts\\georgia.ttf",
    "C:\\Windows\\Fonts\\verdana.ttf",
    # Linux (Ubuntu/Debian)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    # macOS
    "/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Times New Roman.ttf"
]

for path in possible_paths:
    if os.path.exists(path):
        SYSTEM_FONTS.append(path)

# Nếu không tìm thấy font hệ thống nào, sử dụng font mặc định của Pillow
if not SYSTEM_FONTS:
    print("Cảnh báo: Không tìm thấy font hệ thống .ttf tiêu chuẩn. Sẽ dùng font mặc định.")

# ==========================================
# 2. BỘ ĐỒNG BỘ SINH DỮ LIỆU TỰ ĐỘNG
# ==========================================
class PrintedDigitDataset(Dataset):
    def __init__(self, num_samples_per_digit=2000, is_train=True):
        self.num_samples_per_digit = num_samples_per_digit
        self.is_train = is_train
        self.data = []
        self.labels = []
        self._generate_dataset()

    def _generate_dataset(self):
        # Chúng ta phân loại từ 1 đến 9 (tương ứng nhãn từ 0 đến 8)
        for digit in range(1, 10):
            label = digit - 1
            for _ in range(self.num_samples_per_digit):
                # Tạo ảnh đen kích thước 28x28
                img = Image.new('L', (28, 28), color=0)
                draw = ImageDraw.Draw(img)
                
                # Chọn font và kích cỡ ngẫu nhiên
                font_size = random.randint(18, 24)
                if SYSTEM_FONTS:
                    font_path = random.choice(SYSTEM_FONTS)
                    try:
                        font = ImageFont.truetype(font_path, font_size)
                    except:
                        font = ImageFont.load_default()
                else:
                    font = ImageFont.load_default()

                # Vẽ chữ số căn giữa tương đối
                text = str(digit)
                # Lấy kích thước hộp chữ để căn giữa
                text_box = draw.textbbox((0, 0), text, font=font)
                text_w = text_box[2] - text_box[0]
                text_h = text_box[3] - text_box[1]
                
                # Thêm chút độ lệch vị trí ngẫu nhiên (jitter)
                pos_x = (28 - text_w) // 2 + random.randint(-2, 2)
                pos_y = (28 - text_h) // 2 - 2 + random.randint(-2, 2) # thường dịch lên một chút để tránh mất chân chữ
                
                draw.text((pos_x, pos_y), text, fill=255, font=font)

                # Các phép biến đổi tăng cường dữ liệu (Data Augmentation) cho ảnh huấn luyện
                if self.is_train:
                    # 1. Xoay ảnh nhẹ (từ -10 đến 10 độ)
                    angle = random.uniform(-10, 10)
                    img = img.rotate(angle, resample=Image.BICUBIC)
                    
                    # 2. Làm mờ nhẹ ngẫu nhiên (blur) để giả lập ảnh camera hơi out-focus
                    if random.random() < 0.3:
                        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.1, 0.8)))

                # Chuyển đổi thành mảng numpy và chuẩn hóa về dải [0, 1]
                img_np = np.array(img, dtype=np.float32) / 255.0
                # Thêm chiều kênh (channel dimension) thành (1, 28, 28)
                img_np = np.expand_dims(img_np, axis=0)

                self.data.append(img_np)
                self.labels.append(label)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return torch.tensor(self.data[idx]), torch.tensor(self.labels[idx], dtype=torch.long)

# ==========================================
# 3. ĐỊNH NGHĨA KIẾN TRÚC MẠNG CNN
# ==========================================
class SudokuDigitCNN(nn.Module):
    def __init__(self):
        super(SudokuDigitCNN, self).__init__()
        # Đầu vào: 1 x 28 x 28
        self.features = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=3, padding=1), # 16 x 28 x 28
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.MaxPool2d(2),                            # 16 x 14 x 14
            
            nn.Conv2d(16, 32, kernel_size=3, padding=1),# 32 x 14 x 14
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)                             # 32 x 7 x 7
        )
        self.classifier = nn.Sequential(
            nn.Linear(32 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 9)                           # 9 đầu ra tương ứng chữ số từ 1 đến 9
        )

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

# ==========================================
# 4. QUÁ TRÌNH HUẤN LUYỆN
# ==========================================
def train_model():
    print("Đang tạo tập dữ liệu huấn luyện và kiểm thử...")
    train_dataset = PrintedDigitDataset(num_samples_per_digit=3000, is_train=True)
    val_dataset = PrintedDigitDataset(num_samples_per_digit=500, is_train=False)

    train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Đang sử dụng thiết bị: {device}")

    model = SudokuDigitCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    epochs = 8
    print("Bắt đầu huấn luyện...")
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        epoch_loss = running_loss / len(train_loader.dataset)
        epoch_acc = (correct / total) * 100
        
        # Đánh giá trên tập Validation
        model.eval()
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for images, labels in val_loader:
                images, labels = images.to(device), labels.to(device)
                outputs = model(images)
                _, predicted = outputs.max(1)
                val_total += labels.size(0)
                val_correct += predicted.eq(labels).sum().item()
                
        val_acc = (val_correct / val_total) * 100
        print(f"Epoch [{epoch+1}/{epochs}] - Loss: {epoch_loss:.4f} - Train Acc: {epoch_acc:.2f}% - Val Acc: {val_acc:.2f}%")

    print("Huấn luyện hoàn tất.")
    return model

# ==========================================
# 5. XUẤT MODEL SANG ĐỊNH DẠNG ONNX
# ==========================================
def export_to_onnx(model, output_path="app/models/digit_model.onnx"):
    model.eval()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    device = next(model.parameters()).device
    dummy_input = torch.randn(1, 1, 28, 28, device=device)
    
    print(f"Đang xuất mô hình sang định dạng ONNX tại: {output_path}...")
    
    try:
        # Loại bỏ dynamic_axes để xuất mô hình dạng tĩnh (Static Shape: 1x1x28x28)
        torch.onnx.export(
            model, 
            dummy_input, 
            output_path, 
            export_params=True,        
            opset_version=15,          # Opset 15 hoạt động tốt với cơ chế Dynamo mới
            do_constant_folding=True,  
            input_names=['input'],     
            output_names=['output']
        )
        print("✅ Xuất mô hình ONNX thành công!")
    except Exception as e:
        print(f"❌ Lỗi trong quá trình xuất ONNX: {e}")

if __name__ == "__main__":
    trained_model = train_model()
    export_to_onnx(trained_model)