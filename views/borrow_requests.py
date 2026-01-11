"""
Borrow Requests - Quản lý yêu cầu mượn sách (dành cho nhân viên/admin)
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_borrow_requests, approve_borrow_request, 
                      reject_borrow_request, get_pending_requests_count,
                      confirm_book_pickup)
from utils import treeview_sort_column


class BorrowRequestsView(ctk.CTkFrame):
    """Giao diện quản lý yêu cầu mượn sách"""
    
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
            text="📋 Quản lý yêu cầu mượn sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Pending count
        self.pending_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=ctk.CTkFont(size=14),
            text_color="#ffc107"
        )
        self.pending_label.pack(side="left", padx=20)
        
        ctk.CTkButton(
            header_frame,
            text="🔄 Làm mới",
            command=self.load_requests,
            width=100
        ).pack(side="right")
        
        # Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        # Search
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Tìm theo tên đọc giả, sách...",
            width=200
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.load_requests())
        
        # Status filter
        ctk.CTkLabel(filter_frame, text="Trạng thái:").pack(side="left", padx=(15, 5))
        
        self.status_var = ctk.StringVar(value="Chờ xử lý")
        status_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Tất cả", "Chờ xử lý", "Chờ duyệt", "Chờ lấy sách", "Đã lấy", "Từ chối", "Đã hủy"],
            variable=self.status_var,
            command=lambda e: self.load_requests(),
            width=120
        )
        status_combo.pack(side="left")
        
        # Request list
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ma_yeu_cau", "ten_doc_gia", "tieu_de", "ngay_yeu_cau", "so_ngay_de_xuat", "ghi_chu", "trang_thai")
        self.request_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        headings = {
            "ma_yeu_cau": "Mã YC",
            "ten_doc_gia": "Đọc giả",
            "tieu_de": "Tên sách",
            "ngay_yeu_cau": "Ngày YC",
            "so_ngay_de_xuat": "Ngày đề xuất",
            "ghi_chu": "Ghi chú",
            "trang_thai": "Trạng thái"
        }
        for col, text in headings.items():
            self.request_tree.heading(col, text=text,
                                command=lambda t=self.request_tree, c=col: treeview_sort_column(t, c, False))
        
        self.request_tree.column("ma_yeu_cau", width=50, anchor="center")
        self.request_tree.column("ten_doc_gia", width=130)
        self.request_tree.column("tieu_de", width=200)
        self.request_tree.column("ngay_yeu_cau", width=90, anchor="center")
        self.request_tree.column("so_ngay_de_xuat", width=90, anchor="center")
        self.request_tree.column("ghi_chu", width=150)
        self.request_tree.column("trang_thai", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.request_tree.yview)
        self.request_tree.configure(yscrollcommand=scrollbar.set)
        
        self.request_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        self.request_tree.bind('<<TreeviewSelect>>', self.on_request_select)
        self.request_tree.bind('<Double-1>', self.on_double_click)
        
        # Action frame
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.approve_btn = ctk.CTkButton(
            action_frame,
            text="✅ Duyệt yêu cầu",
            command=self.show_approve_dialog,
            fg_color="#28a745",
            hover_color="#218838",
            width=130,
            state="disabled"
        )
        self.approve_btn.pack(side="left", padx=5)
        
        self.pickup_btn = ctk.CTkButton(
            action_frame,
            text="📦 Xác nhận lấy sách",
            command=self.confirm_pickup,
            fg_color="#17a2b8",
            hover_color="#138496",
            width=150,
            state="disabled"
        )
        self.pickup_btn.pack(side="left", padx=5)
        
        self.reject_btn = ctk.CTkButton(
            action_frame,
            text="❌ Từ chối",
            command=self.show_reject_dialog,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=100,
            state="disabled"
        )
        self.reject_btn.pack(side="left", padx=5)
        
        self.detail_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Chi tiết",
            command=self.view_detail,
            width=100,
            state="disabled"
        )
        self.detail_btn.pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Duyệt → Chờ lấy sách → Xác nhận lấy sách → Tạo phiếu mượn",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def load_requests(self):
        """Tải danh sách yêu cầu"""
        for item in self.request_tree.get_children():
            self.request_tree.delete(item)
        
        # Update pending count
        pending_count = get_pending_requests_count()
        if pending_count > 0:
            self.pending_label.configure(text=f"⏳ {pending_count} yêu cầu đang chờ duyệt")
        else:
            self.pending_label.configure(text="✅ Không có yêu cầu chờ duyệt")
            
        status_filter = self.status_var.get()
        status_map = {
            "Chờ duyệt": "CHO_DUYET",
            "Chờ lấy sách": "CHO_LAY_SACH",
            "Đã lấy": "DA_LAY",
            "Từ chối": "TU_CHOI",
            "Đã hủy": "DA_HUY"
        }
        
        # "Chờ xử lý" = CHO_DUYET hoặc CHO_LAY_SACH
        if status_filter == "Chờ xử lý":
            status = None
            search_term = self.search_entry.get().strip()
            requests = get_all_borrow_requests(status=None, search_term=search_term)
            # Lọc chỉ lấy CHO_DUYET và CHO_LAY_SACH
            requests = [r for r in requests if r['trang_thai'] in ['CHO_DUYET', 'CHO_LAY_SACH']]
        else:
            status = status_map.get(status_filter) if status_filter != "Tất cả" else None
            search_term = self.search_entry.get().strip()
            requests = get_all_borrow_requests(status=status, search_term=search_term)
        
        for req in requests:
            status_display = {
                'CHO_DUYET': '⏳ Chờ duyệt',
                'CHO_LAY_SACH': '📦 Chờ lấy sách',
                'DA_LAY': '✅ Đã lấy',
                'TU_CHOI': '❌ Từ chối',
                'DA_HUY': '🚫 Đã hủy'
            }
            
            ghi_chu = req['ghi_chu'] or ''
            if len(ghi_chu) > 30:
                ghi_chu = ghi_chu[:30] + '...'
            
            self.request_tree.insert("", "end", iid=req['ma_yeu_cau'], values=(
                req['ma_yeu_cau'],
                req['ten_doc_gia'],
                req['tieu_de'],
                req['ngay_yeu_cau'],
                f"{req['so_ngay_muon_de_xuat']} ngày",
                ghi_chu,
                status_display.get(req['trang_thai'], req['trang_thai'])
            ))
            
        self.selected_request = None
        self.approve_btn.configure(state="disabled")
        self.pickup_btn.configure(state="disabled")
        self.reject_btn.configure(state="disabled")
        self.detail_btn.configure(state="disabled")
            
    def on_request_select(self, event):
        """Xử lý khi chọn yêu cầu"""
        selection = self.request_tree.selection()
        if selection:
            self.selected_request = int(selection[0])
            item = self.request_tree.item(selection[0])
            trang_thai = item['values'][6]
            
            self.detail_btn.configure(state="normal")
            
            # Chỉ cho duyệt/từ chối nếu đang chờ duyệt
            if "Chờ duyệt" in str(trang_thai):
                self.approve_btn.configure(state="normal")
                self.reject_btn.configure(state="normal")
                self.pickup_btn.configure(state="disabled")
            # Chỉ cho xác nhận lấy sách nếu đang chờ lấy sách
            elif "Chờ lấy sách" in str(trang_thai):
                self.approve_btn.configure(state="disabled")
                self.reject_btn.configure(state="disabled")
                self.pickup_btn.configure(state="normal")
            else:
                self.approve_btn.configure(state="disabled")
                self.reject_btn.configure(state="disabled")
                self.pickup_btn.configure(state="disabled")
        else:
            self.selected_request = None
            self.approve_btn.configure(state="disabled")
            self.reject_btn.configure(state="disabled")
            self.pickup_btn.configure(state="disabled")
            self.detail_btn.configure(state="disabled")
    
    def on_double_click(self, event):
        """Xử lý double click"""
        region = self.request_tree.identify("region", event.x, event.y)
        if region == "cell":
            self.view_detail()
            
    def show_approve_dialog(self):
        """Hiện dialog duyệt yêu cầu"""
        if not self.selected_request:
            return
            
        # Lấy thông tin yêu cầu
        requests = get_all_borrow_requests()
        req = None
        for r in requests:
            if r['ma_yeu_cau'] == self.selected_request:
                req = r
                break
                
        if not req:
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Duyệt yêu cầu mượn sách")
        dialog.geometry("450x380")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Info
        ctk.CTkLabel(
            frame,
            text=f"📖 {req['tieu_de']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            frame,
            text=f"👤 Đọc giả: {req['ten_doc_gia']}",
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Số ngày đề xuất
        ctk.CTkLabel(
            frame,
            text=f"📅 Số ngày đọc giả đề xuất: {req['so_ngay_muon_de_xuat']} ngày",
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        # Ghi chú của đọc giả
        if req['ghi_chu']:
            ctk.CTkLabel(
                frame,
                text=f"📝 Ghi chú: {req['ghi_chu']}",
                anchor="w",
                wraplength=400
            ).pack(fill="x", pady=(0, 10))
        
        # Số ngày mượn chính thức
        ctk.CTkLabel(
            frame,
            text="Số ngày mượn chính thức: * (1-30 ngày)",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(15, 5))
        
        days_frame = ctk.CTkFrame(frame, fg_color="transparent")
        days_frame.pack(fill="x", pady=(0, 10))
        
        days_entry = ctk.CTkEntry(days_frame, width=100)
        days_entry.insert(0, str(req['so_ngay_muon_de_xuat']))  # Mặc định theo đề xuất
        days_entry.pack(side="left")
        
        ctk.CTkLabel(days_frame, text="ngày", text_color="gray").pack(side="left", padx=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        def approve():
            try:
                so_ngay = int(days_entry.get())
                if so_ngay <= 0 or so_ngay > 30:
                    messagebox.showwarning("Cảnh báo", "Số ngày mượn phải từ 1-30 ngày!")
                    return
            except:
                messagebox.showwarning("Cảnh báo", "Số ngày phải là số!")
                return
                
            try:
                approve_borrow_request(
                    ma_yeu_cau=self.selected_request,
                    ma_nd_xu_ly=self.user['ma_nd'],
                    so_ngay_muon=so_ngay
                )
                
                dialog.destroy()
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã duyệt yêu cầu!\n\n"
                    f"📖 {req['tieu_de']}\n"
                    f"👤 {req['ten_doc_gia']}\n"
                    f"📅 Số ngày mượn: {so_ngay} ngày\n\n"
                    f"Trạng thái: Chờ lấy sách\n"
                    f"Vui lòng xác nhận khi đọc giả đến lấy sách."
                )
                self.load_requests()
                
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        
        ctk.CTkButton(
            btn_frame, 
            text="Hủy", 
            command=dialog.destroy, 
            fg_color="gray",
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="✅ Duyệt", 
            command=approve,
            fg_color="#28a745",
            hover_color="#218838",
            width=100
        ).pack(side="right", padx=5)
    
    def confirm_pickup(self):
        """Xác nhận đọc giả đã lấy sách"""
        if not self.selected_request:
            return
            
        # Lấy thông tin yêu cầu
        requests = get_all_borrow_requests()
        req = None
        for r in requests:
            if r['ma_yeu_cau'] == self.selected_request:
                req = r
                break
                
        if not req:
            return
            
        if req['trang_thai'] != 'CHO_LAY_SACH':
            messagebox.showwarning("Cảnh báo", "Yêu cầu này chưa được duyệt hoặc đã lấy sách!")
            return
        
        # Xác nhận
        so_ngay = req.get('so_ngay_muon_chinh_thuc') or req['so_ngay_muon_de_xuat']
        
        if messagebox.askyesno(
            "Xác nhận lấy sách",
            f"Xác nhận đọc giả đã lấy sách?\n\n"
            f"📖 {req['tieu_de']}\n"
            f"👤 {req['ten_doc_gia']}\n"
            f"📅 Số ngày mượn: {so_ngay} ngày\n\n"
            f"Hệ thống sẽ tạo phiếu mượn và bắt đầu tính ngày."
        ):
            try:
                ma_phieu = confirm_book_pickup(
                    ma_yeu_cau=self.selected_request,
                    ma_nd_nhan_vien=self.user['ma_nd']
                )
                
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã xác nhận lấy sách và tạo phiếu mượn!\n\n"
                    f"Mã phiếu: #{ma_phieu}\n"
                    f"📖 {req['tieu_de']}\n"
                    f"👤 {req['ten_doc_gia']}\n"
                    f"📅 Số ngày mượn: {so_ngay} ngày"
                )
                self.load_requests()
                
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        
    def show_reject_dialog(self):
        """Hiện dialog từ chối yêu cầu"""
        if not self.selected_request:
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Từ chối yêu cầu")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text="Lý do từ chối (tùy chọn):",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        reason_textbox = ctk.CTkTextbox(frame, height=80)
        reason_textbox.pack(fill="x", pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        def reject():
            ly_do = reason_textbox.get("1.0", "end").strip()
            
            try:
                reject_borrow_request(
                    ma_yeu_cau=self.selected_request,
                    ma_nd_xu_ly=self.user['ma_nd'],
                    ly_do=ly_do if ly_do else None
                )
                
                dialog.destroy()
                messagebox.showinfo("Thành công", "Đã từ chối yêu cầu!")
                self.load_requests()
                
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
        
        ctk.CTkButton(
            btn_frame, 
            text="Hủy", 
            command=dialog.destroy, 
            fg_color="gray",
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="❌ Từ chối", 
            command=reject,
            fg_color="#dc3545",
            hover_color="#c82333",
            width=100
        ).pack(side="right", padx=5)
        
    def view_detail(self):
        """Xem chi tiết yêu cầu"""
        if not self.selected_request:
            return
            
        requests = get_all_borrow_requests()
        req = None
        for r in requests:
            if r['ma_yeu_cau'] == self.selected_request:
                req = r
                break
                
        if not req:
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết yêu cầu mượn")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=f"📖 {req['tieu_de']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=450
        ).pack(pady=(0, 15))
        
        status_display = {
            'CHO_DUYET': '⏳ Chờ duyệt',
            'CHO_LAY_SACH': '📦 Chờ lấy sách',
            'DA_LAY': '✅ Đã lấy',
            'TU_CHOI': '❌ Từ chối',
            'DA_HUY': '🚫 Đã hủy'
        }
        
        loai_sach = "🌐 Online" if req['loai_sach'] == 'SACH_ONLINE' else "📚 Giấy"
        
        # Thêm số ngày mượn chính thức nếu có
        so_ngay_chinh_thuc = req.get('so_ngay_muon_chinh_thuc')
        
        info_data = [
            ("Mã yêu cầu:", req['ma_yeu_cau']),
            ("", ""),  # Separator
            ("--- THÔNG TIN ĐỌC GIẢ ---", ""),
            ("Họ tên:", req['ten_doc_gia']),
            ("Mã đọc giả:", req['ma_doc_gia']),
            ("SĐT:", req['so_dt'] or 'N/A'),
            ("Email:", req['email'] or 'N/A'),
            ("", ""),
            ("--- THÔNG TIN SÁCH ---", ""),
            ("Tên sách:", req['tieu_de']),
            ("Tác giả:", req['tac_gia'] or 'N/A'),
            ("Thể loại:", req['ten_the_loai'] or 'N/A'),
            ("Loại sách:", loai_sach),
            ("", ""),
            ("--- THÔNG TIN YÊU CẦU ---", ""),
            ("Ngày yêu cầu:", req['ngay_yeu_cau']),
            ("Số ngày đề xuất:", f"{req['so_ngay_muon_de_xuat']} ngày"),
            ("Số ngày chính thức:", f"{so_ngay_chinh_thuc} ngày" if so_ngay_chinh_thuc else '-'),
            ("Trạng thái:", status_display.get(req['trang_thai'], req['trang_thai'])),
            ("Người xử lý:", req['nguoi_xu_ly'] or '-'),
            ("Ngày xử lý:", req['ngay_xu_ly'] or '-'),
        ]
        
        for label, value in info_data:
            if label.startswith("---"):
                ctk.CTkLabel(
                    frame, text=label, 
                    font=ctk.CTkFont(weight="bold"),
                    text_color="gray"
                ).pack(fill="x", pady=(10, 5))
            elif label == "":
                continue
            else:
                row = ctk.CTkFrame(frame, fg_color="transparent")
                row.pack(fill="x", pady=2)
                
                ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=120, anchor="e").pack(side="left")
                ctk.CTkLabel(row, text=str(value), anchor="w", wraplength=300).pack(side="left", padx=10)
        
        # Ghi chú
        if req['ghi_chu']:
            ctk.CTkLabel(frame, text="Ghi chú:", font=ctk.CTkFont(weight="bold"), anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(frame, text=req['ghi_chu'], wraplength=450, anchor="w").pack(fill="x")
        
        # Lý do từ chối
        if req['trang_thai'] == 'TU_CHOI' and req.get('ly_do_tu_choi'):
            ctk.CTkLabel(frame, text="Lý do từ chối:", font=ctk.CTkFont(weight="bold"), 
                        text_color="#dc3545", anchor="w").pack(fill="x", pady=(15, 5))
            ctk.CTkLabel(frame, text=req['ly_do_tu_choi'], wraplength=450, 
                        text_color="#dc3545", anchor="w").pack(fill="x")
        
        # Buttons frame - cố định ở cuối dialog
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(btn_frame, text="Đóng", command=dialog.destroy, fg_color="gray", width=100).pack(side="left")
        
        # Nếu đang chờ duyệt, hiện thêm nút duyệt và từ chối
        if req['trang_thai'] == 'CHO_DUYET':
            def approve_from_detail():
                dialog.destroy()
                self.selected_request = req['ma_yeu_cau']
                self.show_approve_dialog()
            
            def reject_from_detail():
                dialog.destroy()
                self.selected_request = req['ma_yeu_cau']
                self.show_reject_dialog()
            
            ctk.CTkButton(
                btn_frame, 
                text="❌ Từ chối", 
                command=reject_from_detail,
                fg_color="#dc3545",
                hover_color="#c82333",
                width=100
            ).pack(side="right", padx=5)
            
            ctk.CTkButton(
                btn_frame, 
                text="✅ Duyệt yêu cầu", 
                command=approve_from_detail,
                fg_color="#28a745",
                hover_color="#218838",
                width=120
            ).pack(side="right", padx=5)
        
        # Nếu đang chờ lấy sách, hiện nút xác nhận lấy sách
        elif req['trang_thai'] == 'CHO_LAY_SACH':
            def pickup_from_detail():
                dialog.destroy()
                self.selected_request = req['ma_yeu_cau']
                self.confirm_pickup()
            
            ctk.CTkButton(
                btn_frame, 
                text="📦 Xác nhận lấy sách", 
                command=pickup_from_detail,
                fg_color="#17a2b8",
                hover_color="#138496",
                width=150
            ).pack(side="right", padx=5)
