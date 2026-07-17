# =========================================================
# GIAI ĐOẠN 1: BUILDER (Chỉ dùng để biên dịch C++)
# =========================================================
FROM python:3.12-slim AS builder

# Cài đặt các công cụ biên dịch bắt buộc
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Sao chép file cấu hình và thư mục mã nguồn C++
COPY CMakeLists.txt .
COPY src/ ./src/
COPY requirements.txt .

# Cài đặt pybind11 cần cho việc biên dịch
RUN pip install --no-cache-dir pybind11

# Tiến hành loại bỏ cờ tĩnh và biên dịch ra file .so
RUN sed -i 's/-static-libgcc//g' CMakeLists.txt || true && \
    sed -i 's/-static-libstdc++//g' CMakeLists.txt || true && \
    sed -i 's/-static//g' CMakeLists.txt || true && \
    mkdir build && cd build && \
    cmake .. && \
    make -j$(nproc)


# =========================================================
# GIAI ĐOẠN 2: RUNTIME (Bản chạy thực tế - Siêu nhẹ)
# =========================================================
FROM python:3.12-slim

# Chỉ cài đặt thư viện chạy ngầm tối giản cần cho OpenCV
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Sao chép và cài đặt các thư viện Python cần thiết
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn python-multipart

# Chỉ sao chép mã nguồn Python và Model AI của ứng dụng
COPY app/ ./app/

# SAO CHÉP CHỈ FILE BIÊN DỊCH .so TỪ GIAI ĐOẠN 1 SANG
COPY --from=builder /workspace/build/sudoku_solver_cpp*.so ./app/

WORKDIR /workspace/app

EXPOSE 8000

# Khởi chạy server
CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]