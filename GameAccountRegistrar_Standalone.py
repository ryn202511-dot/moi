#!/usr/bin/env python3
"""
Game Account Registrar Tool v2.1-OTP - Standalone Version
🎮 Công cụ đăng ký tài khoản game tự động
🔑 Tích hợp OTP từ CodeSim API (https://codesim.net/)

🚀 CÁCH CHẠY:
    python GameAccountRegistrar_Standalone.py

📦 DEPENDENCIES (cài qua pip):
    pip install selenium webdriver-manager requests

✨ FEATURES:
- Nhập URL tùy chỉnh
- Hỗ trợ Proxy
- Lựa chọn Bank (10 ngân hàng Việt)
- SĐT không OTP (từ file)
- SĐT có OTP (từ CodeSim API)
- Tự động lưu kết quả (ACC_OK.txt, FAIL.txt)

📄 CẤU HÌNH:
- URL: Điền đường dẫn form đăng ký
- Proxy: (tuỳ chọn) http://proxy:port
- Bank: Chọn ngân hàng
- API Key CodeSim: (tuỳ chọn) Để dùng OTP

💾 KẾT QUẢ:
- ACC_OK.txt: Tài khoản đào ký thành công
- FAIL.txt: Tài khoản lỗi + error message
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import sys
import time
import os
import logging
import random
import string
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
from io import StringIO

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException,
    StaleElementReferenceException,
)


# ============================================================================
# PHẦN 1: CODESIM API
# ============================================================================

class CodeSimAPI:
    """Tương tác với CodeSim API (https://codesim.net/)"""
    
    BASE_URL = "https://codesim.net/api"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self.logger = logging.getLogger(__name__)
    
    def get_balance(self) -> Optional[float]:
        """Lấy số dư tài khoản"""
        try:
            url = f"{self.BASE_URL}/user/balance"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                balance = result.get('data', {}).get('balance')
                return balance
            return None
        except Exception as e:
            self.logger.error(f"Lỗi lấy số dư: {e}")
            return None
    
    def rent_number(self, service_id: int, country_id: int = 174) -> Optional[Dict]:
        """Thuê một số điện thoại"""
        try:
            url = f"{self.BASE_URL}/rentals"
            data = {
                'service': service_id,
                'country': country_id
            }
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                rental = result.get('data', {})
                return {
                    'id': rental.get('id'),
                    'phone': rental.get('phone'),
                    'service_id': service_id,
                    'country_id': country_id
                }
            return None
        except Exception as e:
            self.logger.error(f"Lỗi thuê SĐT: {e}")
            return None
    
    def get_otp(self, rental_id: int, wait_seconds: int = 60) -> Optional[str]:
        """Lấy OTP từ số điện thoại thuê"""
        try:
            url = f"{self.BASE_URL}/rentals/{rental_id}/sms"
            start_time = time.time()
            
            while time.time() - start_time < wait_seconds:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                result = response.json()
                
                if result.get('success'):
                    sms_list = result.get('data', [])
                    if sms_list and len(sms_list) > 0:
                        sms = sms_list[0]
                        otp = sms.get('code') or sms.get('text')
                        
                        if otp:
                            import re
                            match = re.search(r'\b\d{4,6}\b', otp)
                            return match.group() if match else otp
                
                time.sleep(2)
            
            return None
        except Exception as e:
            self.logger.error(f"Lỗi lấy OTP: {e}")
            return None
    
    def release_number(self, rental_id: int) -> bool:
        """Giải phóng số điện thoại"""
        try:
            url = f"{self.BASE_URL}/rentals/{rental_id}"
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            return response.json().get('success', False)
        except Exception as e:
            self.logger.error(f"Lỗi giải phóng SĐT: {e}")
            return False


SERVICE_IDS = {
    'gmail': 1, 'whatsapp': 2, 'facebook': 3, 'instagram': 4,
    'telegram': 5, 'viber': 6, 'line': 7, 'twitter': 8,
    'tiktok': 9, 'discord': 10, 'twitch': 11, 'snapchat': 12,
    'paypal': 20, 'uber': 17, 'airbnb': 18, 'booking': 19,
}


# ============================================================================
# PHẦN 2: UTILITIES
# ============================================================================

def setup_logger(name):
    """Tạo logger"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(handler)
    
    return logger


def generate_username(prefix='user', length=10):
    """Tạo username ngẫu nhiên"""
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{random_part}"


def generate_password(length=12):
    """Tạo password mạnh"""
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits + '!@#$%^&*'
    return ''.join(random.choices(characters, k=length))


def generate_email(domain='example.com'):
    """Tạo email ngẫu nhiên"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{domain}"


def generate_phone_number(prefix='84'):
    """Tạo SĐT Việt Nam"""
    return f"{prefix}{''.join(random.choices(string.digits, k=9))}"


def generate_birthdate():
    """Tạo ngày sinh (18-50 tuổi)"""
    today = datetime.today()
    days_back = random.randint(365*18, 365*50)
    birthdate = today - timedelta(days=days_back)
    return birthdate.strftime('%Y-%m-%d')


def wait_random(min_secs=1, max_secs=3):
    """Chờ thời gian ngẫu nhiên"""
    time.sleep(random.uniform(min_secs, max_secs))


def save_successful_account(username, password, email, phone='', bank='', url='', 
                             filename='ACC_OK.txt'):
    """Lưu tài khoản đăng ký thành công"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}|{username}|{password}|{email}|{phone}|{bank}|{url}\n")


def save_failed_account(username, password, email, phone='', bank='', url='', 
                        error_msg='', filename='FAIL.txt'):
    """Lưu tài khoản đăng ký không thành công"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}|{username}|{password}|{email}|{phone}|{bank}|{url}|{error_msg}\n")


