"""
Các hàm tiện ích cho Game Account Registrar
"""
import logging
import os
import random
import string
from datetime import datetime, timedelta

# Thiết lập logging
def setup_logger(name, log_file=None):
    """Tạo logger với file output"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def generate_username(prefix='user', length=10):
    """Tạo username ngẫu nhiên"""
    random_part = ''.join(random.choices(
        string.ascii_lowercase + string.digits, 
        k=length
    ))
    return f"{prefix}_{random_part}"


def generate_password(length=12):
    """Tạo password mạnh"""
    characters = (
        string.ascii_uppercase + 
        string.ascii_lowercase + 
        string.digits + 
        '!@#$%^&*'
    )
    password = ''.join(random.choices(characters, k=length))
    return password


def generate_phone_number(prefix='84'):
    """Tạo số điện thoại ngẫu nhiên (Việt Nam)"""
    phone = f"{prefix}{''.join(random.choices(string.digits, k=9))}"
    return phone


def generate_email(domain='example.com'):
    """Tạo email ngẫu nhiên"""
    username = ''.join(random.choices(
        string.ascii_lowercase + string.digits, 
        k=10
    ))
    return f"{username}@{domain}"


def generate_birthdate():
    """Tạo ngày sinh ngẫu nhiên (18-50 tuổi)"""
    today = datetime.today()
    days_back = random.randint(365*18, 365*50)
    birthdate = today - timedelta(days=days_back)
    return birthdate.strftime('%Y-%m-%d')


def wait_random(min_seconds=1, max_seconds=3):
    """Chờ thời gian ngẫu nhiên để tránh detection"""
    import time
    wait_time = random.uniform(min_seconds, max_seconds)
    time.sleep(wait_time)


def save_account(username, password, email, filename='accounts.txt'):
    """Lưu thông tin tài khoản vào file"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{username}|{password}|{email}\n")
    return True


def save_account_success(username, password, email, phone='', filename='accounts_success.txt'):
    """Lưu tài khoản đã đăng ký thành công"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{username}|{password}|{email}|{phone}\n")
    return True


def load_accounts_from_file(filename):
    """Tải danh sách account từ file (format: username|password|email|phone)"""
    accounts = []
    if not os.path.exists(filename):
        return accounts
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split('|')
            if len(parts) >= 3:
                account = {
                    'username': parts[0],
                    'password': parts[1],
                    'email': parts[2],
                    'phone': parts[3] if len(parts) > 3 else '',
                }
                accounts.append(account)
    return accounts


class AccountData:
    """Lớp để lưu trữ dữ liệu tài khoản"""
    def __init__(self):
        self.username = generate_username()
        self.password = generate_password()
        self.email = generate_email()
        self.birthdate = generate_birthdate()
        self.first_name = f"User_{random.randint(1000, 9999)}"
        self.last_name = "Test"
        self.phone = ''  # SĐT (email từ CodeSim hoặc file)
    
    def __str__(self):
        return (
            f"Username: {self.username}\n"
            f"Password: {self.password}\n"
            f"Email: {self.email}\n"
            f"Phone: {self.phone}\n"
            f"Birthdate: {self.birthdate}"
        )
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'phone': self.phone,
            'birthdate': self.birthdate,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

def load_phone_numbers(filename):
    """Tải danh sách số điện thoại từ file"""
    phones = []
    if not os.path.exists(filename):
        return phones
    
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                phones.append(line)
    return phones


def save_successful_account(username, password, email, phone='', bank='', url='', 
                            filename='ACC_OK.txt'):
    """Lưu tài khoản đăng ký thành công"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', 
                exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}|{username}|{password}|{email}|{phone}|{bank}|{url}\n")
    return True


def save_failed_account(username, password, email, phone='', bank='', url='', 
                       error_msg='', filename='FAIL.txt'):
    """Lưu tài khoản đăng ký không thành công"""
    os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', 
                exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"{timestamp}|{username}|{password}|{email}|{phone}|{bank}|{url}|{error_msg}\n")
    return True


def get_otp_from_codesim(api_key, service_id=20, country_id=174, wait_seconds=60):
    """
    Thuê số điện thoại từ CodeSim và lấy OTP
    
    Args:
        api_key: API key từ CodeSim
        service_id: ID dịch vụ (mặc định 20 = PayPal)
        country_id: ID quốc gia (mặc định 174 = Việt Nam)
        wait_seconds: Thời gian chờ OTP tối đa (giây)
        
    Returns:
        Dict {'phone': số điện thoại, 'otp': mã OTP, 'rental_id': ID thuê số}
        hoặc None nếu lỗi
    """
    try:
        from codesim_api import CodeSimAPI
        
        api = CodeSimAPI(api_key)
        
        # Kiểm tra số dư trước
        balance = api.get_balance()
        if balance is None:
            logging.error("Không thể kết nối tới CodeSim API")
            return None
        
        logging.info(f"Số dư CodeSim: {balance}")
        
        # Thuê số điện thoại
        rental = api.rent_number(service_id, country_id)
        if not rental:
            logging.error("Không thể thuê số điện thoại từ CodeSim")
            return None
        
        phone = rental['phone']
        rental_id = rental['id']
        logging.info(f"Đã thuê số: {phone}")
        
        # Lấy OTP
        otp = api.get_otp(rental_id, wait_seconds)
        if not otp:
            logging.error(f"Không lấy được OTP cho {phone}")
            return None
        
        logging.info(f"Lấy OTP thành công: {otp}")
        
        return {
            'phone': phone,
            'otp': otp,
            'rental_id': rental_id,
            'status': 'success'
        }
        
    except Exception as e:
        logging.error(f"Lỗi khi lấy OTP từ CodeSim: {e}")
        return None


def release_otp_number(api_key, rental_id):
    """
    Giải phóng số điện thoại từ CodeSim
    
    Args:
        api_key: API key từ CodeSim
        rental_id: ID thuê số để giải phóng
        
    Returns:
        True nếu thành công, False nếu lỗi
    """
    try:
        from codesim_api import CodeSimAPI
        
        api = CodeSimAPI(api_key)
        return api.release_number(rental_id)
        
    except Exception as e:
        logging.error(f"Lỗi khi giải phóng SĐT: {e}")
        return False