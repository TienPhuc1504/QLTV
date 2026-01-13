"""
Xem yêu cầu mượn sách của đọc giả
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_reader_borrow_requests, cancel_borrow_request
from utils import treeview_sort_column, center_window


class MyRequests(ctk.CTkFrame):
    """Giao diện xem yêu cầu mượn sách của đọc giả"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_request = None
        
        self.create_widgets()
        self.load_requests()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📋 Yêu cầu mượn sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Làm mới",
            command=self.load_requests,
            width=100
        ).pack(side="right")
        
        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(filter_frame, text="Trạng thái:").pack(side="left", padx=(0, 5))
        
        self.status_var = ctk.StringVar(value="Tất cả")
        status_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Tất cả", "Chờ duyệt", "Chờ lấy sách", "Đã lấy", "Từ chối", "Đã hủy"],
            variable=self.status_var,
            command=lambda e: self.load_requests(),
            width=130
        )
        status_combo.pack(side="left")
        
        # Request list
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ma_yeu_cau", "tieu_de", "ngay_yeu_cau", "so_ngay_de_xuat", "trang_thai", "nguoi_xu_ly")
        self.request_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        headings = {
            "ma_yeu_cau": "Mã YC",
            "tieu_de": "Tên sách",
            "ngay_yeu_cau": "Ngày yêu cầu",
            "so_ngay_de_xuat": "Số ngày đề xuất",
            "trang_thai": "Trạng thái",
            "nguoi_xu_ly": "Người xử lý"
        }
        for col, text in headings.items():
            self.request_tree.heading(col, text=text,
                                command=lambda t=self.request_tree, c=col: treeview_sort_column(t, c, False))
        
        self.request_tree.column("ma_yeu_cau", width=60, anchor="center")
        self.request_tree.column("tieu_de", width=250)
        self.request_tree.column("ngay_yeu_cau", width=100, anchor="center")
        self.request_tree.column("so_ngay_de_xuat", width=110, anchor="center")
        self.request_tree.column("trang_thai", width=100, anchor="center")
        self.request_tree.column("nguoi_xu_ly", width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.request_tree.yview)
        self.request_tree.configure(yscrollcommand=scrollbar.set)
        
        self.request_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.request_tree.bind('<<TreeviewSelect>>', self.on_request_select)
        self.request_tree.bind('<Double-1>', self.on_double_click)
        
        # Action frame
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.cancel_btn = ctk.CTkButton(
            action_frame,
            text="❌ Hủy yêu cầu",
            command=self.cancel_request,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=120,
            state="disabled"
        )
        self.cancel_btn.pack(side="left", padx=5)
        
        self.detail_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Xem chi tiết",
            command=self.view_detail,
            width=120,
            state="disabled"
        )
        self.detail_btn.pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Bạn chỉ có thể hủy yêu cầu đang chờ duyệt. Sau khi được duyệt, hãy đến thư viện để lấy sách.",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def load_requests(self):
        """Tải danh sách yêu cầu"""
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
            
        requests = get_reader_borrow_requests(self.user['ma_nd'])
        
        status_filter = self.status_var.get()
        status_map = {
            "Chờ duyệt": "CHO_DUYET",
            "Chờ lấy sách": "CHO_LAY_SACH",
            "Đã lấy": "DA_LAY",
            "Từ chối": "TU_CHOI",
            "Đã hủy": "DA_HUY"
        }
        
        for req in requests:
            # Filter by status
            if status_filter != "Tất cả":
                if req['trang_thai'] != status_map.get(status_filter):
                    continue
            
            # Format status
            status_display = {
                'CHO_DUYET': '⏳ Chờ duyệt',
                'CHO_LAY_SACH': '📦 Chờ lấy sách',
                'DA_LAY': '✅ Đã lấy',
                'TU_CHOI': '❌ Từ chối',
                'DA_HUY': '🚫 Đã hủy'
            }
            
            self.request_tree.insert("", "end", iid=req['ma_yeu_cau'], values=(
                req['ma_yeu_cau'],
                req['tieu_de'],
                req['ngay_yeu_cau'],
                f"{req['so_ngay_muon_de_xuat']} ngày",
                status_display.get(req['trang_thai'], req['trang_thai']),
                req['nguoi_xu_ly'] or '-'
            ))
            
        self.selected_request = None
        self.cancel_btn.configure(state="disabled")
        self.detail_btn.configure(state="disabled")
            
    def on_request_select(self, event):
        """Xử lý khi chọn yêu cầu"""
        selection = self.request_tree.selection()
        if selection:
            self.selected_request = int(selection[0])
            item = self.request_tree.item(selection[0])
            trang_thai = item['values'][4]
            
            self.detail_btn.configure(state="normal")
            
            # Cho hủy nếu đang chờ duyệt hoặc chờ lấy sách
            if "Chờ duyệt" in str(trang_thai) or "Chờ lấy sách" in str(trang_thai):
                self.cancel_btn.configure(state="normal")
            else:
                self.cancel_btn.configure(state="disabled")
        else:
            self.selected_request = None
            self.cancel_btn.configure(state="disabled")
            self.detail_btn.configure(state="disabled")
    
    def on_double_click(self, event):
        """Xử lý double click"""
        region = self.request_tree.identify("region", event.x, event.y)
        if region == "cell":
            self.view_detail()
            
    def cancel_request(self):
        """Hủy yêu cầu"""
        if not self.selected_request:
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy yêu cầu này?"):
            try:
                cancel_borrow_request(self.selected_request, self.user['ma_nd'])
                messagebox.showinfo("Thành công", "Đã hủy yêu cầu!")
                self.load_requests()
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                
    def view_detail(self):
        """Xem chi tiết yêu cầu"""
        if not self.selected_request:
            return
            
        requests = get_reader_borrow_requests(self.user['ma_nd'])
        req = None
        for r in requests:
            if r['ma_yeu_cau'] == self.selected_request:
                req = r
                break
                
        if not req:
            return
        
        # Xác định màu header dựa trên trạng thái
        status_colors = {
            'CHO_DUYET': '#ffc107',      # Vàng - chờ duyệt
            'CHO_LAY_SACH': '#17a2b8',   # Xanh dương - chờ lấy sách
            'DA_LAY': '#28a745',          # Xanh lá - đã lấy
            'TU_CHOI': '#dc3545',         # Đỏ - từ chối
            'DA_HUY': '#6c757d'           # Xám - đã hủy
        }
        header_color = status_colors.get(req['trang_thai'], '#1f538d')
        
        status_display = {
            'CHO_DUYET': '⏳ Chờ duyệt',
            'CHO_LAY_SACH': '📦 Chờ lấy sách',
            'DA_LAY': '✅ Đã lấy',
            'TU_CHOI': '❌ Từ chối',
            'DA_HUY': '🚫 Đã hủy'
        }
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("📋 Chi tiết yêu cầu mượn")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        center_window(dialog, 500, 520)
        
        # === HEADER ===
        header = ctk.CTkFrame(dialog, fg_color=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📋 Chi tiết yêu cầu mượn sách",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        # === CONTENT ===
        frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Book info card
        book_card = ctk.CTkFrame(frame, fg_color=("#f8f9fa", "#2d2d2d"), corner_radius=8)
        book_card.pack(fill="x", pady=(0, 15))
        
        book_inner = ctk.CTkFrame(book_card, fg_color="transparent")
        book_inner.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            book_inner,
            text="📚 " + req['tieu_de'],
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=420,
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            book_inner,
            text=f"✍️ {req['tac_gia'] or 'N/A'} | 📂 {req['ten_the_loai'] or 'N/A'}",
            text_color="gray",
            anchor="w"
        ).pack(fill="x", pady=(3, 0))
        
        # Status badge
        status_badge_frame = ctk.CTkFrame(frame, fg_color="transparent")
        status_badge_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(
            status_badge_frame,
            text=status_display.get(req['trang_thai'], req['trang_thai']),
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=header_color,
            text_color="white",
            corner_radius=8,
            width=130,
            height=28
        ).pack(side="left")
        
        # Info grid
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)
        
        info_data = [
            ("📌 Mã yêu cầu:", str(req['ma_yeu_cau'])),
            ("📅 Ngày yêu cầu:", req['ngay_yeu_cau']),
            ("⏱️ Số ngày đề xuất:", f"{req['so_ngay_muon_de_xuat']} ngày"),
            ("👤 Người xử lý:", req['nguoi_xu_ly'] or '-'),
            ("📆 Ngày xử lý:", req['ngay_xu_ly'] or '-'),
        ]
        
        # Thêm thông tin số ngày mượn chính thức nếu đã được duyệt
        if req['trang_thai'] in ['CHO_LAY_SACH', 'DA_LAY'] and req.get('so_ngay_muon_chinh_thuc'):
            info_data.append(("✅ Số ngày được duyệt:", f"{req['so_ngay_muon_chinh_thuc']} ngày"))
        
        for i, (label_text, value_text) in enumerate(info_data):
            label = ctk.CTkLabel(
                info_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            label.grid(row=i, column=0, sticky="w", pady=6, padx=(0, 15))
            
            value = ctk.CTkLabel(
                info_frame,
                text=value_text,
                font=ctk.CTkFont(size=13),
                anchor="w"
            )
            value.grid(row=i, column=1, sticky="w", pady=6)
        
        # Thông tin hạn lấy sách nếu đang chờ lấy
        if req['trang_thai'] == 'CHO_LAY_SACH' and req.get('han_lay_sach'):
            from datetime import datetime
            pickup_frame = ctk.CTkFrame(frame, fg_color=("#e3f2fd", "#1a3a5c"), corner_radius=8)
            pickup_frame.pack(fill="x", pady=10)
            
            pickup_inner = ctk.CTkFrame(pickup_frame, fg_color="transparent")
            pickup_inner.pack(fill="x", padx=15, pady=10)
            
            try:
                han_lay = datetime.strptime(req['han_lay_sach'], '%Y-%m-%d %H:%M:%S')
                now = datetime.now()
                remaining = han_lay - now
                
                if remaining.total_seconds() > 0:
                    hours_left = int(remaining.total_seconds() // 3600)
                    if hours_left >= 24:
                        days_left = hours_left // 24
                        time_str = f"⏰ Còn {days_left} ngày {hours_left % 24} giờ"
                    else:
                        time_str = f"⏰ Còn {hours_left} giờ"
                    deadline_text = f"📅 {han_lay.strftime('%d/%m/%Y %H:%M')} ({time_str})"
                    deadline_color = ("#1976d2", "#64b5f6")
                else:
                    deadline_text = f"⚠️ Đã hết hạn ({han_lay.strftime('%d/%m/%Y %H:%M')})"
                    deadline_color = ("#dc3545", "#ff6b6b")
            except:
                deadline_text = req['han_lay_sach']
                deadline_color = ("#1976d2", "#64b5f6")
            
            ctk.CTkLabel(
                pickup_inner,
                text="🏃 Hạn đến lấy sách:",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                pickup_inner,
                text=deadline_text,
                font=ctk.CTkFont(size=12),
                text_color=deadline_color
            ).pack(anchor="w", pady=(5, 0))
        
        # Ghi chú
        if req['ghi_chu']:
            note_frame = ctk.CTkFrame(frame, fg_color=("#f5f5f5", "#383838"), corner_radius=8)
            note_frame.pack(fill="x", pady=10)
            
            note_inner = ctk.CTkFrame(note_frame, fg_color="transparent")
            note_inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                note_inner,
                text="📝 Ghi chú của bạn:",
                font=ctk.CTkFont(weight="bold"),
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                note_inner,
                text=req['ghi_chu'],
                wraplength=420,
                anchor="w",
                justify="left"
            ).pack(fill="x", pady=(5, 0))
        
        # Lý do từ chối
        if req['trang_thai'] == 'TU_CHOI' and req.get('ly_do_tu_choi'):
            reject_frame = ctk.CTkFrame(frame, fg_color=("#ffebee", "#3d1a1a"), corner_radius=8)
            reject_frame.pack(fill="x", pady=10)
            
            reject_inner = ctk.CTkFrame(reject_frame, fg_color="transparent")
            reject_inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                reject_inner,
                text="❌ Lý do từ chối:",
                font=ctk.CTkFont(weight="bold"),
                text_color=("#dc3545", "#ff6b6b"),
                anchor="w"
            ).pack(fill="x")
            
            ctk.CTkLabel(
                reject_inner,
                text=req['ly_do_tu_choi'],
                wraplength=420,
                text_color=("#dc3545", "#ff6b6b"),
                anchor="w",
                justify="left"
            ).pack(fill="x", pady=(5, 0))
        
        # Info hint
        if req['trang_thai'] == 'CHO_DUYET':
            info_hint = ctk.CTkFrame(frame, fg_color=("#fff3e0", "#3d2e1a"), corner_radius=8)
            info_hint.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                info_hint,
                text="💡 Yêu cầu của bạn đang được xử lý. Vui lòng chờ nhân viên thư viện xác nhận.",
                text_color=("#e65100", "#ffb74d"),
                font=ctk.CTkFont(size=11),
                wraplength=420
            ).pack(padx=12, pady=10)
        
        # === BUTTONS ===
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame, 
            text="Đóng", 
            command=dialog.destroy, 
            fg_color="gray",
            width=100
        ).pack(side="left")
        
        # Nếu đang chờ duyệt, hiện thêm nút hủy
        if req['trang_thai'] == 'CHO_DUYET':
            def cancel_from_detail():
                if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn hủy yêu cầu này?"):
                    try:
                        cancel_borrow_request(req['ma_yeu_cau'], self.user['ma_nd'])
                        dialog.destroy()
                        messagebox.showinfo("Thành công", "Đã hủy yêu cầu!")
                        self.load_requests()
                    except Exception as e:
                        messagebox.showerror("Lỗi", str(e))
            
            ctk.CTkButton(
                btn_frame, 
                text="❌ Hủy yêu cầu", 
                command=cancel_from_detail,
                fg_color="#dc3545",
                hover_color="#c82333",
                width=130,
                font=ctk.CTkFont(weight="bold")
            ).pack(side="right")
