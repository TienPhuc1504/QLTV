"""
Giao diện thông báo
"""
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (
    get_notifications, 
    get_unread_notification_count,
    mark_notification_as_read,
    mark_all_notifications_as_read,
    delete_notification
)


class NotificationsView(ctk.CTkFrame):
    """Giao diện xem thông báo"""
    
    def __init__(self, parent, user: dict, on_notification_change=None):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.on_notification_change = on_notification_change  # Callback để cập nhật badge
        
        self.create_widgets()
        self.load_notifications()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Tiêu đề
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="🔔 Thông báo",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Các nút hành động
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        ctk.CTkButton(
            btn_frame,
            text="✅ Đánh dấu tất cả đã đọc",
            command=self.mark_all_read,
            width=180,
            fg_color="#28a745",
            hover_color="#218838"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🔄 Làm mới",
            command=self.load_notifications,
            width=100
        ).pack(side="left", padx=5)
        
        # Khung bộ lọc
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Hiển thị:").pack(side="left", padx=(0, 5))
        
        self.filter_var = ctk.StringVar(value="Tất cả")
        filter_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Tất cả", "Chưa đọc", "Đã đọc"],
            variable=self.filter_var,
            command=lambda e: self.load_notifications(),
            width=120
        )
        filter_combo.pack(side="left")
        
        # Nhãn đếm chưa đọc
        self.unread_label = ctk.CTkLabel(
            filter_frame,
            text="",
            text_color="#dc3545",
            font=ctk.CTkFont(weight="bold")
        )
        self.unread_label.pack(side="left", padx=20)
        
        # Khung danh sách thông báo
        self.list_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Nhãn trạng thái rỗng
        self.empty_label = ctk.CTkLabel(
            self.list_container,
            text="📭 Không có thông báo nào",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        
    def load_notifications(self):
        """Tải danh sách thông báo"""
        # Xóa thông báo hiện tại
        for widget in self.list_container.winfo_children():
            widget.destroy()
            
        # Lấy bộ lọc
        filter_val = self.filter_var.get()
        unread_only = filter_val == "Chưa đọc"
        
        # Lấy thông báo
        notifications = get_notifications(self.user['ma_nd'], limit=50, unread_only=unread_only)
        
        # Lọc chỉ các thông báo đã đọc
        if filter_val == "Đã đọc":
            notifications = [n for n in notifications if n['da_doc'] == 1]
        
        # Cập nhật số lượng chưa đọc
        unread_count = get_unread_notification_count(self.user['ma_nd'])
        if unread_count > 0:
            self.unread_label.configure(text=f"🔴 {unread_count} thông báo chưa đọc")
        else:
            self.unread_label.configure(text="✅ Đã đọc tất cả")
        
        if not notifications:
            self.empty_label = ctk.CTkLabel(
                self.list_container,
                text="📭 Không có thông báo nào",
                font=ctk.CTkFont(size=16),
                text_color="gray"
            )
            self.empty_label.pack(pady=50)
            return
            
        # Vẽ thông báo
        for notif in notifications:
            self.create_notification_card(notif)
            
    def create_notification_card(self, notif: dict):
        """Tạo card hiển thị thông báo"""
        # Xác định màu theo loại và trạng thái đọc
        type_colors = {
            'YEU_CAU_DUYET': '#28a745',      # Xanh lá - đã duyệt
            'YEU_CAU_TU_CHOI': '#dc3545',    # Đỏ - bị từ chối
            'SAP_HET_HAN': '#ffc107',         # Vàng - cảnh báo
            'QUA_HAN': '#dc3545',             # Đỏ - quá hạn
            'SACH_CO_SAN': '#17a2b8',         # Xanh dương - thông tin
            'HE_THONG': '#6c757d'             # Xám - hệ thống
        }
        
        type_icons = {
            'YEU_CAU_DUYET': '✅',
            'YEU_CAU_TU_CHOI': '❌',
            'SAP_HET_HAN': '⏰',
            'QUA_HAN': '⚠️',
            'SACH_CO_SAN': '📚',
            'HE_THONG': '🔔'
        }
        
        bg_color = "#2b2b2b" if notif['da_doc'] else "#1a472a"
        border_color = type_colors.get(notif['loai_thong_bao'], '#6c757d')
        
        # Khung thẻ
        card = ctk.CTkFrame(
            self.list_container,
            fg_color=bg_color,
            border_width=2,
            border_color=border_color if not notif['da_doc'] else "transparent",
            corner_radius=10
        )
        card.pack(fill="x", pady=5, padx=5)
        
        # Khung nội dung
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Hàng tiêu đề
        header_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        header_row.pack(fill="x")
        
        # Biểu tượng và tiêu đề
        icon = type_icons.get(notif['loai_thong_bao'], '🔔')
        title_text = f"{icon} {notif['tieu_de']}"
        
        title_label = ctk.CTkLabel(
            header_row,
            text=title_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w"
        )
        title_label.pack(side="left", fill="x", expand=True)
        
        # Chỉ báo chưa đọc
        if not notif['da_doc']:
            unread_badge = ctk.CTkLabel(
                header_row,
                text="●",
                text_color="#28a745",
                font=ctk.CTkFont(size=16)
            )
            unread_badge.pack(side="right", padx=5)
        
        # Thời gian
        try:
            ngay_tao = datetime.strptime(notif['ngay_tao'], '%Y-%m-%d %H:%M:%S')
            time_ago = self.get_time_ago(ngay_tao)
        except:
            time_ago = notif['ngay_tao']
            
        time_label = ctk.CTkLabel(
            header_row,
            text=time_ago,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        time_label.pack(side="right")
        
        # Nội dung
        content_label = ctk.CTkLabel(
            content_frame,
            text=notif['noi_dung'],
            font=ctk.CTkFont(size=12),
            anchor="w",
            justify="left",
            wraplength=600
        )
        content_label.pack(fill="x", pady=(5, 0))
        
        # Các nút hành động
        action_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        action_row.pack(fill="x", pady=(10, 0))
        
        if not notif['da_doc']:
            ctk.CTkButton(
                action_row,
                text="Đánh dấu đã đọc",
                command=lambda n=notif: self.mark_read(n['ma_thong_bao']),
                width=130,
                height=28,
                fg_color="#28a745",
                hover_color="#218838"
            ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            action_row,
            text="🗑️ Xóa",
            command=lambda n=notif: self.delete_notif(n['ma_thong_bao']),
            width=70,
            height=28,
            fg_color="#dc3545",
            hover_color="#c82333"
        ).pack(side="left")
        
    def get_time_ago(self, dt: datetime) -> str:
        """Chuyển datetime thành chuỗi 'X phút/giờ/ngày trước'"""
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
            return dt.strftime("%d/%m/%Y %H:%M")
            
    def mark_read(self, ma_thong_bao: int):
        """Đánh dấu thông báo đã đọc"""
        mark_notification_as_read(ma_thong_bao)
        self.load_notifications()
        
        if self.on_notification_change:
            self.on_notification_change()
            
    def mark_all_read(self):
        """Đánh dấu tất cả đã đọc"""
        mark_all_notifications_as_read(self.user['ma_nd'])
        self.load_notifications()
        
        if self.on_notification_change:
            self.on_notification_change()
            
    def delete_notif(self, ma_thong_bao: int):
        """Xóa thông báo"""
        delete_notification(ma_thong_bao)
        self.load_notifications()
        
        if self.on_notification_change:
            self.on_notification_change()


class NotificationBell(ctk.CTkFrame):
    """Widget chuông thông báo với badge"""
    
    def __init__(self, parent, user: dict, on_click=None):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.on_click = on_click
        
        self.create_widgets()
        self.update_count()
        
    def create_widgets(self):
        """Tạo widget chuông"""
        self.bell_btn = ctk.CTkButton(
            self,
            text="🔔",
            width=40,
            height=40,
            fg_color="transparent",
            hover_color=("gray70", "gray30"),
            font=ctk.CTkFont(size=20),
            command=self.handle_click
        )
        self.bell_btn.pack()
        
        # Nhãn (badge)
        self.badge = ctk.CTkLabel(
            self,
            text="",
            width=20,
            height=20,
            fg_color="#dc3545",
            corner_radius=10,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        
    def update_count(self):
        """Cập nhật số thông báo chưa đọc"""
        count = get_unread_notification_count(self.user['ma_nd'])
        
        if count > 0:
            display_count = "9+" if count > 9 else str(count)
            self.badge.configure(text=display_count)
            self.badge.place(relx=0.7, rely=0, anchor="center")
        else:
            self.badge.place_forget()
            
    def handle_click(self):
        """Xử lý click vào chuông"""
        if self.on_click:
            self.on_click()
