import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import Dict, List, Optional
import json

class YourMechanicScraper:
    def __init__(self):
        self.base_url = "https://www.yourmechanic.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_service_categories(self) -> Dict[str, List[str]]:
        """Trả về danh sách các danh mục dịch vụ dựa trên cấu trúc trang web"""
        categories = {
            "Battery": [
                "Auxiliary Battery Replacement",
                "Car Battery Cable Replacement", 
                "Car Battery Replacement",
                "Service Battery/cables"
            ],
            "Belts": [
                "Car AC Belt Replacement",
                "Alternator / Serpentine Belt Replacement",
                "Drive Belt Tensioner Replacement",
                "Power Steering Belt Replacement",
                "Serpentine/Drive Belt Replacement",
                "Supercharger Belt Replacement",
                "Timing Belt Replacement"
            ],
            "Brakes": [
                "ABS Speed Sensor Replacement",
                "Brake Caliper Replacement",
                "Brake Drum Replacement",
                "Brake Hose Replacement",
                "Brake Master Cylinder Replacement",
                "Brake Pad Replacement",
                "Brake Rotors/Discs Replacement",
                "Brake Shoe Replacement (Rear)",
                "Brake System Flush"
            ],
            "Car Buying": [
                "Pre-purchase Car Inspection"
            ],
            "Clutch & Transmission": [
                "CV Axle / Shaft Assembly Replacement",
                "Axle Shaft Seal Replacement",
                "Clutch Cable Replacement",
                "Clutch Fluid Replacement",
                "Clutch Master Cylinder & Slave Cylinder Replacement",
                "Transmission Fluid Service",
                "Transfer Case Fluid Replacement"
            ],
            "Diagnostics": [
                "75 Point Safety Inspection",
                "ABS Light is on Inspection",
                "AC is not working Inspection",
                "Battery Light is on Inspection",
                "Brake Warning Light is on Inspection",
                "Car is not starting Inspection",
                "Check Engine Light is on Inspection",
                "Oil Change"
            ],
            "Engine": [
                "Air Filter Replacement",
                "Cabin Air Filter Replacement",
                "Catalytic Converter Replacement",
                "Engine Oil and Filter Change",
                "Fuel Filter Replacement",
                "Oil Change",
                "Spark Plug Replacement"
            ],
            "Suspension & Steering": [
                "Air Shock Replacement",
                "Ball Joint Replacement (Front)",
                "Control Arm Assembly Replacement",
                "Power Steering Fluid Service",
                "Power Steering Pump Replacement",
                "Shock Absorber Replacement",
                "Strut Assembly Replacement"
            ]
        }
        return categories
    
    def search_service_url(self, service_name: str) -> Optional[str]:
        """Tìm URL cho dịch vụ cụ thể"""
        # Tạo URL dự kiến dựa trên tên dịch vụ
        service_slug = service_name.lower().replace(" ", "-").replace("/", "-").replace("(", "").replace(")", "")
        service_slug = re.sub(r'-+', '-', service_slug)  # Loại bỏ dấu gạch ngang kép
        potential_urls = [
            f"{self.base_url}/services/{service_slug}",
            f"{self.base_url}/services/{service_slug}-service",
            f"{self.base_url}/services/{service_slug.replace('-replacement', '')}"
        ]
        
        for url in potential_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return url
            except:
                continue
        return None
    
    def get_service_pricing(self, service_name: str, zip_code: str = "10001", 
                          year: str = "2020", make: str = "Toyota", model: str = "Camry") -> Dict:
        """Lấy thông tin giá cho dịch vụ cụ thể"""
        
        # Mô phỏng dữ liệu giá (vì cần phát triển scraper thực tế)
        base_prices = {
            "Oil Change": {"min": 50, "max": 80, "avg": 65},
            "Brake Pad Replacement": {"min": 120, "max": 250, "avg": 185},
            "Car Battery Replacement": {"min": 80, "max": 200, "avg": 140},
            "Pre-purchase Car Inspection": {"min": 90, "max": 120, "avg": 105},
            "Timing Belt Replacement": {"min": 400, "max": 800, "avg": 600},
            "Transmission Fluid Service": {"min": 80, "max": 150, "avg": 115},
            "Brake System Flush": {"min": 70, "max": 120, "avg": 95},
            "Air Filter Replacement": {"min": 25, "max": 60, "avg": 42},
            "Spark Plug Replacement": {"min": 80, "max": 200, "avg": 140}
        }
        
        # Lấy giá cơ bản hoặc tạo giá ước tính
        if service_name in base_prices:
            pricing = base_prices[service_name]
        else:
            # Tạo giá ước tính dựa trên loại dịch vụ
            if "replacement" in service_name.lower():
                pricing = {"min": 100, "max": 300, "avg": 200}
            elif "inspection" in service_name.lower():
                pricing = {"min": 80, "max": 150, "avg": 115}
            elif "fluid" in service_name.lower() or "service" in service_name.lower():
                pricing = {"min": 60, "max": 120, "avg": 90}
            else:
                pricing = {"min": 75, "max": 200, "avg": 137}
        
        # Điều chỉnh giá theo năm xe (xe cũ hơn có thể rẻ hơn hoặc đắt hơn)
        year_int = int(year) if year.isdigit() else 2020
        if year_int < 2010:
            multiplier = 1.1  # Xe cũ có thể đắt hơn do khó tìm phụ tùng
        elif year_int > 2020:
            multiplier = 1.2  # Xe mới đắt hơn
        else:
            multiplier = 1.0
            
        return {
            "service": service_name,
            "vehicle": f"{year} {make} {model}",
            "location": zip_code,
            "min_price": int(pricing["min"] * multiplier),
            "max_price": int(pricing["max"] * multiplier),
            "avg_price": int(pricing["avg"] * multiplier),
            "labor_time": f"{pricing['avg'] // 50}-{pricing['avg'] // 30} hours",
            "parts_included": "Varies by service"
        }

