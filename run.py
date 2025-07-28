#!/usr/bin/env python3
"""
YourMechanic Price Checker Launcher
Chạy ứng dụng Streamlit để kiểm tra giá dịch vụ từ YourMechanic.com
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_requirements():
    """Kiểm tra xem các thư viện cần thiết đã được cài đặt chưa"""
    try:
        import streamlit
        import requests
        import beautifulsoup4
        import pandas
        import plotly
        print("✅ Tất cả thư viện đã được cài đặt")
        return True
    except ImportError as e:
        print(f"❌ Thiếu thư viện: {e}")
        print("🔧 Chạy lệnh sau để cài đặt: pip install -r requirements.txt")
        return False

def main():
    """Hàm chính"""
    print("🔧 YourMechanic Price Checker")
    print("=" * 50)
    
    # Kiểm tra thư viện
    if not check_requirements():
        sys.exit(1)
    
    # Chọn phiên bản app
    print("\n📱 Chọn phiên bản ứng dụng:")
    print("1. Phiên bản cơ bản (app.py)")
    print("2. Phiên bản nâng cao với biểu đồ (app_advanced.py)")
    
    while True:
        choice = input("\nNhập lựa chọn (1 hoặc 2): ").strip()
        if choice == "1":
            app_file = "app.py"
            break
        elif choice == "2":
            app_file = "app_advanced.py"
            break
        else:
            print("❌ Vui lòng chọn 1 hoặc 2")
    
    # Kiểm tra file tồn tại
    if not Path(app_file).exists():
        print(f"❌ Không tìm thấy file {app_file}")
        sys.exit(1)
    
    print(f"\n🚀 Đang khởi động {app_file}...")
    
    # Khởi động Streamlit
    try:
        # Mở trình duyệt sau 2 giây
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:8501")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Chạy Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_file,
            "--server.headless", "false",
            "--server.fileWatcherType", "none",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n\n👋 Tạm biệt!")
    except Exception as e:
        print(f"❌ Lỗi khi khởi động ứng dụng: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
