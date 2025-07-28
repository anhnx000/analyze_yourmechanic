# YourMechanic Price Checker 🔧

Ứng dụng web để kiểm tra và phân tích giá dịch vụ sửa chữa ô tô từ YourMechanic.com

## ✨ Tính năng

- 🔍 Tìm kiếm giá dịch vụ theo:
  - Năm sản xuất xe
  - Hãng xe
  - Model xe
  - Mã ZIP code
- 📊 Biểu đồ phân tích giá với Plotly
- 💾 Lưu lịch sử tìm kiếm
- 🔄 So sánh giá giữa các lần tìm kiếm
- 🤖 Selenium scraping với Chrome headless
- 📈 Phân tích giá nâng cao

## 🚀 Cài đặt

### Yêu cầu

- Python 3.9+
- pip
- Chrome/Chromium (cho Selenium)
- 2GB RAM trống

### Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Chạy ứng dụng

```bash
python run.py
```

Hoặc:

```bash
streamlit run app_advanced.py
```

### 🐳 Sử dụng Docker

Xem hướng dẫn chi tiết trong [DOCKER_README.md](DOCKER_README.md)

```bash
# Build và chạy với Docker
./docker-run.sh start

# Hoặc sử dụng Docker Compose
docker-compose up -d
```

## 📁 Cấu trúc Project

```
.
├── app_advanced.py         # Ứng dụng Streamlit chính
├── scraper_advanced.py     # Module scraping
├── requirements.txt        # Python dependencies
├── run.py                 # Script khởi động
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── docker-run.sh         # Docker helper script
├── .dockerignore         # Docker ignore patterns
└── README.md             # Tài liệu này
```

## 🔧 Troubleshooting

### Lỗi thường gặp

1. **Chrome/Chromedriver không tương thích**
   ```
   Giải pháp: Cài đặt Chrome và chromedriver cùng version
   ```

2. **Port 8501 đã được sử dụng**
   ```
   Giải pháp: Dừng process đang sử dụng port hoặc đổi port khác
   ```

3. **Thiếu RAM**
   ```
   Giải pháp: Đảm bảo có ít nhất 2GB RAM trống
   ```

### Debug Mode

```bash
streamlit run app_advanced.py --server.headless false --server.fileWatcherType poll
```

## 📝 Ghi chú

- Ứng dụng sử dụng Selenium với Chrome headless để scraping
- Cần ít nhất 2GB RAM để chạy tốt
- Nên sử dụng Docker để tránh các vấn đề về môi trường

## 🤝 Đóng góp

1. Fork project
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

MIT License - xem [LICENSE](LICENSE) để biết thêm chi tiết

## 🙏 Credits

- [Streamlit](https://streamlit.io/)
- [Selenium](https://www.selenium.dev/)
- [Plotly](https://plotly.com/)
- [YourMechanic](https://www.yourmechanic.com/) 
