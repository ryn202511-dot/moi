"""
Game Account Registrar Tool
Công cụ tự động đăng ký tài khoản game sử dụng Selenium
"""
import sys
import time
from typing import Optional, Dict
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

from config import GAME_SERVERS, WEBDRIVER_CONFIG, ACCOUNT_CONFIG
from utils import (
    setup_logger, 
    AccountData, 
    save_account,
    wait_random,
)


class GameAccountRegistrar:
    """Lớp chính để đăng ký tài khoản game"""
    
    def __init__(self, game_name='default', headless=False):
        """
        Khởi tạo registrar
        
        Args:
            game_name: Tên game (key trong GAME_SERVERS)
            headless: Chạy ẩn (không hiển thị trình duyệt)
        """
        self.logger = setup_logger(
            'GameAccountRegistrar',
            log_file='logs/registration.log'
        )
        
        if game_name not in GAME_SERVERS:
            self.logger.error(f"Game '{game_name}' không tìm thấy")
            self.logger.info(f"Các game khả dụng: {list(GAME_SERVERS.keys())}")
            sys.exit(1)
        
        self.game_config = GAME_SERVERS[game_name]
        self.game_name = game_name
        self.logger.info(f"Khởi tạo cho trò chơi: {self.game_config['name']}")
        
        self.driver = None
        self.headless = headless
        self.wait = None
        self.account_data = None
    
    def setup_driver(self):
        """Thiết lập Selenium WebDriver"""
        try:
            self.logger.info("Đang khởi tạo Chrome WebDriver...")
            
            options = Options()
            
            if self.headless:
                options.add_argument('--headless')
                self.logger.info("Chạy ở chế độ headless")
            
            # Các option khác
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument(f'--window-size={WEBDRIVER_CONFIG["window_size"]}')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # User Agent để tránh detection
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            )
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            
            # Implicit wait
            self.driver.implicitly_wait(WEBDRIVER_CONFIG['implicitly_wait'])
            self.wait = WebDriverWait(
                self.driver, 
                WEBDRIVER_CONFIG['explicit_wait']
            )
            
            self.logger.info("WebDriver khởi tạo thành công")
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khởi tạo WebDriver: {e}")
            return False
    
    def navigate_to_register_page(self):
        """Điều hướng đến trang đăng ký"""
        try:
            self.logger.info(f"Đang truy cập: {self.game_config['url']}")
            self.driver.get(self.game_config['url'])
            wait_random(2, 3)
            self.logger.info("Trang đã tải thành công")
            return True
            
        except Exception as e:
            self.logger.error(f"Lỗi khi truy cập trang: {e}")
            return False
    
    def fill_username_field(self, username_selector='#username'):
        """Điền username vào form"""
        try:
            self.logger.info(f"Đang điền username: {self.account_data.username}")
            
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, username_selector))
            )
            element.clear()
            element.send_keys(self.account_data.username)
            wait_random(0.5, 1)
            
            self.logger.info("Username đã được điền")
            return True
            
        except TimeoutException:
            self.logger.error(f"Không tìm thấy trường username: {username_selector}")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi điền username: {e}")
            return False
    
    def fill_email_field(self, email_selector='#email'):
        """Điền email vào form"""
        try:
            self.logger.info(f"Đang điền email: {self.account_data.email}")
            
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, email_selector))
            )
            element.clear()
            element.send_keys(self.account_data.email)
            wait_random(0.5, 1)
            
            self.logger.info("Email đã được điền")
            return True
            
        except TimeoutException:
            self.logger.error(f"Không tìm thấy trường email: {email_selector}")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi điền email: {e}")
            return False
    
    def fill_password_field(self, password_selector='#password'):
        """Điền password vào form"""
        try:
            self.logger.info("Đang điền password...")
            
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, password_selector))
            )
            element.clear()
            element.send_keys(self.account_data.password)
            wait_random(0.5, 1)
            
            self.logger.info("Password đã được điền")
            return True
            
        except TimeoutException:
            self.logger.error(f"Không tìm thấy trường password: {password_selector}")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi điền password: {e}")
            return False
    
    def fill_confirm_password(self, confirm_selector='#confirm_password'):
        """Điền xác nhận password"""
        try:
            self.logger.info("Đang điền xác nhận password...")
            
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, confirm_selector))
            )
            element.clear()
            element.send_keys(self.account_data.password)
            wait_random(0.5, 1)
            
            self.logger.info("Xác nhận password đã được điền")
            return True
            
        except TimeoutException:
            # Nếu không có trường confirm, bỏ qua
            self.logger.warning("Không tìm thấy trường xác nhận password")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi điền xác nhận password: {e}")
            return False
    
    def select_dropdown(self, selector: str, value: str):
        """Chọn giá trị từ dropdown"""
        try:
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            select = Select(element)
            select.select_by_value(value)
            wait_random(0.3, 0.7)
            
            self.logger.info(f"Đã chọn giá trị '{value}' từ dropdown")
            return True
            
        except Exception as e:
            self.logger.warning(f"Lỗi chọn dropdown: {e}")
            return False
    
    def accept_terms(self, checkbox_selector='#terms'):
        """Chấp nhận điều khoản dịch vụ"""
        try:
            self.logger.info("Đang chấp nhận điều khoản dịch vụ...")
            
            checkbox = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector))
            )
            
            if not checkbox.is_selected():
                checkbox.click()
                wait_random(0.3, 0.7)
                self.logger.info("Đã chấp nhận điều khoản")
            return True
            
        except TimeoutException:
            self.logger.warning(f"Không tìm thấy checkbox điều khoản: {checkbox_selector}")
            return True
        except Exception as e:
            self.logger.error(f"Lỗi chấp nhận điều khoản: {e}")
            return False
    
    def submit_form(self, button_selector='button[type="submit"]'):
        """Gửi form đăng ký"""
        try:
            if not ACCOUNT_CONFIG['submit_form']:
                self.logger.info("Bỏ qua gửi form (cấu hình)")
                return True
            
            self.logger.info("Đang gửi form...")
            
            button = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, button_selector))
            )
            button.click()
            
            wait_random(2, 4)
            self.logger.info("Form đã được gửi")
            return True
            
        except TimeoutException:
            self.logger.error(f"Không tìm thấy nút gửi: {button_selector}")
            return False
        except Exception as e:
            self.logger.error(f"Lỗi gửi form: {e}")
            return False
    
    def check_success(self, success_indicators=None):
        """Kiểm tra đăng ký thành công"""
        if success_indicators is None:
            success_indicators = [
                ('text', 'success', 'contains'),
                ('text', 'Welcome', 'contains'),
                ('text', 'registered', 'contains'),
            ]
        
        try:
            # Chờ để trang tải
            wait_random(2, 3)
            
            # Kiểm tra URL thay đổi
            current_url = self.driver.current_url
            if current_url != self.game_config['url']:
                self.logger.info(f"URL đã thay đổi thành: {current_url}")
                self.logger.info("✓ Đăng ký tài khoản thành công!")
                return True
            
            # Kiểm tra thông báo thành công
            page_source = self.driver.page_source.lower()
            for indicator_type, keyword, match_type in success_indicators:
                if match_type == 'contains' and keyword.lower() in page_source:
                    self.logger.info(f"✓ Phát hiện thành công: '{keyword}'")
                    return True
            
            self.logger.warning("Không thể xác nhận đăng ký thành công")
            return False
            
        except Exception as e:
            self.logger.error(f"Lỗi kiểm tra thành công: {e}")
            return False
    
    def register(self, form_selectors: Optional[Dict] = None):
        """
        Thực hiện quy trình đăng ký hoàn chỉnh
        
        Args:
            form_selectors: Dictionary chứa các CSS selectors cho form fields
                           Example: {
                               'username': '#username',
                               'email': '#email',
                               'password': '#password',
                               'confirm_password': '#confirm_password',
                               'terms': '#terms',
                               'submit': 'button[type="submit"]'
                           }
        """
        # Selectors mặc định
        if form_selectors is None:
            form_selectors = {
                'username': '#username',
                'email': '#email',
                'password': '#password',
                'confirm_password': '#confirm_password',
                'terms': '#terms',
                'submit': 'button[type="submit"]'
            }
        
        try:
            # Tạo dữ liệu tài khoản
            self.account_data = AccountData()
            self.logger.info(f"\nTài khoản mới:\n{self.account_data}\n")
            
            # Thiết lập driver
            if not self.setup_driver():
                return False
            
            # Truy cập trang đăng ký
            if not self.navigate_to_register_page():
                return False
            
            # Điền form
            self.logger.info("Đang điền form đăng ký...")
            wait_random(1, 2)
            
            if not self.fill_username_field(form_selectors['username']):
                return False
            
            if not self.fill_email_field(form_selectors['email']):
                return False
            
            if not self.fill_password_field(form_selectors['password']):
                return False
            
            if not self.fill_confirm_password(form_selectors['confirm_password']):
                return False
            
            if not self.accept_terms(form_selectors['terms']):
                return False
            
            # Gửi form
            if not self.submit_form(form_selectors['submit']):
                return False
            
            # Kiểm tra kết quả
            if self.check_success():
                # Lưu tài khoản
                save_account(
                    self.account_data.username,
                    self.account_data.password,
                    self.account_data.email
                )
                self.logger.info("✓ Tài khoản đã được lưu")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Lỗi trong quá trình đăng ký: {e}")
            return False
        
        finally:
            self.close()
    
    def close(self):
        """Đóng WebDriver"""
        if self.driver:
            self.driver.quit()
            self.logger.info("WebDriver đã được đóng")


def main():
    """Hàm main để test tool"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Game Account Registrar Tool'
    )
    parser.add_argument(
        '--game',
        default='default',
        help='Tên game để đăng ký (default, game1, game2, ...)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Chạy ở chế độ headless (ẩn)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Số tài khoản cần tạo'
    )
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print("GAME ACCOUNT REGISTRAR TOOL")
    print(f"{'='*60}\n")
    
    for i in range(args.count):
        print(f"\n[{i+1}/{args.count}] Đang tạo tài khoản...")
        registrar = GameAccountRegistrar(args.game, args.headless)
        success = registrar.register()
        
        if success:
            print(f"✓ Tài khoản #{i+1} đã được tạo thành công")
        else:
            print(f"✗ Lỗi tạo tài khoản #{i+1}")
        
        if i < args.count - 1:
            wait_random(3, 5)
    
    print(f"\n{'='*60}")
    print("Hoàn thành!")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
