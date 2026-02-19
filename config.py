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

# Logging settings
LOG_CONFIG = {
    'level': 'INFO',
    'file': 'logs/registration.log',
}

# Proxy settings (tuỳ chọn)
PROXY_CONFIG = {
    'enabled': False,
    'url': os.getenv('PROXY_URL', 'http://proxy.example.com:8080'),
}
