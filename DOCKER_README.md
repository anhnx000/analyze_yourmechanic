# 🐳 Docker Setup cho YourMechanic Price Checker

Hướng dẫn đóng gói và chạy ứng dụng YourMechanic Price Checker bằng Docker.

## 📋 Yêu cầu

- Docker Desktop hoặc Docker Engine
- Docker Compose (tùy chọn, nhưng được khuyến nghị)

## 🚀 Cách sử dụng

### 1. Sử dụng Script Tự động (Khuyến nghị)

```bash
# Khởi động ứng dụng (tự động build và chạy)
./docker-run.sh start

# Xem logs
./docker-run.sh logs

# Dừng ứng dụng
./docker-run.sh stop

# Khởi động lại
./docker-run.sh restart

# Chỉ build image
./docker-run.sh build
```

### 2. Sử dụng Docker Compose

```bash
# Khởi động ứng dụng
docker-compose up -d

# Xem logs
docker-compose logs -f

# Dừng ứng dụng
docker-compose down

# Khởi động lại
docker-compose restart
```

### 3. Sử dụng Docker Commands

```bash
# Build image
docker build -t yourmechanic-app .

# Chạy container
docker run -d \
    --name yourmechanic-crawler \
    -p 8511:8501 \
    --restart unless-stopped \
    yourmechanic-app

# Xem logs
docker logs -f yourmechanic-crawler

# Dừng container
docker stop yourmechanic-crawler
docker rm yourmechanic-crawler
```

## 🌐 Truy cập ứng dụng

Sau khi khởi động thành công, truy cập ứng dụng tại:
**http://localhost:8511**

## 📝 Cấu hình

### Port Mapping
- **Cổng local**: 8511
- **Cổng container**: 8501
- **URL truy cập**: http://localhost:8511

### Biến môi trường

Có thể tùy chỉnh trong `docker-compose.yml`:
```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

## 🔧 Troubleshooting

### Lỗi port đã được sử dụng
```bash
# Kiểm tra tiến trình sử dụng port 8511
lsof -i :8511

# Hoặc thay đổi port trong docker-compose.yml
ports:
  - "8512:8501"  # Sử dụng port 8512 thay vì 8511
```

### Container không khởi động
```bash
# Xem logs để debug
docker logs yourmechanic-crawler

# Kiểm tra trạng thái container
docker ps -a
```

### Build lỗi
```bash
# Clean Docker cache
docker system prune -f

# Rebuild từ đầu
docker build --no-cache -t yourmechanic-app .
```

## 📁 Cấu trúc Docker Files

```
├── Dockerfile              # Định nghĩa Docker image
├── docker-compose.yml      # Cấu hình Docker Compose  
├── .dockerignore           # Files bị loại trừ khi build
├── docker-run.sh           # Script tiện ích
└── DOCKER_README.md        # Hướng dẫn này
```

## ⚡ Performance Tips

1. **Sử dụng Docker Compose** để quản lý dễ dàng hơn
2. **Mount volumes** cho development:
   ```yaml
   volumes:
     - .:/app
     - /app/__pycache__
   ```
3. **Health check** đã được cấu hình tự động
4. **Auto-restart** khi container crash

## 🔄 Development Mode

Để phát triển với hot-reload:

```yaml
# Thêm vào docker-compose.yml
volumes:
  - .:/app
  - /app/__pycache__
command: ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=poll"]
```

## 📊 Monitoring

Kiểm tra trạng thái container:
```bash
# Xem container đang chạy
docker ps

# Xem resource usage
docker stats yourmechanic-crawler

# Health check status
docker inspect yourmechanic-crawler | grep Health -A 10
```

---

**Lưu ý**: Đảm bảo Docker Desktop đang chạy trước khi thực hiện các lệnh trên. 
