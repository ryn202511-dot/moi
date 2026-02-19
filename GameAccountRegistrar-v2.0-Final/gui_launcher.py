"""
GUI Launcher cho Game Account Registrar Tool
Giao diện để dễ dàng sử dụng tool đăng ký tài khoản game
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import sys
from io import StringIO
from game_account_registrar import GameAccountRegistrar
from config import GAME_SERVERS
import logging


class GUILauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Account Registrar Tool")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Favicon/Icon
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
        
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
            text="Game Account Registrar Tool", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            header_frame, 
            text="Công cụ tự động đăng ký tài khoản game", 
            font=('Arial', 10)
        )
        subtitle_label.pack()
        
        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Control Frame
        control_frame = ttk.LabelFrame(self.root, text="Cấu hình", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Game selection
        game_label = ttk.Label(control_frame, text="Chọn Game:")
        game_label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        self.game_var = tk.StringVar(value='default')
        game_combo = ttk.Combobox(
            control_frame,
            textvariable=self.game_var,
            values=list(GAME_SERVERS.keys()),
            state='readonly',
            width=30
        )
        game_combo.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        # Account count
        count_label = ttk.Label(control_frame, text="Số lượng tài khoản:")
        count_label.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        
        self.count_var = tk.StringVar(value='1')
        count_spin = ttk.Spinbox(
            control_frame,
            from_=1,
            to=100,
            textvariable=self.count_var,
            width=30
        )
        count_spin.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        
        # Headless mode
        self.headless_var = tk.BooleanVar(value=False)
        headless_check = ttk.Checkbutton(
            control_frame,
            text="Chế độ Headless (ẩn trình duyệt)",
            variable=self.headless_var
        )
        headless_check.grid(row=2, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Buttons Frame
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
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
        
        # Log Frame
        log_frame = ttk.LabelFrame(self.root, text="Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log text widget
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=('Courier', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags untuk colors
        self.log_text.tag_config("error", foreground="red")
        self.log_text.tag_config("success", foreground="green")
        self.log_text.tag_config("warning", foreground="orange")
        self.log_text.tag_config("info", foreground="blue")
        
        # Status bar
        self.status_var = tk.StringVar(value="Sẵn sàng")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(fill=tk.X, padx=5, pady=5)
    
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
            if count < 1 or count > 100:
                messagebox.showerror("Lỗi", "Số lượng tài khoản phải từ 1 đến 100")
                return
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng tài khoản phải là số nguyên")
            return
        
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        
        # Chạy trong thread riêng để không block UI
        thread = threading.Thread(target=self.run_registration)
        thread.daemon = True
        thread.start()
    
    def run_registration(self):
        """Chạy quá trình đăng ký"""
        try:
            game = self.game_var.get()
            count = int(self.count_var.get())
            headless = self.headless_var.get()
            
            self.status_var.set(f"Đang xử lý... {game}")
            self.log(f"\n{'='*60}")
            self.log("GAME ACCOUNT REGISTRAR TOOL", "info")
            self.log(f"{'='*60}", "info")
            self.log(f"Game: {game}", "info")
            self.log(f"Số lượng: {count}", "info")
            self.log(f"Headless: {headless}\n", "info")
            
            success_count = 0
            error_count = 0
            
            for i in range(count):
                if not self.is_running:
                    self.log("\n⚠ Quá trình bị dừng bởi người dùng", "warning")
                    break
                
                self.log(f"\n[{i+1}/{count}] Tạo tài khoản...", "info")
                self.status_var.set(f"Tạo tài khoản {i+1}/{count}")
                
                try:
                    registrar = GameAccountRegistrar(game, headless)
                    
                    # Redirect stdout để capture log từ registrar
                    old_stdout = sys.stdout
                    sys.stdout = StringIO()
                    
                    success = registrar.register()
                    
                    # Restore stdout
                    output = sys.stdout.getvalue()
                    sys.stdout = old_stdout
                    
                    if success:
                        self.log(f"✓ Tài khoản #{i+1} đã được tạo thành công", "success")
                        success_count += 1
                    else:
                        self.log(f"✗ Lỗi tạo tài khoản #{i+1}", "error")
                        error_count += 1
                    
                    # Log từ registrar
                    for line in output.split('\n'):
                        if line.strip():
                            self.log(f"  {line}", "info")
                    
                except Exception as e:
                    self.log(f"✗ Exception tài khoản #{i+1}: {str(e)}", "error")
                    error_count += 1
                
                if i < count - 1 and self.is_running:
                    self.log("Chờ 3-5 giây...", "info")
                    for j in range(4):
                        if not self.is_running:
                            break
                        self.root.after(500)
            
            # Summary
            self.log(f"\n{'='*60}")
            self.log("TỔNG KẾT", "info")
            self.log(f"Thành công: {success_count}", "success")
            self.log(f"Lỗi: {error_count}", "error")
            self.log(f"{'='*60}\n", "info")
            
            self.status_var.set("Hoàn thành")
            messagebox.showinfo(
                "Hoàn thành",
                f"Thành công: {success_count}\nLỗi: {error_count}"
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
