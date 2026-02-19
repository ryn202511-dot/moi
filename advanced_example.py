"""
Ví dụ sử dụng advanced Game Account Registrar
Các ví dụ với các selector tùy chỉnh cho các game khác nhau
"""
from game_account_registrar import GameAccountRegistrar
from utils import setup_logger


logger = setup_logger('AdvancedExample', 'logs/advanced_example.log')


def example_basic_registration():
    """Ví dụ 1: Đăng ký cơ bản với selector mặc định"""
    logger.info("="*60)
    logger.info("VÍ DỤ 1: Đăng ký cơ bản")
    logger.info("="*60)
    
    registrar = GameAccountRegistrar(game_name='default', headless=False)
    success = registrar.register()
    
    if success:
        logger.info("✓ Đăng ký thành công!")
    else:
        logger.info("✗ Đăng ký thất bại!")
    
    return success


def example_custom_selectors():
    """Ví dụ 2: Đăng ký với selector tùy chỉnh"""
    logger.info("="*60)
    logger.info("VÍ DỤ 2: Đăng ký với selector tùy chỉnh")
    logger.info("="*60)
    
    registrar = GameAccountRegistrar(game_name='default', headless=False)
    
    # Custom selectors cho game cụ thể
    custom_selectors = {
        'username': 'input[name="user"]',  # Tùy chỉnh selector username
        'email': 'input[class="email-field"]',  # Tùy chỉnh selector email
        'password': 'input[id="pwd"]',  # Tùy chỉnh selector password
        'confirm_password': 'input[id="confirm_pwd"]',
        'terms': 'input[type="checkbox"][class="agree"]',
        'submit': 'button[class="register-btn"]'
    }
    
    success = registrar.register(form_selectors=custom_selectors)
    
    if success:
        logger.info("✓ Đăng ký thành công với selector tùy chỉnh!")
    else:
        logger.info("✗ Đăng ký thất bại!")
    
    return success


def example_headless_mode():
    """Ví dụ 3: Chạy ở chế độ headless (ẩn)"""
    logger.info("="*60)
    logger.info("VÍ DỤ 3: Chế độ headless (ẩn)")
    logger.info("="*60)
    
    registrar = GameAccountRegistrar(game_name='default', headless=True)
    success = registrar.register()
    
    if success:
        logger.info("✓ Đăng ký ở chế độ headless thành công!")
    else:
        logger.info("✗ Đăng ký ở chế độ headless thất bại!")
    
    return success


def example_multiple_accounts():
    """Ví dụ 4: Tạo nhiều tài khoản"""
    logger.info("="*60)
    logger.info("VÍ DỤ 4: Tạo 3 tài khoản")
    logger.info("="*60)
    
    num_accounts = 3
    successful = 0
    
    for i in range(num_accounts):
        logger.info(f"\n[{i+1}/{num_accounts}] Đang tạo tài khoản...")
        
        registrar = GameAccountRegistrar(game_name='default', headless=False)
        success = registrar.register()
        
        if success:
            successful += 1
            logger.info(f"✓ Tài khoản #{i+1} tạo thành công")
        else:
            logger.info(f"✗ Tài khoản #{i+1} tạo thất bại")
        
        # Chờ giữa các lần tạo tài khoản
        import time
        if i < num_accounts - 1:
            time.sleep(5)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Tổng cộng: {successful}/{num_accounts} tài khoản tạo thành công")
    logger.info(f"{'='*60}")
    
    return successful == num_accounts


def example_with_error_handling():
    """Ví dụ 5: Xử lý lỗi nâng cao"""
    logger.info("="*60)
    logger.info("VÍ DỤ 5: Xử lý lỗi nâng cao")
    logger.info("="*60)
    
    try:
        registrar = GameAccountRegistrar(game_name='default', headless=False)
        
        # Thêm logic xử lý lỗi
        if not registrar.setup_driver():
            logger.error("Lỗi khởi tạo driver, dừng lại")
            return False
        
        if not registrar.navigate_to_register_page():
            logger.error("Lỗi truy cập trang đăng ký, dừng lại")
            registrar.close()
            return False
        
        logger.info("✓ Trang tải thành công, tiếp tục đăng ký...")
        
        return True
        
    except Exception as e:
        logger.error(f"Lỗi không mong muốn: {e}")
        return False
    finally:
        if registrar:
            registrar.close()


def main():
    """Chạy các ví dụ"""
    print("\n" + "="*60)
    print("ADVANCED GAME ACCOUNT REGISTRAR EXAMPLES")
    print("="*60 + "\n")
    
    # Chọn ví dụ cần chạy
    examples = {
        '1': ('Basic Registration', example_basic_registration),
        '2': ('Custom Selectors', example_custom_selectors),
        '3': ('Headless Mode', example_headless_mode),
        '4': ('Multiple Accounts', example_multiple_accounts),
        '5': ('Error Handling', example_with_error_handling),
    }
    
    print("Các ví dụ khả dụng:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    print("0. Chạy tất cả")
    
    choice = input("\nChọn ví dụ (0-5): ").strip()
    
    if choice == '0':
        for key in ['1', '2', '3', '4', '5']:
            name, func = examples[key]
            print(f"\nChạy: {name}...")
            func()
            input("Nhấn Enter để tiếp tục...")
    elif choice in examples:
        name, func = examples[choice]
        print(f"\nChạy: {name}...")
        func()
    else:
        print("Lựa chọn không hợp lệ!")


if __name__ == '__main__':
    main()
