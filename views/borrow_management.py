"""
Borrow Management - Quản lý mượn/trả sách
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_all_borrows, get_borrow_by_id, create_borrow, return_book,
                      calculate_fine, get_all_readers, get_all_books, get_all_staff, count_borrows)
from utils.report_generator import generate_borrow_receipt, generate_return_receipt
from utils import treeview_sort_column, PaginationFrame, center_window


class BorrowManagement(ctk.CTkFrame):
    """Giao diện quản lý mượn/trả sách"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_borrow = None
        
        self.create_widgets()
        self.load_borrows()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📋 Quản lý Mượn/Trả Sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Add borrow button
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Tạo phiếu mượn",
            command=self.show_borrow_dialog,
            width=140
        )
        add_btn.pack(side="right")
        
        # Filter & Search frame
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Tìm theo tên đọc giả, mã đọc giả, tên sách...",
            width=350
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_borrows())
        
        # Status filter
        ctk.CTkLabel(filter_frame, text="Trạng thái:").pack(side="left", padx=(20, 5))
        
        self.status_var = ctk.StringVar(value="Tất cả")
        self.status_combo = ctk.CTkComboBox(
            filter_frame,
            values=["Tất cả", "Đang mượn", "Đã trả", "Quá hạn"],
            variable=self.status_var,
            command=lambda e: self.search_borrows(),
            width=120
        )
        self.status_combo.pack(side="left")
        
        refresh_btn = ctk.CTkButton(
            filter_frame,
            text="🔄",
            command=self.load_borrows,
            width=40
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Table frame
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Treeview
        columns = ("ma_phieu", "ma_doc_gia", "ten_doc_gia", "tieu_de", 
                   "ngay_muon", "ngay_hen_tra", "ngay_tra_thuc", "trang_thai", "tien_phat")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Column headings with sorting
        headings = {
            "ma_phieu": "Mã phiếu",
            "ma_doc_gia": "Mã ĐG",
            "ten_doc_gia": "Tên đọc giả",
            "tieu_de": "Tên sách",
            "ngay_muon": "Ngày mượn",
            "ngay_hen_tra": "Hạn trả",
            "ngay_tra_thuc": "Ngày trả",
            "trang_thai": "Trạng thái",
            "tien_phat": "Tiền phạt"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, 
                            command=lambda c=col: treeview_sort_column(self.tree, c, False))
        
        # Column widths
        self.tree.column("ma_phieu", width=70, anchor="center")
        self.tree.column("ma_doc_gia", width=70, anchor="center")
        self.tree.column("ten_doc_gia", width=130)
        self.tree.column("tieu_de", width=150)
        self.tree.column("ngay_muon", width=90, anchor="center")
        self.tree.column("ngay_hen_tra", width=90, anchor="center")
        self.tree.column("ngay_tra_thuc", width=90, anchor="center")
        self.tree.column("trang_thai", width=100, anchor="center")
        self.tree.column("tien_phat", width=90, anchor="e")
        
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
        
        self.return_btn = ctk.CTkButton(
            action_frame,
            text="📥 Trả sách",
            command=self.return_selected,
            width=120,
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"
        )
        self.return_btn.pack(side="left", padx=5)
        
        self.detail_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Chi tiết",
            command=self.show_detail_dialog,
            width=100,
            state="disabled"
        )
        self.detail_btn.pack(side="left", padx=5)
        
        self.print_borrow_btn = ctk.CTkButton(
            action_frame,
            text="🖨️ In phiếu mượn",
            command=self.print_borrow_receipt,
            width=130,
            state="disabled"
        )
        self.print_borrow_btn.pack(side="left", padx=5)
        
        self.print_return_btn = ctk.CTkButton(
            action_frame,
            text="🖨️ In phiếu trả",
            command=self.print_return_receipt,
            width=130,
            state="disabled"
        )
        self.print_return_btn.pack(side="left", padx=5)
        
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
        self.load_borrows_page()
        
    def load_borrows(self):
        """Tải danh sách phiếu mượn"""
        # Reset pagination
        total = count_borrows()
        self.pagination.set_total(total)
        self.pagination.current_page = 1
        self.pagination.update_display()
        
        self.load_borrows_page()
    
    def load_borrows_page(self):
        """Tải dữ liệu cho trang hiện tại"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        borrows = get_all_borrows(
            limit=self.pagination.get_limit(),
            offset=self.pagination.get_offset()
        )
        
        self._populate_tree(borrows)
    
    def _populate_tree(self, borrows):
        """Điền dữ liệu vào tree"""
        for borrow in borrows:
            trang_thai_map = {
                'DANG_MUON': '📖 Đang mượn',
                'DA_TRA': '✅ Đã trả',
                'QUA_HAN': '⚠️ Quá hạn'
            }
            
            # Kiểm tra quá hạn
            if borrow['trang_thai_phieu'] == 'DANG_MUON':
                ngay_hen_tra = datetime.strptime(borrow['ngay_hen_tra'], '%Y-%m-%d')
                if datetime.now() > ngay_hen_tra:
                    trang_thai = '⚠️ Quá hạn'
                else:
                    trang_thai = trang_thai_map.get(borrow['trang_thai_phieu'])
            else:
                trang_thai = trang_thai_map.get(borrow['trang_thai_phieu'], borrow['trang_thai_phieu'])
            
            self.tree.insert("", "end", values=(
                borrow['ma_phieu'],
                borrow['ma_doc_gia'],
                borrow['ten_doc_gia'],
                borrow['tieu_de'],
                borrow['ngay_muon'],
                borrow['ngay_hen_tra'],
                borrow['ngay_tra_thuc'] or "-",
                trang_thai,
                f"{borrow['tien_phat']:,.0f}đ" if borrow['tien_phat'] else "0đ"
            ))
            
    def search_borrows(self):
        """Tìm kiếm phiếu mượn"""
        search_term = self.search_entry.get()
        status_name = self.status_var.get()
        
        status_map = {
            "Tất cả": None,
            "Đang mượn": "DANG_MUON",
            "Đã trả": "DA_TRA",
            "Quá hạn": "QUA_HAN"
        }
        status = status_map.get(status_name)
        
        # Update pagination total
        total = count_borrows(search_term, status)
        self.pagination.set_total(total)
        self.pagination.current_page = 1
        self.pagination.update_display()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        borrows = get_all_borrows(
            search_term, 
            status,
            limit=self.pagination.get_limit(),
            offset=self.pagination.get_offset()
        )
        
        self._populate_tree(borrows)
            
    def on_select(self, event):
        """Xử lý khi chọn item"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            self.selected_borrow = item['values'][0]  # ma_phieu
            
            # Lấy trạng thái
            trang_thai = item['values'][7]
            
            self.detail_btn.configure(state="normal")
            self.print_borrow_btn.configure(state="normal")
            
            # Chỉ cho trả sách nếu đang mượn
            if "Đang mượn" in trang_thai or "Quá hạn" in trang_thai:
                self.return_btn.configure(state="normal")
                self.print_return_btn.configure(state="disabled")
            else:
                self.return_btn.configure(state="disabled")
                self.print_return_btn.configure(state="normal")
        else:
            self.selected_borrow = None
            self.return_btn.configure(state="disabled")
            self.detail_btn.configure(state="disabled")
            self.print_borrow_btn.configure(state="disabled")
            self.print_return_btn.configure(state="disabled")
    
    def on_double_click(self, event):
        """Xử lý double-click - chỉ mở dialog nếu click vào dòng dữ liệu"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_detail_dialog()
            
    def show_borrow_dialog(self):
        """Hiện dialog tạo phiếu mượn"""
        dialog = BorrowDialog(self, self.user)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                ma_phieu = create_borrow(**dialog.result)
                messagebox.showinfo("Thành công", f"Tạo phiếu mượn #{ma_phieu} thành công!")
                self.load_borrows()
                
                # Hỏi in phiếu
                if messagebox.askyesno("In phiếu", "Bạn có muốn in phiếu mượn không?"):
                    borrow = get_borrow_by_id(ma_phieu)
                    output_path = generate_borrow_receipt(borrow)
                    os.startfile(output_path)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")
                
    def return_selected(self):
        """Trả sách"""
        if not self.selected_borrow:
            return
            
        borrow = get_borrow_by_id(self.selected_borrow)
        if not borrow:
            messagebox.showerror("Lỗi", "Không tìm thấy phiếu mượn!")
            return
            
        # Tính tiền phạt
        tien_phat = calculate_fine(self.selected_borrow)
        
        # Dialog xác nhận
        dialog = ctk.CTkToplevel(self)
        dialog.title("Xác nhận trả sách")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 400, 350)
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="THÔNG TIN TRẢ SÁCH", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 15))
        
        info = [
            f"Mã phiếu: {borrow['ma_phieu']}",
            f"Đọc giả: {borrow['ten_doc_gia']} ({borrow['ma_doc_gia']})",
            f"Sách: {borrow['tieu_de']}",
            f"Ngày mượn: {borrow['ngay_muon']}",
            f"Hạn trả: {borrow['ngay_hen_tra']}",
            f"Ngày trả: {datetime.now().strftime('%Y-%m-%d')}",
        ]
        
        for text in info:
            ctk.CTkLabel(frame, text=text, anchor="w").pack(fill="x", pady=2)
        
        # Tiền phạt
        fine_frame = ctk.CTkFrame(frame, fg_color="#fff3cd" if tien_phat > 0 else "transparent")
        fine_frame.pack(fill="x", pady=15)
        
        if tien_phat > 0:
            ctk.CTkLabel(fine_frame, text=f"⚠️ TIỀN PHẠT QUÁ HẠN: {tien_phat:,.0f} VND",
                        font=ctk.CTkFont(weight="bold"), text_color="#856404").pack(pady=10)
        else:
            ctk.CTkLabel(fine_frame, text="✅ Trả đúng hạn - Không phạt",
                        font=ctk.CTkFont(weight="bold"), text_color="#155724").pack(pady=10)
        
        def confirm_return():
            if return_book(self.selected_borrow, tien_phat):
                messagebox.showinfo("Thành công", "Trả sách thành công!")
                dialog.destroy()
                self.load_borrows()
                
                # Hỏi in phiếu trả
                if messagebox.askyesno("In phiếu", "Bạn có muốn in phiếu trả không?"):
                    borrow_updated = get_borrow_by_id(self.selected_borrow)
                    borrow_updated['tien_phat'] = tien_phat
                    output_path = generate_return_receipt(borrow_updated)
                    os.startfile(output_path)
            else:
                messagebox.showerror("Lỗi", "Không thể trả sách!")
        
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="Hủy", command=dialog.destroy, 
                     fg_color="gray", width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Xác nhận trả", command=confirm_return, 
                     fg_color="#28a745", width=120).pack(side="right", padx=5)
                     
    def show_detail_dialog(self):
        """Hiện chi tiết phiếu mượn"""
        if not self.selected_borrow:
            return
            
        borrow = get_borrow_by_id(self.selected_borrow)
        if not borrow:
            messagebox.showerror("Lỗi", "Không tìm thấy phiếu mượn!")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Chi tiết phiếu mượn #{borrow['ma_phieu']}")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 500, 580)
        
        # Header với màu theo trạng thái
        trang_thai = borrow['trang_thai_phieu']
        
        # Kiểm tra quá hạn dựa trên ngày hẹn trả
        is_overdue = False
        if trang_thai == 'DANG_MUON' and borrow['ngay_hen_tra']:
            try:
                ngay_hen_tra = datetime.strptime(borrow['ngay_hen_tra'], '%Y-%m-%d').date()
                if ngay_hen_tra < datetime.now().date():
                    is_overdue = True
            except:
                pass
        
        if trang_thai == 'DA_TRA':
            header_color = "#28a745"  # Green
            status_text = "✅ ĐÃ TRẢ"
        elif is_overdue:
            header_color = "#dc3545"  # Red
            status_text = "⚠️ QUÁ HẠN"
        else:
            header_color = "#17a2b8"  # Blue
            status_text = "📖 ĐANG MƯỢN"
        
        header = ctk.CTkFrame(dialog, fg_color=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text=f"PHIẾU MƯỢN #{borrow['ma_phieu']} - {status_text}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        frame = ctk.CTkScrollableFrame(dialog)
        frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Thông tin đọc giả
        section1 = ctk.CTkFrame(frame, fg_color=("gray90", "gray20"))
        section1.pack(fill="x", pady=5)
        ctk.CTkLabel(section1, text="📚 THÔNG TIN ĐỌC GIẢ",
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        info_frame1 = ctk.CTkFrame(section1, fg_color="transparent")
        info_frame1.pack(fill="x", padx=10, pady=(0, 10))
        
        for label, value in [
            ("Mã đọc giả:", borrow['ma_doc_gia']),
            ("Họ tên:", borrow['ten_doc_gia']),
            ("Địa chỉ:", borrow['dia_chi'] or 'N/A'),
            ("SĐT:", borrow['so_dt'] or 'N/A')
        ]:
            row = ctk.CTkFrame(info_frame1, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left", padx=5)
        
        # Thông tin sách
        section2 = ctk.CTkFrame(frame, fg_color=("gray90", "gray20"))
        section2.pack(fill="x", pady=5)
        ctk.CTkLabel(section2, text="📖 THÔNG TIN SÁCH",
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        info_frame2 = ctk.CTkFrame(section2, fg_color="transparent")
        info_frame2.pack(fill="x", padx=10, pady=(0, 10))
        
        for label, value in [
            ("Tên sách:", borrow['tieu_de']),
            ("Tác giả:", borrow['tac_gia'] or 'N/A'),
            ("Thể loại:", borrow['ten_the_loai'] or 'N/A')
        ]:
            row = ctk.CTkFrame(info_frame2, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left", padx=5)
        
        # Thông tin mượn trả
        section3 = ctk.CTkFrame(frame, fg_color=("gray90", "gray20"))
        section3.pack(fill="x", pady=5)
        ctk.CTkLabel(section3, text="📅 THÔNG TIN MƯỢN TRẢ",
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        info_frame3 = ctk.CTkFrame(section3, fg_color="transparent")
        info_frame3.pack(fill="x", padx=10, pady=(0, 10))
        
        for label, value in [
            ("Ngày mượn:", borrow['ngay_muon']),
            ("Hạn trả:", borrow['ngay_hen_tra']),
            ("Ngày trả thực tế:", borrow['ngay_tra_thuc'] or 'Chưa trả'),
            ("Tiền phạt:", f"{borrow['tien_phat']:,.0f} VND")
        ]:
            row = ctk.CTkFrame(info_frame3, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=label, width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), anchor="w").pack(side="left", padx=5)
        
        # Nhân viên xử lý
        section4 = ctk.CTkFrame(frame, fg_color=("gray90", "gray20"))
        section4.pack(fill="x", pady=5)
        ctk.CTkLabel(section4, text="👤 NHÂN VIÊN XỬ LÝ",
                    font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(section4, text=f"{borrow['ten_nhan_vien']} ({borrow['ma_nhan_vien']})").pack(anchor="w", padx=10, pady=(0, 10))
        
        # Nút chức năng
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        # Nút đóng
        ctk.CTkButton(
            btn_frame, 
            text="Đóng", 
            command=dialog.destroy,
            width=80
        ).pack(side="left")
        
        # Các nút chức năng theo trạng thái
        if trang_thai == 'DANG_MUON' or trang_thai == 'QUA_HAN':
            # Nút trả sách
            def return_and_close():
                dialog.destroy()
                self.return_selected()
            
            ctk.CTkButton(
                btn_frame,
                text="📤 Trả sách",
                command=return_and_close,
                width=100,
                fg_color="#28a745",
                hover_color="#218838"
            ).pack(side="right", padx=5)
            
            # Nút in phiếu mượn
            def print_borrow():
                try:
                    output_path = generate_borrow_receipt(borrow)
                    messagebox.showinfo("Thành công", f"Đã tạo phiếu mượn:\n{output_path}")
                    os.startfile(output_path)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")
            
            ctk.CTkButton(
                btn_frame,
                text="🖨️ In phiếu mượn",
                command=print_borrow,
                width=120,
                fg_color="#17a2b8",
                hover_color="#138496"
            ).pack(side="right", padx=5)
            
        elif trang_thai == 'DA_TRA':
            # Nút in phiếu trả
            def print_return():
                try:
                    output_path = generate_return_receipt(borrow)
                    messagebox.showinfo("Thành công", f"Đã tạo phiếu trả:\n{output_path}")
                    os.startfile(output_path)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")
            
            ctk.CTkButton(
                btn_frame,
                text="🖨️ In phiếu trả",
                command=print_return,
                width=120,
                fg_color="#6c757d",
                hover_color="#5a6268"
            ).pack(side="right", padx=5)
            
            # Nút in phiếu mượn (lưu trữ)
            def print_borrow():
                try:
                    output_path = generate_borrow_receipt(borrow)
                    messagebox.showinfo("Thành công", f"Đã tạo phiếu mượn:\n{output_path}")
                    os.startfile(output_path)
                except Exception as e:
                    messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")
            
            ctk.CTkButton(
                btn_frame,
                text="🖨️ In phiếu mượn",
                command=print_borrow,
                width=120,
                fg_color="#17a2b8",
                hover_color="#138496"
            ).pack(side="right", padx=5)
        
    def print_borrow_receipt(self):
        """In phiếu mượn"""
        if not self.selected_borrow:
            return
            
        borrow = get_borrow_by_id(self.selected_borrow)
        if not borrow:
            messagebox.showerror("Lỗi", "Không tìm thấy phiếu mượn!")
            return
            
        try:
            output_path = generate_borrow_receipt(borrow)
            messagebox.showinfo("Thành công", f"Đã tạo phiếu mượn:\n{output_path}")
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")
            
    def print_return_receipt(self):
        """In phiếu trả"""
        if not self.selected_borrow:
            return
            
        borrow = get_borrow_by_id(self.selected_borrow)
        if not borrow:
            messagebox.showerror("Lỗi", "Không tìm thấy phiếu!")
            return
            
        try:
            output_path = generate_return_receipt(borrow)
            messagebox.showinfo("Thành công", f"Đã tạo phiếu trả:\n{output_path}")
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tạo phiếu: {str(e)}")


class BorrowDialog(ctk.CTkToplevel):
    """Dialog tạo phiếu mượn"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent)
        
        self.title("Tạo phiếu mượn mới")
        self.transient(parent)
        self.grab_set()
        center_window(self, 500, 450)
        
        self.user = user
        self.result = None
        
        # Load data
        self.readers = get_all_readers()
        # Lọc sách có sẵn: sách online hoặc sách giấy có quyển có sẵn
        self.books = [b for b in get_all_books() if 
                     b['loai_sach'] == 'SACH_ONLINE' or b.get('so_quyen_co_san', b.get('so_luong', 0)) > 0]
        self.staff = get_all_staff()
        
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo các widget"""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="TẠO PHIẾU MƯỢN SÁCH",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 20))
        
        # Chọn đọc giả
        ctk.CTkLabel(frame, text="Đọc giả: *", anchor="w").pack(fill="x", pady=(0, 5))
        
        reader_names = [f"{r['ma_doc_gia']} - {r['ho_ten']}" for r in self.readers]
        self.reader_var = ctk.StringVar()
        self.reader_combo = ctk.CTkComboBox(
            frame,
            values=reader_names,
            variable=self.reader_var,
            width=400
        )
        self.reader_combo.pack(fill="x", pady=(0, 15))
        
        # Chọn sách
        ctk.CTkLabel(frame, text="Sách: *", anchor="w").pack(fill="x", pady=(0, 5))
        
        book_names = [f"{b['ma_sach']} - {b['tieu_de']} ({b['tac_gia'] or 'N/A'})" for b in self.books]
        self.book_var = ctk.StringVar()
        self.book_combo = ctk.CTkComboBox(
            frame,
            values=book_names,
            variable=self.book_var,
            width=400
        )
        self.book_combo.pack(fill="x", pady=(0, 15))
        
        if not book_names:
            ctk.CTkLabel(frame, text="⚠️ Không có sách khả dụng!", 
                        text_color="red").pack(anchor="w")
        
        # Nhân viên xử lý
        ctk.CTkLabel(frame, text="Nhân viên xử lý: *", anchor="w").pack(fill="x", pady=(0, 5))
        
        staff_names = [f"{s['ma_nhan_vien']} - {s['ho_ten']}" for s in self.staff]
        self.staff_var = ctk.StringVar()
        
        # Nếu user là nhân viên, tự động chọn
        if self.user['loai_nguoi_dung'] == 'NHAN_VIEN':
            for s in self.staff:
                if s['ma_nd'] == self.user['ma_nd']:
                    self.staff_var.set(f"{s['ma_nhan_vien']} - {s['ho_ten']}")
                    break
        
        self.staff_combo = ctk.CTkComboBox(
            frame,
            values=staff_names,
            variable=self.staff_var,
            width=400
        )
        self.staff_combo.pack(fill="x", pady=(0, 15))
        
        # Số ngày mượn
        ctk.CTkLabel(frame, text="Số ngày mượn:", anchor="w").pack(fill="x", pady=(0, 5))
        self.days_entry = ctk.CTkEntry(frame)
        self.days_entry.insert(0, "14")
        self.days_entry.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(btn_frame, text="Hủy", command=self.destroy, 
                     fg_color="gray", width=100).pack(side="left", padx=5)
        self.save_btn = ctk.CTkButton(btn_frame, text="Tạo phiếu", command=self.save, 
                     width=120)
        self.save_btn.pack(side="right", padx=5)
        
    def save(self):
        """Lưu phiếu mượn"""
        # Disable button ngay khi click để tránh double-submit
        self.save_btn.configure(state="disabled", text="⏳ Đang xử lý...")
        
        reader_sel = self.reader_var.get()
        book_sel = self.book_var.get()
        staff_sel = self.staff_var.get()
        
        if not all([reader_sel, book_sel, staff_sel]):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn đầy đủ thông tin!")
            self.save_btn.configure(state="normal", text="Tạo phiếu")
            return
        
        try:
            so_ngay = int(self.days_entry.get())
            if so_ngay <= 0:
                messagebox.showwarning("Cảnh báo", "Số ngày mượn phải lớn hơn 0!")
                self.save_btn.configure(state="normal", text="Tạo phiếu")
                return
            if so_ngay > 30:
                messagebox.showwarning("Cảnh báo", "Số ngày mượn tối đa là 30 ngày!")
                self.save_btn.configure(state="normal", text="Tạo phiếu")
                return
        except ValueError:
            messagebox.showwarning("Cảnh báo", "Số ngày phải là số nguyên!")
            self.save_btn.configure(state="normal", text="Tạo phiếu")
            return
        
        # Lấy ID từ selection
        reader_code = reader_sel.split(" - ")[0]
        book_id = int(book_sel.split(" - ")[0])
        staff_code = staff_sel.split(" - ")[0]
        
        # Tìm ma_nd
        ma_nd_doc_gia = None
        for r in self.readers:
            if r['ma_doc_gia'] == reader_code:
                ma_nd_doc_gia = r['ma_nd']
                break
        
        ma_nd_nhan_vien = None
        for s in self.staff:
            if s['ma_nhan_vien'] == staff_code:
                ma_nd_nhan_vien = s['ma_nd']
                break
        
        if not all([ma_nd_doc_gia, ma_nd_nhan_vien]):
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin!")
            return
        
        self.result = {
            'ma_nd_doc_gia': ma_nd_doc_gia,
            'ma_nd_nhan_vien': ma_nd_nhan_vien,
            'ma_sach': book_id,
            'so_ngay_muon': so_ngay
        }
        
        self.destroy()
