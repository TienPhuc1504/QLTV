"""
Account View - Thông tin tài khoản
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_reader_by_id, get_staff_by_id, change_password, create_card_request


class AccountView(ctk.CTkFrame):
    """Giao diện thông tin tài khoản"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="👤 Thông tin tài khoản",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tab 1: Thông tin cá nhân
        tab1 = self.tabview.add("📋 Thông tin cá nhân")
        self.create_info_tab(tab1)
        
        # Tab 2: Đổi mật khẩu
        tab2 = self.tabview.add("🔐 Đổi mật khẩu")
        self.create_password_tab(tab2)
        
    def create_info_tab(self, parent):
        """Tạo tab thông tin cá nhân"""
        self.info_frame = ctk.CTkScrollableFrame(parent)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_password_tab(self, parent):
        """Tạo tab đổi mật khẩu"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(
            frame,
            text="ĐỔI MẬT KHẨU",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(30, 20))
        
        # Form frame
        form_frame = ctk.CTkFrame(frame, width=400, fg_color="transparent")
        form_frame.pack()
        
        # Current password
        ctk.CTkLabel(form_frame, text="Mật khẩu hiện tại:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(20, 5))
        self.current_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        self.current_pw.pack()
        
        # New password
        ctk.CTkLabel(form_frame, text="Mật khẩu mới:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(15, 5))
        self.new_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        self.new_pw.pack()
        
        # Confirm password
        ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(15, 5))
        self.confirm_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        self.confirm_pw.pack()
        
        # Button
        ctk.CTkButton(
            form_frame,
            text="Đổi mật khẩu",
            command=self.do_change_password,
            width=300
        ).pack(pady=25)
        
        # Note
        ctk.CTkLabel(
            frame,
            text="⚠️ Mật khẩu phải có ít nhất 4 ký tự",
            text_color="gray"
        ).pack(pady=10)
        
    def load_data(self):
        """Tải dữ liệu người dùng"""
        self.load_info()
        
    def load_info(self):
        """Hiển thị thông tin cá nhân"""
        # Clear
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        # Title
        ctk.CTkLabel(
            self.info_frame,
            text="THÔNG TIN CÁ NHÂN",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 30))
        
        user_type = self.user.get('loai_nguoi_dung', '')
        
        if user_type == 'DOC_GIA':
            # Lấy thông tin đọc giả đầy đủ
            reader = get_reader_by_id(self.user['ma_nd'])
            if reader:
                self.show_reader_info(reader)
            else:
                self.show_basic_info()
        elif user_type == 'NHAN_VIEN':
            # Lấy thông tin nhân viên đầy đủ
            staff = get_staff_by_id(self.user['ma_nd'])
            if staff:
                self.show_staff_info(staff)
            else:
                self.show_basic_info()
        else:
            # Admin
            self.show_admin_info()
            
    def show_reader_info(self, reader: dict):
        """Hiển thị thông tin đọc giả"""
        info_data = [
            ("Mã đọc giả:", reader.get('ma_doc_gia', 'N/A')),
            ("Họ và tên:", reader.get('ho_ten', 'N/A')),
            ("Địa chỉ:", reader.get('dia_chi', 'N/A')),
            ("Số điện thoại:", reader.get('so_dt', 'N/A')),
            ("Email:", reader.get('email', 'N/A')),
            ("Ngày đăng ký:", reader.get('ngay_dk', 'N/A')),
            ("", ""),
            ("Mã thẻ:", str(reader.get('ma_the', 'N/A'))),
            ("Ngày cấp thẻ:", reader.get('ngay_cap', 'N/A')),
            ("Ngày hết hạn:", reader.get('ngay_het_han', 'N/A')),
            ("Trạng thái thẻ:", reader.get('trang_thai_the', 'N/A')),
        ]
        
        self.display_info_rows(info_data)
        # Button: Yêu cầu in thẻ / Yêu cầu cấp lại thẻ
        btn_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        btn_frame.pack(pady=(15, 20))

        has_card = bool(reader.get('ma_the'))
        btn_text = "Yêu cầu cấp lại thẻ" if has_card else "Yêu cầu in thẻ"

        def on_request_card():
            try:
                create_card_request(reader['ma_nd'])
                messagebox.showinfo("Thành công", "Đã gửi yêu cầu in thẻ! Nhân viên sẽ xử lý sớm.")
                self.load_info()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))

        ctk.CTkButton(
            btn_frame,
            text=btn_text,
            command=on_request_card,
            width=220
        ).pack()
        
    def show_staff_info(self, staff: dict):
        """Hiển thị thông tin nhân viên"""
        info_data = [
            ("Mã nhân viên:", staff.get('ma_nhan_vien', 'N/A')),
            ("Họ và tên:", staff.get('ho_ten', 'N/A')),
            ("Địa chỉ:", staff.get('dia_chi') or 'N/A'),
            ("Số điện thoại:", staff.get('so_dt') or 'N/A'),
            ("Email:", staff.get('email') or 'N/A'),
            ("", ""),
            ("Tên tài khoản:", self.user.get('ten_tk', 'N/A')),
            ("Loại tài khoản:", "Nhân viên"),
        ]
        
        self.display_info_rows(info_data)
    
    def show_admin_info(self):
        """Hiển thị thông tin admin"""
        info_data = [
            ("Họ và tên:", self.user.get('ho_ten', 'N/A')),
            ("Địa chỉ:", self.user.get('dia_chi') or 'N/A'),
            ("Số điện thoại:", self.user.get('so_dt') or 'N/A'),
            ("Email:", self.user.get('email') or 'N/A'),
            ("", ""),
            ("Tên tài khoản:", self.user.get('ten_tk', 'N/A')),
            ("Loại tài khoản:", "Quản trị viên"),
        ]
        
        self.display_info_rows(info_data)
        
    def show_basic_info(self):
        """Hiển thị thông tin cơ bản khi không tìm được chi tiết"""
        info_data = [
            ("Họ và tên:", self.user.get('ho_ten', 'N/A')),
            ("Địa chỉ:", self.user.get('dia_chi', 'N/A')),
            ("Số điện thoại:", self.user.get('so_dt', 'N/A')),
            ("Email:", self.user.get('email', 'N/A')),
            ("", ""),
            ("Tên tài khoản:", self.user.get('ten_tk', 'N/A')),
        ]
        
        self.display_info_rows(info_data)
        
    def display_info_rows(self, info_data: list):
        """Hiển thị các dòng thông tin"""
        for label, value in info_data:
            if label == "":
                # Separator
                ctk.CTkLabel(self.info_frame, text="").pack(pady=5)
                continue
                
            row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=50)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(weight="bold"),
                width=160,
                anchor="e"
            ).pack(side="left")
            
            # Hiển thị trạng thái thẻ với màu
            if "Trạng thái" in label and value:
                if value == "CON_HAN":
                    display_value = "✅ Còn hạn"
                elif value == "HET_HAN":
                    display_value = "❌ Hết hạn"
                else:
                    display_value = value
            else:
                display_value = str(value) if value else "N/A"
            
            ctk.CTkLabel(
                row,
                text=display_value,
                anchor="w"
            ).pack(side="left", padx=15)
            
    def do_change_password(self):
        """Thực hiện đổi mật khẩu"""
        old = self.current_pw.get()
        new = self.new_pw.get()
        confirm = self.confirm_pw.get()
        
        if not all([old, new, confirm]):
            messagebox.showwarning("Cảnh báo", "Vui lòng điền đầy đủ thông tin!")
            return
            
        if new != confirm:
            messagebox.showwarning("Cảnh báo", "Mật khẩu xác nhận không khớp!")
            return
            
        if len(new) < 4:
            messagebox.showwarning("Cảnh báo", "Mật khẩu mới phải có ít nhất 4 ký tự!")
            return
            
        if change_password(self.user['ma_nd'], old, new):
            messagebox.showinfo("Thành công", "Đổi mật khẩu thành công!")
            self.current_pw.delete(0, 'end')
            self.new_pw.delete(0, 'end')
            self.confirm_pw.delete(0, 'end')
        else:
            messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!")
