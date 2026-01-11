"""
My Requests - Xem yêu cầu mượn sách của đọc giả
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_reader_borrow_requests, cancel_borrow_request
from utils import treeview_sort_column


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
            
            # Chỉ cho hủy nếu đang chờ duyệt
            if "Chờ duyệt" in str(trang_thai):
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
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết yêu cầu mượn")
        dialog.geometry("450x450")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"📖 {req['tieu_de']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400
        ).pack(pady=(0, 15))
        
        status_display = {
            'CHO_DUYET': '⏳ Chờ duyệt',
            'CHO_LAY_SACH': '📦 Chờ lấy sách',
            'DA_LAY': '✅ Đã lấy',
            'TU_CHOI': '❌ Từ chối',
            'DA_HUY': '🚫 Đã hủy'
        }
        
        info_data = [
            ("Mã yêu cầu:", req['ma_yeu_cau']),
            ("Tác giả:", req['tac_gia'] or 'N/A'),
            ("Thể loại:", req['ten_the_loai'] or 'N/A'),
            ("Ngày yêu cầu:", req['ngay_yeu_cau']),
            ("Số ngày đề xuất:", f"{req['so_ngay_muon_de_xuat']} ngày"),
            ("Trạng thái:", status_display.get(req['trang_thai'], req['trang_thai'])),
            ("Người xử lý:", req['nguoi_xu_ly'] or '-'),
            ("Ngày xử lý:", req['ngay_xu_ly'] or '-'),
        ]
        
        # Thêm thông tin số ngày mượn chính thức nếu đã được duyệt
        if req['trang_thai'] in ['CHO_LAY_SACH', 'DA_LAY'] and req.get('so_ngay_muon_chinh_thuc'):
            info_data.append(("Số ngày mượn (duyệt):", f"{req['so_ngay_muon_chinh_thuc']} ngày"))
        
        for label, value in info_data:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=120, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left", padx=10)
        
        # Ghi chú
        if req['ghi_chu']:
            ctk.CTkLabel(frame, text="Ghi chú:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(frame, text=req['ghi_chu'], wraplength=400, anchor="w").pack(fill="x")
        
        # Lý do từ chối
        if req['trang_thai'] == 'TU_CHOI' and req.get('ly_do_tu_choi'):
            ctk.CTkLabel(frame, text="Lý do từ chối:", font=ctk.CTkFont(weight="bold"), 
                        text_color="#dc3545", anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(frame, text=req['ly_do_tu_choi'], wraplength=400, 
                        text_color="#dc3545", anchor="w").pack(fill="x")
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(btn_frame, text="Đóng", command=dialog.destroy, fg_color="gray", width=100).pack(side="left")
        
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
                width=120
            ).pack(side="right", padx=5)
