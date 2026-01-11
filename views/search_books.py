"""
Search Books - Tìm và mượn sách (dành cho đọc giả)
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_reader_by_id, get_all_books, create_borrow_request, 
                      get_book_by_id, get_all_categories)
from utils import treeview_sort_column


class SearchBooks(ctk.CTkFrame):
    """Giao diện tìm và mượn sách cho đọc giả"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_book = None
        
        self.create_widgets()
        self.load_books()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="🔍 Tìm và Mượn sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Tìm kiếm sách theo tên, tác giả...",
            width=250
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_books())
        
        # Category filter
        ctk.CTkLabel(search_frame, text="Thể loại:").pack(side="left", padx=(15, 5))
        
        self.categories = get_all_categories()
        category_names = ["Tất cả"] + [c['ten_the_loai'] for c in self.categories]
        
        self.category_var = ctk.StringVar(value="Tất cả")
        self.category_combo = ctk.CTkComboBox(
            search_frame,
            values=category_names,
            variable=self.category_var,
            command=lambda e: self.filter_books(),
            width=120
        )
        self.category_combo.pack(side="left")
        
        # Book type filter
        ctk.CTkLabel(search_frame, text="Loại:").pack(side="left", padx=(15, 5))
        
        self.book_type_var = ctk.StringVar(value="Tất cả")
        self.book_type_combo = ctk.CTkComboBox(
            search_frame,
            values=["Tất cả", "Sách giấy", "Sách online"],
            variable=self.book_type_var,
            command=lambda e: self.filter_books(),
            width=110
        )
        self.book_type_combo.pack(side="left")
        
        # Status filter
        ctk.CTkLabel(search_frame, text="Trạng thái:").pack(side="left", padx=(15, 5))
        
        self.status_var = ctk.StringVar(value="Tất cả")
        self.status_combo = ctk.CTkComboBox(
            search_frame,
            values=["Tất cả", "Có sẵn", "Hết sách"],
            variable=self.status_var,
            command=lambda e: self.filter_books(),
            width=100
        )
        self.status_combo.pack(side="left")
        
        # Refresh button
        ctk.CTkButton(
            search_frame,
            text="🔄",
            command=self.reset_filters,
            width=40
        ).pack(side="left", padx=10)
        
        # Book list
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        columns = ("ma_sach", "tieu_de", "tac_gia", "the_loai", "loai_sach", "trang_thai")
        self.book_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Headings with sorting
        headings = {
            "ma_sach": "Mã sách",
            "tieu_de": "Tên sách",
            "tac_gia": "Tác giả",
            "the_loai": "Thể loại",
            "loai_sach": "Loại sách",
            "trang_thai": "Trạng thái"
        }
        for col, text in headings.items():
            self.book_tree.heading(col, text=text, 
                            command=lambda t=self.book_tree, c=col: treeview_sort_column(t, c, False))
        
        self.book_tree.column("ma_sach", width=80, anchor="center")
        self.book_tree.column("tieu_de", width=250)
        self.book_tree.column("tac_gia", width=150)
        self.book_tree.column("the_loai", width=120)
        self.book_tree.column("loai_sach", width=100, anchor="center")
        self.book_tree.column("trang_thai", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        
        self.book_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
        
        # Action frame
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.borrow_btn = ctk.CTkButton(
            action_frame,
            text="� Gửi yêu cầu mượn",
            command=self.request_borrow_book,
            width=160,
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"
        )
        self.borrow_btn.pack(side="left", padx=5)
        
        self.view_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Xem chi tiết",
            command=self.view_book_detail,
            width=120,
            state="disabled"
        )
        self.view_btn.pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Chọn sách → Gửi yêu cầu mượn → Nhân viên sẽ xác nhận yêu cầu của bạn.",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def load_books(self):
        """Tải danh sách sách"""
        self.filter_books()
    
    def reset_filters(self):
        """Reset bộ lọc"""
        self.search_entry.delete(0, 'end')
        self.category_var.set("Tất cả")
        self.book_type_var.set("Tất cả")
        self.status_var.set("Tất cả")
        self.filter_books()
            
    def filter_books(self):
        """Lọc sách theo các tiêu chí"""
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
            
        books = get_all_books()
        
        search_term = self.search_entry.get().lower()
        category_filter = self.category_var.get()
        book_type_filter = self.book_type_var.get()
        status_filter = self.status_var.get()
        
        for book in books:
            # Lọc theo từ khóa
            if search_term:
                if (search_term not in book['tieu_de'].lower() and 
                    search_term not in (book['tac_gia'] or '').lower() and
                    search_term not in (book['ten_the_loai'] or '').lower()):
                    continue
            
            # Lọc theo thể loại
            if category_filter != "Tất cả":
                if book['ten_the_loai'] != category_filter:
                    continue
            
            # Lọc theo loại sách
            if book_type_filter == "Sách giấy" and book['loai_sach'] != 'SACH_GIAY':
                continue
            elif book_type_filter == "Sách online" and book['loai_sach'] != 'SACH_ONLINE':
                continue
            
            # Xác định trạng thái
            if book['so_luong'] > 0:
                trang_thai = "✅ Có sẵn"
                trang_thai_check = "Có sẵn"
            else:
                trang_thai = "❌ Hết sách"
                trang_thai_check = "Hết sách"
            
            # Lọc theo trạng thái
            if status_filter != "Tất cả" and status_filter != trang_thai_check:
                continue
            
            loai_sach = "🌐 Online" if book['loai_sach'] == 'SACH_ONLINE' else "📚 Giấy"
            
            self.book_tree.insert("", "end", iid=book['ma_sach'], values=(
                book['ma_sach'],
                book['tieu_de'],
                book['tac_gia'] or 'N/A',
                book['ten_the_loai'] or 'N/A',
                loai_sach,
                trang_thai
            ))
            
    def on_book_select(self, event):
        """Xử lý khi chọn sách"""
        selection = self.book_tree.selection()
        if selection:
            self.selected_book = int(selection[0])
            item = self.book_tree.item(selection[0])
            trang_thai = item['values'][5]
            
            self.view_btn.configure(state="normal")
            
            # Chỉ cho mượn nếu còn sách
            if "Có sẵn" in str(trang_thai):
                self.borrow_btn.configure(state="normal")
            else:
                self.borrow_btn.configure(state="disabled")
        else:
            self.selected_book = None
            self.borrow_btn.configure(state="disabled")
            self.view_btn.configure(state="disabled")
            
    def view_book_detail(self):
        """Xem chi tiết sách"""
        if not self.selected_book:
            return
            
        book = get_book_by_id(self.selected_book)
        if not book:
            return
            
        # Hiển thị dialog chi tiết
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết sách")
        dialog.geometry("450x400")
        dialog.transient(self)
        dialog.grab_set()
        
        # Content
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            frame,
            text=book['tieu_de'],
            font=ctk.CTkFont(size=18, weight="bold"),
            wraplength=400
        ).pack(pady=(0, 20))
        
        info_data = [
            ("Mã sách:", book['ma_sach']),
            ("Tác giả:", book['tac_gia'] or 'N/A'),
            ("Thể loại:", book['ten_the_loai'] or 'N/A'),
            ("NXB:", book['nxb'] or 'N/A'),
            ("Năm XB:", book['nam_xb'] or 'N/A'),
            ("Loại sách:", "Online" if book['loai_sach'] == 'SACH_ONLINE' else "Giấy"),
            ("Số lượng:", book['so_luong']),
        ]
        
        for label, value in info_data:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left", padx=10)
        
        ctk.CTkButton(dialog, text="Đóng", command=dialog.destroy, width=100).pack(pady=10)
            
    def request_borrow_book(self):
        """Gửi yêu cầu mượn sách"""
        if not self.selected_book:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách!")
            return
            
        book = get_book_by_id(self.selected_book)
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin sách!")
            return
            
        item = self.book_tree.item(self.book_tree.selection()[0])
        trang_thai = item['values'][5]
        
        # Kiểm tra sách có sẵn không
        if "Có sẵn" not in str(trang_thai):
            messagebox.showwarning("Cảnh báo", "Sách này hiện không có sẵn để mượn!")
            return
        
        # Kiểm tra thẻ đọc giả
        reader = get_reader_by_id(self.user['ma_nd'])
        if not reader:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin đọc giả!")
            return
            
        if reader.get('trang_thai_the') != 'HOAT_DONG':
            messagebox.showwarning("Cảnh báo", "Thẻ đọc giả của bạn không hoạt động!\nVui lòng liên hệ thư viện để gia hạn.")
            return
        
        # Hiện dialog nhập số ngày mượn
        self.show_borrow_request_dialog(book)
    
    def show_borrow_request_dialog(self, book):
        """Hiện dialog yêu cầu mượn sách"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Yêu cầu mượn sách")
        dialog.geometry("450x420")
        dialog.transient(self)
        dialog.grab_set()
        
        # Main container
        main_container = ctk.CTkFrame(dialog, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        # Content frame - scrollable
        frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        
        # Book info
        ctk.CTkLabel(
            frame,
            text="📖 " + book['tieu_de'],
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=400
        ).pack(pady=(0, 5))
        
        ctk.CTkLabel(
            frame,
            text=f"Tác giả: {book['tac_gia'] or 'N/A'}",
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # Số ngày muốn mượn
        ctk.CTkLabel(
            frame,
            text="Số ngày muốn mượn: * (tối đa 30 ngày)",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        days_frame = ctk.CTkFrame(frame, fg_color="transparent")
        days_frame.pack(fill="x", pady=(0, 15))
        
        days_entry = ctk.CTkEntry(days_frame, width=100, placeholder_text="1-30")
        days_entry.insert(0, "14")
        days_entry.pack(side="left")
        
        ctk.CTkLabel(days_frame, text="ngày", text_color="gray").pack(side="left", padx=10)
        
        # Ghi chú
        ctk.CTkLabel(
            frame,
            text="Ghi chú (tùy chọn):",
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        note_textbox = ctk.CTkTextbox(frame, height=80)
        note_textbox.pack(fill="x", pady=(0, 10))
        
        # Thông tin
        info_label = ctk.CTkLabel(
            frame,
            text="💡 Nhân viên thư viện sẽ xác nhận yêu cầu và quyết định\nsố ngày mượn chính thức (có thể khác với đề xuất).",
            text_color="gray",
            justify="left"
        )
        info_label.pack(fill="x", pady=10)
        
        # Buttons - nằm ngoài scrollable frame, cố định ở cuối
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        def submit_request():
            try:
                so_ngay = int(days_entry.get())
                if so_ngay <= 0 or so_ngay > 30:
                    messagebox.showwarning("Cảnh báo", "Số ngày mượn phải từ 1-30 ngày!")
                    return
            except:
                messagebox.showwarning("Cảnh báo", "Số ngày phải là số!")
                return
            
            ghi_chu = note_textbox.get("1.0", "end").strip()
            
            try:
                ma_yeu_cau = create_borrow_request(
                    ma_nd_doc_gia=self.user['ma_nd'],
                    ma_sach=book['ma_sach'],
                    so_ngay_muon_de_xuat=so_ngay,
                    ghi_chu=ghi_chu if ghi_chu else None
                )
                
                dialog.destroy()
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã gửi yêu cầu mượn sách thành công!\n\n"
                    f"📖 {book['tieu_de']}\n"
                    f"📅 Số ngày đề xuất: {so_ngay} ngày\n\n"
                    f"Vui lòng chờ nhân viên thư viện xác nhận."
                )
                
                self.load_books()
                
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
            text="📝 Gửi yêu cầu", 
            command=submit_request,
            fg_color="#28a745",
            hover_color="#218838",
            width=120
        ).pack(side="right", padx=5)