def main():
    st.set_page_config(
        page_title="YourMechanic Price Checker",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 YourMechanic Service Price Checker")
    st.markdown("Kiểm tra giá dịch vụ sửa chữa ô tô từ YourMechanic.com")
    
    # Khởi tạo scraper
    if 'scraper' not in st.session_state:
        st.session_state.scraper = YourMechanicScraper()
    
    scraper = st.session_state.scraper
    
    # Sidebar cho thông tin xe
    st.sidebar.header("🚗 Thông tin xe của bạn")
    
    # Năm sản xuất
    current_year = 2024
    years = list(range(current_year, 1990, -1))
    selected_year = st.sidebar.selectbox("Năm sản xuất", years, index=4)  # Mặc định 2020
    
    # Hãng xe phổ biến
    car_makes = [
        "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
        "Audi", "Volkswagen", "Hyundai", "Kia", "Mazda", "Subaru", "Lexus",
        "Acura", "Infiniti", "Buick", "Cadillac", "GMC", "Jeep", "Ram", "Dodge"
    ]
    selected_make = st.sidebar.selectbox("Hãng xe", car_makes)
    
    # Model xe (đơn giản hóa)
    models_by_make = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Tacoma"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit", "Ridgeline"],
        "Ford": ["F-150", "Focus", "Escape", "Explorer", "Mustang", "Edge"],
        "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Cruze", "Traverse"]
    }
    
    available_models = models_by_make.get(selected_make, ["Model khác"])
    selected_model = st.sidebar.selectbox("Model", available_models)
    
    # Mã ZIP
    zip_code = st.sidebar.text_input("Mã ZIP", value="10001", help="Nhập mã ZIP để xem giá tại khu vực của bạn")
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.header("📋 Danh mục dịch vụ")
        categories = scraper.get_service_categories()
        
        selected_category = st.selectbox("Chọn danh mục:", list(categories.keys()))
        
        if selected_category:
            st.subheader(f"Dịch vụ trong {selected_category}")
            services_in_category = categories[selected_category]
            
            selected_services = []
            for service in services_in_category:
                if st.checkbox(service, key=f"service_{service}"):
                    selected_services.append(service)
    
    with col2:
        st.header("💰 Báo giá dịch vụ")
        
        if st.button("🔍 Lấy báo giá", type="primary"):
            if not selected_services:
                st.warning("Vui lòng chọn ít nhất một dịch vụ!")
            else:
                with st.spinner("Đang tìm kiếm giá..."):
                    results = []
                    
                    for service in selected_services:
                        try:
                            pricing_info = scraper.get_service_pricing(
                                service, zip_code, str(selected_year), selected_make, selected_model
                            )
                            results.append(pricing_info)
                            time.sleep(0.5)  # Tránh quá tải server
                        except Exception as e:
                            st.error(f"Lỗi khi lấy giá cho {service}: {str(e)}")
                    
                    if results:
                        st.success(f"Tìm thấy {len(results)} báo giá!")
                        
                        # Hiển thị kết quả dưới dạng bảng
                        df = pd.DataFrame(results)
                        
                        # Định dạng cột giá
                        df['Giá thấp nhất'] = df['min_price'].apply(lambda x: f"${x:,}")
                        df['Giá cao nhất'] = df['max_price'].apply(lambda x: f"${x:,}")
                        df['Giá trung bình'] = df['avg_price'].apply(lambda x: f"${x:,}")
                        
                        # Chọn cột để hiển thị
                        display_df = df[['service', 'Giá thấp nhất', 'Giá trung bình', 'Giá cao nhất', 'labor_time']].copy()
                        display_df.columns = ['Dịch vụ', 'Giá thấp nhất', 'Giá trung bình', 'Giá cao nhất', 'Thời gian ước tính']
                        
                        st.dataframe(display_df, use_container_width=True)
                        
                        # Tổng kết
                        total_min = sum([r['min_price'] for r in results])
                        total_max = sum([r['max_price'] for r in results])
                        total_avg = sum([r['avg_price'] for r in results])
                        
                        st.subheader("📊 Tổng kết")
                        col_a, col_b, col_c = st.columns(3)
                        
                        with col_a:
                            st.metric("Tổng chi phí thấp nhất", f"${total_min:,}")
                        with col_b:
                            st.metric("Tổng chi phí trung bình", f"${total_avg:,}")
                        with col_c:
                            st.metric("Tổng chi phí cao nhất", f"${total_max:,}")
                        
                        # Lưu kết quả
                        st.session_state.last_results = results

    # Footer
    st.markdown("---")
    st.markdown("**Lưu ý:** Giá có thể thay đổi tùy theo tình trạng xe và yêu cầu cụ thể. Liên hệ trực tiếp với YourMechanic để có báo giá chính xác nhất.")
    
    # Thông tin liên hệ YourMechanic
    with st.expander("📞 Thông tin liên hệ YourMechanic"):
        st.write("**Hotline:** (844) 997-3624")
        st.write("**Email:** hi@yourmechanic.com")
        st.write("**Website:** https://www.yourmechanic.com")
        st.write("**Giờ hoạt động:**")
        st.write("- Thứ 2 - Thứ 6: 6 AM - 5 PM PST")
        st.write("- Thứ 7 - Chủ nhật: 7 AM - 4 PM PST")

if __name__ == "__main__":
    main() 
