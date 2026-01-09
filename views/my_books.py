"""
My Books - Xem sách của đọc giả (dành cho đọc giả đăng nhập)
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_reader_by_id, get_reader_borrow_history, get_all_books,
                      create_borrow, get_all_staff, get_book_by_id, return_book, calculate_fine)
from utils.report_generator import generate_borrow_receipt, generate_return_receipt


class MyBooks(ctk.CTkFrame):
    """Giao diện sách của tôi cho đọc giả"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📚 Sách của tôi",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tab 1: Thông tin cá nhân
        tab1 = self.tabview.add("👤 Thông tin cá nhân")
        self.create_info_tab(tab1)
        
        # Tab 2: Sách đang mượn
        tab2 = self.tabview.add("📖 Sách đang mượn")
        self.create_borrowing_tab(tab2)
        
        # Tab 3: Lịch sử mượn
        tab3 = self.tabview.add("📜 Lịch sử mượn")
        self.create_history_tab(tab3)
        
        # Tab 4: Tìm sách
        tab4 = self.tabview.add("🔍 Tìm sách")
        self.create_search_tab(tab4)
        
    def create_info_tab(self, parent):
        """Tạo tab thông tin cá nhân"""
        self.info_frame = ctk.CTkFrame(parent)
        self.info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
    def create_borrowing_tab(self, parent):
        """Tạo tab sách đang mượn"""
        # Tree frame
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ma_phieu", "tieu_de", "tac_gia", "ngay_muon", "ngay_hen_tra", "loai_sach", "trang_thai")
        self.borrowing_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
        
        self.borrowing_tree.heading("ma_phieu", text="Mã phiếu")
        self.borrowing_tree.heading("tieu_de", text="Tên sách")
        self.borrowing_tree.heading("tac_gia", text="Tác giả")
        self.borrowing_tree.heading("ngay_muon", text="Ngày mượn")
        self.borrowing_tree.heading("ngay_hen_tra", text="Hạn trả")
        self.borrowing_tree.heading("loai_sach", text="Loại sách")
        self.borrowing_tree.heading("trang_thai", text="Trạng thái")
        
        self.borrowing_tree.column("ma_phieu", width=70, anchor="center")
        self.borrowing_tree.column("tieu_de", width=180)
        self.borrowing_tree.column("tac_gia", width=120)
        self.borrowing_tree.column("ngay_muon", width=90, anchor="center")
        self.borrowing_tree.column("ngay_hen_tra", width=90, anchor="center")
        self.borrowing_tree.column("loai_sach", width=90, anchor="center")
        self.borrowing_tree.column("trang_thai", width=90, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.borrowing_tree.yview)
        self.borrowing_tree.configure(yscrollcommand=scrollbar.set)
        
        self.borrowing_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.borrowing_tree.bind('<<TreeviewSelect>>', self.on_borrowing_select)
        
        # Action frame
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        self.return_book_btn = ctk.CTkButton(
            action_frame,
            text="📤 Trả sách",
            command=self.return_selected_book,
            width=120,
            fg_color="#17a2b8",
            hover_color="#138496",
            state="disabled"
        )
        self.return_book_btn.pack(side="left", padx=5)
        
        self.read_online_btn = ctk.CTkButton(
            action_frame,
            text="🌐 Đọc Online",
            command=self.open_online_book,
            width=120,
            fg_color="#6f42c1",
            hover_color="#5a32a3",
            state="disabled"
        )
        self.read_online_btn.pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Sách online có thể đọc trực tiếp qua link",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def create_history_tab(self, parent):
        """Tạo tab lịch sử mượn"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ma_phieu", "tieu_de", "ngay_muon", "ngay_hen_tra", "ngay_tra", "tien_phat")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        self.history_tree.heading("ma_phieu", text="Mã phiếu")
        self.history_tree.heading("tieu_de", text="Tên sách")
        self.history_tree.heading("ngay_muon", text="Ngày mượn")
        self.history_tree.heading("ngay_hen_tra", text="Hạn trả")
        self.history_tree.heading("ngay_tra", text="Ngày trả")
        self.history_tree.heading("tien_phat", text="Tiền phạt")
        
        self.history_tree.column("ma_phieu", width=80, anchor="center")
        self.history_tree.column("tieu_de", width=250)
        self.history_tree.column("ngay_muon", width=100, anchor="center")
        self.history_tree.column("ngay_hen_tra", width=100, anchor="center")
        self.history_tree.column("ngay_tra", width=100, anchor="center")
        self.history_tree.column("tien_phat", width=100, anchor="e")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
    def create_search_tab(self, parent):
        """Tạo tab tìm sách"""
        # Search bar
        search_frame = ctk.CTkFrame(parent, fg_color="transparent")
        search_frame.pack(fill="x", padx=10, pady=10)
        
        self.book_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Tìm kiếm sách theo tên, tác giả...",
            width=400
        )
        self.book_search_entry.pack(side="left")
        self.book_search_entry.bind('<KeyRelease>', lambda e: self.search_books())
        
        ctk.CTkButton(
            search_frame,
            text="Tìm",
            command=self.search_books,
            width=80
        ).pack(side="left", padx=10)
        
        # Book list
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ma_sach", "tieu_de", "tac_gia", "the_loai", "trang_thai")
        self.book_tree = ttk.Treeview(frame, columns=columns, show="headings", height=10)
        
        self.book_tree.heading("ma_sach", text="Mã sách")
        self.book_tree.heading("tieu_de", text="Tên sách")
        self.book_tree.heading("tac_gia", text="Tác giả")
        self.book_tree.heading("the_loai", text="Thể loại")
        self.book_tree.heading("trang_thai", text="Trạng thái")
        
        self.book_tree.column("ma_sach", width=80, anchor="center")
        self.book_tree.column("tieu_de", width=250)
        self.book_tree.column("tac_gia", width=150)
        self.book_tree.column("the_loai", width=120)
        self.book_tree.column("trang_thai", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.book_tree.yview)
        self.book_tree.configure(yscrollcommand=scrollbar.set)
        
        self.book_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
        
        # Action frame
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
        self.borrow_btn = ctk.CTkButton(
            action_frame,
            text="📚 Mượn sách",
            command=self.borrow_selected_book,
            width=150,
            fg_color="#28a745",
            hover_color="#218838",
            state="disabled"
        )
        self.borrow_btn.pack(side="left", padx=5)
        
        self.view_detail_btn = ctk.CTkButton(
            action_frame,
            text="👁️ Xem chi tiết",
            command=self.view_book_detail,
            width=120,
            state="disabled"
        )
        self.view_detail_btn.pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Chọn sách có trạng thái 'Có sẵn' để mượn",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def load_data(self):
        """Tải dữ liệu"""
        try:
            # Lấy thông tin đọc giả
            reader = get_reader_by_id(self.user['ma_nd'])
            
            if reader:
                self.load_info(reader)
                self.load_borrowing(self.user['ma_nd'])
                self.load_history(self.user['ma_nd'])
            else:
                # Nếu không có thông tin đọc giả, hiển thị thông báo
                ctk.CTkLabel(
                    self.info_frame,
                    text="Không tìm thấy thông tin đọc giả",
                    font=ctk.CTkFont(size=14)
                ).pack(pady=20)
                
            self.load_all_books()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading data: {e}")
        
    def load_info(self, reader: dict):
        """Hiển thị thông tin cá nhân"""
        # Clear
        for widget in self.info_frame.winfo_children():
            widget.destroy()
            
        # Title
        ctk.CTkLabel(
            self.info_frame,
            text="THÔNG TIN ĐỌC GIẢ",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 30))
        
        info_data = [
            ("Mã đọc giả:", reader.get('ma_doc_gia', 'N/A')),
            ("Họ và tên:", reader.get('ho_ten', 'N/A')),
            ("Địa chỉ:", reader.get('dia_chi', 'N/A')),
            ("Số điện thoại:", reader.get('so_dt', 'N/A')),
            ("Email:", reader.get('email', 'N/A')),
            ("Ngày đăng ký:", reader.get('ngay_dk', 'N/A')),
            ("", ""),
            ("Mã thẻ:", str(reader.get('ma_the', 'N/A'))),
            ("Ngày cấp thẻ:", reader.get('ngay_cap', 'N/A')),
            ("Ngày hết hạn:", reader.get('ngay_het_han', 'N/A')),
            ("Trạng thái thẻ:", reader.get('trang_thai_the', 'N/A')),
        ]
        
        for label, value in info_data:
            if label == "":
                ctk.CTkLabel(self.info_frame, text="").pack()
                continue
                
            row = ctk.CTkFrame(self.info_frame, fg_color="transparent")
            row.pack(fill="x", pady=3, padx=50)
            
            ctk.CTkLabel(
                row,
                text=label,
                font=ctk.CTkFont(weight="bold"),
                width=150,
                anchor="e"
            ).pack(side="left")
            
            ctk.CTkLabel(
                row,
                text=value,
                anchor="w"
            ).pack(side="left", padx=15)
            
    def load_borrowing(self, ma_nd: int):
        """Tải sách đang mượn"""
        for item in self.borrowing_tree.get_children():
            self.borrowing_tree.delete(item)
            
        history = get_reader_borrow_history(ma_nd)
        
        # Lưu thông tin URL sách online
        self.borrowing_urls = {}
        
        for item in history:
            if item['trang_thai_phieu'] == 'DANG_MUON':
                from datetime import datetime
                ngay_hen_tra = datetime.strptime(item['ngay_hen_tra'], '%Y-%m-%d')
                if datetime.now() > ngay_hen_tra:
                    trang_thai = '⚠️ Quá hạn'
                else:
                    trang_thai = '📖 Đang mượn'
                
                # Xác định loại sách
                loai_sach = '🌐 Online' if item.get('loai_sach') == 'SACH_ONLINE' else '📚 Giấy'
                
                # Lưu URL nếu là sách online
                if item.get('url_tai_lieu'):
                    self.borrowing_urls[item['ma_phieu']] = item['url_tai_lieu']
                    
                self.borrowing_tree.insert("", "end", values=(
                    item['ma_phieu'],
                    item['tieu_de'],
                    item['tac_gia'] or 'N/A',
                    item['ngay_muon'],
                    item['ngay_hen_tra'],
                    loai_sach,
                    trang_thai
                ))
                
    def load_history(self, ma_nd: int):
        """Tải lịch sử mượn"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        history = get_reader_borrow_history(ma_nd)
        
        for item in history:
            if item['trang_thai_phieu'] == 'DA_TRA':
                self.history_tree.insert("", "end", values=(
                    item['ma_phieu'],
                    item['tieu_de'],
                    item['ngay_muon'],
                    item['ngay_hen_tra'],
                    item['ngay_tra_thuc'] or 'N/A',
                    f"{item['tien_phat']:,.0f}đ" if item['tien_phat'] else "0đ"
                ))
                
    def load_all_books(self):
        """Tải danh sách tất cả sách"""
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
            
        books = get_all_books()
        
        for book in books:
            # Xác định trạng thái hiển thị
            if book['trang_thai_sach'] == 'HONG':
                trang_thai = '❌ Hỏng'
            elif book['trang_thai_sach'] == 'MAT':
                trang_thai = '❌ Mất'
            elif book['loai_sach'] == 'SACH_GIAY' and (book.get('so_luong') is None or book.get('so_luong', 0) <= 0):
                trang_thai = '📕 Hết sách'
            elif book['trang_thai_sach'] == 'DA_MUON':
                trang_thai = '📕 Hết sách'
            else:
                trang_thai = '✅ Có sẵn'
            
            self.book_tree.insert("", "end", values=(
                book['ma_sach'],
                book['tieu_de'],
                book['tac_gia'] or 'N/A',
                book['ten_the_loai'] or 'N/A',
                trang_thai
            ))
            
    def search_books(self):
        """Tìm kiếm sách"""
        search_term = self.book_search_entry.get()
        
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)
            
        books = get_all_books(search_term)
        
        for book in books:
            # Xác định trạng thái hiển thị
            if book['trang_thai_sach'] == 'HONG':
                trang_thai = '❌ Hỏng'
            elif book['trang_thai_sach'] == 'MAT':
                trang_thai = '❌ Mất'
            elif book['loai_sach'] == 'SACH_GIAY' and (book.get('so_luong') is None or book.get('so_luong', 0) <= 0):
                trang_thai = '📕 Hết sách'
            elif book['trang_thai_sach'] == 'DA_MUON':
                trang_thai = '📕 Hết sách'
            else:
                trang_thai = '✅ Có sẵn'
            
            self.book_tree.insert("", "end", values=(
                book['ma_sach'],
                book['tieu_de'],
                book['tac_gia'] or 'N/A',
                book['ten_the_loai'] or 'N/A',
                trang_thai
            ))
            
    def on_book_select(self, event):
        """Xử lý khi chọn sách"""
        selection = self.book_tree.selection()
        if selection:
            item = self.book_tree.item(selection[0])
            trang_thai = item['values'][4]  # Trạng thái
            
            self.view_detail_btn.configure(state="normal")
            
            # Chỉ cho mượn nếu sách có sẵn
            if "Có sẵn" in trang_thai:
                self.borrow_btn.configure(state="normal")
            else:
                self.borrow_btn.configure(state="disabled")
        else:
            self.borrow_btn.configure(state="disabled")
            self.view_detail_btn.configure(state="disabled")
            
    def view_book_detail(self):
        """Xem chi tiết sách"""
        selection = self.book_tree.selection()
        if not selection:
            return
            
        item = self.book_tree.item(selection[0])
        ma_sach = item['values'][0]
        
        book = get_book_by_id(ma_sach)
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy sách!")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("Chi tiết sách")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="📖 THÔNG TIN SÁCH",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(0, 15))
        
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
        
        for label, value in info:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=100, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=10)
            
        ctk.CTkButton(dialog, text="Đóng", command=dialog.destroy).pack(pady=15)
        
    def borrow_selected_book(self):
        """Mượn sách đã chọn"""
        selection = self.book_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách cần mượn!")
            return
            
        item = self.book_tree.item(selection[0])
        ma_sach = item['values'][0]
        tieu_de = item['values'][1]
        trang_thai = item['values'][4]
        
        # Lấy thông tin sách để biết loại sách
        book = get_book_by_id(ma_sach)
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin sách!")
            return
        
        is_online = book.get('loai_sach') == 'SACH_ONLINE'
        
        # Kiểm tra sách có sẵn không
        if "Có sẵn" not in trang_thai:
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
        
        # Lấy nhân viên mặc định (nhân viên đầu tiên)
        staff_list = get_all_staff()
        if not staff_list:
            messagebox.showerror("Lỗi", "Không có nhân viên trong hệ thống!")
            return
        
        default_staff = staff_list[0]
        
        # Dialog xác nhận với thông báo phù hợp loại sách
        if is_online:
            confirm_msg = f"Bạn có muốn mượn sách online:\n\n📖 {tieu_de}\n\n🌐 Sách online - Có thể đọc ngay sau khi mượn\n⏰ Thời hạn truy cập: 14 ngày"
        else:
            confirm_msg = f"Bạn có muốn mượn sách:\n\n📖 {tieu_de}\n\n📚 Sách giấy - Đến thư viện để nhận\n⏰ Thời hạn: 14 ngày"
        
        if messagebox.askyesno("Xác nhận mượn sách", confirm_msg):
            try:
                ma_phieu = create_borrow(
                    ma_nd_doc_gia=self.user['ma_nd'],
                    ma_nd_nhan_vien=default_staff['ma_nd'],
                    ma_sach=ma_sach,
                    so_ngay_muon=14
                )
                
                # Thông báo thành công phù hợp loại sách
                if is_online:
                    messagebox.showinfo("Thành công", 
                                       f"Mượn sách online thành công!\n\nMã phiếu: #{ma_phieu}\n🌐 Bạn có thể đọc ngay trong tab 'Sách đang mượn'\n\nBấm nút 'Đọc Online' để mở sách.")
                else:
                    messagebox.showinfo("Thành công", 
                                       f"Mượn sách thành công!\n\nMã phiếu: #{ma_phieu}\n📚 Vui lòng đến thư viện để nhận sách.")
                
                # Reload data
                self.load_all_books()
                self.load_borrowing(self.user['ma_nd'])
                
                # Chuyển sang tab sách đang mượn
                self.tabview.set("📖 Sách đang mượn")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể mượn sách: {str(e)}")
                
    def on_borrowing_select(self, event):
        """Xử lý khi chọn sách đang mượn"""
        selection = self.borrowing_tree.selection()
        if selection:
            self.return_book_btn.configure(state="normal")
            
            # Kiểm tra xem có phải sách online không
            item = self.borrowing_tree.item(selection[0])
            ma_phieu = item['values'][0]
            loai_sach = item['values'][5]  # Cột loại sách
            
            # Bật nút "Đọc Online" nếu là sách online và có URL
            if "Online" in str(loai_sach) and ma_phieu in getattr(self, 'borrowing_urls', {}):
                self.read_online_btn.configure(state="normal")
            else:
                self.read_online_btn.configure(state="disabled")
        else:
            self.return_book_btn.configure(state="disabled")
            self.read_online_btn.configure(state="disabled")
            
    def open_online_book(self):
        """Mở link sách online"""
        selection = self.borrowing_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách online!")
            return
            
        item = self.borrowing_tree.item(selection[0])
        ma_phieu = item['values'][0]
        tieu_de = item['values'][1]
        
        # Lấy URL từ dictionary đã lưu
        url = getattr(self, 'borrowing_urls', {}).get(ma_phieu)
        
        if url:
            import webbrowser
            webbrowser.open(url)
            messagebox.showinfo("Đọc sách online", f"Đang mở sách:\n📖 {tieu_de}\n\n🔗 {url}")
        else:
            messagebox.showwarning("Thông báo", "Không tìm thấy link sách online!")
            
    def return_selected_book(self):
        """Trả sách đã chọn"""
        selection = self.borrowing_tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách cần trả!")
            return
            
        item = self.borrowing_tree.item(selection[0])
        ma_phieu = item['values'][0]
        tieu_de = item['values'][1]
        trang_thai = item['values'][6]  # Index 6 sau khi thêm cột loại sách
        
        # Tính tiền phạt nếu quá hạn
        tien_phat = calculate_fine(ma_phieu)
        
        # Hiển thị thông tin và xác nhận
        if tien_phat > 0:
            confirm_msg = f"Bạn có muốn trả sách:\n\n📖 {tieu_de}\n\n⚠️ Sách quá hạn!\n💰 Tiền phạt: {tien_phat:,.0f}đ\n\n(Vui lòng đến thư viện để thanh toán tiền phạt)"
        else:
            confirm_msg = f"Bạn có muốn trả sách:\n\n📖 {tieu_de}\n\n✅ Trả đúng hạn - Không phạt"
        
        if messagebox.askyesno("Xác nhận trả sách", confirm_msg):
            try:
                result = return_book(ma_phieu, tien_phat)
                
                if result:
                    if tien_phat > 0:
                        messagebox.showinfo("Thành công", 
                                           f"Trả sách thành công!\n\nMã phiếu: #{ma_phieu}\n💰 Tiền phạt: {tien_phat:,.0f}đ\n\nVui lòng đến thư viện để thanh toán.")
                    else:
                        messagebox.showinfo("Thành công", 
                                           f"Trả sách thành công!\n\nMã phiếu: #{ma_phieu}\n✅ Cảm ơn bạn đã trả đúng hạn!")
                    
                    # Reload data
                    self.load_borrowing(self.user['ma_nd'])
                    self.load_history(self.user['ma_nd'])
                    self.load_all_books()
                    
                    # Disable nút trả sách
                    self.return_book_btn.configure(state="disabled")
                else:
                    messagebox.showerror("Lỗi", "Không thể trả sách. Vui lòng thử lại!")
                    
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể trả sách: {str(e)}")