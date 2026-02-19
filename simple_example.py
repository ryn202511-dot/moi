"""
Ví dụ đơn giản sử dụng Game Account Registrar
"""
from game_account_registrar import GameAccountRegistrar


def main():
    """Hàm main để test tool"""
    
    print("\n" + "="*60)
    print("GAME ACCOUNT REGISTRAR - SIMPLE EXAMPLE")
    print("="*60 + "\n")
    
    # Tạo instance registrar
    registrar = GameAccountRegistrar(game_name='default', headless=False)
    
    # Thực hiện đăng ký với selector mặc định
    print("Đang bắt đầu quy trình đăng ký...")
    success = registrar.register()
    
    # Hiển thị kết quả
    print("\n" + "="*60)
    if success:
        print("✓ ĐÃ ĐĂNG KÝ TÀI KHOẢN THÀNH CÔNG!")
        print(f"Username: {registrar.account_data.username}")
        print(f"Email: {registrar.account_data.email}")
        print(f"Password: {registrar.account_data.password}")
        print("\nThông tin tài khoản được lưu vào: accounts.txt")
    else:
        print("✗ ĐĂNG KÝ THẤT BẠI")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
