#!/bin/bash

# YourMechanic Docker Runner Script
# Script để build và chạy ứng dụng YourMechanic trong Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${PURPLE}🚀 YourMechanic Docker Runner${NC}"
    echo -e "${PURPLE}==========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker chưa được cài đặt. Vui lòng cài đặt Docker trước."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_warning "Docker Compose chưa được cài đặt. Sẽ sử dụng docker run thay thế."
        return 1
    fi
    
    return 0
}

# Build Docker image
build_image() {
    print_info "Đang build Docker image..."
    print_info "Platform: linux/amd64"
    
    docker build --platform linux/amd64 -t yourmechanic-app .
    
    print_success "Build thành công!"
}

# Run with Docker Compose
run_with_compose() {
    print_info "Đang khởi động ứng dụng với Docker Compose..."
    docker-compose up -d
    print_success "Ứng dụng đã được khởi động!"
    print_info "🌐 Truy cập ứng dụng tại: http://localhost:8511"
    print_info "📊 Giao diện có biểu đồ và scraping nâng cao"
}

# Run with Docker
run_with_docker() {
    print_info "Đang khởi động ứng dụng với Docker..."
    
    local container_name="yourmechanic-crawler"
    
    # Stop existing container if running
    if docker ps -q -f name=$container_name | grep -q .; then
        print_warning "Đang dừng container cũ: $container_name"
        docker stop $container_name
        docker rm $container_name
    fi
    
    # Run container
    docker run -d \
        --name $container_name \
        -p 8511:8501 \
        --restart unless-stopped \
        --memory=1g \
        -e PYTHONUNBUFFERED=1 \
        yourmechanic-app
        
    print_success "Ứng dụng đã được khởi động!"
    print_info "🌐 Truy cập ứng dụng tại: http://localhost:8511"
    print_info "📊 Giao diện có biểu đồ và scraping nâng cao"
}

# Stop containers
stop_containers() {
    print_info "Đang dừng các container..."
    
    if check_docker && command -v docker-compose &> /dev/null; then
        docker-compose down
    else
        if docker ps -q -f name=yourmechanic-crawler | grep -q .; then
            docker stop yourmechanic-crawler
            docker rm yourmechanic-crawler
        fi
    fi
    
    print_success "Đã dừng tất cả container!"
}

# Show logs
show_logs() {
    if docker ps -q -f name=yourmechanic-crawler | grep -q .; then
        print_info "Hiển thị logs của container..."
        docker logs -f yourmechanic-crawler
    else
        print_error "Container không đang chạy!"
    fi
}

# Monitor resources
monitor_resources() {
    if docker ps -q -f name=yourmechanic-crawler | grep -q .; then
        print_info "📊 Theo dõi tài nguyên container..."
        print_warning "⚠️  Nhấn Ctrl+C để thoát"
        docker stats yourmechanic-crawler
    else
        print_error "Container không đang chạy!"
    fi
}

# Main function
main() {
    print_header
    
    # Check arguments
    case "${1:-}" in
        "build")
            check_docker
            build_image
            ;;
        "start"|"run")
            check_docker
            build_image
            if check_docker && command -v docker-compose &> /dev/null; then
                run_with_compose
            else
                run_with_docker
            fi
            ;;
        "stop")
            check_docker
            stop_containers
            ;;
        "logs")
            check_docker
            show_logs
            ;;
        "monitor"|"stats")
            check_docker
            monitor_resources
            ;;
        "restart")
            check_docker
            stop_containers
            sleep 2
            build_image
            if check_docker && command -v docker-compose &> /dev/null; then
                run_with_compose
            else
                run_with_docker
            fi
            ;;
        *)
            echo ""
            print_info "Cách sử dụng: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  build    - Build Docker image"
            echo "  start    - Build và khởi động ứng dụng"
            echo "  stop     - Dừng ứng dụng"
            echo "  restart  - Khởi động lại ứng dụng"
            echo "  logs     - Xem logs của ứng dụng"
            echo "  monitor  - Theo dõi tài nguyên container"
            echo ""
            print_info "Ví dụ:"
            echo "  $0 start    # Chạy ứng dụng"
            echo ""
            print_info "🌟 Tính năng:"
            echo "   • 📊 Biểu đồ Plotly interactive"
            echo "   • 🤖 Selenium scraping với Chrome headless"
            echo "   • 📈 Phân tích giá nâng cao"
            echo "   • 💾 Lưu lịch sử và so sánh"
            echo ""
            print_warning "⚠️  Yêu cầu tối thiểu: 2GB RAM"
            echo ""
            ;;
    esac
}

# Run main function
main "$@" 
