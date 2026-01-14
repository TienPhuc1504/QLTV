"""
Giao diện chính của ứng dụng
"""
import customtkinter as ctk
from tkinter import messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_book_statistics, get_borrow_statistics, get_unread_notification_count, check_and_notify_due_books, get_notifications, delete_notification, delete_all_notifications
from utils import center_window as center_window_util


class MainView(ctk.CTkToplevel):
    """Giao diện chính sau khi đăng nhập"""
    
    # Màu cho nút menu
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
        
        # Xử lý khi đóng cửa sổ
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Căn giữa cửa sổ
        self.center_window()
        
        # Tạo giao diện
        self.create_widgets()
        
        # Cập nhật chỉ số thông báo
        self.update_notification_badge()
        
        # Bắt đầu kiểm tra thông báo định kỳ
        self.start_notification_checker()
        
        # (Phiên không có timeout — bỏ bắt/đặt timer phiên)
        
        # Hiển thị dashboard mặc định
        self.show_dashboard()
        
    def center_window(self):
        """Căn giữa cửa sổ"""
        center_window_util(self, 1200, 700)
        
    def create_widgets(self):
        """Tạo giao diện chính"""
        # Thanh bên (Sidebar)
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
        
        # Thông tin người dùng
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
        
        # Các nút menu
        menu_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        menu_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Nút Dashboard
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
        
        # Nút đăng xuất
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
        
        # Khu vực nội dung chính
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
        # Đặt lại trạng thái tất cả nút thành inactive
        for btn in self.menu_buttons:
            btn.configure(fg_color=self.INACTIVE_COLOR, text_color=("gray10", "gray90"))
        
        # Đặt nút được chọn thành active
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
        
        # Main content area with 2 columns
        main_content = ctk.CTkFrame(self.current_frame, fg_color="transparent")
        main_content.pack(fill="both", expand=True, pady=10)
        main_content.grid_columnconfigure(0, weight=1)
        main_content.grid_columnconfigure(1, weight=1)
        main_content.grid_rowconfigure(0, weight=1)
        
        # Cột trái - Chào mừng & Hành động nhanh
        left_frame = ctk.CTkFrame(main_content)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        
        welcome_text = ctk.CTkLabel(
            left_frame,
            text=f"Xin chào, {self.user['ho_ten']}! 👋",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        welcome_text.pack(pady=(20, 10))
        
        role_display = {
            'ADMIN': 'Quản trị viên',
            'NHAN_VIEN': 'Nhân viên',
            'DOC_GIA': 'Độc giả'
        }
        
        guide_text = ctk.CTkLabel(
            left_frame,
            text=f"Vai trò: {role_display.get(self.user['loai_nguoi_dung'], '')}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        guide_text.pack(pady=(0, 20))
        
        # Quick actions based on role
        ctk.CTkLabel(
            left_frame,
            text="⚡ Thao tác nhanh",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=20, pady=(10, 5))
        
        quick_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=10)
        
        if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
            ctk.CTkButton(
                quick_frame,
                text="📝 Xử lý yêu cầu mượn",
                command=lambda: self.set_active_and_show(self.requests_btn, self.show_borrow_requests),
                width=200
            ).pack(pady=5)
            
            ctk.CTkButton(
                quick_frame,
                text="📖 Quản lý sách",
                command=lambda: self.set_active_and_show(self.book_btn, self.show_book_management),
                width=200
            ).pack(pady=5)
        else:
            ctk.CTkButton(
                quick_frame,
                text="🔍 Tìm & Mượn sách",
                command=lambda: self.set_active_and_show(self.search_books_btn, self.show_search_books),
                width=200
            ).pack(pady=5)
            
            ctk.CTkButton(
                quick_frame,
                text="📚 Sách đã mượn",
                command=lambda: self.set_active_and_show(self.my_borrows_btn, self.show_my_borrows),
                width=200
            ).pack(pady=5)
        
        # Cột phải - Thông báo
        right_frame = ctk.CTkFrame(main_content)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        
        # Notification header
        notif_header = ctk.CTkFrame(right_frame, fg_color="transparent")
        notif_header.pack(fill="x", padx=15, pady=(15, 5))
        
        unread_count = get_unread_notification_count(self.user['ma_nd'])
        notif_title = f"🔔 Thông báo ({unread_count} chưa đọc)" if unread_count > 0 else "🔔 Thông báo"
        
        ctk.CTkLabel(
            notif_header,
            text=notif_title,
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            notif_header,
            text="🔄",
            command=self.show_dashboard,
            width=35,
            height=28,
            fg_color="#17a2b8",
            hover_color="#138496"
        ).pack(side="right", padx=(5, 0))
        
        ctk.CTkButton(
            notif_header,
            text="🗑️ Xóa tất cả",
            command=self.delete_all_notifications_action,
            width=100,
            height=28,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="right")
        
        # Notification list
        notif_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        notif_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        notifications = get_notifications(self.user['ma_nd'], limit=20)
        
        if not notifications:
            ctk.CTkLabel(
                notif_scroll,
                text="📭 Không có thông báo nào",
                text_color="gray"
            ).pack(pady=30)
        else:
            # Group notifications by type
            self.render_notifications_grouped(notif_scroll, notifications)
        
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
    
    def render_notifications_grouped(self, parent, notifications):
        """Render thông báo được chia theo nhóm"""
        from datetime import datetime
        
        # Nhóm thông báo theo loại
        groups = {
            'staff': {
                'title': '📝 Yêu cầu cần xử lý',
                'types': ['YEU_CAU_MOI'],
                'color': '#17a2b8',
                'items': []
            },
            'approved': {
                'title': '✅ Yêu cầu đã duyệt',
                'types': ['YEU_CAU_DUYET', 'CHO_LAY_SACH'],
                'color': '#28a745',
                'items': []
            },
            'rejected': {
                'title': '❌ Yêu cầu từ chối',
                'types': ['YEU_CAU_TU_CHOI'],
                'color': '#dc3545',
                'items': []
            },
            'due': {
                'title': '⏰ Nhắc nhở hạn trả',
                'types': ['SAP_HET_HAN', 'QUA_HAN'],
                'color': '#ffc107',
                'items': []
            },
            'other': {
                'title': '🔔 Thông báo khác',
                'types': ['SACH_CO_SAN', 'HE_THONG'],
                'color': '#6c757d',
                'items': []
            }
        }
        
        # Phân loại thông báo
        for notif in notifications:
            for group_key, group in groups.items():
                if notif['loai_thong_bao'] in group['types']:
                    group['items'].append(notif)
                    break
        
        # Render từng nhóm
        for group_key, group in groups.items():
            if not group['items']:
                continue
                
            # Group header
            group_frame = ctk.CTkFrame(parent, fg_color=group['color'], corner_radius=8)
            group_frame.pack(fill="x", pady=5)
            
            header = ctk.CTkFrame(group_frame, fg_color="transparent")
            header.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                header,
                text=f"{group['title']} ({len(group['items'])})",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="white"
            ).pack(side="left")
            
            # Items container
            items_frame = ctk.CTkFrame(group_frame, fg_color=("gray90", "gray20"), corner_radius=5)
            items_frame.pack(fill="x", padx=5, pady=(0, 5))
            
            for notif in group['items'][:5]:  # Limit 5 per group
                self.create_notification_item(items_frame, notif)
                
            if len(group['items']) > 5:
                ctk.CTkLabel(
                    items_frame,
                    text=f"... và {len(group['items']) - 5} thông báo khác",
                    text_color="gray",
                    font=ctk.CTkFont(size=11)
                ).pack(pady=5)
    
    def create_notification_item(self, parent, notif):
        """Tạo item thông báo"""
        from datetime import datetime
        
        bg_color = ("gray85", "gray25") if notif['da_doc'] else ("gray80", "gray30")
        
        item = ctk.CTkFrame(parent, fg_color=bg_color, corner_radius=5)
        item.pack(fill="x", padx=5, pady=2)
        
        content = ctk.CTkFrame(item, fg_color="transparent")
        content.pack(fill="x", padx=10, pady=8)
        
        # Title row
        title_row = ctk.CTkFrame(content, fg_color="transparent")
        title_row.pack(fill="x")
        
        # Unread indicator
        if not notif['da_doc']:
            ctk.CTkLabel(
                title_row,
                text="●",
                text_color="#28a745",
                font=ctk.CTkFont(size=10)
            ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            title_row,
            text=notif['tieu_de'],
            font=ctk.CTkFont(size=12, weight="bold" if not notif['da_doc'] else "normal"),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)
        
        # Time
        try:
            ngay_tao = datetime.strptime(notif['ngay_tao'], '%Y-%m-%d %H:%M:%S')
            time_ago = self.get_time_ago(ngay_tao)
        except:
            time_ago = ""
            
        ctk.CTkLabel(
            title_row,
            text=time_ago,
            text_color="gray",
            font=ctk.CTkFont(size=10)
        ).pack(side="right")
        
        # Content
        ctk.CTkLabel(
            content,
            text=notif['noi_dung'][:100] + "..." if len(notif['noi_dung']) > 100 else notif['noi_dung'],
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w",
            justify="left",
            wraplength=350
        ).pack(fill="x", pady=(3, 0))
        
        # Action buttons
        btn_row = ctk.CTkFrame(content, fg_color="transparent")
        btn_row.pack(fill="x", pady=(5, 0))
        
        # Delete notification button
        ctk.CTkButton(
            btn_row,
            text="🗑️ Xóa",
            command=lambda n=notif: self.mark_notification_read(n['ma_thong_bao']),
            width=60,
            height=24,
            font=ctk.CTkFont(size=10),
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left", padx=(0, 5))
        
        # Navigation button based on notification type
        nav_info = self.get_notification_navigation(notif)
        if nav_info:
            ctk.CTkButton(
                btn_row,
                text=nav_info['text'],
                command=nav_info['command'],
                width=100,
                height=24,
                font=ctk.CTkFont(size=10),
                fg_color="#007bff",
                hover_color="#0056b3"
            ).pack(side="left")
    
    def get_notification_navigation(self, notif):
        """Lấy thông tin chuyển hướng dựa trên loại thông báo"""
        notif_type = notif['loai_thong_bao']
        
        if notif_type == 'YEU_CAU_MOI':
            # Nhân viên - chuyển đến xử lý yêu cầu
            if self.user['loai_nguoi_dung'] in ['ADMIN', 'NHAN_VIEN']:
                return {
                    'text': '📝 Xử lý',
                    'command': lambda: self.navigate_to_requests(notif)
                }
        
        elif notif_type in ['YEU_CAU_DUYET', 'CHO_LAY_SACH']:
            # Đọc giả - xem yêu cầu của tôi
            if self.user['loai_nguoi_dung'] == 'DOC_GIA':
                return {
                    'text': '📋 Xem yêu cầu',
                    'command': lambda: self.navigate_to_my_requests(notif)
                }
        
        elif notif_type == 'YEU_CAU_TU_CHOI':
            if self.user['loai_nguoi_dung'] == 'DOC_GIA':
                return {
                    'text': '📋 Xem chi tiết',
                    'command': lambda: self.navigate_to_my_requests(notif)
                }
        
        elif notif_type in ['SAP_HET_HAN', 'QUA_HAN']:
            if self.user['loai_nguoi_dung'] == 'DOC_GIA':
                return {
                    'text': '📚 Xem sách mượn',
                    'command': lambda: self.navigate_to_my_borrows(notif)
                }
        
        return None
    
    def navigate_to_requests(self, notif):
        """Chuyển đến trang yêu cầu mượn (nhân viên)"""
        delete_notification(notif['ma_thong_bao'])
        self.update_notification_badge()
        self.set_active_and_show(self.requests_btn, self.show_borrow_requests)
    
    def navigate_to_my_requests(self, notif):
        """Chuyển đến trang yêu cầu của tôi (đọc giả)"""
        delete_notification(notif['ma_thong_bao'])
        self.update_notification_badge()
        self.set_active_and_show(self.my_requests_btn, self.show_my_requests)
    
    def navigate_to_my_borrows(self, notif):
        """Chuyển đến trang sách đã mượn (đọc giả)"""
        delete_notification(notif['ma_thong_bao'])
        self.update_notification_badge()
        self.set_active_and_show(self.my_borrows_btn, self.show_my_borrows)
    
    def mark_notification_read(self, ma_thong_bao):
        """Đánh dấu thông báo đã đọc (xóa thông báo) và refresh"""
        delete_notification(ma_thong_bao)
        self.show_dashboard()
        self.update_notification_badge()
    
    def delete_all_notifications_action(self):
        """Xóa tất cả thông báo"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa tất cả thông báo?"):
            delete_all_notifications(self.user['ma_nd'])
            self.show_dashboard()
            self.update_notification_badge()
    
    def get_time_ago(self, dt):
        """Chuyển datetime thành chuỗi 'X phút/giờ/ngày trước'"""
        from datetime import datetime
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Vừa xong"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes} phút trước"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours} giờ trước"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days} ngày trước"
        else:
            return dt.strftime("%d/%m/%Y")
        
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
    
    def update_notification_badge(self):
        """Cập nhật title Dashboard với số thông báo chưa đọc"""
        try:
            count = get_unread_notification_count(self.user['ma_nd'])
            
            if count > 0:
                self.dashboard_btn.configure(text=f"📊  Tổng quan ({count})")
            else:
                self.dashboard_btn.configure(text="📊  Tổng quan")
        except Exception:
            pass
    
    def start_notification_checker(self):
        """Bắt đầu kiểm tra thông báo định kỳ"""
        def check():
            try:
                # Kiểm tra sách sắp hết hạn và quá hạn
                check_and_notify_due_books()
                # Cập nhật badge
                self.update_notification_badge()
            except Exception:
                pass
            # Lặp lại mỗi 5 phút
            self.after(300000, check)
        
        # Kiểm tra ngay khi khởi động
        self.after(1000, check)
    
    
    def force_logout(self):
        """Đăng xuất bắt buộc (không hỏi xác nhận)"""
        self.destroy()
        self.parent.deiconify()
        
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
