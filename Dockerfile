# Sử dụng Python 3.9 slim làm base image
FROM --platform=linux/amd64 python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các package hệ thống cần thiết
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements trước để tận dụng Docker layer caching
COPY requirements.txt .

# Cài đặt Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Expose cổng 8501 (cổng mặc định của Streamlit)
EXPOSE 8501

# Tạo thư mục cho Streamlit config
RUN mkdir -p ~/.streamlit

# Tạo file config cho Streamlit để tắt các thông báo không cần thiết
RUN echo "\
[general]\n\
email = \"\"\n\
" > ~/.streamlit/credentials.toml

RUN echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
enableXsrfProtection = false\n\
fileWatcherType = \"none\"\n\
" > ~/.streamlit/config.toml

# Thiết lập health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Chạy ứng dụng Streamlit Advanced
CMD ["streamlit", "run", "app_advanced.py", "--server.port=8501", "--server.address=0.0.0.0"] 
