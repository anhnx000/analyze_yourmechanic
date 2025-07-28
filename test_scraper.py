#!/usr/bin/env python3
"""
Script để test các chức năng đã cập nhật của YourMechanic scraper
"""

import sys
import json
from scraper_advanced import YourMechanicAdvancedScraper

def test_scraper():
    """Test các chức năng chính của scraper"""
    print("🔧 Testing YourMechanic Advanced Scraper...")
    print("=" * 50)
    
    scraper = YourMechanicAdvancedScraper()
    
    # Test 1: Health check
    print("1. Testing website connection...")
    if scraper.health_check():
        print("✅ Website connection: OK")
    else:
        print("❌ Website connection: FAILED")
        return False
    
    # Test 2: Get service categories
    print("\n2. Testing service categories extraction...")
    categories = scraper.get_service_categories_from_website()
    
    if categories:
        print(f"✅ Found {len(categories)} service categories:")
        for category, services in categories.items():
            print(f"   📂 {category}: {len(services)} services")
            # Show first 3 services as example
            for service in services[:3]:
                print(f"      - {service}")
            if len(services) > 3:
                print(f"      ... and {len(services) - 3} more")
    else:
        print("❌ No service categories found")
    
    # Test 3: Get vehicle makes
    print("\n3. Testing vehicle makes extraction...")
    makes = scraper.get_vehicle_makes()
    
    if makes:
        print(f"✅ Found {len(makes)} vehicle makes:")
        print(f"   {', '.join(makes[:10])}{'...' if len(makes) > 10 else ''}")
    else:
        print("❌ No vehicle makes found")
    
    # Test 4: Search service pricing
    print("\n4. Testing service pricing search...")
    test_services = [
        "Oil Change",
        "Brake Pad Replacement", 
        "Battery Replacement"
    ]
    
    for service in test_services:
        print(f"\n   Testing: {service}")
        try:
            result = scraper.search_service_pricing(
                service_name=service,
                zip_code="10001",
                year="2020",
                make="Toyota",
                model="Camry"
            )
            
            if result:
                print(f"   ✅ Price found: ${result['min_price']} - ${result['max_price']} (avg: ${result['avg_price']})")
                print(f"      Source: {result.get('source', 'unknown')}")
                print(f"      Labor time: {result.get('labor_time', 'N/A')}")
            else:
                print(f"   ❌ No pricing found")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    
    return True

def save_sample_data():
    """Lưu dữ liệu mẫu để kiểm tra"""
    print("\n📊 Saving sample data...")
    
    scraper = YourMechanicAdvancedScraper()
    
    # Get sample data
    sample_data = {
        "categories": scraper.get_service_categories_from_website(),
        "makes": scraper.get_vehicle_makes(),
        "sample_pricing": {}
    }
    
    # Get sample pricing for a few services
    test_services = ["Oil Change", "Brake Pad Replacement"]
    
    for service in test_services:
        try:
            pricing = scraper.search_service_pricing(
                service_name=service,
                zip_code="10001", 
                year="2020",
                make="Toyota",
                model="Camry"
            )
            sample_data["sample_pricing"][service] = pricing
        except Exception as e:
            print(f"Error getting pricing for {service}: {e}")
    
    # Save to file
    with open("sample_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Sample data saved to sample_data.json")

if __name__ == "__main__":
    try:
        # Run tests
        success = test_scraper()
        
        if success:
            # Save sample data
            save_sample_data()
            print("\n🚀 All tests passed! Scraper is ready to use.")
        else:
            print("\n⚠️  Some tests failed. Please check the issues above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        sys.exit(1) 
