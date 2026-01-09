"""
Main View - Giao diện chính của ứng dụng
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import change_password, get_book_statistics, get_borrow_statistics


class MainView(ctk.CTkToplevel):
    """Giao diện chính sau khi đăng nhập"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        
        self.parent = parent
        self.user = user
        self.current_frame = None
        
        # Cấu hình cửa sổ
        self.title(f"Quản lý Thư viện - {user['ho_ten']} ({user['loai_nguoi_dung']})")
        self.geometry("1200x700")
        self.minsize(1000, 600)
        
        # Xử lý đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Căn giữa
        self.center_window()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Hiển thị dashboard mặc định
        self.show_dashboard()
        
    def center_window(self):
        """Căn giữa cửa sổ"""
        self.update_idletasks()
        width = 1200
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
        
    def create_widgets(self):
        """Tạo giao diện chính"""
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=20, pady=20)
        
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="📚 THƯ VIỆN SỐ",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_label.pack()
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar, fg_color=("gray85", "gray25"))
        user_frame.pack(fill="x", padx=10, pady=10)
        
        user_icon = ctk.CTkLabel(user_frame, text="👤", font=ctk.CTkFont(size=30))
        user_icon.pack(pady=(10, 5))
        
        user_name = ctk.CTkLabel(
            user_frame,
            text=self.user['ho_ten'],
            font=ctk.CTkFont(size=14, weight="bold")
        )
        user_name.pack()
        
        user_role = ctk.CTkLabel(
            user_frame,
            text=self.get_role_display(self.user['loai_nguoi_dung']),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        user_role.pack(pady=(0, 10))
        
        # Menu buttons
        menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dashboard button
        self.dashboard_btn = ctk.CTkButton(
            menu_frame,
            text="📊  Tổng quan",
            command=self.show_dashboard,
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14)
        )
        self.dashboard_btn.pack(fill="x", pady=2)
        
        # Quản lý sách (Nhân viên & Admin)
        if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
            self.book_btn = ctk.CTkButton(
                menu_frame,
                text="📖  Quản lý Sách",
                command=self.show_book_management,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.book_btn.pack(fill="x", pady=2)
            
            # Quản lý đọc giả
            self.reader_btn = ctk.CTkButton(
                menu_frame,
                text="👥  Quản lý Đọc giả",
                command=self.show_reader_management,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.reader_btn.pack(fill="x", pady=2)
            
            # Quản lý mượn/trả
            self.borrow_btn = ctk.CTkButton(
                menu_frame,
                text="📋  Mượn/Trả Sách",
                command=self.show_borrow_management,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.borrow_btn.pack(fill="x", pady=2)
        
        # Quản lý nhân viên (chỉ Admin)
        if self.user['loai_nguoi_dung'] == 'ADMIN':
            self.staff_btn = ctk.CTkButton(
                menu_frame,
                text="👔  Quản lý Nhân viên",
                command=self.show_staff_management,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.staff_btn.pack(fill="x", pady=2)
        
        # Đọc giả - Xem thông tin cá nhân và lịch sử mượn
        if self.user['loai_nguoi_dung'] == 'DOC_GIA':
            self.my_books_btn = ctk.CTkButton(
                menu_frame,
                text="📚  Sách của tôi",
                command=self.show_my_books,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.my_books_btn.pack(fill="x", pady=2)
        
        # Thống kê
        if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
            self.stats_btn = ctk.CTkButton(
                menu_frame,
                text="📈  Thống kê",
                command=self.show_statistics,
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.stats_btn.pack(fill="x", pady=2)
        
        # Đổi mật khẩu
        self.password_btn = ctk.CTkButton(
            menu_frame,
            text="🔐  Đổi mật khẩu",
            command=self.show_change_password,
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray75", "gray35")
        )
        self.password_btn.pack(fill="x", pady=2)
        
        # Logout button
        logout_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logout_frame.pack(fill="x", side="bottom", padx=10, pady=20)
        
        logout_btn = ctk.CTkButton(
            logout_frame,
            text="🚪  Đăng xuất",
            command=self.logout,
            height=40,
            fg_color="#dc3545",
            hover_color="#c82333",
            font=ctk.CTkFont(size=14)
        )
        logout_btn.pack(fill="x")
        
        # Main content area
        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
    def get_role_display(self, role: str) -> str:
        """Chuyển mã role thành tên hiển thị"""
        roles = {
            'ADMIN': 'Quản trị viên',
            'NHAN_VIEN': 'Nhân viên',
            'DOC_GIA': 'Độc giả'
        }
        return roles.get(role, role)
        
    def clear_content(self):
        """Xóa nội dung hiện tại"""
        if self.current_frame:
            self.current_frame.destroy()
            
    def show_dashboard(self):
        """Hiển thị tổng quan"""
        self.clear_content()
        
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            self.current_frame,
            text="📊 Tổng quan Thư viện",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Stats cards
        cards_frame = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        
        # Lấy thống kê
        book_stats = get_book_statistics()
        borrow_stats = get_borrow_statistics()
        
        # Card 1: Tổng số sách
        self.create_stat_card(cards_frame, "📚", "Tổng số sách", 
                             str(book_stats.get('total_books', 0)), "#3498db")
        
        # Card 2: Đang mượn
        borrowing = borrow_stats.get('by_status', {}).get('DANG_MUON', 0)
        self.create_stat_card(cards_frame, "📖", "Đang mượn", 
                             str(borrowing), "#2ecc71")
        
        # Card 3: Quá hạn
        self.create_stat_card(cards_frame, "⚠️", "Quá hạn", 
                             str(borrow_stats.get('overdue', 0)), "#e74c3c")
        
        # Card 4: Tổng tiền phạt
        self.create_stat_card(cards_frame, "💰", "Tiền phạt", 
                             f"{borrow_stats.get('total_fines', 0):,.0f}đ", "#f39c12")
        
        # Welcome message
        welcome_frame = ctk.CTkFrame(self.current_frame)
        welcome_frame.pack(fill="x", pady=20)
        
        welcome_text = ctk.CTkLabel(
            welcome_frame,
            text=f"Xin chào, {self.user['ho_ten']}! 👋",
            font=ctk.CTkFont(size=18)
        )
        welcome_text.pack(pady=20)
        
        guide_text = ctk.CTkLabel(
            welcome_frame,
            text="Sử dụng menu bên trái để điều hướng đến các chức năng của hệ thống.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        guide_text.pack(pady=(0, 20))
        
    def create_stat_card(self, parent, icon: str, title: str, value: str, color: str):
        """Tạo thẻ thống kê"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=10)
        card.pack(side="left", fill="both", expand=True, padx=5)
        
        icon_label = ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=30), text_color="white")
        icon_label.pack(pady=(15, 5))
        
        value_label = ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=24, weight="bold"), text_color="white")
        value_label.pack()
        
        title_label = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12), text_color="white")
        title_label.pack(pady=(0, 15))
        
    def show_book_management(self):
        """Hiển thị quản lý sách"""
        self.clear_content()
        from views.book_management import BookManagement
        self.current_frame = BookManagement(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_reader_management(self):
        """Hiển thị quản lý đọc giả"""
        self.clear_content()
        from views.reader_management import ReaderManagement
        self.current_frame = ReaderManagement(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_borrow_management(self):
        """Hiển thị quản lý mượn/trả"""
        self.clear_content()
        from views.borrow_management import BorrowManagement
        self.current_frame = BorrowManagement(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_staff_management(self):
        """Hiển thị quản lý nhân viên"""
        self.clear_content()
        from views.staff_management import StaffManagement
        self.current_frame = StaffManagement(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_my_books(self):
        """Hiển thị sách của đọc giả"""
        self.clear_content()
        try:
            from views.my_books import MyBooks
            self.current_frame = MyBooks(self.content_frame, self.user)
            self.current_frame.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể tải trang: {str(e)}")
        
    def show_statistics(self):
        """Hiển thị thống kê"""
        self.clear_content()
        from views.statistics_view import StatisticsView
        self.current_frame = StatisticsView(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
    def show_change_password(self):
        """Hiển thị đổi mật khẩu"""
        self.clear_content()
        
        self.current_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.current_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(
            self.current_frame,
            text="🔐 Đổi mật khẩu",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(anchor="w", pady=(0, 30))
        
        # Form frame
        form_frame = ctk.CTkFrame(self.current_frame, width=400)
        form_frame.pack(anchor="w")
        
        # Current password
        ctk.CTkLabel(form_frame, text="Mật khẩu hiện tại:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(20, 5))
        current_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        current_pw.pack(padx=20)
        
        # New password
        ctk.CTkLabel(form_frame, text="Mật khẩu mới:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(15, 5))
        new_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        new_pw.pack(padx=20)
        
        # Confirm password
        ctk.CTkLabel(form_frame, text="Xác nhận mật khẩu:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20, pady=(15, 5))
        confirm_pw = ctk.CTkEntry(form_frame, show="•", width=300)
        confirm_pw.pack(padx=20)
        
        def do_change_password():
            old = current_pw.get()
            new = new_pw.get()
            confirm = confirm_pw.get()
            
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
                current_pw.delete(0, 'end')
                new_pw.delete(0, 'end')
                confirm_pw.delete(0, 'end')
            else:
                messagebox.showerror("Lỗi", "Mật khẩu hiện tại không đúng!")
        
        # Button
        ctk.CTkButton(
            form_frame,
            text="Đổi mật khẩu",
            command=do_change_password,
            width=300
        ).pack(padx=20, pady=20)
        
    def logout(self):
        """Đăng xuất"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn đăng xuất?"):
            self.destroy()
            self.parent.deiconify()  # Hiện lại cửa sổ đăng nhập
            
    def on_closing(self):
        """Xử lý đóng cửa sổ"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn thoát?"):
            self.parent.destroy()
            self.destroy()
