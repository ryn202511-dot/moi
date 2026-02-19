"""
Advanced GUI Launcher cho Game Account Registrar Tool
Giao diện cấp cao với tính năng URL, Proxy, File Data, Phone Options
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import sys
from io import StringIO
from game_account_registrar import GameAccountRegistrar
from config import GAME_SERVERS, PHONE_CONFIG, PROXY_CONFIG, DATA_FILE_CONFIG
from utils import load_accounts_from_file
import logging


class AdvancedGUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar Tool - Advanced")
        self.root.geometry("1000x700")
        
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        self.is_running = False
        self.registrar = None
        
    def create_widgets(self):
        """Tạo các widget UI"""
        # Notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Settings
        self.settings_frame = ttk.Frame(notebook)
        notebook.add(self.settings_frame, text="⚙️ Cấu hình")
        self.create_settings_tab()
        
        # Tab 2: Phone Options
        self.phone_frame = ttk.Frame(notebook)
        notebook.add(self.phone_frame, text="📱 SĐT")
        self.create_phone_tab()
        
        # Tab 3: Proxy
        self.proxy_frame = ttk.Frame(notebook)
        notebook.add(self.proxy_frame, text="🔀 Proxy")
        self.create_proxy_tab()
        
        # Tab 4: Data File
        self.data_frame = ttk.Frame(notebook)
        notebook.add(self.data_frame, text="📄 File Data")
        self.create_data_tab()
        
        # Tab 5: Control & Log
        self.control_frame = ttk.Frame(notebook)
        notebook.add(self.control_frame, text="▶️ Chạy")
        self.create_control_tab()
        
        # Tab 6: View Accounts
        self.view_frame = ttk.Frame(notebook)
        notebook.add(self.view_frame, text="👥 Xem Tài Khoản")
        self.create_view_tab()
    
    def create_settings_tab(self):
        """Tab cài đặt chính"""
        frame = ttk.LabelFrame(self.settings_frame, text="Cài đặt Cơ bản", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game selection
        ttk.Label(frame, text="Chọn Game:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.game_var = tk.StringVar(value='default')
        game_combo = ttk.Combobox(frame, textvariable=self.game_var, 
                                  values=list(GAME_SERVERS.keys()), state='readonly', width=30)
        game_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # URL input
        ttk.Label(frame, text="URL Đăng ký:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.url_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.url_var, width=40).grid(row=1, column=1, sticky='w', padx=5, pady=5)
        ttk.Label(frame, text="(Để trống = dùng URL game)", font=('Arial', 8)).grid(row=1, column=2, sticky='w')
        
        # Account count
        ttk.Label(frame, text="Số lượng tài khoản:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.count_var = tk.StringVar(value='1')
        ttk.Spinbox(frame, from_=1, to=1000, textvariable=self.count_var, width=15).grid(row=2, column=1, sticky='w', padx=5, pady=5)
        
        # Headless mode
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Chế độ Headless (ẩn trình duyệt)", 
                       variable=self.headless_var).grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Load from file
        self.load_file_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Tải từ file data", 
                       variable=self.load_file_var).grid(row=4, column=0, columnspan=2, sticky='w', padx=5, pady=5)
    
    def create_phone_tab(self):
        """Tab tùy chọn SĐT"""
        frame = ttk.LabelFrame(self.phone_frame, text="Cấu hình Số Điện Thoại", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Use phone
        self.use_phone_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Sử dụng SĐT để đăng ký", 
                       variable=self.use_phone_var).pack(anchor='w', padx=5, pady=5)
        
        # Phone type
        ttk.Label(frame, text="Loại SĐT:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=10)
        
        self.phone_type_var = tk.StringVar(value='no_otp')
        ttk.Radiobutton(frame, text="SĐT không cần OTP (xác minh tự động)", 
                       variable=self.phone_type_var, value='no_otp').pack(anchor='w', padx=20, pady=5)
        ttk.Radiobutton(frame, text="SĐT có OTP (cần xác minh thủ công)", 
                       variable=self.phone_type_var, value='with_otp').pack(anchor='w', padx=20, pady=5)
        
        # Phone prefix
        ttk.Label(frame, text="Đầu số SĐT:").pack(anchor='w', padx=5, pady=10)
        self.phone_prefix_var = tk.StringVar(value='84')
        ttk.Combobox(frame, textvariable=self.phone_prefix_var, 
                    values=['84', '85', '86', '87', '88', '89'], width=10).pack(anchor='w', padx=20, pady=5)
    
    def create_proxy_tab(self):
        """Tab cấu hình Proxy"""
        frame = ttk.LabelFrame(self.proxy_frame, text="Cấu hình Proxy", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Enable proxy
        self.use_proxy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Sử dụng Proxy", 
                       variable=self.use_proxy_var).pack(anchor='w', padx=5, pady=5)
        
        # Proxy type
        ttk.Label(frame, text="Loại Proxy:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=10)
        
        self.proxy_type_var = tk.StringVar(value='http')
        ttk.Radiobutton(frame, text="HTTP Proxy", 
                       variable=self.proxy_type_var, value='http').pack(anchor='w', padx=20, pady=5)
        ttk.Radiobutton(frame, text="SOCKS5 Proxy", 
                       variable=self.proxy_type_var, value='socks5').pack(anchor='w', padx=20, pady=5)
        
        # Proxy input
        ttk.Label(frame, text="Danh sách Proxy (1 proxy/dòng):").pack(anchor='w', padx=5, pady=10)
        self.proxy_text = scrolledtext.ScrolledText(frame, height=8, wrap=tk.WORD)
        self.proxy_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Rotate proxy
        self.rotate_proxy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frame, text="Xoay Proxy (mỗi request)", 
                       variable=self.rotate_proxy_var).pack(anchor='w', padx=5, pady=5)
    
    def create_data_tab(self):
        """Tab cài đặt file data"""
        frame = ttk.LabelFrame(self.data_frame, text="File Dữ liệu Tài khoản", padding=15)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File path
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(file_frame, text="File Data:").pack(side=tk.LEFT, padx=5)
        self.data_file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.data_file_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Chọn File...", command=self.browse_data_file).pack(side=tk.LEFT, padx=5)
        
        # Format info
        ttk.Label(frame, text="Format file (mỗi dòng):", font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=10)
        ttk.Label(frame, text="username|password|email|phone", 
                 font=('Courier', 10), background='#f0f0f0').pack(anchor='w', padx=20, pady=5, fill=tk.X)
        
        # Preview
        ttk.Label(frame, text="Preview dữ liệu:", font=('Arial', 10, 'bold')).pack(anchor='w', padx=5, pady=10)
        self.data_preview = scrolledtext.ScrolledText(frame, height=6, wrap=tk.WORD)
        self.data_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Load button
        ttk.Button(frame, text="Tải preview", command=self.load_data_preview).pack(anchor='w', padx=5, pady=5)
    
    def create_control_tab(self):
        """Tab điều khiển chính"""
        # Buttons
        button_frame = ttk.Frame(self.control_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="▶ Bắt đầu", command=self.start_registration)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ Dừng", command=self.stop_registration, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🗑 Xóa log", command=self.clear_log).pack(side=tk.LEFT, padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self.control_frame, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
        
        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(self.control_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def create_view_tab(self):
        """Tab xem tài khoản đã lưu"""
        button_frame = ttk.Frame(self.view_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Tải Danh sách", command=self.load_accounts_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa Tất cả", command=self.clear_accounts).pack(side=tk.LEFT, padx=5)
        
        # Accounts display
        list_frame = ttk.LabelFrame(self.view_frame, text="Danh sách Tài khoản Thành công", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.accounts_text = scrolledtext.ScrolledText(list_frame, wrap=tk.WORD, font=('Courier', 9))
        self.accounts_text.pack(fill=tk.BOTH, expand=True)
    
    def browse_data_file(self):
        """Chọn file data"""
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.data_file_var.set(filename)
            self.load_data_preview()
    
    def load_data_preview(self):
        """Tải preview file data"""
        filepath = self.data_file_var.get()
        if not filepath:
            messagebox.showwarning("Cảnh báo", "Hãy chọn file data trước")
            return
        
        accounts = load_accounts_from_file(filepath)
        self.data_preview.delete('1.0', tk.END)
        
        for i, acc in enumerate(accounts[:5], 1):
            text = f"[{i}] {acc['username']} | {acc['email']} | {acc.get('phone', '')}\n"
            self.data_preview.insert(tk.END, text)
        
        if len(accounts) > 5:
            self.data_preview.insert(tk.END, f"\n... và {len(accounts)-5} tài khoản khác")
    
    def load_accounts_list(self):
        """Tải danh sách tài khoản thành công"""
        accounts = load_accounts_from_file('accounts_success.txt')
        self.accounts_text.delete('1.0', tk.END)
        
        if not accounts:
            self.accounts_text.insert(tk.END, "Chưa có tài khoản thành công nào")
            return
        
        for i, acc in enumerate(accounts, 1):
            text = f"{i}. {acc['username']} | {acc['email']} | {acc.get('phone', '')}\n"
            self.accounts_text.insert(tk.END, text)
        
        self.accounts_text.insert(tk.END, f"\n\nTổng: {len(accounts)} tài khoản")
    
    def clear_accounts(self):
        """Xóa file accounts"""
        if messagebox.askyesno("Xác nhận", "Bạn chắc chắn muốn xóa tất cả tài khoản?"):
            import os
            try:
                os.remove('accounts_success.txt')
                messagebox.showinfo("Thành công", "Đã xóa file accounts")
                self.load_accounts_list()
            except:
                messagebox.showerror("Lỗi", "Không thể xóa file")
    
    def log(self, message, level="info"):
        """Ghi log"""
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete('1.0', tk.END)
    
    def start_registration(self):
        """Bắt đầu đăng ký"""
        try:
            count = int(self.count_var.get())
            if count < 1:
                messagebox.showerror("Lỗi", "Số lượng phải >= 1")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng không hợp lệ")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run_registration)
        thread.daemon = True
        thread.start()
    
    def run_registration(self):
        """Chạy đăng ký"""
        try:
            game = self.game_var.get()
            count = int(self.count_var.get())
            headless = self.headless_var.get()
            use_phone = self.use_phone_var.get()
            use_proxy = self.use_proxy_var.get()
            
            self.status_var.set(f"Đang xử lý... {game}")
            self.log(f"{'='*60}", "info")
            self.log("GAME ACCOUNT REGISTRAR ADVANCED", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"Game: {game}", "info")
            self.log(f"Số lượng: {count}", "info")
            self.log(f"SĐT: {'✓' if use_phone else '✗'}", "info")
            self.log(f"Proxy: {'✓' if use_proxy else '✗'}", "info")
            
            success_count = 0
            error_count = 0
            
            for i in range(count):
                if not self.is_running:
                    self.log("\n⚠ Quá trình bị dừng", "warning")
                    break
                
                self.log(f"\n[{i+1}/{count}] Tạo tài khoản...", "info")
                self.status_var.set(f"Tạo tài khoản {i+1}/{count}")
                
                try:
                    registrar = GameAccountRegistrar(game, headless)
                    success = registrar.register()
                    
                    if success:
                        self.log(f"✓ Tài khoản #{i+1} thành công", "success")
                        success_count += 1
                    else:
                        self.log(f"✗ Lỗi tài khoản #{i+1}", "error")
                        error_count += 1
                
                except Exception as e:
                    self.log(f"✗ Exception: {str(e)}", "error")
                    error_count += 1
            
            # Summary
            self.log(f"\n{'='*60}", "info")
            self.log(f"Thành công: {success_count}", "success")
            self.log(f"Lỗi: {error_count}", "error")
            self.log(f"{'='*60}\n", "info")
            
            self.status_var.set("Hoàn thành")
            messagebox.showinfo("Hoàn thành", f"Thành công: {success_count}\nLỗi: {error_count}")
            
        except Exception as e:
            self.log(f"Lỗi nghiêm trọng: {str(e)}", "error")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
        
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_registration(self):
        """Dừng"""
        self.is_running = False
        self.log("\n⏹ Đang dừng...", "warning")
        self.status_var.set("Đang dừng...")


def main():
    root = tk.Tk()
    app = AdvancedGUILauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
