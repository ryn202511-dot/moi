"""
GUI Launcher cho Game Account Registrar Tool v2.0
Giao diện nâng cao với hỗ trợ URL, Proxy, Bank, Phone
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import sys
from io import StringIO
from game_account_registrar import GameAccountRegistrar
from config import GAME_SERVERS, BANK_OPTIONS, DATA_FILE_CONFIG
from utils import load_accounts_from_file, load_phone_numbers
import logging


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")


class GUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar Tool v2.0")
        self.root.geometry("900x700")
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.create_widgets()
        self.is_running = False
        self.registrar = None
        
    def create_widgets(self):
        """Tạo các widget UI"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            header_frame, 
            text="Game Account Registrar Tool v2.0", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame, 
            text="Công cụ đăng ký tài khoản với hỗ trợ URL, Proxy, Bank, Phone", 
            font=('Arial', 9)
        )
        subtitle_label.pack()
        
        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Main Frame with Scrollbar
        main_frame = ScrollableFrame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        cf = main_frame.scrollable_frame
        
        # ===== URL CONFIG =====
        url_frame = ttk.LabelFrame(cf, text="🌐 URL Đăng ký", padding=8)
        url_frame.pack(fill=tk.X, pady=5)
        
        url_label = ttk.Label(url_frame, text="URL:")
        url_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.url_var = tk.StringVar(value='https://example.com/register')
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        url_entry.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # ===== PROXY CONFIG =====
        proxy_frame = ttk.LabelFrame(cf, text="🔗 Proxy (tuỳ chọn)", padding=8)
        proxy_frame.pack(fill=tk.X, pady=5)
        
        self.proxy_enabled_var = tk.BooleanVar(value=False)
        proxy_check = ttk.Checkbutton(
            proxy_frame,
            text="Sử dụng Proxy",
            variable=self.proxy_enabled_var,
            command=self.toggle_proxy
        )
        proxy_check.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        proxy_label = ttk.Label(proxy_frame, text="Proxy URL:")
        proxy_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.proxy_var = tk.StringVar(value='http://proxy.example.com:8080')
        proxy_entry = ttk.Entry(proxy_frame, textvariable=self.proxy_var, width=60, 
                               state=tk.DISABLED)
        proxy_entry.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        self.proxy_entry = proxy_entry
        
        # ===== DATA FILES =====
        data_frame = ttk.LabelFrame(cf, text="📄 Tệp dữ liệu", padding=8)
        data_frame.pack(fill=tk.X, pady=5)
        
        # Account file
        acc_label = ttk.Label(data_frame, text="File Account\n(username|password|email):")
        acc_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        acc_file_frame = ttk.Frame(data_frame)
        acc_file_frame.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        self.acc_file_var = tk.StringVar(value='TK_REG.txt')
        acc_entry = ttk.Entry(acc_file_frame, textvariable=self.acc_file_var, width=40)
        acc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        acc_btn = ttk.Button(acc_file_frame, text="Browse", 
                            command=lambda: self.browse_file(self.acc_file_var))
        acc_btn.pack(side=tk.LEFT, padx=5)
        
        # Phone file
        phone_label = ttk.Label(data_frame, text="File SĐT\n(một số mỗi dòng):")
        phone_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        phone_file_frame = ttk.Frame(data_frame)
        phone_file_frame.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        self.phone_file_var = tk.StringVar(value='sdt.txt')
        phone_entry = ttk.Entry(phone_file_frame, textvariable=self.phone_file_var, 
                               width=40)
        phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        phone_btn = ttk.Button(phone_file_frame, text="Browse", 
                              command=lambda: self.browse_file(self.phone_file_var))
        phone_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== BANK & PHONE CONFIG =====
        bank_frame = ttk.LabelFrame(cf, text="🏦 Ngân hàng & SĐT", padding=8)
        bank_frame.pack(fill=tk.X, pady=5)
        
        bank_label = ttk.Label(bank_frame, text="Chọn Ngân hàng:")
        bank_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.bank_var = tk.StringVar(value='vietcombank')
        bank_combo = ttk.Combobox(
            bank_frame,
            textvariable=self.bank_var,
            values=list(BANK_OPTIONS.values()),
            state='readonly',
            width=30
        )
        bank_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Phone options
        self.phone_mode_var = tk.StringVar(value='no_otp')
        phone_mode_frame = ttk.Frame(bank_frame)
        phone_mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        radio1 = ttk.Radiobutton(phone_mode_frame, text="Không dùng SĐT", 
                                variable=self.phone_mode_var, value='none')
        radio1.pack(side=tk.LEFT, padx=5)
        
        radio2 = ttk.Radiobutton(phone_mode_frame, text="SĐT không OTP (từ file)", 
                                variable=self.phone_mode_var, value='no_otp')
        radio2.pack(side=tk.LEFT, padx=5)
        
        radio3 = ttk.Radiobutton(phone_mode_frame, text="SĐT có OTP", 
                                variable=self.phone_mode_var, value='with_otp')
        radio3.pack(side=tk.LEFT, padx=5)
        
        # ===== GENERAL CONFIG =====
        config_frame = ttk.LabelFrame(cf, text="⚙️ Cấu hình chung", padding=8)
        config_frame.pack(fill=tk.X, pady=5)
        
        count_label = ttk.Label(config_frame, text="Số lượng tài khoản:")
        count_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.count_var = tk.StringVar(value='1')
        count_spin = ttk.Spinbox(
            config_frame,
            from_=1,
            to=1000,
            textvariable=self.count_var,
            width=30
        )
        count_spin.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(
            config_frame,
            text="Chế độ Headless (ẩn trình duyệt)",
            variable=self.headless_var
        )
        headless_check.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # ===== BUTTONS =====
        button_frame = ttk.Frame(cf)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(
            button_frame,
            text="▶ Bắt đầu đăng ký",
            command=self.start_registration
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            button_frame,
            text="⏹ Dừng",
            command=self.stop_registration,
            state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame,
            text="🗑 Xóa log",
            command=self.clear_log
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # ===== LOG AREA =====
        log_label = ttk.Label(self.root, text="📋 LOG", font=('Arial', 10, 'bold'))
        log_label.pack(anchor=tk.W, padx=10, pady=(10, 0))
        
        log_frame = ttk.Frame(self.root)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
        
        # ===== STATUS BAR =====
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
    def toggle_proxy(self):
        """Bật/tắt proxy input"""
        if self.proxy_enabled_var.get():
            self.proxy_entry.config(state=tk.NORMAL)
        else:
            self.proxy_entry.config(state=tk.DISABLED)
    
    def browse_file(self, var):
        """Chọn file"""
        filename = filedialog.askopenfilename(
            title="Chọn file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            var.set(filename)
    
    def log(self, message, level="info"):
        """Ghi log vào text widget"""
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete('1.0', tk.END)
    
    def start_registration(self):
        """Bắt đầu quá trình đăng ký"""
        try:
            count = int(self.count_var.get())
            if count < 1:
                messagebox.showerror("Lỗi", "Số lượng tài khoản phải >= 1")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng tài khoản phải là số nguyên")
            return
        
        # Validate URL
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        thread = threading.Thread(target=self.run_registration)
        thread.daemon = True
        thread.start()
    
    def run_registration(self):
        """Chạy quá trình đăng ký"""
        try:
            url = self.url_var.get().strip()
            count = int(self.count_var.get())
            headless = self.headless_var.get()
            proxy = self.proxy_var.get() if self.proxy_enabled_var.get() else None
            bank = self.bank_var.get()
            phone_mode = self.phone_mode_var.get()
            acc_file = self.acc_file_var.get()
            phone_file = self.phone_file_var.get()
            
            self.status_var.set(f"Đang xử lý...")
            self.log(f"\n{'='*60}")
            self.log("GAME ACCOUNT REGISTRAR TOOL v2.0", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"URL: {url}", "info")
            self.log(f"Proxy: {proxy if proxy else 'Không'}", "info")
            self.log(f"Ngân hàng: {bank}", "info")
            self.log(f"SĐT Mode: {phone_mode}", "info")
            self.log(f"Account File: {acc_file}", "info")
            self.log(f"Phone File: {phone_file}", "info")
            self.log(f"Số lượng: {count}", "info")
            self.log(f"Headless: {headless}\n", "info")
            
            success_count = 0
            fail_count = 0
            
            for i in range(count):
                if not self.is_running:
                    self.log("\n⚠ Quá trình bị dừng bởi người dùng", "warning")
                    break
                
                self.log(f"\n[{i+1}/{count}] Tạo tài khoản...", "info")
                self.status_var.set(f"Tạo tài khoản {i+1}/{count}")
                
                try:
                    registrar = GameAccountRegistrar(
                        url=url,
                        proxy=proxy,
                        bank=bank,
                        phone_mode=phone_mode,
                        headless=headless
                    )
                    
                    if registrar.register():
                        self.log(f"✓ Tài khoản #{i+1} đã được tạo thành công", "success")
                        success_count += 1
                    else:
                        self.log(f"✗ Lỗi tạo tài khoản #{i+1}", "error")
                        fail_count += 1
                    
                except Exception as e:
                    self.log(f"✗ Exception tài khoản #{i+1}: {str(e)}", "error")
                    fail_count += 1
                
                if i < count - 1 and self.is_running:
                    import time
                    for j in range(4):
                        if not self.is_running:
                            break
                        time.sleep(0.5)
            
            # Summary
            self.log(f"\n{'='*60}")
            self.log("TỔNG KẾT", "info")
            self.log(f"Thành công: {success_count}", "success")
            self.log(f"Lỗi: {fail_count}", "error")
            self.log(f"{'='*60}\n", "info")
            
            self.status_var.set("Hoàn thành")
            messagebox.showinfo(
                "Hoàn thành",
                f"Thành công: {success_count}\nLỗi: {fail_count}"
            )
            
        except Exception as e:
            self.log(f"Lỗi nghiêm trọng: {str(e)}", "error")
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")
            self.status_var.set("Lỗi")
        
        finally:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
    
    def stop_registration(self):
        """Dừng quá trình đăng ký"""
        self.is_running = False
        self.log("\n⏹ Đang dừng...", "warning")
        self.status_var.set("Đang dừng...")


def main():
    root = tk.Tk()
    app = GUILauncher(root)
    root.mainloop()


if __name__ == '__main__':
    main()
