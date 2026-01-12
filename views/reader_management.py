"""
Reader Management - Quản lý đọc giả
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_readers, get_reader_by_id, add_reader, 
                      update_reader, delete_reader, update_reader_card,
                      get_reader_borrow_history, count_readers)
from utils.report_generator import generate_reader_card
from utils import treeview_sort_column, PaginationFrame, center_window


class ReaderManagement(ctk.CTkFrame):
    """Giao diện quản lý đọc giả"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_reader = None
        
        self.create_widgets()
        self.load_readers()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="👥 Quản lý Đọc giả",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Add button
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Thêm đọc giả",
            command=self.show_add_dialog,
            width=130
        )
        add_btn.pack(side="right")
        
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Tìm kiếm theo tên, mã đọc giả, SĐT...",
            width=350
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_readers())
        
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="🔄",
            command=self.load_readers,
            width=40
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ma_doc_gia", "ho_ten", "so_dt", "email", "ngay_dk", "trang_thai_the")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Column headings with sorting
        headings = {
            "ma_doc_gia": "Mã đọc giả",
            "ho_ten": "Họ tên",
            "so_dt": "Số điện thoại",
            "email": "Email",
            "ngay_dk": "Ngày đăng ký",
            "trang_thai_the": "Trạng thái thẻ"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, 
                            command=lambda c=col: treeview_sort_column(self.tree, c, False))
        
        # Column widths
        self.tree.column("ma_doc_gia", width=100, anchor="center")
        self.tree.column("ho_ten", width=180)
        self.tree.column("so_dt", width=120, anchor="center")
        self.tree.column("email", width=200)
        self.tree.column("ngay_dk", width=110, anchor="center")
        self.tree.column("trang_thai_the", width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Action buttons
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=20, pady=10)
        
        self.edit_btn = ctk.CTkButton(
            action_frame,
            text="✏️ Sửa",
            command=self.show_edit_dialog,
            width=100,
            state="disabled"
        )
        self.edit_btn.pack(side="left", padx=5)
        
        self.delete_btn = ctk.CTkButton(
            action_frame,
            text="🗑️ Xóa",
            command=self.delete_selected,
            width=100,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.delete_btn.pack(side="left", padx=5)
        
        self.card_btn = ctk.CTkButton(
            action_frame,
            text="🪪 Cập nhật thẻ",
            command=self.show_card_dialog,
            width=130,
            state="disabled"
        )
        self.card_btn.pack(side="left", padx=5)
        
        self.history_btn = ctk.CTkButton(
            action_frame,
            text="📜 Lịch sử mượn",
            command=self.show_history_dialog,
            width=130,
            state="disabled"
        )
        self.history_btn.pack(side="left", padx=5)
        
        self.print_card_btn = ctk.CTkButton(
            action_frame,
            text="🖨️ In thẻ",
            command=self.print_reader_card,
            width=100,
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"
        )
        self.print_card_btn.pack(side="left", padx=5)
        
        # Pagination frame
        self.pagination = PaginationFrame(
            self,
            total_items=0,
            items_per_page=20,
            on_page_change=self.on_page_change
        )
        self.pagination.pack(fill="x", padx=20, pady=(0, 10))
        
    def on_page_change(self, page, per_page):
        """Điều hướng khi chuyển trang"""
        self.load_readers_page()
        
    def load_readers(self):
        """Đặt lại và tải danh sách đọc giả"""
        self.search_entry.delete(0, 'end')
        
        # Reset pagination
        total = count_readers()
        self.pagination.set_total(total)
        self.pagination.current_page = 1
        self.pagination.update_display()
        
        self.load_readers_page()
    
    def load_readers_page(self):
        """Tải dữ liệu cho trang hiện tại"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        readers = get_all_readers(
            limit=self.pagination.get_limit(),
            offset=self.pagination.get_offset()
        )
        
        self._populate_tree(readers)
    
    def _populate_tree(self, readers):
        """Điền dữ liệu vào tree"""
        for reader in readers:
            trang_thai_map = {
                'HOAT_DONG': '✅ Hoạt động',
                'HET_HAN': '⚠️ Hết hạn',
                'KHOA': '🔒 Khóa'
            }
            trang_thai = trang_thai_map.get(reader['trang_thai_the'], reader['trang_thai_the'] or 'N/A')
            
            self.tree.insert("", "end", iid=reader['ma_nd'], values=(
                reader['ma_doc_gia'],
                reader['ho_ten'],
                reader['so_dt'] or "N/A",
                reader['email'] or "N/A",
                reader['ngay_dk'],
                trang_thai
            ))
            
    def search_readers(self):
        """Tìm kiếm đọc giả"""
        search_term = self.search_entry.get()
        
        # Update pagination total
        total = count_readers(search_term)
        self.pagination.set_total(total)
        self.pagination.current_page = 1
        self.pagination.update_display()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        readers = get_all_readers(
            search_term,
            limit=self.pagination.get_limit(),
            offset=self.pagination.get_offset()
        )
        
        self._populate_tree(readers)
            
    def on_select(self, event):
        """Xử lý khi chọn item"""
        selection = self.tree.selection()
        if selection:
            self.selected_reader = int(selection[0])  # iid là ma_nd
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            self.card_btn.configure(state="normal")
            self.history_btn.configure(state="normal")
            self.print_card_btn.configure(state="normal")
        else:
            self.selected_reader = None
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.card_btn.configure(state="disabled")
            self.history_btn.configure(state="disabled")
            self.print_card_btn.configure(state="disabled")    
    def on_double_click(self, event):
        """Xử lý double-click - chỉ mở dialog nếu click vào dòng dữ liệu"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_edit_dialog()            
    def show_add_dialog(self):
        """Hiện dialog thêm đọc giả"""
        dialog = ReaderDialog(self, "Thêm đọc giả mới")
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                add_reader(**dialog.result)
                messagebox.showinfo("Thành công", "Thêm đọc giả thành công!\nTài khoản mặc định: mã đọc giả/mã đọc giả")
                self.load_readers()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
                
    def show_edit_dialog(self):
        """Hiện dialog sửa đọc giả"""
        if not self.selected_reader:
            return
            
        reader = get_reader_by_id(self.selected_reader)
        if not reader:
            messagebox.showerror("Lỗi", "Không tìm thấy đọc giả!")
            return
            
        dialog = ReaderDialog(self, "Sửa thông tin đọc giả", reader)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                update_reader(self.selected_reader, **dialog.result)
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.load_readers()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
                
    def delete_selected(self):
        """Xóa đọc giả đã chọn"""
        if not self.selected_reader:
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa đọc giả này?\nMọi dữ liệu liên quan sẽ bị xóa!"):
            try:
                delete_reader(self.selected_reader)
                messagebox.showinfo("Thành công", "Xóa đọc giả thành công!")
                self.load_readers()
                self.selected_reader = None
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {str(e)}")
                
    def show_card_dialog(self):
        """Hiện dialog cập nhật thẻ"""
        if not self.selected_reader:
            return
            
        reader = get_reader_by_id(self.selected_reader)
        if not reader:
            messagebox.showerror("Lỗi", "Không tìm thấy đọc giả!")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cập nhật thẻ đọc giả")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 400, 300)
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Thông tin hiện tại
        ctk.CTkLabel(frame, text=f"Đọc giả: {reader['ho_ten']}", 
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w")
        ctk.CTkLabel(frame, text=f"Mã thẻ: {reader['ma_the'] or 'N/A'}").pack(anchor="w")
        ctk.CTkLabel(frame, text=f"Ngày hết hạn: {reader['ngay_het_han'] or 'N/A'}").pack(anchor="w", pady=(0, 15))
        
        # Trạng thái
        ctk.CTkLabel(frame, text="Trạng thái thẻ:").pack(anchor="w", pady=(0, 5))
        status_var = ctk.StringVar(value=reader['trang_thai_the'] or 'HOAT_DONG')
        status_combo = ctk.CTkComboBox(
            frame,
            values=['HOAT_DONG', 'HET_HAN', 'KHOA'],
            variable=status_var
        )
        status_combo.pack(fill="x", pady=(0, 10))
        
        # Gia hạn
        ctk.CTkLabel(frame, text="Gia hạn thêm (ngày):").pack(anchor="w", pady=(0, 5))
        extend_entry = ctk.CTkEntry(frame)
        extend_entry.insert(0, "0")
        extend_entry.pack(fill="x", pady=(0, 15))
        
        def save():
            try:
                extend_days = int(extend_entry.get())
                if extend_days < 0:
                    messagebox.showwarning("Cảnh báo", "Số ngày gia hạn không được âm!")
                    return
            except ValueError:
                messagebox.showwarning("Cảnh báo", "Số ngày phải là số nguyên!")
                return
            
            update_reader_card(self.selected_reader, status_var.get(), extend_days)
            messagebox.showinfo("Thành công", "Cập nhật thẻ thành công!")
            self.load_readers()
            dialog.destroy()
            
        ctk.CTkButton(frame, text="Lưu", command=save).pack(pady=10)
        
    def show_history_dialog(self):
        """Hiện dialog lịch sử mượn"""
        if not self.selected_reader:
            return
            
        reader = get_reader_by_id(self.selected_reader)
        history = get_reader_borrow_history(self.selected_reader)
        
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Lịch sử mượn sách - {reader['ho_ten']}")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 700, 400)
        
        frame = ctk.CTkFrame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Treeview
        columns = ("ma_phieu", "tieu_de", "ngay_muon", "ngay_hen_tra", "ngay_tra_thuc", "trang_thai")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        
        tree.heading("ma_phieu", text="Mã phiếu")
        tree.heading("tieu_de", text="Tên sách")
        tree.heading("ngay_muon", text="Ngày mượn")
        tree.heading("ngay_hen_tra", text="Hạn trả")
        tree.heading("ngay_tra_thuc", text="Ngày trả")
        tree.heading("trang_thai", text="Trạng thái")
        
        tree.column("ma_phieu", width=70, anchor="center")
        tree.column("tieu_de", width=200)
        tree.column("ngay_muon", width=100, anchor="center")
        tree.column("ngay_hen_tra", width=100, anchor="center")
        tree.column("ngay_tra_thuc", width=100, anchor="center")
        tree.column("trang_thai", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for item in history:
            trang_thai_map = {
                'DANG_MUON': '📖 Đang mượn',
                'DA_TRA': '✅ Đã trả',
                'QUA_HAN': '⚠️ Quá hạn'
            }
            
            tree.insert("", "end", values=(
                item['ma_phieu'],
                item['tieu_de'],
                item['ngay_muon'],
                item['ngay_hen_tra'],
                item['ngay_tra_thuc'] or "Chưa trả",
                trang_thai_map.get(item['trang_thai_phieu'], item['trang_thai_phieu'])
            ))
            
        ctk.CTkButton(dialog, text="Đóng", command=dialog.destroy).pack(pady=10)
        
    def print_reader_card(self):
        """In thẻ đọc giả"""
        if not self.selected_reader:
            return
            
        reader = get_reader_by_id(self.selected_reader)
        if not reader:
            messagebox.showerror("Lỗi", "Không tìm thấy đọc giả!")
            return
            
        try:
            output_path = generate_reader_card(reader)
            messagebox.showinfo("Thành công", f"Đã tạo thẻ đọc giả:\n{output_path}")
            os.startfile(output_path)  # Mở file trên Windows
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo thẻ: {str(e)}")


class ReaderDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa đọc giả"""
    
    def __init__(self, parent, title: str, reader: dict = None):
        super().__init__(parent)
        
        self.title(title)
        self.transient(parent)
        self.grab_set()
        center_window(self, 400, 400)
        
        self.reader = reader
        self.result = None
        
        self.create_widgets()
        
        if reader:
            self.populate_fields()
            
    def create_widgets(self):
        """Tạo các widget"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Mã đọc giả (chỉ khi thêm mới)
        if not self.reader:
            ctk.CTkLabel(frame, text="Mã đọc giả: *", anchor="w").pack(fill="x", pady=(0, 5))
            self.code_entry = ctk.CTkEntry(frame, placeholder_text="VD: DG002")
            self.code_entry.pack(fill="x", pady=(0, 10))
        
        # Họ tên
        ctk.CTkLabel(frame, text="Họ tên: *", anchor="w").pack(fill="x", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(frame)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Địa chỉ
        ctk.CTkLabel(frame, text="Địa chỉ:", anchor="w").pack(fill="x", pady=(0, 5))
        self.address_entry = ctk.CTkEntry(frame)
        self.address_entry.pack(fill="x", pady=(0, 10))
        
        # Số điện thoại
        ctk.CTkLabel(frame, text="Số điện thoại:", anchor="w").pack(fill="x", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(frame)
        self.phone_entry.pack(fill="x", pady=(0, 10))
        
        # Email
        ctk.CTkLabel(frame, text="Email:", anchor="w").pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(frame)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(btn_frame, text="Hủy", command=self.destroy, 
                     fg_color="gray", width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Lưu", command=self.save, width=100).pack(side="right", padx=5)
        
    def populate_fields(self):
        """Điền dữ liệu khi sửa"""
        self.name_entry.insert(0, self.reader['ho_ten'])
        self.address_entry.insert(0, self.reader['dia_chi'] or "")
        self.phone_entry.insert(0, self.reader['so_dt'] or "")
        self.email_entry.insert(0, self.reader['email'] or "")
        
    def save(self):
        """Lưu thông tin"""
        import re
        
        ho_ten = self.name_entry.get().strip()
        so_dt = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        
        if not ho_ten:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập họ tên!")
            return
        
        # Validate số điện thoại (10-11 số)
        if so_dt:
            if not re.match(r'^\d{10,11}$', so_dt):
                messagebox.showwarning("Cảnh báo", "Số điện thoại phải có 10-11 chữ số!")
                return
        
        # Validate email
        if email:
            if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
                messagebox.showwarning("Cảnh báo", "Email không hợp lệ!")
                return
        
        if self.reader:
            # Update
            self.result = {
                'ho_ten': ho_ten,
                'dia_chi': self.address_entry.get().strip() or None,
                'so_dt': so_dt or None,
                'email': email or None
            }
        else:
            # Add new
            ma_doc_gia = self.code_entry.get().strip()
            if not ma_doc_gia:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập mã đọc giả!")
                return
                
            self.result = {
                'ho_ten': ho_ten,
                'dia_chi': self.address_entry.get().strip() or None,
                'so_dt': so_dt or None,
                'email': email or None,
                'ma_doc_gia': ma_doc_gia.upper()
            }
            
        self.destroy()
