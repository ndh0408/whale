# Wheel of Names - Gia Nguyễn APT

Ứng dụng web Wheel of Names cho công ty Gia Nguyễn APT, cho phép quay vòng chọn người thắng ngẫu nhiên từ danh sách người chơi.

## Tính năng

- Nhập nhiều tên người chơi cùng lúc (phân cách bằng dấu phẩy hoặc xuống dòng)
- Hiển thị danh sách người chơi
- Vòng quay animation với Canvas
- Chọn người thắng ngẫu nhiên
- Giao diện thân thiện và dễ sử dụng

## Yêu cầu hệ thống

- Python 3.7 trở lên
- Flask
- Modern web browser

## Cài đặt

1. Clone repository:
```bash
git clone [repository-url]
cd wheel-of-names
```

2. Tạo môi trường ảo và cài đặt dependencies:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

3. Thay thế logo:
- Đặt logo của công ty vào thư mục `static/logo.png`

## Chạy ứng dụng

```bash
python app.py
```

Truy cập ứng dụng tại: http://localhost:5000

## Sử dụng

1. Truy cập trang chủ và nhập tên người chơi
2. Xem danh sách người chơi đã nhập
3. Bắt đầu quay vòng và chọn người thắng
4. Có thể reset để bắt đầu lại từ đầu

## Bảo mật

- Thay đổi `secret_key` trong `app.py` trước khi triển khai
- Không lưu trữ dữ liệu nhạy cảm trong session

## Giấy phép

© 2024 Gia Nguyễn APT. All rights reserved. 