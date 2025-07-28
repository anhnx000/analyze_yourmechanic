import requests
from bs4 import BeautifulSoup
import json
import time
import re
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin, quote
from fake_useragent import UserAgent
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YourMechanicAdvancedScraper:
    def __init__(self):
        self.base_url = "https://www.yourmechanic.com"
        self.session = requests.Session()
        self.ua = UserAgent()
        
        # Thiết lập headers để giống trình duyệt thật
        self.session.headers.update({
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Cache để tránh request liên tục
        self.cache = {}
        
    def get_service_categories_from_website(self) -> Dict[str, List[str]]:
        """Lấy danh sách dịch vụ thực tế từ website"""
        try:
            response = self.session.get(f"{self.base_url}/services", timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            categories = {}
            
            # Tìm các section chứa danh mục dịch vụ
            service_sections = soup.find_all(['div', 'section'], class_=re.compile(r'service|category'))
            
            for section in service_sections:
                # Tìm tiêu đề danh mục
                category_header = section.find(['h2', 'h3', 'h4'], class_=re.compile(r'category|heading'))
                if category_header:
                    category_name = category_header.get_text(strip=True)
                    
                    # Tìm danh sách dịch vụ trong danh mục
                    service_links = section.find_all('a', href=re.compile(r'/services/'))
                    services = []
                    
                    for link in service_links:
                        service_name = link.get_text(strip=True)
                        if service_name and len(service_name) > 5:  # Filter out empty or very short text
                            services.append(service_name)
                    
                    if services:
                        categories[category_name] = services[:15]  # Limit to 15 services per category
            
            return categories if categories else self._get_fallback_categories()
            
        except Exception as e:
            logger.error(f"Error fetching service categories: {e}")
            return self._get_fallback_categories()
    
    def _get_fallback_categories(self) -> Dict[str, List[str]]:
        """Danh sách dịch vụ dự phòng nếu không thể scrape từ website"""
        return {
            "Battery": [
                "Car Battery Replacement",
                "Auxiliary Battery Replacement", 
                "Car Battery Cable Replacement",
                "Service Battery/cables"
            ],
            "Brakes": [
                "Brake Pad Replacement",
                "Brake Rotors/Discs Replacement",
                "Brake Caliper Replacement",
                "Brake System Flush",
                "Brake Master Cylinder Replacement",
                "ABS Speed Sensor Replacement"
            ],
            "Engine": [
                "Oil Change",
                "Air Filter Replacement",
                "Spark Plug Replacement",
                "Timing Belt Replacement",
                "Catalytic Converter Replacement",
                "Engine Oil and Filter Change"
            ],
            "Diagnostics": [
                "Check Engine Light is on Inspection",
                "Car is not starting Inspection",
                "Pre-purchase Car Inspection",
                "75 Point Safety Inspection",
                "AC is not working Inspection"
            ],
            "Transmission": [
                "Transmission Fluid Service",
                "CV Axle / Shaft Assembly Replacement",
                "Clutch Replacement",
                "Transfer Case Fluid Replacement"
            ],
            "Suspension": [
                "Shock Absorber Replacement",  
                "Strut Assembly Replacement",
                "Ball Joint Replacement (Front)",
                "Power Steering Pump Replacement"
            ]
        }
    
    def get_vehicle_makes(self) -> List[str]:
        """Lấy danh sách hãng xe từ website"""
        try:
            # Thử lấy từ trang quote hoặc service
            response = self.session.get(f"{self.base_url}/quote", timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm dropdown hoặc select cho hãng xe
            make_select = soup.find('select', attrs={'name': re.compile(r'make|brand', re.I)})
            if make_select:
                options = make_select.find_all('option')
                makes = [opt.get_text(strip=True) for opt in options if opt.get_text(strip=True)]
                return makes[1:]  # Skip first empty option
        except:
            pass
        
        # Fallback list
        return [
            "Toyota", "Honda", "Ford", "Chevrolet", "Nissan", "BMW", "Mercedes-Benz",
            "Audi", "Volkswagen", "Hyundai", "Kia", "Mazda", "Subaru", "Lexus",
            "Acura", "Infiniti", "Buick", "Cadillac", "GMC", "Jeep", "Ram", "Dodge",
            "Mitsubishi", "Volvo", "Land Rover", "Jaguar", "Porsche", "Mini"
        ]
    
    def search_service_pricing(self, service_name: str, zip_code: str = "10001", 
                              year: str = "2020", make: str = "Toyota", model: str = "Camry") -> Dict:
        """Tìm kiếm giá dịch vụ thực tế từ website"""
        
        cache_key = f"{service_name}_{zip_code}_{year}_{make}_{model}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Method 1: Thử tìm trang dịch vụ cụ thể
            service_url = self._find_service_page(service_name)
            if service_url:
                pricing_info = self._extract_pricing_from_service_page(
                    service_url, zip_code, year, make, model
                )
                if pricing_info:
                    self.cache[cache_key] = pricing_info
                    return pricing_info
            
            # Method 2: Thử sử dụng quote API
            quote_info = self._get_quote_via_api(service_name, zip_code, year, make, model)
            if quote_info:
                self.cache[cache_key] = quote_info
                return quote_info
            
            # Method 3: Fallback - estimated pricing
            estimated_pricing = self._get_estimated_pricing(service_name, year, make, model)
            self.cache[cache_key] = estimated_pricing
            return estimated_pricing
            
        except Exception as e:
            logger.error(f"Error getting pricing for {service_name}: {e}")
            return self._get_estimated_pricing(service_name, year, make, model)
    
    def _find_service_page(self, service_name: str) -> Optional[str]:
        """Tìm URL trang dịch vụ cụ thể"""
        # Chuẩn hóa tên dịch vụ thành URL slug
        slug = service_name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces and multiple hyphens
        
        potential_urls = [
            f"{self.base_url}/services/{slug}",
            f"{self.base_url}/services/{slug.replace('-replacement', '')}",
            f"{self.base_url}/services/{slug}-service",
        ]
        
        for url in potential_urls:
            try:
                response = self.session.head(url, timeout=10)
                if response.status_code == 200:
                    return url
            except:
                continue
        
        return None
    
    def _extract_pricing_from_service_page(self, url: str, zip_code: str, year: str, make: str, model: str) -> Optional[Dict]:
        """Trích xuất thông tin giá từ trang dịch vụ"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tìm thông tin giá
            price_elements = soup.find_all(text=re.compile(r'\$\d+'))
            prices = []
            
            for element in price_elements:
                # Extract numeric values from price strings
                price_matches = re.findall(r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)', element)
                for match in price_matches:
                    price = int(match.replace(',', '').split('.')[0])
                    if 20 <= price <= 5000:  # Reasonable price range
                        prices.append(price)
            
            if prices:
                min_price = min(prices)
                max_price = max(prices)
                avg_price = sum(prices) // len(prices)
                
                return {
                    "service": self._extract_service_name_from_url(url),
                    "vehicle": f"{year} {make} {model}",
                    "location": zip_code,
                    "min_price": min_price,
                    "max_price": max_price,
                    "avg_price": avg_price,
                    "labor_time": self._estimate_labor_time(avg_price),
                    "parts_included": "Varies by service",
                    "source": "service_page"
                }
        
        except Exception as e:
            logger.error(f"Error extracting pricing from {url}: {e}")
        
        return None
    
    def _get_quote_via_api(self, service_name: str, zip_code: str, year: str, make: str, model: str) -> Optional[Dict]:
        """Thử lấy báo giá qua API (nếu có)"""
        try:
            # Chuẩn bị data cho quote request
            quote_data = {
                'service': service_name,
                'zip': zip_code,
                'year': year,
                'make': make,
                'model': model
            }
            
            # Thử POST request tới quote endpoint
            quote_endpoints = [
                f"{self.base_url}/api/quote",
                f"{self.base_url}/quote/api",
                f"{self.base_url}/services/quote"
            ]
            
            for endpoint in quote_endpoints:
                try:
                    response = self.session.post(
                        endpoint, 
                        json=quote_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if 'price' in data or 'cost' in data:
                            return self._parse_api_response(data, service_name, year, make, model, zip_code)
                except:
                    continue
                    
        except Exception as e:
            logger.error(f"Error getting quote via API: {e}")
        
        return None
    
    def _get_estimated_pricing(self, service_name: str, year: str, make: str, model: str) -> Dict:
        """Ước tính giá dựa trên logic nghiệp vụ"""
        
        # Base pricing tham khảo từ thị trường
        base_prices = {
            # Engine services
            "oil change": {"min": 40, "max": 80, "avg": 60},
            "air filter replacement": {"min": 25, "max": 60, "avg": 42},
            "spark plug replacement": {"min": 80, "max": 200, "avg": 140},
            "timing belt replacement": {"min": 400, "max": 800, "avg": 600},
            "catalytic converter replacement": {"min": 800, "max": 2000, "avg": 1400},
            
            # Brake services  
            "brake pad replacement": {"min": 120, "max": 250, "avg": 185},
            "brake rotors replacement": {"min": 200, "max": 400, "avg": 300},
            "brake system flush": {"min": 70, "max": 120, "avg": 95},
            "brake caliper replacement": {"min": 300, "max": 600, "avg": 450},
            
            # Battery services
            "car battery replacement": {"min": 80, "max": 200, "avg": 140},
            "battery cable replacement": {"min": 50, "max": 150, "avg": 100},
            
            # Transmission services
            "transmission fluid service": {"min": 80, "max": 150, "avg": 115},
            "cv axle replacement": {"min": 300, "max": 600, "avg": 450},
            "clutch replacement": {"min": 800, "max": 1500, "avg": 1150},
            
            # Suspension services
            "shock absorber replacement": {"min": 200, "max": 400, "avg": 300},
            "strut assembly replacement": {"min": 300, "max": 600, "avg": 450},
            "ball joint replacement": {"min": 150, "max": 350, "avg": 250},
            
            # Diagnostics
            "inspection": {"min": 80, "max": 150, "avg": 115},
            "pre-purchase car inspection": {"min": 90, "max": 120, "avg": 105}
        }
        
        # Tìm giá tương ứng
        service_lower = service_name.lower()
        pricing = None
        
        for key, price in base_prices.items():
            if key in service_lower:
                pricing = price
                break
        
        # Nếu không tìm thấy, ước tính dựa trên loại dịch vụ
        if not pricing:
            if "replacement" in service_lower:
                if any(word in service_lower for word in ["engine", "transmission", "clutch"]):
                    pricing = {"min": 500, "max": 1500, "avg": 1000}
                elif any(word in service_lower for word in ["brake", "suspension", "steering"]):
                    pricing = {"min": 200, "max": 500, "avg": 350}
                else:
                    pricing = {"min": 100, "max": 300, "avg": 200}
            elif "service" in service_lower or "flush" in service_lower:
                pricing = {"min": 60, "max": 120, "avg": 90}
            elif "inspection" in service_lower:
                pricing = {"min": 80, "max": 150, "avg": 115}
            else:
                pricing = {"min": 75, "max": 200, "avg": 137}
        
        # Điều chỉnh giá theo năm và hãng xe
        multiplier = self._get_price_multiplier(year, make, model)
        
        return {
            "service": service_name,
            "vehicle": f"{year} {make} {model}",
            "location": "Estimated",
            "min_price": int(pricing["min"] * multiplier),
            "max_price": int(pricing["max"] * multiplier),
            "avg_price": int(pricing["avg"] * multiplier),
            "labor_time": self._estimate_labor_time(pricing["avg"]),
            "parts_included": "Varies by service",
            "source": "estimated"
        }
    
    def _get_price_multiplier(self, year: str, make: str, model: str) -> float:
        """Tính hệ số điều chỉnh giá theo xe"""
        multiplier = 1.0
        
        # Điều chỉnh theo năm
        try:
            year_int = int(year)
            if year_int < 2000:
                multiplier *= 0.9  # Xe rất cũ rẻ hơn
            elif year_int < 2010:
                multiplier *= 1.1  # Xe cũ đắt hơn do khó tìm phụ tùng
            elif year_int > 2020:
                multiplier *= 1.2  # Xe mới đắt hơn
        except:
            pass
        
        # Điều chỉnh theo hãng
        luxury_brands = ["BMW", "Mercedes-Benz", "Audi", "Lexus", "Acura", "Infiniti", "Jaguar", "Land Rover", "Porsche"]
        if make in luxury_brands:
            multiplier *= 1.4
        elif make in ["Toyota", "Honda", "Nissan", "Mazda"]:
            multiplier *= 0.9  # Xe Nhật rẻ hơn
        
        return multiplier
    
    def _estimate_labor_time(self, avg_price: float) -> str:
        """Ước tính thời gian làm việc dựa trên giá"""
        hours = max(0.5, avg_price / 100)  # Assuming $100/hour labor rate
        return f"{hours:.1f} giờ"
    
    def _extract_service_name_from_url(self, url: str) -> str:
        """Trích xuất tên dịch vụ từ URL"""
        parts = url.split('/')
        if len(parts) > 0:
            slug = parts[-1]
            # Convert slug back to readable name
            name = slug.replace('-', ' ').title()
            return name
        return "Unknown Service"
    
    def _parse_api_response(self, data: Dict, service_name: str, year: str, make: str, model: str, zip_code: str) -> Dict:
        """Parse API response thành format chuẩn"""
        price = data.get('price', data.get('cost', 0))
        
        return {
            "service": service_name,
            "vehicle": f"{year} {make} {model}",
            "location": zip_code,
            "min_price": int(price * 0.8),
            "max_price": int(price * 1.2),
            "avg_price": int(price),
            "labor_time": data.get('labor_time', self._estimate_labor_time(price)),
            "parts_included": data.get('parts_included', "Varies by service"),
            "source": "api"
        }
    
    def health_check(self) -> bool:
        """Kiểm tra kết nối tới website"""
        try:
            response = self.session.get(self.base_url, timeout=10)
            return response.status_code == 200
        except:
            return False 
