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


class AccountData:
    """Lớp để lưu trữ dữ liệu tài khoản"""
    def __init__(self):
        self.username = generate_username()
        self.password = generate_password()
        self.email = generate_email()
        self.birthdate = generate_birthdate()
        self.first_name = f"User_{random.randint(1000, 9999)}"
        self.last_name = "Test"
    
    def __str__(self):
        return (
            f"Username: {self.username}\n"
            f"Password: {self.password}\n"
            f"Email: {self.email}\n"
            f"Birthdate: {self.birthdate}"
        )
    
    def to_dict(self):
        """Chuyển đổi thành dictionary"""
        return {
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'birthdate': self.birthdate,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }
