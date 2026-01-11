"""
Book Management - Quản lý sách
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_books, get_book_by_id, add_book, update_book, 
                      delete_book, get_all_categories, add_category)
from utils import treeview_sort_column


class BookManagement(ctk.CTkFrame):
    """Giao diện quản lý sách"""
    
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
            text="📖 Quản lý Sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Add button
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Thêm sách",
            command=self.show_add_dialog,
            width=120
        )
        add_btn.pack(side="right")
        
        # Add category button
        add_cat_btn = ctk.CTkButton(
            header_frame,
            text="📁 Thêm thể loại",
            command=self.show_add_category_dialog,
            width=120,
            fg_color="#6c757d",
            hover_color="#5a6268"
        )
        add_cat_btn.pack(side="right", padx=10)
        
        # Search frame
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Tìm kiếm theo tên sách, tác giả...",
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
            values=["Tất cả", "Có sẵn", "Hết sách", "Hỏng", "Mất"],
            variable=self.status_var,
            command=lambda e: self.filter_books(),
            width=100
        )
        self.status_combo.pack(side="left")
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="🔄",
            command=self.load_books,
            width=40
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ma_sach", "tieu_de", "tac_gia", "the_loai", "loai_sach", "so_luong", "trang_thai")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        # Column headings with sort
        headings = {
            "ma_sach": "Mã sách",
            "tieu_de": "Tiêu đề",
            "tac_gia": "Tác giả",
            "the_loai": "Thể loại",
            "loai_sach": "Loại sách",
            "so_luong": "Số lượng",
            "trang_thai": "Trạng thái"
        }
        for col in columns:
            self.tree.heading(col, text=headings.get(col, col), 
                            command=lambda c=col: treeview_sort_column(self.tree, c, False))
        
        # Column widths
        self.tree.column("ma_sach", width=70, anchor="center")
        self.tree.column("tieu_de", width=200)
        self.tree.column("tac_gia", width=150)
        self.tree.column("the_loai", width=120)
        self.tree.column("loai_sach", width=100, anchor="center")
        self.tree.column("so_luong", width=80, anchor="center")
        self.tree.column("trang_thai", width=100, anchor="center")
        
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
        
        self.view_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Xem chi tiết",
            command=self.show_detail_dialog,
            width=120,
            state="disabled"
        )
        self.view_btn.pack(side="left", padx=5)
        
    def load_books(self):
        """Tải danh sách sách"""
        # Reset filters
        self.search_entry.delete(0, 'end')
        self.category_var.set("Tất cả")
        self.book_type_var.set("Tất cả")
        self.status_var.set("Tất cả")
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        books = get_all_books()
        
        for book in books:
            loai_sach = "Sách giấy" if book['loai_sach'] == 'SACH_GIAY' else "Sách online"
            
            # Xác định trạng thái hiển thị
            if book['trang_thai_sach'] == 'HONG':
                trang_thai = 'Hỏng'
            elif book['trang_thai_sach'] == 'MAT':
                trang_thai = 'Mất'
            elif book['loai_sach'] == 'SACH_GIAY' and book['so_luong'] <= 0:
                trang_thai = 'Hết sách'
            elif book['trang_thai_sach'] == 'DA_MUON':
                trang_thai = 'Hết sách'
            else:
                trang_thai = 'Có sẵn'
            
            self.tree.insert("", "end", values=(
                book['ma_sach'],
                book['tieu_de'],
                book['tac_gia'] or "N/A",
                book['ten_the_loai'] or "N/A",
                loai_sach,
                book['so_luong'] if book['loai_sach'] == 'SACH_GIAY' else "∞",
                trang_thai
            ))
            
    def search_books(self):
        """Tìm kiếm sách - gọi filter_books"""
        self.filter_books()
        
    def filter_books(self):
        """Lọc sách theo nhiều tiêu chí"""
        search_term = self.search_entry.get()
        category_name = self.category_var.get()
        book_type = self.book_type_var.get()
        status = self.status_var.get()
        
        # Lấy category_id
        category_id = None
        if category_name != "Tất cả":
            for cat in self.categories:
                if cat['ten_the_loai'] == category_name:
                    category_id = cat['ma_the_loai']
                    break
        
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        books = get_all_books(search_term, category_id)
        
        for book in books:
            # Lọc theo loại sách
            if book_type == "Sách giấy" and book['loai_sach'] != 'SACH_GIAY':
                continue
            if book_type == "Sách online" and book['loai_sach'] != 'SACH_ONLINE':
                continue
            
            # Lọc theo trạng thái
            if status == "Có sẵn":
                if book['trang_thai_sach'] != 'CO_SAN':
                    continue
                if book['loai_sach'] == 'SACH_GIAY' and book['so_luong'] <= 0:
                    continue
            elif status == "Hết sách":
                if book['loai_sach'] == 'SACH_GIAY':
                    if book['so_luong'] > 0 and book['trang_thai_sach'] == 'CO_SAN':
                        continue
                else:
                    continue  # Sách online không hết
            elif status == "Hỏng" and book['trang_thai_sach'] != 'HONG':
                continue
            elif status == "Mất" and book['trang_thai_sach'] != 'MAT':
                continue
            
            loai_sach = "Sách giấy" if book['loai_sach'] == 'SACH_GIAY' else "Sách online"
            
            # Xác định trạng thái hiển thị
            if book['trang_thai_sach'] == 'HONG':
                trang_thai = 'Hỏng'
            elif book['trang_thai_sach'] == 'MAT':
                trang_thai = 'Mất'
            elif book['loai_sach'] == 'SACH_GIAY' and book['so_luong'] <= 0:
                trang_thai = 'Hết sách'
            elif book['trang_thai_sach'] == 'DA_MUON':
                trang_thai = 'Hết sách'
            else:
                trang_thai = 'Có sẵn'
            
            self.tree.insert("", "end", values=(
                book['ma_sach'],
                book['tieu_de'],
                book['tac_gia'] or "N/A",
                book['ten_the_loai'] or "N/A",
                loai_sach,
                book['so_luong'] if book['loai_sach'] == 'SACH_GIAY' else "∞",
                trang_thai
            ))
            
    def on_select(self, event):
        """Xử lý khi chọn item"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_book = item['values'][0]  # ma_sach
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
            self.view_btn.configure(state="normal")
        else:
            self.selected_book = None
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")
            self.view_btn.configure(state="disabled")    
    def on_double_click(self, event):
        """Xử lý double-click - chỉ mở dialog nếu click vào dòng dữ liệu"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_edit_dialog()            
    def show_add_dialog(self):
        """Hiện dialog thêm sách"""
        dialog = BookDialog(self, "Thêm sách mới", self.categories)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                # dialog.result là list các sách cần thêm (có thể là 1 hoặc 2 sách)
                added_count = 0
                added_types = []
                for book_data in dialog.result:
                    add_book(**book_data)
                    added_count += 1
                    if book_data['loai_sach'] == 'SACH_GIAY':
                        added_types.append("Sách giấy")
                    else:
                        added_types.append("Sách online")
                
                if added_count == 1:
                    messagebox.showinfo("Thành công", f"Đã thêm {added_types[0]} thành công!")
                else:
                    messagebox.showinfo("Thành công", f"Đã thêm thành công:\n• {added_types[0]}\n• {added_types[1]}")
                self.load_books()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm sách: {str(e)}")
                
    def show_edit_dialog(self):
        """Hiện dialog sửa sách"""
        if not self.selected_book:
            return
            
        book = get_book_by_id(self.selected_book)
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy sách!")
            return
            
        dialog = BookDialog(self, "Sửa thông tin sách", self.categories, book)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                update_book(self.selected_book, **dialog.result)
                messagebox.showinfo("Thành công", "Cập nhật sách thành công!")
                self.load_books()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
                
    def show_detail_dialog(self):
        """Hiện dialog xem chi tiết"""
        if not self.selected_book:
            return
            
        book = get_book_by_id(self.selected_book)
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy sách!")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết sách")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Content
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        info = [
            ("Mã sách:", str(book['ma_sach'])),
            ("Tiêu đề:", book['tieu_de']),
            ("Tác giả:", book['tac_gia'] or "N/A"),
            ("Thể loại:", book['ten_the_loai'] or "N/A"),
            ("Loại sách:", "Sách giấy" if book['loai_sach'] == 'SACH_GIAY' else "Sách online"),
            ("Trạng thái:", book['trang_thai_sach']),
        ]
        
        if book['loai_sach'] == 'SACH_GIAY':
            info.append(("Số lượng:", str(book['so_luong'])))
        else:
            info.append(("URL:", book['url_tai_lieu'] or "N/A"))
            info.append(("Định dạng:", book['dinh_dang'] or "N/A"))
        
        for label, value in info:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=10)
            
        ctk.CTkButton(dialog, text="Đóng", command=dialog.destroy).pack(pady=20)
        
    def delete_selected(self):
        """Xóa sách đã chọn"""
        if not self.selected_book:
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa sách này?"):
            try:
                delete_book(self.selected_book)
                messagebox.showinfo("Thành công", "Xóa sách thành công!")
                self.load_books()
                self.selected_book = None
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa sách: {str(e)}")
                
    def show_add_category_dialog(self):
        """Hiện dialog thêm thể loại"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Thêm thể loại sách")
        dialog.geometry("350x180")
        dialog.transient(self)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Tên thể loại:", font=ctk.CTkFont(size=14)).pack(pady=(20, 5))
        
        entry = ctk.CTkEntry(dialog, width=250)
        entry.pack(pady=10)
        entry.focus()
        
        def save():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên thể loại!")
                return
            try:
                add_category(name)
                messagebox.showinfo("Thành công", "Thêm thể loại thành công!")
                # Refresh categories
                self.categories = get_all_categories()
                category_names = ["Tất cả"] + [c['ten_the_loai'] for c in self.categories]
                self.category_combo.configure(values=category_names)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
        
        ctk.CTkButton(dialog, text="Lưu", command=save).pack(pady=20)


class BookDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa sách"""
    
    def __init__(self, parent, title: str, categories: list, book: dict = None):
        super().__init__(parent)
        
        self.title(title)
        self.geometry("500x580")
        self.transient(parent)
        self.grab_set()
        
        self.categories = categories
        self.book = book
        self.result = None
        
        self.create_widgets()
        
        if book:
            self.populate_fields()
            
    def create_widgets(self):
        """Tạo các widget"""
        # Main container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        # Scrollable frame cho nội dung
        frame = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        frame.pack(fill="both", expand=True)
        
        # Tiêu đề
        ctk.CTkLabel(frame, text="Tiêu đề sách: *", anchor="w").pack(fill="x", pady=(0, 5))
        self.title_entry = ctk.CTkEntry(frame)
        self.title_entry.pack(fill="x", pady=(0, 10))
        
        # Tác giả
        ctk.CTkLabel(frame, text="Tác giả:", anchor="w").pack(fill="x", pady=(0, 5))
        self.author_entry = ctk.CTkEntry(frame)
        self.author_entry.pack(fill="x", pady=(0, 10))
        
        # Thể loại
        ctk.CTkLabel(frame, text="Thể loại: *", anchor="w").pack(fill="x", pady=(0, 5))
        category_names = [c['ten_the_loai'] for c in self.categories]
        self.category_var = ctk.StringVar(value=category_names[0] if category_names else "")
        self.category_combo = ctk.CTkComboBox(frame, values=category_names, variable=self.category_var)
        self.category_combo.pack(fill="x", pady=(0, 10))
        
        # Loại sách - Checkbox cho phép chọn nhiều (chỉ khi thêm mới)
        if not self.book:
            ctk.CTkLabel(frame, text="Loại sách: * (có thể chọn cả 2)", anchor="w").pack(fill="x", pady=(0, 5))
            type_frame = ctk.CTkFrame(frame, fg_color="transparent")
            type_frame.pack(fill="x", pady=(0, 10))
            
            self.paper_var = ctk.BooleanVar(value=True)
            self.online_var = ctk.BooleanVar(value=False)
            
            ctk.CTkCheckBox(type_frame, text="📚 Sách giấy", variable=self.paper_var, 
                           command=self.on_type_change).pack(side="left", padx=10)
            ctk.CTkCheckBox(type_frame, text="🌐 Sách online", variable=self.online_var, 
                           command=self.on_type_change).pack(side="left", padx=10)
        else:
            # Khi sửa, chỉ cho chọn 1 loại (radio button)
            ctk.CTkLabel(frame, text="Loại sách: *", anchor="w").pack(fill="x", pady=(0, 5))
            self.type_var = ctk.StringVar(value="SACH_GIAY")
            type_frame = ctk.CTkFrame(frame, fg_color="transparent")
            type_frame.pack(fill="x", pady=(0, 10))
            
            ctk.CTkRadioButton(type_frame, text="Sách giấy", variable=self.type_var, 
                              value="SACH_GIAY", command=self.on_type_change_edit).pack(side="left", padx=10)
            ctk.CTkRadioButton(type_frame, text="Sách online", variable=self.type_var, 
                              value="SACH_ONLINE", command=self.on_type_change_edit).pack(side="left", padx=10)
        
        # Frame cho sách giấy
        self.paper_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.paper_frame.pack(fill="x")
        
        ctk.CTkLabel(self.paper_frame, text="📚 Số lượng sách giấy:", anchor="w").pack(fill="x", pady=(0, 5))
        self.quantity_entry = ctk.CTkEntry(self.paper_frame)
        self.quantity_entry.insert(0, "1")
        self.quantity_entry.pack(fill="x", pady=(0, 10))
        
        # Frame cho sách online
        self.online_frame = ctk.CTkFrame(frame, fg_color="transparent")
        
        ctk.CTkLabel(self.online_frame, text="🌐 URL tài liệu:", anchor="w").pack(fill="x", pady=(0, 5))
        self.url_entry = ctk.CTkEntry(self.online_frame)
        self.url_entry.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(self.online_frame, text="Định dạng:", anchor="w").pack(fill="x", pady=(0, 5))
        self.format_entry = ctk.CTkEntry(self.online_frame)
        self.format_entry.insert(0, "PDF")
        self.format_entry.pack(fill="x", pady=(0, 10))
        
        # Trạng thái (chỉ khi sửa)
        if self.book:
            ctk.CTkLabel(frame, text="Trạng thái:", anchor="w").pack(fill="x", pady=(10, 5))
            self.status_var = ctk.StringVar(value=self.book['trang_thai_sach'])
            status_combo = ctk.CTkComboBox(
                frame,
                values=['CO_SAN', 'DA_MUON', 'HONG', 'MAT'],
                variable=self.status_var
            )
            status_combo.pack(fill="x", pady=(0, 10))
        
        # Buttons - nằm ngoài scrollable frame, luôn ở cuối cửa sổ
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        ctk.CTkButton(btn_frame, text="Hủy", command=self.destroy, 
                     fg_color="gray", width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Lưu", command=self.save, width=100).pack(side="right", padx=5)
    
    def on_type_change(self):
        """Xử lý khi thay đổi loại sách (thêm mới - checkbox)"""
        if self.paper_var.get():
            self.paper_frame.pack(fill="x")
        else:
            self.paper_frame.pack_forget()
            
        if self.online_var.get():
            self.online_frame.pack(fill="x")
        else:
            self.online_frame.pack_forget()
            
        # Đảm bảo ít nhất 1 loại được chọn
        if not self.paper_var.get() and not self.online_var.get():
            self.paper_var.set(True)
            self.paper_frame.pack(fill="x")
    
    def on_type_change_edit(self):
        """Xử lý khi thay đổi loại sách (sửa - radio)"""
        if self.type_var.get() == "SACH_GIAY":
            self.online_frame.pack_forget()
            self.paper_frame.pack(fill="x")
        else:
            self.paper_frame.pack_forget()
            self.online_frame.pack(fill="x")
            
    def populate_fields(self):
        """Điền dữ liệu khi sửa"""
        self.title_entry.insert(0, self.book['tieu_de'])
        self.author_entry.insert(0, self.book['tac_gia'] or "")
        
        # Set category
        for cat in self.categories:
            if cat['ma_the_loai'] == self.book['ma_the_loai']:
                self.category_var.set(cat['ten_the_loai'])
                break
        
        # Set type (khi sửa dùng radio button)
        self.type_var.set(self.book['loai_sach'])
        self.on_type_change_edit()
        
        if self.book['loai_sach'] == 'SACH_GIAY':
            self.quantity_entry.delete(0, 'end')
            self.quantity_entry.insert(0, str(self.book['so_luong']))
        else:
            self.url_entry.insert(0, self.book['url_tai_lieu'] or "")
            self.format_entry.delete(0, 'end')
            self.format_entry.insert(0, self.book['dinh_dang'] or "PDF")
            
    def save(self):
        """Lưu thông tin"""
        tieu_de = self.title_entry.get().strip()
        tac_gia = self.author_entry.get().strip()
        category_name = self.category_var.get()
        
        if not tieu_de:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tiêu đề sách!")
            return
            
        # Tìm mã thể loại
        ma_the_loai = None
        for cat in self.categories:
            if cat['ten_the_loai'] == category_name:
                ma_the_loai = cat['ma_the_loai']
                break
                
        if not ma_the_loai:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thể loại!")
            return
        
        if self.book:
            # Khi sửa - chỉ 1 loại
            loai_sach = self.type_var.get()
            self.result = {
                'tieu_de': tieu_de,
                'tac_gia': tac_gia or None,
                'ma_the_loai': ma_the_loai,
                'trang_thai': self.status_var.get()
            }
            
            if loai_sach == 'SACH_GIAY':
                try:
                    so_luong = int(self.quantity_entry.get())
                    self.result['so_luong'] = so_luong
                except:
                    messagebox.showwarning("Cảnh báo", "Số lượng phải là số!")
                    return
            else:
                self.result['url_tai_lieu'] = self.url_entry.get().strip() or None
                self.result['dinh_dang'] = self.format_entry.get().strip() or None
        else:
            # Thêm mới - có thể chọn cả 2 loại
            is_paper = self.paper_var.get()
            is_online = self.online_var.get()
            
            if not is_paper and not is_online:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 loại sách!")
                return
            
            # Trả về list các sách cần thêm
            self.result = []
            
            if is_paper:
                try:
                    so_luong = int(self.quantity_entry.get())
                    if so_luong <= 0:
                        raise ValueError()
                except:
                    messagebox.showwarning("Cảnh báo", "Số lượng sách giấy phải là số dương!")
                    return
                    
                self.result.append({
                    'tieu_de': tieu_de,
                    'tac_gia': tac_gia or None,
                    'ma_the_loai': ma_the_loai,
                    'loai_sach': 'SACH_GIAY',
                    'so_luong': so_luong
                })
            
            if is_online:
                url = self.url_entry.get().strip()
                if not url:
                    messagebox.showwarning("Cảnh báo", "Vui lòng nhập URL cho sách online!")
                    return
                    
                self.result.append({
                    'tieu_de': tieu_de,
                    'tac_gia': tac_gia or None,
                    'ma_the_loai': ma_the_loai,
                    'loai_sach': 'SACH_ONLINE',
                    'url_tai_lieu': url,
                    'dinh_dang': self.format_entry.get().strip() or 'PDF'
                })
                
        self.destroy()
