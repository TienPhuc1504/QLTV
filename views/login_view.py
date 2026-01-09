"""
Login View - Giao diện đăng nhập
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import authenticate_user, init_database, insert_sample_data


class LoginView(ctk.CTk):
    """Giao diện đăng nhập"""
    
    def __init__(self):
        super().__init__()
        
        # Khởi tạo database
        init_database()
        insert_sample_data()
        
        # Cấu hình cửa sổ
        self.title("Đăng nhập - Quản lý Thư viện")
        self.geometry("400x650")
        self.resizable(False, False)
        
        # Đặt theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Căn giữa cửa sổ
        self.center_window()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Bind Enter key
        self.bind('<Return>', lambda e: self.login())
        
    def center_window(self):
        """Căn giữa cửa sổ trên màn hình"""
        self.update_idletasks()
        width = 400
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Tạo các widget giao diện"""
        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=40, pady=30)
        
        # Logo/Title
        title_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, 30))
        
        # Icon thư viện
        icon_label = ctk.CTkLabel(
            title_frame,
            text="📚",
            font=ctk.CTkFont(size=60)
        )
        icon_label.pack()
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="THƯ VIỆN SỐ",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(10, 0))
        
        subtitle_label = ctk.CTkLabel(
            title_frame,
            text="Hệ thống Quản lý Thư viện",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack()
        
        # Login form frame
        form_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        form_frame.pack(fill="x", pady=20)
        
        # Username
        username_label = ctk.CTkLabel(
            form_frame,
            text="Tên đăng nhập",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 5))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Nhập tên đăng nhập",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.username_entry.pack(fill="x", pady=(0, 15))
        
        # Password
        password_label = ctk.CTkLabel(
            form_frame,
            text="Mật khẩu",
            font=ctk.CTkFont(size=14),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Nhập mật khẩu",
            show="•",
            height=45,
            font=ctk.CTkFont(size=14)
        )
        self.password_entry.pack(fill="x", pady=(0, 5))
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        show_password_cb = ctk.CTkCheckBox(
            form_frame,
            text="Hiện mật khẩu",
            variable=self.show_password_var,
            command=self.toggle_password,
            font=ctk.CTkFont(size=12)
        )
        show_password_cb.pack(anchor="w", pady=(0, 20))
        
        # Login button
        login_btn = ctk.CTkButton(
            form_frame,
            text="ĐĂNG NHẬP",
            command=self.login,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        login_btn.pack(fill="x", pady=(0, 10))
        
        # Exit button
        exit_btn = ctk.CTkButton(
            form_frame,
            text="Thoát",
            command=self.quit,
            height=40,
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            hover_color=("gray80", "gray30")
        )
        exit_btn.pack(fill="x")
        
        # Footer
        footer_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom")
        
        footer_label = ctk.CTkLabel(
            footer_frame,
            text="© 2026 Thư Viện Số - QLTV",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        footer_label.pack()
        
        # Demo accounts info
        demo_label = ctk.CTkLabel(
            footer_frame,
            text="Demo: admin/admin123, nhanvien/nv123, docgia/dg123",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        demo_label.pack(pady=(5, 0))
        
        # Focus vào username entry
        self.username_entry.focus()
        
    def toggle_password(self):
        """Hiện/ẩn mật khẩu"""
        if self.show_password_var.get():
            self.password_entry.configure(show="")
        else:
            self.password_entry.configure(show="•")
            
    def login(self):
        """Xử lý đăng nhập"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên đăng nhập!")
            self.username_entry.focus()
            return
            
        if not password:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập mật khẩu!")
            self.password_entry.focus()
            return
        
        # Xác thực
        user = authenticate_user(username, password)
        
        if user:
            messagebox.showinfo("Thành công", f"Đăng nhập thành công!\nXin chào {user['ho_ten']}")
            self.open_main_view(user)
        else:
            messagebox.showerror("Lỗi", "Tên đăng nhập hoặc mật khẩu không đúng!")
            self.password_entry.delete(0, 'end')
            self.password_entry.focus()
            
    def open_main_view(self, user: dict):
        """Mở giao diện chính"""
        self.withdraw()  # Ẩn cửa sổ đăng nhập
        
        from views.main_view import MainView
        main_view = MainView(self, user)
        main_view.mainloop()


if __name__ == "__main__":
    app = LoginView()
    app.mainloop()
