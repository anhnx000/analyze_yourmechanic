import streamlit as st
import pandas as pd
import time
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from scraper_advanced import YourMechanicAdvancedScraper
import json

# Cấu hình trang
st.set_page_config(
    page_title="YourMechanic Price Analyzer",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .service-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .price-metric {
        background: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .sidebar-info {
        background: #e6f3ff;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Khởi tạo session state"""
    if 'scraper' not in st.session_state:
        st.session_state.scraper = YourMechanicAdvancedScraper()
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    if 'comparison_list' not in st.session_state:
        st.session_state.comparison_list = []

def display_header():
    """Hiển thị header"""
    st.markdown('<h1 class="main-header">🔧 YourMechanic Price Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("📊 **So sánh giá dịch vụ**")
    with col2:
        st.success("🎯 **Ước tính chính xác**")
    with col3:
        st.warning("🚗 **Theo từng loại xe**")
    with col4:
        st.error("📍 **Theo khu vực**")

def sidebar_vehicle_info():
    """Sidebar cho thông tin xe"""
    st.sidebar.markdown('<div class="sidebar-info"><h3>🚗 Thông tin xe của bạn</h3></div>', unsafe_allow_html=True)
    
    # Kiểm tra kết nối
    if st.sidebar.button("🔄 Kiểm tra kết nối"):
        with st.sidebar:
            with st.spinner("Đang kiểm tra..."):
                health = st.session_state.scraper.health_check()
                if health:
                    st.success("✅ Kết nối tốt!")
                else:
                    st.error("❌ Không thể kết nối")
    
    # Năm sản xuất
    current_year = datetime.now().year
    years = list(range(current_year, 1990, -1))
    selected_year = st.sidebar.selectbox(
        "📅 Năm sản xuất", 
        years, 
        index=4,
        help="Chọn năm sản xuất của xe"
    )
    
    # Hãng xe
    try:
        car_makes = st.session_state.scraper.get_vehicle_makes()
    except:
        car_makes = [
            "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
            "Audi", "Volkswagen", "Hyundai", "Kia", "Mazda", "Subaru", "Lexus"
        ]
    
    selected_make = st.sidebar.selectbox("🏭 Hãng xe", car_makes)
    
    # Model xe
    models_by_make = {
        "Toyota": ["Camry", "Corolla", "RAV4", "Highlander", "Prius", "Tacoma", "4Runner", "Sienna"],
        "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Fit", "Ridgeline", "Odyssey", "HR-V"],
        "Ford": ["F-150", "Focus", "Escape", "Explorer", "Mustang", "Edge", "Fusion", "Expedition"],
        "Chevrolet": ["Silverado", "Equinox", "Malibu", "Tahoe", "Cruze", "Traverse", "Impala", "Suburban"],
        "Nissan": ["Altima", "Sentra", "Rogue", "Pathfinder", "Maxima", "Titan", "Murano", "Versa"],
        "BMW": ["3 Series", "5 Series", "X3", "X5", "7 Series", "X1", "4 Series", "2 Series"],
        "Mercedes-Benz": ["C-Class", "E-Class", "S-Class", "GLC", "GLE", "A-Class", "CLA", "GLS"]
    }
    
    available_models = models_by_make.get(selected_make, ["Camry", "Accord", "F-150", "Silverado"])
    selected_model = st.sidebar.selectbox("🚙 Model", available_models)
    
    # Mã ZIP
    zip_code = st.sidebar.text_input(
        "📍 Mã ZIP", 
        value="10001", 
        help="Nhập mã ZIP để xem giá tại khu vực của bạn",
        max_chars=5
    )
    
    # Hiển thị thông tin xe đã chọn
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Xe đã chọn:**")
    st.sidebar.info(f"🚗 {selected_year} {selected_make} {selected_model}")
    st.sidebar.info(f"📍 Khu vực: {zip_code}")
    
    return selected_year, selected_make, selected_model, zip_code

def service_selection():
    """Giao diện chọn dịch vụ"""
    st.header("📋 Chọn dịch vụ cần báo giá")
    
    # Lấy danh mục dịch vụ
    try:
        categories = st.session_state.scraper.get_service_categories_from_website()
    except:
        categories = st.session_state.scraper._get_fallback_categories()
    
    # Tab cho các danh mục
    category_tabs = st.tabs(list(categories.keys()))
    selected_services = []
    
    for i, (category_name, services) in enumerate(categories.items()):
        with category_tabs[i]:
            st.subheader(f"{category_name} Services")
            
            # Checkbox cho từng dịch vụ
            for service in services:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.checkbox(service, key=f"service_{category_name}_{service}"):
                        selected_services.append(service)
                with col2:
                    if st.button("ℹ️", key=f"info_{category_name}_{service}", help="Thông tin dịch vụ"):
                        st.info(f"Dịch vụ: {service}")
    
    return selected_services

def price_analysis(results, vehicle_info):
    """Phân tích và hiển thị giá"""
    if not results:
        return
    
    st.header("💰 Phân tích giá dịch vụ")
    
    # Tạo DataFrame
    df = pd.DataFrame(results)
    
    # Metrics tổng quan
    col1, col2, col3, col4 = st.columns(4)
    
    total_min = df['min_price'].sum()
    total_max = df['max_price'].sum()
    total_avg = df['avg_price'].sum()
    service_count = len(df)
    
    with col1:
        st.metric("🔧 Số dịch vụ", service_count)
    with col2:
        st.metric("💵 Chi phí thấp nhất", f"${total_min:,}")
    with col3:
        st.metric("💰 Chi phí trung bình", f"${total_avg:,}")
    with col4:
        st.metric("💸 Chi phí cao nhất", f"${total_max:,}")
    
    # Biểu đồ so sánh giá
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart cho từng dịch vụ
        fig_bar = px.bar(
            df, 
            x='service', 
            y=['min_price', 'avg_price', 'max_price'],
            title="So sánh giá các dịch vụ",
            labels={'value': 'Giá ($)', 'variable': 'Loại giá'},
            color_discrete_map={
                'min_price': '#90EE90',
                'avg_price': '#FFD700', 
                'max_price': '#FF6B6B'
            }
        )
        fig_bar.update_xaxes(tickangle=45)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    with col2:
        # Pie chart phân bố chi phí
        fig_pie = px.pie(
            df,
            values='avg_price',
            names='service',
            title="Phân bố chi phí theo dịch vụ"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Bảng chi tiết
    st.subheader("📊 Chi tiết báo giá")
    
    display_df = df.copy()
    display_df['Giá thấp nhất'] = display_df['min_price'].apply(lambda x: f"${x:,}")
    display_df['Giá trung bình'] = display_df['avg_price'].apply(lambda x: f"${x:,}")
    display_df['Giá cao nhất'] = display_df['max_price'].apply(lambda x: f"${x:,}")
    
    final_df = display_df[['service', 'Giá thấp nhất', 'Giá trung bình', 'Giá cao nhất', 'labor_time']].copy()
    final_df.columns = ['Dịch vụ', 'Giá thấp nhất', 'Giá trung bình', 'Giá cao nhất', 'Thời gian ước tính']
    
    st.dataframe(final_df, use_container_width=True)
    
    # Nút thêm vào so sánh
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Lưu vào lịch sử"):
            st.session_state.search_history.append({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'vehicle': f"{vehicle_info[0]} {vehicle_info[1]} {vehicle_info[2]}",
                'services': len(results),
                'total_cost': total_avg,
                'results': results
            })
            st.success("✅ Đã lưu vào lịch sử!")
    
    with col2:
        if st.button("🔄 So sánh với tìm kiếm khác"):
            st.session_state.comparison_list.extend(results)
            st.success("✅ Đã thêm vào danh sách so sánh!")
    
    with col3:
        # Xuất CSV
        csv = final_df.to_csv(index=False)
        st.download_button(
            label="📥 Tải xuống CSV",
            data=csv,
            file_name=f"yourmechanic_quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )

def search_history():
    """Hiển thị lịch sử tìm kiếm"""
    if not st.session_state.search_history:
        st.info("📝 Chưa có lịch sử tìm kiếm nào.")
        return
    
    st.header("📚 Lịch sử tìm kiếm")
    
    for i, search in enumerate(reversed(st.session_state.search_history)):
        with st.expander(f"🔍 {search['timestamp']} - {search['vehicle']} ({search['services']} dịch vụ)"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Xe:** {search['vehicle']}")
                st.write(f"**Số dịch vụ:** {search['services']}")
            with col2:
                st.write(f"**Tổng chi phí TB:** ${search['total_cost']:,}")
                
            # Hiển thị kết quả
            if st.button(f"👁️ Xem chi tiết", key=f"view_{i}"):
                df = pd.DataFrame(search['results'])
                st.dataframe(df[['service', 'avg_price', 'labor_time']])

def main():
    """Hàm chính"""
    init_session_state()
    display_header()
    
    # Sidebar
    vehicle_info = sidebar_vehicle_info()
    selected_year, selected_make, selected_model, zip_code = vehicle_info
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Tìm kiếm giá", "📊 So sánh", "📚 Lịch sử"])
    
    with tab1:
        # Chọn dịch vụ
        selected_services = service_selection()
        
        # Nút tìm kiếm
        if st.button("🔍 Lấy báo giá ngay", type="primary", use_container_width=True):
            if not selected_services:
                st.warning("⚠️ Vui lòng chọn ít nhất một dịch vụ!")
            else:
                with st.spinner("🔄 Đang tìm kiếm giá từ YourMechanic..."):
                    results = []
                    progress_bar = st.progress(0)
                    
                    for i, service in enumerate(selected_services):
                        try:
                            pricing_info = st.session_state.scraper.search_service_pricing(
                                service, zip_code, str(selected_year), selected_make, selected_model
                            )
                            results.append(pricing_info)
                            progress_bar.progress((i + 1) / len(selected_services))
                            time.sleep(0.3)  # Tránh quá tải server
                        except Exception as e:
                            st.error(f"❌ Lỗi khi lấy giá cho {service}: {str(e)}")
                    
                    if results:
                        st.success(f"✅ Tìm thấy {len(results)} báo giá!")
                        price_analysis(results, vehicle_info)
    
    with tab2:
        st.header("🔄 So sánh giá dịch vụ")
        if st.session_state.comparison_list:
            df_compare = pd.DataFrame(st.session_state.comparison_list)
            
            # Biểu đồ so sánh
            fig = px.scatter(
                df_compare,
                x='service',
                y='avg_price',
                size='max_price',
                color='vehicle',
                title="So sánh giá trung bình các dịch vụ",
                hover_data=['min_price', 'max_price', 'labor_time']
            )
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Bảng so sánh
            st.dataframe(df_compare[['service', 'vehicle', 'avg_price', 'labor_time']])
            
            if st.button("🗑️ Xóa danh sách so sánh"):
                st.session_state.comparison_list = []
                st.experimental_rerun()
        else:
            st.info("📝 Chưa có dữ liệu để so sánh. Hãy thực hiện tìm kiếm và thêm vào so sánh.")
    
    with tab3:
        search_history()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📞 Liên hệ YourMechanic:**")
        st.write("Hotline: (844) 997-3624")
        st.write("Email: hi@yourmechanic.com")
    
    with col2:
        st.markdown("**🕒 Giờ hoạt động:**")
        st.write("T2-T6: 6AM-5PM PST")
        st.write("T7-CN: 7AM-4PM PST")
    
    with col3:
        st.markdown("**ℹ️ Lưu ý:**")
        st.write("Giá có thể thay đổi theo")
        st.write("tình trạng xe thực tế")

if __name__ == "__main__":
    main() 
