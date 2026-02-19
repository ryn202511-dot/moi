# CodeSim OTP Integration Guide

## Giới thiệu về CodeSim API

CodeSim (https://codesim.net/) là dịch vụ thuê số điện thoại để nhận SMS OTP. Tính năng này cho phép tự động đăng ký tài khoản với xác minh qua SĐT OTP.

## Chuẩn bị

### 1. Đăng ký tài khoản CodeSim
- Truy cập https://codesim.net/
- Tạo tài khoản và nạp tiền
- Sao chép API Key từ dashboard

### 2. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

Các library cần thiết:
- `requests>=2.31.0` - Để gọi API CodeSim
- `selenium>=4.15.2` - Để tự động hóa trình duyệt
- `webdriver-manager>=4.0.1` - Để quản lý ChromeDriver

## Cách sử dụng

### Trong GUI Launcher

1. **Chọn mode SĐT**: Chọn "SĐT có OTP"
2. **Nhập API Key**: Dán API key từ CodeSim vào trường "CodeSim API Key"
3. **Chọn Service**: Chọn loại dịch vụ (Gmail, WhatsApp, Facebook, v.v.)
4. **Đặt thời gian chờ**: Tùy chỉnh thời gian chờ OTP (mặc định 60 giây)
5. **Kiểm tra số dư**: Nhấn "🔍 Kiểm tra số dư" để xác nhận API key có hiệu lực
6. **Bắt đầu**: Nhấn "▶ Bắt đầu đăng ký"

### Sử dụng API trực tiếp

```python
from codesim_api import CodeSimAPI

# Khởi tạo API client
api = CodeSimAPI('YOUR_API_KEY')

# 1. Kiểm tra số dư
balance = api.get_balance()
print(f"Số dư: {balance}")

# 2. Lấy danh sách quốc gia
countries = api.get_countries()

# 3. Lấy danh sách dịch vụ
services = api.get_services(country_id=174)  # 174 = Việt Nam

# 4. Thuê số điện thoại
rental = api.rent_number(service_id=20, country_id=174)
# service_id: 1=Gmail, 2=WhatsApp, 3=Facebook, 4=Instagram, 20=PayPal, etc.
# Returns: {'id': <rental_id>, 'phone': <number>}

# 5. Lấy OTP
if rental:
    otp = api.get_otp(rental['id'], wait_seconds=60)
    print(f"OTP: {otp}")
    
    # 6. Giải phóng số
    api.release_number(rental['id'])
```

### Sử dụng hàm tiện ích

```python
from utils import get_otp_from_codesim, release_otp_number

# Lấy OTP
result = get_otp_from_codesim(
    api_key='YOUR_API_KEY',
    service_id=20,  # PayPal
    country_id=174,  # Việt Nam
    wait_seconds=60
)

if result:
    print(f"Phone: {result['phone']}")
    print(f"OTP: {result['otp']}")
    print(f"Rental ID: {result['rental_id']}")
    
    # Giải phóng sau khi sử dụng
    release_otp_number('YOUR_API_KEY', result['rental_id'])
```

## Service IDs (Phổ biến)

| ID | Service |
|----|---------|
| 1 | Gmail |
| 2 | WhatsApp |
| 3 | Facebook |
| 4 | Instagram |
| 5 | Telegram |
| 6 | Viber |
| 7 | Line |
| 8 | Twitter |
| 9 | TikTok |
| 10 | Discord |
| 11 | Twitch |
| 15 | Alipay |
| 17 | Uber |
| 18 | Airbnb |
| 19 | Booking |
| 20 | PayPal |

## Country IDs

| ID | Country |
|----|---------|
| 174 | Việt Nam |
| 213 | Thái Lan |
| 101 | Indonesia |
| 179 | Philippines |
| 195 | Singapore |
| 149 | Malaysia |
| 222 | USA |
| 221 | UK |

## Tệp kết quả

### ACC_OK.txt
```
2026-02-19 10:30:45|user_abc123|password123|user@example.com|+84901234567|vietcombank|https://example.com/register
```

### FAIL.txt
```
2026-02-19 10:35:22|user_xyz789|password456|user2@example.com|+84987654321|bidv|https://example.com/register|OTP timeout after 60 seconds
```

## Cấu hình môi trường (tùy chọn)

Tạo file `.env` trong thư mục chương trình:
```
CODESIM_API_KEY=your_api_key_here
```

Sau đó load trong code:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('CODESIM_API_KEY')
```

## Xử lý lỗi thường gặp

### 1. "API Key không hợp lệ"
- Kiểm tra API key từ dashboard CodeSim
- Đảm bảo đã nạp tiền vào tài khoản
- Thử kiểm tra số dư bằng nút "🔍 Kiểm tra số dư"

### 2. "Không nhận được OTP"
- Tăng thời gian chờ OTP (time-out default 60s)
- Một số dịch vụ (GameSim, etc.) có thể cần điều chỉnh
- Kiểm tra xem số SĐT thuê đã sẵn sàng tiếp nhận SMS hay chưa

### 3. "Số dư không đủ"
- Nạp thêm tiền vào tài khoản CodeSim
- Mỗi lần thuê số có giá khác nhau tùy dịch vụ

### 4. "Service không khả dụng cho Việt Nam"
- Kiểm tra danh sách dịch vụ hỗ trợ bằng `api.get_services(174)`
- Thử service khác

## Tips & Tricks

1. **Tiết kiệm tiền**: Đặt thời gian chờ OTP thấp hơn nếu chắc là số sẽ nhận OTP nhanh
2. **Kiểm tra trước**: Luôn dùng "🔍 Kiểm tra số dư" trước khi bắt đầu
3. **Ghi log**: Tất cả hoạt động đều được ghi vào `logs/registration.log`
4. **Giải phóng tự động**: Số SĐT sẽ được giải phóng tự động sau khi đăng ký hoàn tất
5. **Retry logic**: Nếu OTP timeout, hãy thử lại - CodeSim có thể trễ một chút

## Kiến trúc Code

### codesim_api.py
- Lớp chính: `CodeSimAPI`
- Các method: `rent_number()`, `get_otp()`, `release_number()`, `get_balance()`
- Hàm tiện ích: `rent_and_get_otp()`

### game_account_registrar.py (cập nhật)
- Method: `get_otp_from_codesim()` - Lấy OTP từ CodeSim
- Variable: `otp_phone`, `otp_code`, `rental_id`
- Tự động giải phóng SĐT trong `finally` block

### gui_launcher.py (cập nhật)
- Widget mới: OTP configuration frame
- Input fields: API Key, Service selection, Wait time
- Button: "🔍 Kiểm tra số dư"
- Passes parameters: `codesim_api_key`, `codesim_service`, `otp_wait_seconds`

## Troubleshooting

Nếu có vấn đề, hãy:
1. Kiểm tra file log: `logs/registration.log`
2. Bật console window (uncheck Headless mode) để xem trình duyệt
3. Kiểm tra số dư CodeSim
4. Thử test API key bằng nút "🔍 Kiểm tra số dư"
5. Xem lại form selectors (CSS selectors) có đúng với form input không

## Liên hệ hỗ trợ

- CodeSim Documentation: https://codesim.net/docs
- API Docs: https://codesim.net/api/docs
- GitHub Issues: [Your repo]/issues
