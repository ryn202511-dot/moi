"""
Advanced Game Account Registrar with Selenium Integration
GUI hoàn chỉnh với Selenium tự động đăng ký thực tế
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

class AdvancedGUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar - Advanced")
        self.root.geometry("1200x800")
        
        self.is_running = False
        self.registrar = None
        self.accounts_data = []
        self.sdt_data = []
        
        self.create_widgets()
        self.load_config()
        
    def create_widgets(self):
        """Tạo toàn bộ UI"""
        # ========== MAIN FRAME ==========
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ========== LEFT PANEL (INPUT) ==========
        left_panel = ttk.LabelFrame(main_frame, text="⚙️ CẤU HÌNH", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)
        
        # URL Registration
        ttk.Label(left_panel, text="📍 URL Đăng Ký:").grid(row=0, column=0, sticky='w', pady=5)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(left_panel, textvariable=self.url_var, width=40)
        self.url_entry.grid(row=0, column=1, sticky='ew', pady=5)
        
        # Proxy
        ttk.Label(left_panel, text="🔗 Proxy:").grid(row=1, column=0, sticky='w', pady=5)
        self.proxy_var = tk.StringVar(value="(không dùng)")
        self.proxy_entry = ttk.Entry(left_panel, textvariable=self.proxy_var, width=40)
        self.proxy_entry.grid(row=1, column=1, sticky='ew', pady=5)
        
        # Game/Bank Selection
        ttk.Label(left_panel, text="🎮 Chọn Game:").grid(row=2, column=0, sticky='w', pady=5)
        self.game_var = tk.StringVar(value='default')
        game_combo = ttk.Combobox(
            left_panel,
            textvariable=self.game_var,
            values=list(GAME_SERVERS.keys()),
            state='readonly',
            width=37
        )
        game_combo.grid(row=2, column=1, sticky='ew', pady=5)
        
        # Account Count
        ttk.Label(left_panel, text="📊 Số lượng:").grid(row=3, column=0, sticky='w', pady=5)
        self.count_var = tk.StringVar(value='1')
        count_spin = ttk.Spinbox(left_panel, from_=1, to=1000, textvariable=self.count_var, width=40)
        count_spin.grid(row=3, column=1, sticky='ew', pady=5)
        
        # Data File Selection
        ttk.Label(left_panel, text="📁 File Data (TK REG.TXT):").grid(row=4, column=0, sticky='w', pady=5)
        self.data_file_var = tk.StringVar(value="TK REG.TXT")
        data_frame = ttk.Frame(left_panel)
        data_frame.grid(row=4, column=1, sticky='ew', pady=5)
        ttk.Entry(data_frame, textvariable=self.data_file_var, readonlybackground='lightgray').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(data_frame, text="Browse", command=self.browse_data_file, width=10).pack(side=tk.LEFT, padx=5)
        
        # SDT File Selection (No OTP)
        ttk.Label(left_panel, text="📱 SDT Không OTP (sdt.txt):").grid(row=5, column=0, sticky='w', pady=5)
        self.sdt_file_var = tk.StringVar(value="sdt.txt")
        sdt_frame = ttk.Frame(left_panel)
        sdt_frame.grid(row=5, column=1, sticky='ew', pady=5)
        ttk.Entry(sdt_frame, textvariable=self.sdt_file_var, readonlybackground='lightgray').pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(sdt_frame, text="Browse", command=self.browse_sdt_file, width=10).pack(side=tk.LEFT, padx=5)
        
        # OTP Settings
        ttk.Label(left_panel, text="🔐 SDT Có OTP:").grid(row=6, column=0, sticky='w', pady=5)
        self.use_otp_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_panel, text="Dùng SDT có OTP", variable=self.use_otp_var).grid(row=6, column=1, sticky='w', pady=5)
        
        # CodeSim API
        ttk.Label(left_panel, text="🔑 CodeSim API Key:").grid(row=7, column=0, sticky='w', pady=5)
        self.api_key_var = tk.StringVar()
        ttk.Entry(left_panel, textvariable=self.api_key_var, show='*', width=40).grid(row=7, column=1, sticky='ew', pady=5)
        
        # Headless Mode
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(left_panel, text="Chế độ Headless", variable=self.headless_var).grid(row=8, column=0, columnspan=2, sticky='w', pady=5)
        
        # Separator
        ttk.Separator(left_panel, orient=tk.HORIZONTAL).grid(row=9, column=0, columnspan=2, sticky='ew', pady=10)
        
        # Buttons 
        button_frame = ttk.Frame(left_panel)
        button_frame.grid(row=10, column=0, columnspan=2, sticky='ew', pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="▶ BẮT ĐẦU", command=self.start)
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ DỪNG", command=self.stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.clear_btn = ttk.Button(button_frame, text="🗑 XÓA LOG", command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # ========== RIGHT PANEL (STATUS) ==========
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Status Info
        info_frame = ttk.LabelFrame(right_panel, text="📊 THỐNG KÊ", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.success_label = ttk.Label(info_frame, text="✓ Thành công: 0", foreground="green")
        self.success_label.pack(anchor='w', pady=2)
        
        self.fail_label = ttk.Label(info_frame, text="✗ Thất bại: 0", foreground="red")
        self.fail_label.pack(anchor='w', pady=2)
        
        self.current_label = ttk.Label(info_frame, text="► Đang xử lý: --", foreground="blue")
        self.current_label.pack(anchor='w', pady=2)
        
        # Progress Bar
        self.progress = ttk.Progressbar(info_frame, mode='determinate')
        self.progress.pack(fill=tk.X, pady=10)
        
        # Log Area
        log_frame = ttk.LabelFrame(right_panel, text="📝 LOG", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=30, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
        
        # Status Bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
        
        # Make columns expandable
        for i in range(2):
            left_panel.grid_columnconfigure(i, weight=1)
    
    def browse_data_file(self):
        """Chọn file data"""
        file = filedialog.askopenfilename(
            title="Chọn file data (TK REG.TXT)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.data_file_var.set(file)
            self.load_data_file(file)
    
    def browse_sdt_file(self):
        """Chọn file SDT"""
        file = filedialog.askopenfilename(
            title="Chọn file SDT (sdt.txt)",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file:
            self.sdt_file_var.set(file)
            self.load_sdt_file(file)
    
    def load_data_file(self, filepath):
        """Tải dữ liệu từ file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.accounts_data = [line.strip() for line in f if line.strip()]
            self.log(f"✓ Tải {len(self.accounts_data)} tài khoản từ: {filepath}", "success")
        except Exception as e:
            self.log(f"✗ Lỗi tải file data: {str(e)}", "error")
    
    def load_sdt_file(self, filepath):
        """Tải danh sách SDT"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.sdt_data = [line.strip() for line in f if line.strip()]
            self.log(f"✓ Tải {len(self.sdt_data)} SDT từ: {filepath}", "success")
        except Exception as e:
            self.log(f"✗ Lỗi tải file SDT: {str(e)}", "error")
    
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
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL đăng ký")
            return
        
        if not self.accounts_data:
            messagebox.showerror("Lỗi", "Vui lòng chọn file data tài khoản")
            return
        
        if self.use_otp_var.get() and not self.sdt_data:
            messagebox.showerror("Lỗi", "Vui lòng chọn file SDT")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress['value'] = 0
        
        thread = threading.Thread(target=self.run_registration)
        thread.daemon = True
        thread.start()
    
    def run_registration(self):
        """Chạy quá trình đăng ký với Selenium"""
        driver = None
        try:
            url = self.url_var.get().strip()
            game = self.game_var.get()
            headless = self.headless_var.get()
            use_otp = self.use_otp_var.get()
            proxy = self.proxy_var.get() if self.proxy_var.get() != "(không dùng)" else None
            api_key = self.api_key_var.get().strip() if use_otp else None
            
            self.log(f"\n{'='*60}", "info")
            self.log("GAME ACCOUNT REGISTRAR - ADVANCED SELENIUM", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"📍 URL: {url}", "info")
            self.log(f"🎮 Game: {game}", "info")
            self.log(f"🔗 Proxy: {proxy or '(không dùng)'}", "info")
            self.log(f"📱 SDT OTP: {'Có' if use_otp else 'Không'}", "info")
            self.log(f"🔐 Headless: {headless}\n", "info")
            
            success_count = 0
            fail_count = 0
            total = len(self.accounts_data)
            
            for idx, line in enumerate(self.accounts_data):
                if not self.is_running:
                    self.log("\n⚠ Quá trình bị dừng bởi người dùng", "warning")
                    break
                
                self.progress['value'] = ((idx + 1) / total) * 100
                self.current_label.config(text=f"► Đang xử lý: {idx + 1}/{total}")
                self.status_var.set(f"Đăng ký {idx + 1}/{total}...")
                
                driver = None
                try:
                    # Parse account data
                    parts = line.split('|')
                    if len(parts) < 2:
                        self.log(f"[{idx + 1}] ✗ Format không hợp lệ: {line}", "error")
                        with open('FAIL.TXT', 'a', encoding='utf-8') as f:
                            f.write(f"{line}|ERROR: Format không hợp lệ\n")
                        fail_count += 1
                        continue
                    
                    username = parts[0].strip()
                    email = parts[1].strip() if len(parts) > 1 else ""
                    password = parts[2].strip() if len(parts) > 2 else ""
                    
                    self.log(f"\n[{idx + 1}/{total}] 🔄 Bắt đầu đăng ký: {username}", "info")
                    self.log(f"  📧 Email: {email}", "info")
                    self.log(f"  🔑 Password: ***{password[-3:] if len(password) > 3 else password}", "info")
                    
                    sdt = None
                    if use_otp and self.sdt_data:
                        sdt = self.sdt_data[idx % len(self.sdt_data)]
                        self.log(f"  📱 SDT OTP: {sdt}", "info")
                        if api_key:
                            self.log(f"  🔐 API Key: ***{api_key[-4:] if len(api_key) > 4 else api_key}", "info")
                    
                    # Setup Selenium WebDriver
                    self.log(f"  ▶ Khởi tạo Chrome WebDriver...", "info")
                    options = Options()
                    
                    if headless:
                        options.add_argument('--headless')
                        self.log(f"  ▶ Chế độ Headless: ON", "info")
                    
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--disable-blink-features=AutomationControlled')
                    options.add_experimental_option("excludeSwitches", ["enable-automation"])
                    options.add_experimental_option('useAutomationExtension', False)
                    
                    if proxy:
                        options.add_argument(f'--proxy-server={proxy}')
                        self.log(f"  ▶ Sử dụng Proxy: {proxy}", "info")
                    
                    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
                    
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=options)
                    self.log(f"  ✓ WebDriver khởi tạo thành công", "success")
                    
                    # Navigate to URL
                    self.log(f"  ▶ Truy cập: {url}", "info")
                    driver.get(url)
                    time.sleep(random.uniform(2, 4))
                    self.log(f"  ✓ Trang được tải", "success")
                    
                    # Try to fill form fields - Look for common selectors
                    wait = WebDriverWait(driver, 10)
                    
                    # Try to fill username field
                    try:
                        self.log(f"  ▶ Tìm trường Username...", "info")
                        username_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='username'], input[name*='user'], input[id*='username'], #username"))
                        )
                        username_field.clear()
                        username_field.send_keys(username)
                        time.sleep(random.uniform(0.5, 1))
                        self.log(f"  ✓ Điền Username: {username}", "success")
                    except TimeoutException:
                        self.log(f"  ⚠ Không tìm thấy trường Username", "warning")
                    
                    # Try to fill email field
                    try:
                        self.log(f"  ▶ Tìm trường Email...", "info")
                        email_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='email'], input[type='email'], #email"))
                        )
                        email_field.clear()
                        email_field.send_keys(email)
                        time.sleep(random.uniform(0.5, 1))
                        self.log(f"  ✓ Điền Email: {email}", "success")
                    except TimeoutException:
                        self.log(f"  ⚠ Không tìm thấy trường Email", "warning")
                    
                    # Try to fill password field
                    try:
                        self.log(f"  ▶ Tìm trường Password...", "info")
                        password_field = wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name*='password'], input[type='password'], #password"))
                        )
                        password_field.clear()
                        password_field.send_keys(password)
                        time.sleep(random.uniform(0.5, 1))
                        self.log(f"  ✓ Điền Password", "success")
                    except TimeoutException:
                        self.log(f"  ⚠ Không tìm thấy trường Password", "warning")
                    
                    # Try to accept terms
                    try:
                        self.log(f"  ▶ Tìm checkbox điều khoản...", "info")
                        terms_checkbox = driver.find_element(By.CSS_SELECTOR, "input[type='checkbox'], #terms, [name*='agree']")
                        if not terms_checkbox.is_selected():
                            terms_checkbox.click()
                            time.sleep(random.uniform(0.3, 0.7))
                            self.log(f"  ✓ Chấp nhận điều khoản", "success")
                    except NoSuchElementException:
                        self.log(f"  ⚠ Không tìm thấy checkbox điều khoản", "warning")
                    
                    # Try to submit form
                    try:
                        self.log(f"  ▶ Tìm nút Submit...", "info")
                        submit_btn = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button[name*='submit'], input[type='submit'], .btn-submit"))
                        )
                        self.log(f"  ▶ Gửi form...", "info")
                        submit_btn.click()
                        time.sleep(random.uniform(2, 4))
                        self.log(f"  ✓ Form đã được gửi", "success")
                    except TimeoutException:
                        self.log(f"  ⚠ Không tìm thấy nút Submit", "warning")
                    
                    # Check if registration was successful
                    self.log(f"  ▶ Kiểm tra kết quả...", "info")
                    time.sleep(2)
                    
                    page_source = driver.page_source.lower()
                    current_url = driver.current_url
                    
                    success = False
                    if 'success' in page_source or 'welcome' in page_source or 'registered' in page_source:
                        success = True
                        self.log(f"  ✓ Phát hiện từ khóa thành công trên trang", "success")
                    
                    if current_url != url:
                        success = True
                        self.log(f"  ✓ URL đã thay đổi - Có thể thành công", "success")
                    
                    if success:
                        # Save success
                        with open('ACC OK.TXT', 'a', encoding='utf-8') as f:
                            f.write(f"{username}|{password}|{email}\n")
                        
                        self.log(f"  ✓✓✓ ĐĂNG KÝ THÀNH CÔNG! ✓✓✓", "success")
                        success_count += 1
                    else:
                        # Save failed
                        with open('FAIL.TXT', 'a', encoding='utf-8') as f:
                            f.write(f"{line}|ERROR: Không xác nhận được thành công\n")
                        
                        self.log(f"  ✗ Không xác nhận được đăng ký thành công", "error")
                        fail_count += 1
                    
                except Exception as e:
                    self.log(f"  ✗ Lỗi: {str(e)}", "error")
                    
                    # Save failed
                    with open('FAIL.TXT', 'a', encoding='utf-8') as f:
                        f.write(f"{line}|ERROR: {str(e)}\n")
                    
                    fail_count += 1
                
                finally:
                    if driver:
                        try:
                            driver.quit()
                            self.log(f"  ▶ WebDriver đã đóng", "info")
                        except:
                            pass
                
                self.success_label.config(text=f"✓ Thành công: {success_count}")
                self.fail_label.config(text=f"✗ Thất bại: {fail_count}")
                
                # Random delay between accounts
                if idx < total - 1:
                    delay = random.uniform(3, 5)
                    self.log(f"  ⏳ Chờ {delay:.1f}s trước tài khoản tiếp theo...\n", "info")
                    time.sleep(delay)
            
            # Summary
            self.log(f"\n{'='*60}", "info")
            self.log("📊 TỔNG KẾT KẾT QUẢ", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"✓ Thành công: {success_count}/{total}", "success")
            self.log(f"✗ Thất bại: {fail_count}/{total}", "error")
            self.log(f"📁 Lưu vào: ACC OK.TXT & FAIL.TXT", "info")
            self.log(f"{'='*60}\n", "info")
            
            self.status_var.set("Hoàn thành")
            self.progress['value'] = 100
            messagebox.showinfo("Hoàn thành", f"✓ Thành công: {success_count}\n✗ Thất bại: {fail_count}\n\nKết quả lưu trong:\n- ACC OK.TXT\n- FAIL.TXT")
            
        except Exception as e:
            self.log(f"❌ Lỗi nghiêm trọng: {str(e)}", "error")
            messagebox.showerror("Lỗi", f"❌ Lỗi: {str(e)}")
        
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
        """Dừng quá trình"""
        self.is_running = False
        self.log("\n⏹ Đang dừng...", "warning")
        self.status_var.set("Đã dừng")

def main():
    root = tk.Tk()
    app = AdvancedGUILauncher(root)
    root.mainloop()

if __name__ == '__main__':
    main()
