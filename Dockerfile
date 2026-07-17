# =========================================================
# GIAI ĐOẠN 1: BUILDER (Chỉ dùng để biên dịch C++)
# =========================================================
FROM python:3.12-slim AS builder

# 1. Cài đặt các công cụ biên dịch bắt buộc (Thêm cờ --no-install-recommends)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 2. TỐI ƯU CACHE: Sao chép requirements và cài pybind11 TRƯỚC
COPY requirements.txt .
RUN pip install --no-cache-dir pybind11

# 3. Sao chép file cấu hình và thư mục mã nguồn C++ SAU
COPY CMakeLists.txt .
COPY src/ ./src/

# 4. Tiến hành loại bỏ cờ tĩnh, biên dịch và nén file .so (bằng lệnh strip)
RUN sed -i 's/-static-libgcc//g' CMakeLists.txt || true && \
    sed -i 's/-static-libstdc++//g' CMakeLists.txt || true && \
    sed -i 's/-static//g' CMakeLists.txt || true && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc) && \
    strip sudoku_solver_cpp*.so || true


# =========================================================
# GIAI ĐOẠN 2: RUNTIME (Bản chạy thực tế - Siêu nhẹ)
# =========================================================
FROM python:3.12-slim

# 1. Chỉ cài đặt thư viện chạy ngầm tối giản cần cho OpenCV (Thêm cờ --no-install-recommends)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# 2. TỐI ƯU CACHE: Cài đặt thư viện Python trước khi sao chép toàn bộ code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn python-multipart

# 3. Chỉ sao chép mã nguồn Python và Model AI của ứng dụng vào sau cùng
COPY app/ ./app/

# 4. SAO CHÉP CHỈ FILE BIÊN DỊCH .so ĐÃ BIÊN DỊCH TỪ GIAI ĐOẠN 1 SANG
COPY --from=builder /workspace/build/sudoku_solver_cpp*.so ./app/

WORKDIR /workspace/app

EXPOSE 8000

# Khởi chạy server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]