def load_phone_numbers(filename):
    """Tải danh sách SĐT từ file"""
    phones = []
    if not os.path.exists(filename):
        return phones
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                phones.append(line)
    return phones


class AccountData:
    """Dữ liệu tài khoản"""
    def __init__(self):
        self.username = generate_username()
        self.password = generate_password()
        self.email = generate_email()
        self.phone = ''
        self.birthdate = generate_birthdate()
        self.first_name = f"User_{random.randint(1000, 9999)}"
        self.last_name = "Test"
    
    def __str__(self):
        return (
            f"Username: {self.username}\n"
            f"Password: {self.password}\n"
            f"Email: {self.email}\n"
            f"Phone: {self.phone}\n"
            f"Birthdate: {self.birthdate}"
        )


# ============================================================================
# PHẦN 3: GAME ACCOUNT REGISTRAR
# ============================================================================

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

GAME_SERVERS = {
    'default': {
        'url': 'https://example-game.com/register',
        'name': 'Example Game',
    }
}

WEBDRIVER_CONFIG = {
    'headless': False,
    'implicitly_wait': 10,
    'explicit_wait': 15,
    'window_size': '1920,1080',
}


class GameAccountRegistrar:
    """Công cụ đăng ký tài khoản game"""
    
    def __init__(self, url=None, proxy=None, bank='vietcombank', phone_mode='none',
                 headless=False, codesim_api_key='', codesim_service='gmail', 
                 otp_wait_seconds=60):
        """Khởi tạo registrar"""
        self.logger = setup_logger('GameAccountRegistrar')
        
        self.game_config = {
            'url': url or 'https://example-game.com/register',
            'name': 'Game Account',
        }
        
        self.driver = None
        self.headless = headless
        self.wait = None
        self.account_data = None
        self.proxy = proxy
        self.bank = bank
        self.phone_mode = phone_mode
        self.codesim_api_key = codesim_api_key
        self.codesim_service = codesim_service
        self.otp_wait_seconds = otp_wait_seconds
        self.otp_phone = None
        self.otp_code = None
        self.rental_id = None
        
        self.logger.info(f"Khởi tạo: {self.game_config['url']}")
        if proxy:
            self.logger.info(f"Proxy: {proxy}")
        self.logger.info(f"Bank: {bank} | Phone Mode: {phone_mode}")
    
    def setup_driver(self):
        """Thiết lập Selenium WebDriver"""
        try:
            self.logger.info("Đang khởi tạo WebDriver...")
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
            
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--window-size={WEBDRIVER_CONFIG["window_size"]}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
            
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(WEBDRIVER_CONFIG['implicitly_wait'])
            self.wait = WebDriverWait(self.driver, WEBDRIVER_CONFIG['explicit_wait'])
            
            self.logger.info("WebDriver khởi tạo thành công")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo WebDriver: {e}")
            return False
    
    def navigate_to_register_page(self):
        """Điều hướng tới trang đăng ký"""
        try:
            self.logger.info(f"Truy cập: {self.game_config['url']}")
            self.driver.get(self.game_config['url'])
            wait_random(2, 3)
            self.logger.info("Trang đã tải")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi truy cập: {e}")
            return False
    
    def fill_field(self, selector, value, field_name):
        """Điền trường form"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            element.clear()
            element.send_keys(value)
            wait_random(0.5, 1)
            self.logger.info(f"Điền {field_name}: {value if 'password' not in field_name else '****'}")
            return True
        except:
            self.logger.warning(f"Không tìm thấy {field_name}: {selector}")
            return True  # Bỏ qua nếu không có
    
    def get_otp_from_codesim(self):
        """Thuê SĐT và lấy OTP từ CodeSim"""
        try:
            if not self.codesim_api_key:
                return None
            
            api = CodeSimAPI(self.codesim_api_key)
            service_id = SERVICE_IDS.get(self.codesim_service, 20)
            
            self.logger.info(f"Thuê SĐT từ CodeSim (Service: {self.codesim_service})...")
            rental = api.rent_number(service_id, 174)
            
            if not rental:
                self.logger.error("Không thể thuê SĐT")
                return None
            
            phone = rental['phone']
            self.otp_phone = phone
            self.rental_id = rental['id']
            self.logger.info(f"✓ Thuê SĐT: {phone}")
            
            self.logger.info(f"Chờ OTP ({self.otp_wait_seconds}s)...")
            otp = api.get_otp(rental['id'], self.otp_wait_seconds)
            
            if not otp:
                self.logger.error(f"Timeout OTP")
                return None
            
            self.otp_code = otp
            self.logger.info(f"✓ OTP: {otp}")
            
            return {'phone': phone, 'otp': otp, 'rental_id': rental['id']}
        except Exception as e:
            self.logger.error(f"Lỗi CodeSim: {e}")
            return None
    
    def register(self):
        """Thực hiện đăng ký"""
        try:
            self.account_data = AccountData()
            self.logger.info(f"\nTài khoản:\n{self.account_data}\n")
            
            phone = ''
            
            # Lấy OTP nếu cần
            if self.phone_mode == 'with_otp' and self.codesim_api_key:
                otp_result = self.get_otp_from_codesim()
                if not otp_result:
                    return False
                phone = otp_result['phone']
                self.account_data.phone = phone
            
            # Setup & navigate
            if not self.setup_driver():
                return False
            if not self.navigate_to_register_page():
                return False
            
            # Fill form (generic - selectors có thể tuỳ chỉnh)
            self.logger.info("Điền form...")
            wait_random(1, 2)
            
            self.fill_field('#username', self.account_data.username, 'Username')
            self.fill_field('#email', self.account_data.email, 'Email')
            self.fill_field('#password', self.account_data.password, 'Password')
            self.fill_field('#confirm_password', self.account_data.password, 'Confirm Password')
            
            if phone:
                self.fill_field('#phone', phone, 'Phone')
            
            if self.otp_code:
                wait_random(1, 2)
                self.fill_field('#otp', self.otp_code, 'OTP')
            
            # Submit
            try:
                button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
                )
                button.click()
                wait_random(2, 3)
            except:
                pass
            
            # Check success
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            success = (
                current_url != self.game_config['url'] or
                'success' in page_source or
                'welcome' in page_source or
                'registered' in page_source
            )
            
            if success:
                save_successful_account(
                    self.account_data.username, self.account_data.password,
                    self.account_data.email, phone, self.bank,
                    self.game_config['url'], 'ACC_OK.txt'
                )
                self.logger.info("✓ Lưu ACC_OK.txt")
                return True
            else:
                save_failed_account(
                    self.account_data.username, self.account_data.password,
                    self.account_data.email, phone, self.bank,
                    self.game_config['url'], 'Không xác nhận đặng ký thành công',
                    'FAIL.txt'
                )
                self.logger.error("✗ Lưu FAIL.txt")
                return False
        
        except Exception as e:
            self.logger.error(f"Lỗi: {e}")
            if self.account_data:
                save_failed_account(
                    self.account_data.username, self.account_data.password,
                    self.account_data.email, phone=getattr(self, 'otp_phone', ''),
                    bank=self.bank, url=self.game_config['url'],
                    error_msg=str(e), filename='FAIL.txt'
                )
            return False
        
        finally:
            # Release OTP number
            if self.rental_id and self.phone_mode == 'with_otp':
                try:
                    api = CodeSimAPI(self.codesim_api_key)
                    if api.release_number(self.rental_id):
                        self.logger.info(f"✓ Giải phóng SĐT")
                except:
                    pass
            
            # Close driver
            if self.driver:
                self.driver.quit()
                self.logger.info("WebDriver đóng")


# ============================================================================
# PHẦN 4: GUI
# ============================================================================

class ScrollableFrame(ttk.Frame):
    """Frame có scrollbar"""
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class GUILauncher:
    """Giao diện GUI"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar v2.1-OTP")
        self.root.geometry("900x750")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.is_running = False
        self.create_widgets()
    
    def create_widgets(self):
        """Tạo UI"""
        # Header
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header, text="Game Account Registrar Tool v2.1-OTP", 
                 font=('Arial', 16, 'bold')).pack()
        ttk.Label(header, text="Đăng ký tài khoản tự động với OTP từ CodeSim", 
                 font=('Arial', 9)).pack()
        
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Main scrollable frame
        main = ScrollableFrame(self.root)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        cf = main.scrollable_frame
        
        # URL
        url_frame = ttk.LabelFrame(cf, text="🌐 URL Đăng ký", padding=8)
        url_frame.pack(fill=tk.X, pady=5)
        self.url_var = tk.StringVar(value='https://example.com/register')
        ttk.Entry(url_frame, textvariable=self.url_var, width=70).pack(fill=tk.X, padx=5, pady=5)
        
        # Proxy
        proxy_frame = ttk.LabelFrame(cf, text="🔗 Proxy (tuỳ chọn)", padding=8)
        proxy_frame.pack(fill=tk.X, pady=5)
        self.proxy_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(proxy_frame, text="Sử dụng Proxy", 
                       variable=self.proxy_enabled,
                       command=self.toggle_proxy).pack(anchor=tk.W, padx=5)
        self.proxy_var = tk.StringVar(value='http://proxy.example.com:8080')
        self.proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, 
                                     width=70, state=tk.DISABLED)
        self.proxy_entry.pack(fill=tk.X, padx=5, pady=5)
        
        # Bank & Phone
        bank_frame = ttk.LabelFrame(cf, text="🏦 Ngân hàng & SĐT", padding=8)
        bank_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bank_frame, text="Chọn Bank:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.bank_var = tk.StringVar(value='vietcombank')
        ttk.Combobox(bank_frame, textvariable=self.bank_var,
                    values=list(BANK_OPTIONS.values()), state='readonly',
                    width=30).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(bank_frame, text="Chế độ SĐT:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.phone_mode_var = tk.StringVar(value='no_otp')
        phone_frame = ttk.Frame(bank_frame)
        phone_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Radiobutton(phone_frame, text="Không dùng", variable=self.phone_mode_var, 
                       value='none').pack(side=tk.LEFT)
        ttk.Radiobutton(phone_frame, text="SĐT không OTP", variable=self.phone_mode_var,
                       value='no_otp').pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(phone_frame, text="SĐT có OTP", variable=self.phone_mode_var,
                       value='with_otp').pack(side=tk.LEFT)
        
        # CodeSim
        otp_frame = ttk.LabelFrame(cf, text="📱 OTP từ CodeSim", padding=8)
        otp_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(otp_frame, text="API Key:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.codesim_api = tk.StringVar(value='')
        ttk.Entry(otp_frame, textvariable=self.codesim_api, width=50, 
                 show='*').grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(otp_frame, text="Service:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.codesim_service = tk.StringVar(value='gmail')
        ttk.Combobox(otp_frame, textvariable=self.codesim_service,
                    values=list(SERVICE_IDS.keys()), state='readonly',
                    width=20).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(otp_frame, text="Chờ OTP (s):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.otp_wait = tk.StringVar(value='60')
        ttk.Spinbox(otp_frame, from_=10, to=300, textvariable=self.otp_wait,
                   width=20).grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Button(otp_frame, text="🔍 Kiểm tra số dư",
                  command=self.check_balance).grid(row=3, column=0, columnspan=2,
                                                  sticky=tk.EW, padx=5, pady=5)
        
        # General
        gen_frame = ttk.LabelFrame(cf, text="⚙️ Cấu hình chung", padding=8)
        gen_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(gen_frame, text="Số lượng:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.count_var = tk.StringVar(value='1')
        ttk.Spinbox(gen_frame, from_=1, to=1000, textvariable=self.count_var,
                   width=20).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(gen_frame, text="Chế độ Headless (ẩn trình duyệt)",
                       variable=self.headless_var).grid(row=1, column=0, columnspan=2,
                                                       sticky=tk.W, padx=5, pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(cf)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="▶ Bắt đầu",
                                    command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Dừng",
                                   command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="🗑 Xóa log",
                  command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Log
        ttk.Label(self.root, text="📋 LOG", font=('Arial', 10, 'bold')).pack(anchor=tk.W, padx=10)
        
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD,
                                                 font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
        
        # Status
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_proxy(self):
        state = tk.NORMAL if self.proxy_enabled.get() else tk.DISABLED
        self.proxy_entry.config(state=state)
    
    def check_balance(self):
        api_key = self.codesim_api.get().strip()
        if not api_key:
            messagebox.showwarning("Cảnh báo", "Nhập API Key CodeSim")
            return
        try:
            api = CodeSimAPI(api_key)
            balance = api.get_balance()
            if balance is not None:
                messagebox.showinfo("CodeSim Balance", f"Số dư: {balance}")
                self.log(f"✓ Số dư: {balance}", "success")
            else:
                messagebox.showerror("Lỗi", "Không thể lấy số dư")
                self.log("✗ Lỗi CodeSim", "error")
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
            self.log(f"✗ Lỗi: {e}", "error")
    
    def log(self, msg, level="info"):
        self.log_text.insert(tk.END, f"{msg}\n", level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        self.log_text.delete('1.0', tk.END)
    
    def start(self):
        try:
            count = int(self.count_var.get())
            if count < 1:
                messagebox.showerror("Lỗi", "Số lượng >= 1")
                return
        except:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ")
            return
        
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Nhập URL")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
    
    def run(self):
        try:
            url = self.url_var.get().strip()
            count = int(self.count_var.get())
            proxy = self.proxy_var.get() if self.proxy_enabled.get() else None
            bank = list(BANK_OPTIONS.keys())[list(BANK_OPTIONS.values()).index(self.bank_var.get())]
            
            self.log(f"\n{'='*60}")
            self.log("GAME ACCOUNT REGISTRAR v2.1-OTP", "info")
            self.log(f"URL: {url}\nBank: {self.bank_var.get()}\nSĐT: {self.phone_mode_var.get()}", "info")
            self.log(f"{'='*60}\n", "info")
            
            success = fail = 0
            
            for i in range(count):
                if not self.is_running:
                    break
                
                self.log(f"\n[{i+1}/{count}] Đăng ký...", "info")
                self.status_var.set(f"Tài khoản {i+1}/{count}")
                
                try:
                    reg = GameAccountRegistrar(
                        url=url, proxy=proxy, bank=bank,
                        phone_mode=self.phone_mode_var.get(),
                        headless=self.headless_var.get(),
                        codesim_api_key=self.codesim_api.get(),
                        codesim_service=self.codesim_service.get(),
                        otp_wait_seconds=int(self.otp_wait.get())
                    )
                    
                    if reg.register():
                        self.log(f"✓ Tài khoản #{i+1} thành công", "success")
                        success += 1
                    else:
                        self.log(f"✗ Tài khoản #{i+1} lỗi", "error")
                        fail += 1
                except Exception as e:
                    self.log(f"✗ Exception: {e}", "error")
                    fail += 1
                
                if i < count - 1:
                    for _ in range(4):
                        if not self.is_running:
                            break
                        time.sleep(0.5)
            
            self.log(f"\n{'='*60}")
            self.log(f"Thành công: {success} | Lỗi: {fail}", "info")
            self.log(f"{'='*60}\n", "info")
            self.status_var.set("Hoàn thành")
            messagebox.showinfo("Kết quả", f"Thành công: {success}\nLỗi: {fail}")
        
        except Exception as e:
            self.log(f"Lỗi: {e}", "error")
            messagebox.showerror("Lỗi", str(e))
        
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop(self):
        self.is_running = False
        self.log("⏹ Dừng...", "warning")
        self.status_var.set("Đang dừng...")


def main():
    root = tk.Tk()
    app = GUILauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
