"""
Main View - Giao diện chính của ứng dụng
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_book_statistics, get_borrow_statistics


class MainView(ctk.CTkToplevel):
    """Giao diện chính sau khi đăng nhập"""
    
    # Màu cho menu button
    ACTIVE_COLOR = "#1f538d"  # Màu khi active
    INACTIVE_COLOR = "transparent"  # Màu khi không active
    
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        
        self.parent = parent
        self.user = user
        self.current_frame = None
        self.menu_buttons = []  # Danh sách các menu button
        self.active_button = None  # Button đang active
        
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
            command=lambda: self.set_active_and_show(self.dashboard_btn, self.show_dashboard),
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color=self.INACTIVE_COLOR,
            text_color=("gray10", "gray90"),
            hover_color=("gray75", "gray35")
        )
        self.dashboard_btn.pack(fill="x", pady=2)
        self.menu_buttons.append(self.dashboard_btn)
        
        # Quản lý sách (Nhân viên & Admin)
        if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
            self.book_btn = ctk.CTkButton(
                menu_frame,
                text="📖  Quản lý Sách",
                command=lambda: self.set_active_and_show(self.book_btn, self.show_book_management),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.book_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.book_btn)
            
            # Quản lý đọc giả
            self.reader_btn = ctk.CTkButton(
                menu_frame,
                text="👥  Quản lý Đọc giả",
                command=lambda: self.set_active_and_show(self.reader_btn, self.show_reader_management),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.reader_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.reader_btn)
            
            # Quản lý mượn/trả
            self.borrow_btn = ctk.CTkButton(
                menu_frame,
                text="📋  Mượn/Trả Sách",
                command=lambda: self.set_active_and_show(self.borrow_btn, self.show_borrow_management),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.borrow_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.borrow_btn)
            
            # Yêu cầu mượn sách (từ đọc giả)
            self.requests_btn = ctk.CTkButton(
                menu_frame,
                text="📝  Yêu cầu mượn sách",
                command=lambda: self.set_active_and_show(self.requests_btn, self.show_borrow_requests),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.requests_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.requests_btn)
        
        # Quản lý nhân viên (chỉ Admin)
        if self.user['loai_nguoi_dung'] == 'ADMIN':
            self.staff_btn = ctk.CTkButton(
                menu_frame,
                text="👔  Quản lý Nhân viên",
                command=lambda: self.set_active_and_show(self.staff_btn, self.show_staff_management),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.staff_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.staff_btn)
        
        # Đọc giả - Menu tìm và mượn sách
        if self.user['loai_nguoi_dung'] == 'DOC_GIA':
            self.search_books_btn = ctk.CTkButton(
                menu_frame,
                text="🔍  Tìm & Mượn sách",
                command=lambda: self.set_active_and_show(self.search_books_btn, self.show_search_books),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.search_books_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.search_books_btn)
            
            self.my_borrows_btn = ctk.CTkButton(
                menu_frame,
                text="📚  Sách đã mượn",
                command=lambda: self.set_active_and_show(self.my_borrows_btn, self.show_my_borrows),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.my_borrows_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.my_borrows_btn)
            
            # Yêu cầu của tôi
            self.my_requests_btn = ctk.CTkButton(
                menu_frame,
                text="📝  Yêu cầu của tôi",
                command=lambda: self.set_active_and_show(self.my_requests_btn, self.show_my_requests),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.my_requests_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.my_requests_btn)
        
        # Thống kê
        if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
            self.stats_btn = ctk.CTkButton(
                menu_frame,
                text="📈  Thống kê",
                command=lambda: self.set_active_and_show(self.stats_btn, self.show_statistics),
                height=40,
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color=self.INACTIVE_COLOR,
                text_color=("gray10", "gray90"),
                hover_color=("gray75", "gray35")
            )
            self.stats_btn.pack(fill="x", pady=2)
            self.menu_buttons.append(self.stats_btn)
        
        # Thông tin tài khoản
        self.account_btn = ctk.CTkButton(
            menu_frame,
            text="👤  Thông tin tài khoản",
            command=lambda: self.set_active_and_show(self.account_btn, self.show_account),
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color=self.INACTIVE_COLOR,
            text_color=("gray10", "gray90"),
            hover_color=("gray75", "gray35")
        )
        self.account_btn.pack(fill="x", pady=2)
        self.menu_buttons.append(self.account_btn)
        
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
    
    def set_active_button(self, button):
        """Set button là active và reset các button khác"""
        # Reset tất cả button về trạng thái inactive
        for btn in self.menu_buttons:
            btn.configure(fg_color=self.INACTIVE_COLOR, text_color=("gray10", "gray90"))
        
        # Set button được chọn là active
        if button:
            button.configure(fg_color=self.ACTIVE_COLOR, text_color="white")
            self.active_button = button
    
    def set_active_and_show(self, button, show_func):
        """Set active button và gọi hàm hiển thị"""
        self.set_active_button(button)
        show_func()
            
    def show_dashboard(self):
        """Hiển thị tổng quan"""
        self.set_active_button(self.dashboard_btn)
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
        
    def show_search_books(self):
        """Hiển thị tìm và mượn sách"""
        self.clear_content()
        try:
            from views.search_books import SearchBooks
            self.current_frame = SearchBooks(self.content_frame, self.user)
            self.current_frame.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể tải trang: {str(e)}")
    
    def show_my_borrows(self):
        """Hiển thị sách đã mượn"""
        self.clear_content()
        try:
            from views.my_borrows import MyBorrows
            self.current_frame = MyBorrows(self.content_frame, self.user)
            self.current_frame.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể tải trang: {str(e)}")
    
    def show_my_requests(self):
        """Hiển thị yêu cầu mượn của đọc giả"""
        self.clear_content()
        try:
            from views.my_requests import MyRequests
            self.current_frame = MyRequests(self.content_frame, self.user)
            self.current_frame.pack(fill="both", expand=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Lỗi", f"Không thể tải trang: {str(e)}")
    
    def show_borrow_requests(self):
        """Hiển thị quản lý yêu cầu mượn (nhân viên/admin)"""
        self.clear_content()
        try:
            from views.borrow_requests import BorrowRequestsView
            self.current_frame = BorrowRequestsView(self.content_frame, self.user)
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
        
    def show_account(self):
        """Hiển thị thông tin tài khoản"""
        self.clear_content()
        from views.account_view import AccountView
        self.current_frame = AccountView(self.content_frame, self.user)
        self.current_frame.pack(fill="both", expand=True)
        
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
