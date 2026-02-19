╔══════════════════════════════════════════════════════════════════════════╗
║     GAME ACCOUNT REGISTRAR TOOL v2.1-OTP - STANDALONE VERSION             ║
║           🎮 Công cụ đăng ký tài khoản game tự động với OTP              ║
╚══════════════════════════════════════════════════════════════════════════╝

📦 DANH SÁCH CÁC FILE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ GameAccountRegistrar_Standalone.py  ← FILE CHÍNH (chứa tất cả code)
  ✓ requirements.txt                      ← Dependencies
  ✓ build_to_exe.bat                      ← Build thành .EXE (Windows)
  ✓ README.txt                            ← File này


🚀 CÁCH CHẠY (Nhanh nhất):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CÀI ĐẶT DEPENDENCIES:
   
   Windows/Mac/Linux:
   └─ pip install -r requirements.txt
   
   Hoặc cài thủ công:
   └─ pip install selenium webdriver-manager requests


2. CHẠY CHƯƠNG TRÌNH:
   
   Windows:
   └─ python GameAccountRegistrar_Standalone.py
   
   Mac/Linux:
   └─ python3 GameAccountRegistrar_Standalone.py


3. GIA DIỆN SẬP HIỆN:
   
   ┌─ 🌐 URL Đăng ký
   │  └─ Nhập đường dẫn form đăng ký
   │
   ├─ 🔗 Proxy (tuỳ chọn)
   │  └─ Bật tích chọn nếu cần dùng Proxy
   │
   ├─ 🏦 Ngân hàng & SĐT
   │  ├─ Chọn 10 ngân hàng Việt Nam
   │  └─ Chế độ SĐT:
   │     ├─ Không dùng
   │     ├─ SĐT không OTP (từ file)
   │     └─ SĐT có OTP (từ CodeSim API)
   │
   ├─ 📱 OTP từ CodeSim
   │  ├─ API Key: Dán API key từ https://codesim.net/
   │  ├─ Service: Gmail, WhatsApp, Facebook, Instagram, v.v.
   │  ├─ Chờ OTP: Thường 60 giây (tuỳ dịch vụ)
   │  └─ 🔍 Nút kiểm tra số dư
   │
   ├─ ⚙️ Cấu hình chung
   │  ├─ Số lượng tài khoản
   │  └─ Chế độ Headless
   │
   ├─ ▶ Bắt đầu | ⏹ Dừng | 🗑 Xóa log
   │
   └─ 📋 LOG (xem chi tiết quá trình)


🔑 SETUP CODESIM API (ĐỂ DÙNG OTP):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Truy cập: https://codesim.net/
2. Tạo tài khoản & đăng nhập
3. Nạp tiền vào tài khoản
4. Vào Dashboard → Lấy API Key
5. Copy API Key → Dán vào trường "API Key" trong GUI


📝 HƯỚNG DẪN TỪNG BƯỚC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRƯỜNG HỢP 1: SĐT không OTP (từ file)
─────────────────────────────────────

1. Tạo file "sdt.txt" trong thư mục chương trình
   Nội dung:
   ──────────
   84901234567
   84912345678
   84923456789
   ──────────

2. Chọn "SĐT không OTP" trong GUI
3. Nhập URL
4. Nhấn "▶ Bắt đầu"


TRƯỜNG HỢP 2: SĐT có OTP (từ CodeSim)
─────────────────────────────────────

1. Chuẩn bị API Key từ CodeSim
2. Chọn "SĐT có OTP" trong GUI
3. Dán API Key vào trường "API Key"
4. Chọn Service (mặc định: Gmail)
5. Nhấn "🔍 Kiểm tra số dư" (để xác nhận API hoạt động)
6. Nhập URL
7. Nhập số lượng tài khoản
8. Nhấn "▶ Bắt đầu"


📊 KẾT QUẢ ĐƯỢC LƯU:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ ACC_OK.txt (Tài khoản đăng ký thành công)
   Format: timestamp|username|password|email|phone|bank|url
   
   Ví dụ:
   2026-02-19 14:30:45|user_abc123|Pass@123!|user@email.com|84901234567|vietcombank|https://example.com/register


