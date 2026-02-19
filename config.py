"""
Cấu hình cho Game Account Registrar Tool
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Thông tin game servers
GAME_SERVERS = {
    'default': {
        'url': 'https://example-game.com/register',
        'name': 'Example Game',
    },
    'game1': {
        'url': 'https://game1.example.com/account/register',
        'name': 'Game 1',
    },
    'game2': {
        'url': 'https://game2.example.com/signup',
        'name': 'Game 2',
    }
}

# Bank list for registration
BANK_OPTIONS = {
    'vietcombank': 'Vietcombank',
    'bidv': 'BIDV',
    'techcombank': 'Techcombank',
    'vpbank': 'VPBank',
    'acb': 'ACB',
    'mb': 'MB',
    'agribank': 'Agribank',
    'sacombank': 'Sacombank',
    'donga': 'Dong A',
    'vib': 'VIB',
}

# Selenium WebDriver settings
WEBDRIVER_CONFIG = {
    'headless': False,  # Đặt True để chạy ẩn
    'implicitly_wait': 10,  # Đợi phần tử trong vòng 10 giây
    'explicit_wait': 15,   # Đợi điều kiện explicit trong 15 giây
    'window_size': '1920,1080',
}

# Account settings
ACCOUNT_CONFIG = {
    'auto_fill': True,
    'submit_form': True,
    'verify_email': False,
}

# Phone number settings
PHONE_CONFIG = {
    'use_phone': False,  # Sử dụng SĐT để đăng ký
    'no_otp': True,      # SĐT không cần OTP
    'with_otp': False,   # SĐT có OTP
    'verify_phone': False,  # Xác minh SĐT
}

# Logging settings
LOG_CONFIG = {
    'level': 'INFO',
    'file': 'logs/registration.log',
}

# Proxy settings (tuỳ chọn)
PROXY_CONFIG = {
    'enabled': False,
    'proxy_list': [],
    'rotate': False,
}

# Data file settings
DATA_FILE_CONFIG = {
    'enabled': False,
    'account_data_file': 'TK_REG.txt',  # username|password|email
    'phone_no_otp_file': 'sdt.txt',     # Danh sách SĐT không OTP
    'success_file': 'ACC_OK.txt',       # Tài khoản đăng ký thành công
    'fail_file': 'FAIL.txt',             # Tài khoản đăng ký không thành công
}
