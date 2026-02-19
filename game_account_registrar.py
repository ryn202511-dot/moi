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
    save_successful_account,
    save_failed_account,
    wait_random,
)


class GameAccountRegistrar:
    """Lớp chính để đăng ký tài khoản game"""
    
    def __init__(self, game_name='default', headless=False, url=None, proxy=None, 
                 bank='vietcombank', phone_mode='none', codesim_api_key='',
                 codesim_service='gmail', otp_wait_seconds=60):
        """
        Khởi tạo registrar
        
        Args:
            game_name: Tên game (key trong GAME_SERVERS)
            headless: Chạy ẩn (không hiển thị trình duyệt)
            url: URL custom để đăng ký (nếu không cung cấp, dùng từ GAME_SERVERS)
            proxy: Proxy URL (tuỳ chọn)
            bank: Ngân hàng được chọn
            phone_mode: 'none', 'no_otp', 'with_otp'
            codesim_api_key: API key từ CodeSim
            codesim_service: Service name trên CodeSim (gmail, whatsapp, etc.)
            otp_wait_seconds: Thời gian chờ OTP (giây)
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
        
        # Custom URL if provided
        if url:
            self.game_config['url'] = url
            self.logger.info(f"Sử dụng URL custom: {url}")
        
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
        
        if proxy:
            self.logger.info(f"Sử dụng Proxy: {proxy}")
        self.logger.info(f"Ngân hàng: {bank}")
        self.logger.info(f"Phone Mode: {phone_mode}")
        
        if phone_mode == 'with_otp' and codesim_api_key:
            self.logger.info(f"CodeSim Service: {codesim_service}")
            self.logger.info(f"OTP Wait Time: {otp_wait_seconds}s")
    
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
            
            # Proxy support
            if self.proxy:
                options.add_argument(f'--proxy-server={self.proxy}')
                self.logger.info(f"Thêm Proxy: {self.proxy}")
            
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
    
    def get_otp_from_codesim(self):
        """
        Thuê số điện thoại từ CodeSim và lấy OTP
        
        Returns:
            Dict {'phone': số điện thoại, 'otp': mã OTP, 'rental_id': ID}
            hoặc None nếu lỗi
        """
        try:
            from codesim_api import CodeSimAPI, SERVICE_IDS
            
            if not self.codesim_api_key:
                self.logger.error("CodeSim API Key không được cung cấp")
                return None
            
            api = CodeSimAPI(self.codesim_api_key)
            
            # Lấy service ID
            service_id = SERVICE_IDS.get(self.codesim_service, 20)
            
            self.logger.info(f"Đang thuê SĐT từ CodeSim (Service: {self.codesim_service})...")
            
            # Thuê số
            rental = api.rent_number(service_id, country_id=174)
            if not rental:
                self.logger.error("Không thể thuê SĐT từ CodeSim")
                return None
            
            phone = rental['phone']
            rental_id = rental['id']
            
            self.logger.info(f"✓ Đã thuê SĐT: {phone}")
            self.otp_phone = phone
            self.rental_id = rental_id
            
            # Lấy OTP
            self.logger.info(f"Đang chờ OTP ({self.otp_wait_seconds}s)...")
            otp = api.get_otp(rental_id, self.otp_wait_seconds)
            
            if not otp:
                self.logger.error(f"Không nhận được OTP cho {phone} trong {self.otp_wait_seconds}s")
                return None
            
            self.otp_code = otp
            self.logger.info(f"✓ Lấy OTP thành công: {otp}")
            
            return {
                'phone': phone,
                'otp': otp,
                'rental_id': rental_id
            }
            
        except Exception as e:
            self.logger.error(f"Lỗi lấy OTP từ CodeSim: {e}")
            return None
    
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
                               'phone': '#phone',
                               'otp': '#otp',
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
                'phone': '#phone',
                'otp': '#otp',
                'terms': '#terms',
                'submit': 'button[type="submit"]'
            }
        
        try:
            # Tạo dữ liệu tài khoản
            self.account_data = AccountData()
            self.logger.info(f"\nTài khoản mới:\n{self.account_data}\n")
            
            phone = ''
            
            # Lấy OTP từ CodeSim nếu cần
            if self.phone_mode == 'with_otp' and self.codesim_api_key:
                self.logger.info("Mode: SĐT có OTP (từ CodeSim)")
                otp_result = self.get_otp_from_codesim()
                
                if not otp_result:
                    self.logger.error("Không thể lấy OTP từ CodeSim, dừng quá trình")
                    return False
                
                phone = otp_result['phone']
                self.account_data.phone = phone
            
            elif self.phone_mode == 'no_otp':
                self.logger.info("Mode: SĐT không OTP")
                # Phone sẽ được lấy từ file ở tầng GUI
                pass
            
            else:
                self.logger.info("Mode: Không dùng SĐT")
            
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
            
            # Điền số điện thoại nếu có
            if phone and form_selectors.get('phone'):
                try:
                    phone_element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, form_selectors['phone']))
                    )
                    phone_element.clear()
                    phone_element.send_keys(phone)
                    wait_random(0.5, 1)
                    self.logger.info(f"Điền SĐT: {phone}")
                except:
                    self.logger.warning("Không thể điền số điện thoại")
            
            # Điền OTP nếu có
            if self.otp_code and form_selectors.get('otp'):
                try:
                    self.logger.info("Chờ trước khi điền OTP...")
                    wait_random(2, 3)
                    
                    otp_element = self.wait.until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, form_selectors['otp']))
                    )
                    otp_element.clear()
                    otp_element.send_keys(self.otp_code)
                    wait_random(0.5, 1)
                    self.logger.info(f"Điền OTP: {self.otp_code}")
                except:
                    self.logger.warning("Không thể điền OTP")
            
            if not self.accept_terms(form_selectors['terms']):
                return False
            
            # Gửi form
            if not self.submit_form(form_selectors['submit']):
                return False
            
            # Kiểm tra kết quả
            if self.check_success():
                # Lưu tài khoản thành công
                save_successful_account(
                    self.account_data.username,
                    self.account_data.password,
                    self.account_data.email,
                    phone=phone,
                    bank=self.bank,
                    url=self.game_config['url'],
                    filename='ACC_OK.txt'
                )
                self.logger.info("✓ Tài khoản đã được lưu vào ACC_OK.txt")
                return True
            else:
                # Lưu tài khoản fail
                save_failed_account(
                    self.account_data.username,
                    self.account_data.password,
                    self.account_data.email,
                    phone=phone,
                    bank=self.bank,
                    url=self.game_config['url'],
                    error_msg='Không xác nhận đăng ký thành công',
                    filename='FAIL.txt'
                )
                self.logger.error("✗ Tài khoản lưu vào FAIL.txt")
                return False
            
        except Exception as e:
            self.logger.error(f"Lỗi trong quá trình đăng ký: {e}")
            # Lưu account fail với error message
            if self.account_data:
                save_failed_account(
                    self.account_data.username,
                    self.account_data.password,
                    self.account_data.email,
                    phone=phone if hasattr(self, 'otp_phone') else '',
                    bank=self.bank,
                    url=self.game_config['url'],
                    error_msg=str(e),
                    filename='FAIL.txt'
                )
            return False
        
        finally:
            # Giải phóng SĐT từ CodeSim nếu cần
            if self.rental_id and self.phone_mode == 'with_otp':
                try:
                    from codesim_api import CodeSimAPI
                    api = CodeSimAPI(self.codesim_api_key)
                    if api.release_number(self.rental_id):
                        self.logger.info(f"✓ Giải phóng SĐT {self.otp_phone} thành công")
                except Exception as e:
                    self.logger.warning(f"Lỗi giải phóng SĐT: {e}")
            
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
