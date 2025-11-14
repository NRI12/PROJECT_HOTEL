# Hotel Booking Backend API

Backend API cho hệ thống đặt phòng khách sạn sử dụng Flask.

## Công nghệ sử dụng

- **Framework**: Flask 3.0
- **Database**: MySQL + SQLAlchemy ORM
- **Authentication**: JWT (Flask-JWT-Extended)
- **Validation**: Marshmallow
- **Payment**: VNPay, Momo
- **Cloud Storage**: Cloudinary
- **Email**: Flask-Mail

## Cài đặt

### 1. Clone repository
```bash
git clone <repository-url>
cd hotel_booking_backend
```

### 2. Tạo môi trường ảo
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường
```bash
cp .env.example .env
# Chỉnh sửa file .env với thông tin của bạn
```

### 5. Khởi tạo database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 6. Chạy ứng dụng
```bash
python run.py
```

API sẽ chạy tại: http://localhost:5000

## Cấu trúc dự án
```
hotel_booking_backend/
├── app/                    # Thư mục chính của ứng dụng
│   ├── models/            # Các model database
│   ├── controllers/       # Business logic
│   ├── routes/           # API endpoints
│   ├── services/         # External services
│   ├── middleware/       # Middleware functions
│   ├── utils/            # Utility functions
│   └── schemas/          # Validation schemas
├── config/               # Configuration files
├── migrations/           # Database migrations
├── tests/               # Unit tests
└── uploads/             # Upload directory
```

## API Endpoints

### Authentication
- POST /api/auth/register - Đăng ký tài khoản
- POST /api/auth/login - Đăng nhập
- POST /api/auth/refresh - Refresh token
- POST /api/auth/forgot-password - Quên mật khẩu
- POST /api/auth/reset-password - Đặt lại mật khẩu

### Hotels
- GET /api/hotels - Danh sách khách sạn
- GET /api/hotels/:id - Chi tiết khách sạn
- POST /api/hotels - Tạo khách sạn mới (owner)
- PUT /api/hotels/:id - Cập nhật khách sạn (owner)
- DELETE /api/hotels/:id - Xóa khách sạn (owner)

### Rooms
- GET /api/rooms - Danh sách phòng
- GET /api/rooms/:id - Chi tiết phòng
- POST /api/rooms - Tạo phòng mới (owner)
- PUT /api/rooms/:id - Cập nhật phòng (owner)
- DELETE /api/rooms/:id - Xóa phòng (owner)

### Bookings
- GET /api/bookings - Danh sách đặt phòng
- GET /api/bookings/:id - Chi tiết đặt phòng
- POST /api/bookings - Tạo đặt phòng mới
- PUT /api/bookings/:id/cancel - Hủy đặt phòng
- PUT /api/bookings/:id/confirm - Xác nhận đặt phòng (owner)

### Payments
- POST /api/payments/vnpay - Tạo thanh toán VNPay
- GET /api/payments/vnpay-return - VNPay return URL
- POST /api/payments/momo - Tạo thanh toán Momo
- POST /api/payments/momo-notify - Momo IPN

### Reviews
- GET /api/reviews - Danh sách đánh giá
- POST /api/reviews - Tạo đánh giá mới
- PUT /api/reviews/:id - Cập nhật đánh giá
- DELETE /api/reviews/:id - Xóa đánh giá

## Testing
```bash
pytest
pytest --cov=app tests/
```

## License

MIT License
