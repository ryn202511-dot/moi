"""
Tích hợp CodeSim API cho OTP Phone Numbers
Website: https://codesim.net/
"""
import requests
import time
import logging
from typing import Optional, Dict, Tuple

logger = logging.getLogger(__name__)


class CodeSimAPI:
    """Lớp để tương tác với CodeSim API"""
    
    BASE_URL = "https://codesim.net/api"
    
    def __init__(self, api_key: str):
        """
        Khởi tạo CodeSim API client
        
        Args:
            api_key: API key từ CodeSim (https://codesim.net/)
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })
        self.logger = logger
    
    def get_countries(self) -> Dict:
        """Lấy danh sách các quốc gia hỗ trợ"""
        try:
            url = f"{self.BASE_URL}/countries"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.logger.info("Lấy danh sách quốc gia thành công")
            return response.json()
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách quốc gia: {e}")
            return {}
    
    def get_services(self, country_id: int = 174) -> Dict:
        """
        Lấy danh sách các dịch vụ hỗ trợ (mặc định Việt Nam)
        
        Args:
            country_id: ID quốc gia (174 = Việt Nam)
        """
        try:
            url = f"{self.BASE_URL}/services"
            params = {'country': country_id}
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            self.logger.info(f"Lấy danh sách dịch vụ cho quốc gia {country_id} thành công")
            return response.json()
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy danh sách dịch vụ: {e}")
            return {}
    
    def rent_number(self, service_id: int, country_id: int = 174) -> Optional[Dict]:
        """
        Thuê một số điện thoại
        
        Args:
            service_id: ID dịch vụ (ví dụ: 1 = Gmail, 2 = WhatsApp, v.v.)
            country_id: ID quốc gia (174 = Việt Nam)
            
        Returns:
            Dict chứa thông tin số điện thoại hoặc None nếu lỗi
        """
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
                phone_number = rental.get('phone')
                rental_id = rental.get('id')
                self.logger.info(f"Thuê SĐT thành công: {phone_number} (ID: {rental_id})")
                return {
                    'id': rental_id,
                    'phone': phone_number,
                    'service_id': service_id,
                    'country_id': country_id
                }
            else:
                self.logger.error(f"Lỗi thuê SĐT: {result.get('message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khi thuê SĐT: {e}")
            return None
    
    def get_otp(self, rental_id: int, wait_seconds: int = 60) -> Optional[str]:
        """
        Lấy OTP từ số điện thoại thuê
        
        Args:
            rental_id: ID thuê số
            wait_seconds: Thời gian chờ OTP (giây)
            
        Returns:
            String chứa OTP hoặc None nếu lỗi
        """
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
                            self.logger.info(f"Lấy OTP thành công: {otp}")
                            # Trích xuất mã số từ text nếu cần
                            otp_code = self._extract_otp(otp)
                            return otp_code
                
                time.sleep(2)  # Chờ 2 giây trước khi kiểm tra lại
            
            self.logger.warning(f"Không nhận được OTP trong vòng {wait_seconds} giây")
            return None
            
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy OTP: {e}")
            return None
    
    def _extract_otp(self, text: str) -> str:
        """
        Trích xuất mã OTP từ văn bản SMS
        
        Args:
            text: Nội dung SMS
            
        Returns:
            Mã OTP (chuỗi số 4-6 ký tự)
        """
        import re
        # Tìm số có 4-6 chữ số liên tiếp
        match = re.search(r'\b\d{4,6}\b', text)
        if match:
            return match.group()
        # Nếu không tìm được, trả lại toàn bộ text
        return text
    
    def release_number(self, rental_id: int) -> bool:
        """
        Giải phóng số điện thoại
        
        Args:
            rental_id: ID thuê số
            
        Returns:
            True nếu thành công, False nếu lỗi
        """
        try:
            url = f"{self.BASE_URL}/rentals/{rental_id}"
            response = self.session.delete(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                self.logger.info(f"Giải phóng SĐT thành công (ID: {rental_id})")
                return True
            else:
                self.logger.error(f"Lỗi giải phóng SĐT: {result.get('message')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Lỗi khi giải phóng SĐT: {e}")
            return False
    
    def get_balance(self) -> Optional[float]:
        """
        Lấy số dư tài khoản
        
        Returns:
            Số dư (float) hoặc None nếu lỗi
        """
        try:
            url = f"{self.BASE_URL}/user/balance"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                balance = result.get('data', {}).get('balance')
                self.logger.info(f"Số dư tài khoản: {balance}")
                return balance
            else:
                self.logger.error(f"Lỗi lấy số dư: {result.get('message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy số dư: {e}")
            return None
    
    def get_rental_status(self, rental_id: int) -> Optional[Dict]:
        """
        Lấy trạng thái của một thuê số
        
        Args:
            rental_id: ID thuê số
            
        Returns:
            Dict chứa thông tin trạng thái hoặc None nếu lỗi
        """
        try:
            url = f"{self.BASE_URL}/rentals/{rental_id}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            if result.get('success'):
                return result.get('data')
            else:
                self.logger.error(f"Lỗi lấy trạng thái: {result.get('message')}")
                return None
                
        except Exception as e:
            self.logger.error(f"Lỗi khi lấy trạng thái: {e}")
            return None


def rent_and_get_otp(api_key: str, service_id: int, 
                     country_id: int = 174, wait_seconds: int = 60) -> Tuple[Optional[str], Optional[int]]:
    """
    Hàm tiện ích: Thuê số điện thoại và lấy OTP
    
    Args:
        api_key: API key từ CodeSim
        service_id: ID dịch vụ
        country_id: ID quốc gia (mặc định 174 = Việt Nam)
        wait_seconds: Thời gian chờ OTP (giây)
        
    Returns:
        Tuple (phone_number, rental_id) hoặc (None, None) nếu lỗi
    """
    api = CodeSimAPI(api_key)
    
    # Thuê số
    rental = api.rent_number(service_id, country_id)
    if not rental:
        return None, None
    
    phone = rental['phone']
    rental_id = rental['id']
    
    # Lấy OTP
    otp = api.get_otp(rental_id, wait_seconds)
    
    if otp:
        logger.info(f"Thêm OTP thành công cho {phone}: {otp}")
    else:
        logger.warning(f"Không lấy được OTP cho {phone}")
    
    return (phone, rental_id), otp


# Service ID mapping (phổ biến)
SERVICE_IDS = {
    'gmail': 1,
    'whatsapp': 2,
    'facebook': 3,
    'instagram': 4,
    'telegram': 5,
    'viber': 6,
    'line': 7,
    'twitter': 8,
    'tiktok': 9,
    'discord': 10,
    'twitch': 11,
    'snapchat': 12,
    'wechat': 13,
    'qq': 14,
    'alipay': 15,
    'wealthsimple': 16,
    'uber': 17,
    'airbnb': 18,
    'booking': 19,
    'paypal': 20,
}

# Country ID mapping
COUNTRY_IDS = {
    'vietnam': 174,
    'thailand': 213,
    'indonesia': 101,
    'philippines': 179,
    'singapore': 195,
    'malaysia': 149,
    'usa': 222,
    'uk': 221,
    'uk_private': 221,
}
