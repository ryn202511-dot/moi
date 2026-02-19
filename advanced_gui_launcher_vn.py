"""
Advanced Game Account Registrar - Vietnam Banks Edition
GUI hoàn chỉnh với hỗ trợ ngân hàng Việt Nam và form preview
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import os
import json
import requests
from datetime import datetime
from game_account_registrar import GameAccountRegistrar
from config import GAME_SERVERS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random

# Vietnam Banks
VIETNAM_BANKS = {
    'vietcombank': 'Vietcombank (VCBK)',
    'acb': 'ACB - Asia Commercial Bank',
    'techcombank': 'Techcombank',
    'vpbank': 'VP Bank',
    'bidv': 'BIDV - Bank for Investment and Development of Vietnam',
    'scb': 'SCB - Saigon Commercial Bank',
    'oceanbank': 'OceanBank',
    'agribank': 'Agribank',
    'dab': 'DAB - Direct Asia Bank',
    'eximbank': 'Eximbank',
    'maritime': 'Maritime Bank',
    'mbbank': 'MB Bank',
    'tpbank': 'TPBank',
    'sacombank': 'SacomBank',
    'abbank': 'AB Bank',
}


class AdvancedVNGUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar - Vietnam Edition")
        self.root.geometry("1400x850")
        
        self.is_running = False
        self.registrar = None
        self.accounts_data = []
        self.sdt_data = []
        self.form_fields = {}
        
        # Form Tab variables
        self.form_url_var = tk.StringVar()
        self.form_proxy_var = tk.StringVar(value="(không dùng)")
        self.form_otp_var = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_config()
        
    def create_widgets(self):
        """Tạo UI hoàn chỉnh"""
        # ========== TAB INTERFACE ==========
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # TAB 1: Configuration
        config_tab = ttk.Frame(self.notebook)
        self.notebook.add(config_tab, text="⚙️ CẤU HÌNH")
        self.create_config_tab(config_tab)
        
        # TAB 2: Form Preview
        form_tab = ttk.Frame(self.notebook)
        self.notebook.add(form_tab, text="📝 FORM ĐĂC KÝ")
        self.create_form_tab(form_tab)
        
        # TAB 3: Log
        log_tab = ttk.Frame(self.notebook)
        self.notebook.add(log_tab, text="📊 LOG KẾT QUẢ")
        self.create_log_tab(log_tab)
    
    def create_config_tab(self, parent):
        """Tab cấu hình"""
        config_frame = ttk.Frame(parent, padding=10)
        config_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Column
        left_col = ttk.LabelFrame(config_frame, text="🔗 THÔNG TIN ĐẠO DIỆN", padding=10)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10, ipadx=10, ipady=10)
        
        # URL
        ttk.Label(left_col, text="📍 URL Đăng Ký:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=8)
        self.url_var = tk.StringVar()
        ttk.Entry(left_col, textvariable=self.url_var, width=45, font=('Arial', 10)).grid(row=0, column=1, sticky='ew', pady=8, padx=10)
        
        # Proxy
        ttk.Label(left_col, text="🔗 Proxy:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=8)
        self.proxy_var = tk.StringVar(value="(không dùng)")
        ttk.Entry(left_col, textvariable=self.proxy_var, width=45, font=('Arial', 10)).grid(row=1, column=1, sticky='ew', pady=8, padx=10)
        
        # Vietnam Bank Selection
        ttk.Label(left_col, text="🏦 Ngân Hàng VN:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=8)
        self.bank_var = tk.StringVar(value='vietcombank')
        bank_combo = ttk.Combobox(
            left_col,
            textvariable=self.bank_var,
            values=list(VIETNAM_BANKS.values()),
            state='readonly',
            width=42,
            font=('Arial', 10)
        )
        bank_combo.grid(row=2, column=1, sticky='ew', pady=8, padx=10)
        
        # Game Selection
        ttk.Label(left_col, text="🎮 Chọn Game:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', pady=8)
        self.game_var = tk.StringVar(value='default')
        game_combo = ttk.Combobox(
            left_col,
            textvariable=self.game_var,
            values=list(GAME_SERVERS.keys()),
            state='readonly',
            width=42,
            font=('Arial', 10)
        )
        game_combo.grid(row=3, column=1, sticky='ew', pady=8, padx=10)
        
        # Account Count
        ttk.Label(left_col, text="📊 Số Lượng:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', pady=8)
        self.count_var = tk.StringVar(value='1')
        ttk.Spinbox(left_col, from_=1, to=1000, textvariable=self.count_var, font=('Arial', 10), width=42).grid(row=4, column=1, sticky='ew', pady=8, padx=10)
        
        # Separator
        ttk.Separator(left_col, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, sticky='ew', pady=15)
        
        # Data Files
        ttk.Label(left_col, text="📁 DỮ LIỆU TÀI KHOẢN", font=('Arial', 10, 'bold')).grid(row=6, column=0, columnspan=2, sticky='w', pady=8)
        
        ttk.Label(left_col, text="File Data (TK REG.TXT):", font=('Arial', 9)).grid(row=7, column=0, sticky='w', pady=5)
        self.data_file_var = tk.StringVar(value="TK REG.TXT")
        data_frame = ttk.Frame(left_col)
        data_frame.grid(row=7, column=1, sticky='ew', pady=5, padx=10)
        ttk.Entry(data_frame, textvariable=self.data_file_var).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(data_frame, text="Browse", command=self.browse_data_file, width=10).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(left_col, orient=tk.HORIZONTAL).grid(row=8, column=0, columnspan=2, sticky='ew', pady=15)
        
        # OTP Settings
        ttk.Label(left_col, text="📱 CẤU HÌNH OTP", font=('Arial', 10, 'bold')).grid(row=9, column=0, columnspan=2, sticky='w', pady=8)
        
        self.use_otp_var = tk.BooleanVar(value=False)
        otp_check = ttk.Checkbutton(
            left_col,
            text="✓ Sử dụng SDT có OTP",
            variable=self.use_otp_var,
            command=self.toggle_otp_fields,
            font=('Arial', 10)
        )
        otp_check.grid(row=10, column=0, columnspan=2, sticky='w', pady=8, padx=10)
        
        ttk.Label(left_col, text="File SDT (sdt.txt):", font=('Arial', 9)).grid(row=11, column=0, sticky='w', pady=5)
        self.sdt_file_var = tk.StringVar(value="sdt.txt")
        sdt_frame = ttk.Frame(left_col)
        sdt_frame.grid(row=11, column=1, sticky='ew', pady=5, padx=10)
        ttk.Entry(sdt_frame, textvariable=self.sdt_file_var, state='disabled').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(sdt_frame, text="Browse", state='disabled', width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(left_col, text="CodeSim API Key:", font=('Arial', 9)).grid(row=12, column=0, sticky='w', pady=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(left_col, textvariable=self.api_key_var, show='*', font=('Arial', 10), state='disabled').grid(row=12, column=1, sticky='ew', pady=5, padx=10)
        
        # Separator
        ttk.Separator(left_col, orient=tk.HORIZONTAL).grid(row=13, column=0, columnspan=2, sticky='ew', pady=15)
        
        # Options
        ttk.Label(left_col, text="⚡ TÙY CHỌN", font=('Arial', 10, 'bold')).grid(row=14, column=0, columnspan=2, sticky='w', pady=8)
        
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_col, text="Chế độ Headless (ẩn trình duyệt)", variable=self.headless_var, font=('Arial', 9)).grid(row=15, column=0, columnspan=2, sticky='w', padx=10, pady=5)
        
        # Right Column - Status
        right_col = ttk.LabelFrame(config_frame, text="📊 THỐNG KÊ VÀ ĐIỀU KHIỂN", padding=10)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10, ipadx=10, ipady=10)
        
        # Status Info
        self.success_var = tk.StringVar(value="✓ Thành công: 0")
        self.success_label = ttk.Label(right_col, textvariable=self.success_var, font=('Arial', 11, 'bold'), foreground="green")
        self.success_label.pack(anchor='w', pady=10, padx=10)
        
        self.fail_var = tk.StringVar(value="✗ Thất bại: 0")
        self.fail_label = ttk.Label(right_col, textvariable=self.fail_var, font=('Arial', 11, 'bold'), foreground="red")
        self.fail_label.pack(anchor='w', pady=10, padx=10)
        
        self.current_var = tk.StringVar(value="► Đang xử lý: --")
        self.current_label = ttk.Label(right_col, textvariable=self.current_var, font=('Arial', 11, 'bold'), foreground="blue")
        self.current_label.pack(anchor='w', pady=10, padx=10)
        
        # Progress Bar
        self.progress = ttk.Progressbar(right_col, mode='determinate', length=300)
        self.progress.pack(fill=tk.X, pady=20, padx=10)
        
        # Button Frame
        button_frame = ttk.Frame(right_col)
        button_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=10)
        
        self.start_btn = ttk.Button(button_frame, text="▶  BẮT ĐẦU ĐĂNG KÝ", command=self.start)
        self.start_btn.pack(fill=tk.X, pady=10, ipady=10)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹  DỪNG", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(fill=tk.X, pady=10, ipady=10)
        
        self.clear_btn = ttk.Button(button_frame, text="🗑  XÓA LOG", command=self.clear_log)
        self.clear_btn.pack(fill=tk.X, pady=10, ipady=10)
        
        left_col.grid_columnconfigure(1, weight=1)
    
    def create_form_tab(self, parent):
        """Tab xem trước form đăng ký"""
        form_frame = ttk.Frame(parent, padding=10)
        form_frame.pack(fill=tk.BOTH, expand=True)
        
        # ========== INPUT SECTION ==========
        input_section = ttk.LabelFrame(form_frame, text="⚙️ CẤU HÌNH TẠMCHWI TRƯỚC KHI ĐĂNG KÝ", padding=10)
        input_section.pack(fill=tk.X, padx=10, pady=10)
        
        # URL input
        ttk.Label(input_section, text="🔗 URL Đăng Ký:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', pady=8, padx=5)
        self.form_url_var = tk.StringVar()
        ttk.Entry(input_section, textvariable=self.form_url_var, font=('Arial', 10), width=70).grid(row=0, column=1, sticky='ew', pady=8, padx=5)
        
        # Proxy input
        ttk.Label(input_section, text="🔗 Proxy:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', pady=8, padx=5)
        self.form_proxy_var = tk.StringVar(value="(không dùng)")
        ttk.Entry(input_section, textvariable=self.form_proxy_var, font=('Arial', 10), width=70).grid(row=1, column=1, sticky='ew', pady=8, padx=5)
        
        # OTP toggle
        ttk.Label(input_section, text="📱 Sử dụng SDT OTP:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', pady=8, padx=5)
        otp_frame = ttk.Frame(input_section)
        otp_frame.grid(row=2, column=1, sticky='w', pady=8, padx=5)
        self.form_otp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(otp_frame, text="✓ Bật OTP", variable=self.form_otp_var).pack(side=tk.LEFT)
        
        input_section.grid_columnconfigure(1, weight=1)
        
        # ========== FORM PREVIEW SECTION ==========
        info_label = ttk.Label(form_frame, text="📝 Các trường form đăng ký sẽ hiển thị và có thể chỉnh sửa tại đây", font=('Arial', 10, 'bold'))
        info_label.pack(pady=10)
        
        # Scrollable form area
        self.form_canvas = tk.Canvas(form_frame)
        scrollbar = ttk.Scrollbar(form_frame, orient="vertical", command=self.form_canvas.yview)
        self.form_scrollable = ttk.Frame(self.form_canvas)
        
        self.form_scrollable.bind(
            "<Configure>",
            lambda e: self.form_canvas.configure(scrollregion=self.form_canvas.bbox("all"))
        )
        
        self.form_canvas.create_window((0, 0), window=self.form_scrollable, anchor="nw")
        self.form_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.form_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Sample form fields
        self.create_sample_form_fields()
    
    def create_sample_form_fields(self):
        """Tạo các trường form mẫu"""
        sample_fields = [
            ("Username", "user_abc123"),
            ("Email", "user_abc@gmail.com"),
            ("Password", "Pass123!@#"),
            ("Confirm Password", "Pass123!@#"),
            ("Số điện thoại", "0912345678"),
            ("Ngân hàng", "Vietcombank"),
            ("Số tài khoản", "0123456789"),
            ("Họ tên", "Nguyễn Văn A"),
            ("Ngày sinh", "01/01/1990"),
            ("Địa chỉ", "Hà Nội, Việt Nam"),
        ]
        
        for field_name, field_value in sample_fields:
            field_frame = ttk.LabelFrame(self.form_scrollable, text=f"📌 {field_name}", padding=10)
            field_frame.pack(fill=tk.X, padx=10, pady=10, ipadx=10, ipady=10)
            
            var = tk.StringVar(value=field_value)
            self.form_fields[field_name] = var
            
            entry = ttk.Entry(field_frame, textvariable=var, font=('Arial', 11), width=50)
            entry.pack(fill=tk.X, ipady=8)
            
            hint = ttk.Label(field_frame, text=f"Giá trị mặc định: {field_value}", font=('Arial', 8), foreground="gray")
            hint.pack(anchor='w', pady=5)
    
    def create_log_tab(self, parent):
        """Tab log kết quả"""
        log_frame = ttk.Frame(parent, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red", font=('Courier', 9, 'bold'))
        self.log_text.tag_config("success", foreground="green", font=('Courier', 9, 'bold'))
        self.log_text.tag_config("warning", foreground="orange", font=('Courier', 9, 'bold'))
        self.log_text.tag_config("info", foreground="blue", font=('Courier', 9))
        self.log_text.tag_config("header", foreground="darkblue", font=('Courier', 10, 'bold'))
    
    def toggle_otp_fields(self):
        """Bật/tắt OTP fields"""
        state = 'normal' if self.use_otp_var.get() else 'disabled'
        # Update widget states for OTP fields
    
    def browse_data_file(self):
        """Chọn file data"""
        file = filedialog.askopenfilename(
            title="Chọn file data (TK REG.TXT)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.data_file_var.set(file)
            self.load_data_file(file)
    
    def load_data_file(self, filepath):
        """Tải dữ liệu từ file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.accounts_data = [line.strip() for line in f if line.strip()]
            self.log(f"✓ Tải {len(self.accounts_data)} tài khoản từ: {filepath}", "success")
        except Exception as e:
            self.log(f"✗ Lỗi tải file data: {str(e)}", "error")
    
    def load_config(self):
        """Tải cấu hình mặc định"""
        default_url = GAME_SERVERS.get(self.game_var.get(), {}).get('url', '')
        self.url_var.set(default_url)
    
    def log(self, message, level="info"):
        """Ghi log"""
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n", level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete('1.0', tk.END)
    
    def start(self):
        """Bắt đầu đăng ký"""
        # Ưu tiên URL từ Form Tab
        url = self.form_url_var.get().strip()
        if not url:
            url = self.url_var.get().strip()
        
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL ở tab 'FORM ĐĂNG KÝ' hoặc 'CẤU HÌNH'")
            return
        
        # Check accounts_data
        if not self.accounts_data:
            data_file = self.data_file_var.get().strip()
            if not data_file or not os.path.exists(data_file):
                messagebox.showerror("Lỗi", "Vui lòng:\n1. Nhập tài khoản ở tab 'NHẬP TRỰC TIẾP', HOẶC\n2. Chọn file data tài khoản")
                return
            self.load_data_file(data_file)
            if not self.accounts_data:
                messagebox.showerror("Lỗi", "File data không có tài khoản nào")
                return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        
        # Pass URL to registration
        thread = threading.Thread(target=self.run_registration, args=(url,))
        thread.daemon = True
        thread.start()
    
    def run_registration(self, url=None):
        """Chạy quá trình đăng ký"""
        driver = None
        try:
            # Lấy URL từ parameter hoặc config
            if not url:
                url = self.url_var.get().strip()
            
            # Lấy proxy: ưu tiên Form Tab
            proxy = self.form_proxy_var.get().strip()
            if not proxy or proxy == "(không dùng)":
                proxy = self.proxy_var.get().strip()
            if not proxy or proxy == "(không dùng)":
                proxy = None
            
            # Lấy OTP: ưu tiên Form Tab
            use_otp = self.form_otp_var.get() if hasattr(self, 'form_otp_var') else self.use_otp_var.get()
            
            bank = self.bank_var.get()
            headless = self.headless_var.get()
            
            self.log(f"\n{'='*70}", "header")
            self.log("🎮 GAME ACCOUNT REGISTRAR - VIETNAM EDITION 🇻🇳", "header")
            self.log(f"{'='*70}", "header")
            self.log(f"📍 URL: {url}", "info")
            self.log(f"🏦 Ngân Hàng: {bank}", "info")
            self.log(f"🔗 Proxy: {proxy or '(không dùng)'}", "info")
            self.log(f"📱 OTP Mode: {'✓ BẬT' if use_otp else '✗ TẮT'}", "info")
            self.log(f"🔐 Headless: {'✓ BẬT' if headless else '✗ TẮT'}", "info")
            
            success_count = 0
            fail_count = 0
            total = len(self.accounts_data)
            
            for idx, line in enumerate(self.accounts_data):
                if not self.is_running:
                    self.log("\n⚠ Quá trình bị dừng bởi người dùng", "warning")
                    break
                
                self.progress['value'] = ((idx + 1) / total) * 100
                self.current_var.set(f"► Đang xử lý: {idx + 1}/{total}")
                
                driver = None
                try:
                    parts = line.split('|')
                    if len(parts) < 2:
                        self.log(f"[{idx + 1}] ✗ Format không hợp lệ: {line}", "error")
                        fail_count += 1
                        continue
                    
                    username = parts[0].strip()
                    email = parts[1].strip() if len(parts) > 1 else ""
                    password = parts[2].strip() if len(parts) > 2 else ""
                    
                    self.log(f"\n[{idx + 1}/{total}] 🔄 Đăng ký: {username}", "info")
                    self.log(f"  📧 Email: {email}", "info")
                    self.log(f"  🏦 Ngân Hàng: {bank}", "info")
                    
                    # Setup Selenium
                    self.log(f"  ▶ Khởi tạo Chrome WebDriver...", "info")
                    options = Options()
                    
                    if headless:
                        options.add_argument('--headless')
                    
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    
                    if proxy:
                        options.add_argument(f'--proxy-server={proxy}')
                    
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    
                    self.log(f"  ✓ WebDriver OK", "success")
                    self.log(f"  ▶ Truy cập: {url}", "info")
                    driver.get(url)
                    time.sleep(random.uniform(2, 4))
                    self.log(f"  ✓ Trang tải thành công", "success")
                    
                    # Try fill form with collected data
                    wait = WebDriverWait(driver, 10)
                    
                    # Fill username
                    try:
                        username_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='username'], input[id*='username'], #username"))
                        )
                        username_field.clear()
                        username_field.send_keys(username)
                        self.log(f"  ✓ Điền Username", "success")
                    except:
                        self.log(f"  ⚠ Không tìm Username field", "warning")
                    
                    # Fill email
                    try:
                        email_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name*='email'], #email"))
                        )
                        email_field.clear()
                        email_field.send_keys(email)
                        self.log(f"  ✓ Điền Email", "success")
                    except:
                        self.log(f"  ⚠ Không tìm Email field", "warning")
                    
                    # Fill password
                    try:
                        password_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name*='password'], #password"))
                        )
                        password_field.clear()
                        password_field.send_keys(password)
                        self.log(f"  ✓ Điền Password", "success")
                    except:
                        self.log(f"  ⚠ Không tìm Password field", "warning")
                    
                    # Submit
                    try:
                        submit_btn = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], .btn-submit"))
                        )
                        self.log(f"  ▶ Gửi form...", "info")
                        submit_btn.click()
                        time.sleep(random.uniform(2, 4))
                        self.log(f"  ✓ Form gửi thành công", "success")
                    except:
                        self.log(f"  ⚠ Không tìm nút Submit", "warning")
                    
                    # Check result
                    time.sleep(2)
                    success = False
                    page_source = driver.page_source.lower()
                    
                    if any(keyword in page_source for keyword in ['success', 'welcome', 'registered', 'hoàn tất', 'thành công']):
                        success = True
                    
                    if success:
                        with open('ACC OK.TXT', 'a', encoding='utf-8') as f:
                            f.write(f"{username}|{password}|{email}|{bank}\n")
                        self.log(f"  ✓✓✓ ĐĂNG KÝ THÀNH CÔNG ✓✓✓", "success")
                        success_count += 1
                    else:
                        with open('FAIL.TXT', 'a', encoding='utf-8') as f:
                            f.write(f"{line}|BANK:{bank}|ERROR: Không xác nhận được thành công\n")
                        self.log(f"  ✗ Không xác nhận thành công", "error")
                        fail_count += 1
                    
                except Exception as e:
                    self.log(f"  ✗ Lỗi: {str(e)}", "error")
                    fail_count += 1
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                        except:
                            pass
                
                self.success_var.set(f"✓ Thành công: {success_count}")
                self.fail_var.set(f"✗ Thất bại: {fail_count}")
                
                if idx < total - 1:
                    delay = random.uniform(3, 5)
                    time.sleep(delay)
            
            # Summary
            self.log(f"\n{'='*70}", "header")
            self.log(f"✓ THÀNH CÔNG: {success_count}/{total}", "success")
            self.log(f"✗ THẤT BẠI: {fail_count}/{total}", "error")
            self.log(f"📁 Kết quả lưu: ACC OK.TXT & FAIL.TXT", "info")
            self.log(f"{'='*70}\n", "header")
            
            self.progress['value'] = 100
            messagebox.showinfo("Hoàn thành", f"✓ Thành công: {success_count}\n✗ Thất bại: {fail_count}")
            
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}", "error")
            messagebox.showerror("Lỗi", f"❌ {str(e)}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop(self):
        """Dừng"""
        self.is_running = False
        self.log("\n⏹ Đang dừng...", "warning")


def main():
    root = tk.Tk()
    app = AdvancedVNGUILauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