✗ FAIL.txt (Tài khoản đăng ký thất bại)
   Format: timestamp|username|password|email|phone|bank|url|error_message
   
   Ví dụ:
   2026-02-19 14:35:22|user_xyz789|Pass@456!|user2@email.com|84987654321|bidv|https://example.com/register|OTP timeout after 60 seconds


🎯 CÁC SERVICE HỖ TRỢ CODESIM:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

gmail, whatsapp, facebook, instagram, telegram, viber, line, twitter, 
tiktok, discord, twitch, snapchat, paypal, uber, airbnb, booking, ...

(Danh sách đầy đủ xem tại https://codesim.net/)


🔧 BUILD THÀNH .EXE (WINDOWS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Mở Command Prompt
2. cd [đường dẫn thư mục chứa file]
3. Chạy: build_to_exe.bat

   Hoặc chạy thủ công:
   python -m PyInstaller --onefile --windowed --name GameAccountRegistrar GameAccountRegistrar_Standalone.py

4. File .exe sẽ nằm trong thư mục "dist"


⚠️ LƯỚI Ý (TROUBLESHOOTING):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q: Lỗi "No module named 'selenium'"
A: Chạy: pip install selenium webdriver-manager requests

Q: Lỗi "không tìm thấy ChromeDriver"
A: webdriver-manager sẽ tự download. Nếu vẫn lỗi, cài thủ công:
   - Download: https://chromedriver.chromium.org/
   - Đặt vào thư mục của file chương trình

Q: "OTP timeout" từ CodeSim
A: - Tăng thời gian chờ OTP (ví dụ: 120 giây)
   - Kiểm tra số dư CodeSim (nút 🔍)
   - Thử service khác

Q: "API Key không hợp lệ"
A: - Kiểm tra lại API Key từ https://codesim.net/
   - Đảm bảo tài khoản đã nạp tiền
   - Thử kiểm tra số dư bằng nút 🔍

Q: Form không filling được
A: - CSS selector mặc định là generic (#username, #email, #password, #otp)
   - Nếu website khác cấu trúc → cần điều chỉnh selectors trong code
   - Dùng Developer Tools (F12) để xem form structure


🎮 CẤU HÌNH FORM (ADVANCED):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Nếu form website khác cấu trúc, mở GameAccountRegistrar_Standalone.py
và tìm phần "Mặc định selectors":

    Dòng ~730 trong hàm register():
    ─────────────────────────────
    self.fill_field('#username', ..., 'Username')
    self.fill_field('#email', ..., 'Email')
    self.fill_field('#password', ..., 'Password')
    self.fill_field('#otp', ..., 'OTP')

Thay thế CSS selector:
  #username → name="user" hoặc [placeholder="Username"]
  #email    → input[type="email"]
  #password → input[id="pwd"]
  v.v.


📱 FEATURES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Giao diện GUI đơn giản, dễ sử dụng
✅ Thêm URL, Proxy, Bank, Phone modes tùy chỉnh
✅ Integrated CodeSim API cho OTP
✅ Tự động lưu kết quả (thành công/thất bại)
✅ Real-time logging + color-coded output
✅ Hỗ trợ batch registration (nhiều tài khoản)
✅ Xử lý lỗi toàn diện
✅ Cross-platform (Windows/Mac/Linux)


🌐 LINKS & RESOURCES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CodeSim API:      https://codesim.net/
Selenium Docs:    https://selenium.dev/
ChromeDriver:     https://chromedriver.chromium.org/
GitHub:           https://github.com/ryn202511-dot/moi


📞 SUPPORT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Có vấn đề? Hãy:
1. Kiểm tra file log trong console
2. Thử kiểm tra số dư CodeSim
3. Xem xét adjust CSS selectors cho form
4. Tăng thời gian chờ OTP/form


═══════════════════════════════════════════════════════════════════════════════

                        Happy Account Registration! 🚀
                         Enjoy automated registration!

═══════════════════════════════════════════════════════════════════════════════
