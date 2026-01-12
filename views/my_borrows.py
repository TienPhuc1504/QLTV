"""
My Borrows - Quản lý sách đã mượn và lịch sử (dành cho đọc giả)
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_reader_borrow_history
from utils import treeview_sort_column, center_window


class MyBorrows(ctk.CTkFrame):
    """Giao diện quản lý sách đã mượn cho đọc giả"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.borrowing_urls = {}
        
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📚 Sách đã mượn",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Tabs
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Tab 1: Sách đang mượn
        tab1 = self.tabview.add("📖 Đang mượn")
        self.create_borrowing_tab(tab1)
        
        # Tab 2: Lịch sử mượn
        tab2 = self.tabview.add("📜 Lịch sử")
        self.create_history_tab(tab2)
        
    def create_borrowing_tab(self, parent):
        """Tạo tab sách đang mượn"""
        # Tree frame
        tree_frame = ctk.CTkFrame(parent)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ma_phieu", "tieu_de", "tac_gia", "ngay_muon", "ngay_hen_tra", "loai_sach", "trang_thai")
        self.borrowing_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)
        
        # Headings with sorting
        borrowing_headings = {
            "ma_phieu": "Mã phiếu",
            "tieu_de": "Tên sách",
            "tac_gia": "Tác giả",
            "ngay_muon": "Ngày mượn",
            "ngay_hen_tra": "Hạn trả",
            "loai_sach": "Loại sách",
            "trang_thai": "Trạng thái"
        }
        for col, text in borrowing_headings.items():
            self.borrowing_tree.heading(col, text=text, 
                            command=lambda t=self.borrowing_tree, c=col: treeview_sort_column(t, c, False))
        
        self.borrowing_tree.column("ma_phieu", width=70, anchor="center")
        self.borrowing_tree.column("tieu_de", width=200)
        self.borrowing_tree.column("tac_gia", width=130)
        self.borrowing_tree.column("ngay_muon", width=100, anchor="center")
        self.borrowing_tree.column("ngay_hen_tra", width=100, anchor="center")
        self.borrowing_tree.column("loai_sach", width=90, anchor="center")
        self.borrowing_tree.column("trang_thai", width=100, anchor="center")
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.borrowing_tree.yview)
        self.borrowing_tree.configure(yscrollcommand=scrollbar.set)
        
        self.borrowing_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.borrowing_tree.bind('<<TreeviewSelect>>', self.on_borrowing_select)
        self.borrowing_tree.bind('<Double-1>', self.on_borrowing_double_click)
        
        # Action frame
        action_frame = ctk.CTkFrame(parent, fg_color="transparent")
        action_frame.pack(fill="x", padx=10, pady=10)
        
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
        
        ctk.CTkButton(
            action_frame,
            text="🔄 Làm mới",
            command=self.load_data,
            width=100
        ).pack(side="left", padx=5)
        
        # Note
        note = ctk.CTkLabel(
            action_frame,
            text="💡 Sách online có thể đọc trực tiếp qua link. Để trả sách, vui lòng liên hệ nhân viên thư viện.",
            text_color="gray"
        )
        note.pack(side="right", padx=10)
        
    def create_history_tab(self, parent):
        """Tạo tab lịch sử mượn"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ("ma_phieu", "tieu_de", "ngay_muon", "ngay_hen_tra", "ngay_tra", "tien_phat")
        self.history_tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        
        # Headings with sorting
        history_headings = {
            "ma_phieu": "Mã phiếu",
            "tieu_de": "Tên sách",
            "ngay_muon": "Ngày mượn",
            "ngay_hen_tra": "Hạn trả",
            "ngay_tra": "Ngày trả",
            "tien_phat": "Tiền phạt"
        }
        for col, text in history_headings.items():
            self.history_tree.heading(col, text=text, 
                            command=lambda t=self.history_tree, c=col: treeview_sort_column(t, c, False))
        
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
        
        # Bind double-click event
        self.history_tree.bind('<Double-1>', self.on_history_double_click)
        
    def load_data(self):
        """Tải dữ liệu"""
        try:
            self.load_borrowing()
            self.load_history()
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"Error loading data: {e}")
        
    def load_borrowing(self):
        """Tải sách đang mượn"""
        for item in self.borrowing_tree.get_children():
            self.borrowing_tree.delete(item)
            
        history = get_reader_borrow_history(self.user['ma_nd'])
        
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
                
    def load_history(self):
        """Tải lịch sử mượn"""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        history = get_reader_borrow_history(self.user['ma_nd'])
        
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
                
    def on_borrowing_select(self, event):
        """Xử lý khi chọn sách đang mượn"""
        selection = self.borrowing_tree.selection()
        if selection:
            # Kiểm tra xem có phải sách online không
            item = self.borrowing_tree.item(selection[0])
            ma_phieu = item['values'][0]
            loai_sach = item['values'][5]  # Cột loại sách
            
            # Bật nút "Đọc Online" nếu là sách online và có URL
            if "Online" in str(loai_sach) and ma_phieu in self.borrowing_urls:
                self.read_online_btn.configure(state="normal")
            else:
                self.read_online_btn.configure(state="disabled")
        else:
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
        url = self.borrowing_urls.get(ma_phieu)
        
        if url:
            import webbrowser
            webbrowser.open(url)
            messagebox.showinfo("Đọc sách online", f"Đang mở sách:\n📖 {tieu_de}\n\n🔗 {url}")
        else:
            messagebox.showwarning("Thông báo", "Không tìm thấy link sách online!")
    
    def on_borrowing_double_click(self, event):
        """Xử lý double-click trên bảng sách đang mượn"""
        region = self.borrowing_tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_borrow_detail_dialog(is_history=False)
    
    def on_history_double_click(self, event):
        """Xử lý double-click trên bảng lịch sử"""
        region = self.history_tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_borrow_detail_dialog(is_history=True)
    
    def show_borrow_detail_dialog(self, is_history=False):
        """Hiển thị dialog chi tiết phiếu mượn"""
        from datetime import datetime
        
        # Lấy item được chọn
        tree = self.history_tree if is_history else self.borrowing_tree
        selection = tree.selection()
        if not selection:
            return
        
        item = tree.item(selection[0])
        values = item['values']
        ma_phieu = values[0]
        
        # Lấy thông tin đầy đủ từ history
        history = get_reader_borrow_history(self.user['ma_nd'])
        borrow_info = None
        for h in history:
            if h['ma_phieu'] == ma_phieu:
                borrow_info = h
                break
        
        if not borrow_info:
            return
        
        # Xác định màu header và trạng thái
        is_overdue = False
        if borrow_info['trang_thai_phieu'] == 'DANG_MUON':
            ngay_hen_tra = datetime.strptime(borrow_info['ngay_hen_tra'], '%Y-%m-%d')
            if datetime.now() > ngay_hen_tra:
                is_overdue = True
                header_color = "#dc3545"
                status_text = "⚠️ Quá hạn"
            else:
                header_color = "#17a2b8"
                status_text = "📖 Đang mượn"
        else:
            header_color = "#28a745"
            status_text = "✅ Đã trả"
        
        is_online = borrow_info.get('loai_sach') == 'SACH_ONLINE'
        
        # Tạo dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("📋 Chi tiết phiếu mượn")
        dialog.transient(self)
        dialog.resizable(False, False)
        
        # Ẩn dialog trong khi build UI
        dialog.withdraw()
        
        # === HEADER ===
        header = ctk.CTkFrame(dialog, fg_color=header_color, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📋 Chi tiết phiếu mượn sách",
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
        
        book_icon = "🌐" if is_online else "📚"
        ctk.CTkLabel(
            book_inner,
            text=f"{book_icon} {borrow_info['tieu_de']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=420,
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            book_inner,
            text=f"✍️ {borrow_info['tac_gia'] or 'Chưa cập nhật'}",
            text_color="gray",
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
        
        # Status and type badges
        badge_frame = ctk.CTkFrame(frame, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 10))
        
        # Status badge
        ctk.CTkLabel(
            badge_frame,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=header_color,
            text_color="white",
            corner_radius=8,
            width=90,
            height=24
        ).pack(side="left", padx=(0, 8))
        
        # Type badge
        type_color = "#17a2b8" if is_online else "#6c757d"
        type_text = "ONLINE" if is_online else "SÁCH GIẤY"
        ctk.CTkLabel(
            badge_frame,
            text=type_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=type_color,
            text_color="white",
            corner_radius=8,
            width=85,
            height=24
        ).pack(side="left")
        
        # Info grid
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)
        
        info_data = [
            ("📌 Mã phiếu:", str(borrow_info['ma_phieu'])),
            ("📅 Ngày mượn:", borrow_info['ngay_muon']),
            ("⏰ Hạn trả:", borrow_info['ngay_hen_tra']),
            ("👤 Nhân viên:", borrow_info.get('ten_nhan_vien') or 'N/A'),
        ]
        
        if borrow_info['trang_thai_phieu'] == 'DA_TRA':
            info_data.append(("📆 Ngày trả:", borrow_info.get('ngay_tra_thuc') or 'N/A'))
            if borrow_info.get('tien_phat') and borrow_info['tien_phat'] > 0:
                info_data.append(("💰 Tiền phạt:", f"{borrow_info['tien_phat']:,.0f}đ"))
        
        for i, (label_text, value_text) in enumerate(info_data):
            label = ctk.CTkLabel(
                info_frame,
                text=label_text,
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w"
            )
            label.grid(row=i, column=0, sticky="w", pady=6, padx=(0, 15))
            
            # Highlight ngày trả nếu quá hạn
            text_color = None
            if "Hạn trả" in label_text and is_overdue:
                text_color = "#dc3545"
            
            value = ctk.CTkLabel(
                info_frame,
                text=value_text,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                anchor="w"
            )
            value.grid(row=i, column=1, sticky="w", pady=6)
        
        # Tính số ngày còn lại hoặc quá hạn
        if borrow_info['trang_thai_phieu'] == 'DANG_MUON':
            ngay_hen_tra = datetime.strptime(borrow_info['ngay_hen_tra'], '%Y-%m-%d')
            now = datetime.now()
            delta = ngay_hen_tra - now
            
            if is_overdue:
                days_overdue = abs(delta.days)
                deadline_frame = ctk.CTkFrame(frame, fg_color=("#ffebee", "#3d1a1a"), corner_radius=8)
                deadline_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    deadline_frame,
                    text=f"⚠️ Bạn đã quá hạn {days_overdue} ngày. Vui lòng trả sách sớm để tránh phạt thêm!",
                    text_color=("#dc3545", "#ff6b6b"),
                    font=ctk.CTkFont(size=12),
                    wraplength=420
                ).pack(padx=12, pady=10)
            else:
                days_left = delta.days
                deadline_frame = ctk.CTkFrame(frame, fg_color=("#e3f2fd", "#1a3a5c"), corner_radius=8)
                deadline_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    deadline_frame,
                    text=f"⏰ Còn {days_left} ngày nữa là đến hạn trả sách.",
                    text_color=("#1976d2", "#64b5f6"),
                    font=ctk.CTkFont(size=12),
                    wraplength=420
                ).pack(padx=12, pady=10)
        
        # URL box for online books
        if is_online and borrow_info.get('url_tai_lieu'):
            url_frame = ctk.CTkFrame(frame, fg_color=("#e8f5e9", "#1b3d1b"), corner_radius=8)
            url_frame.pack(fill="x", pady=10)
            
            url_inner = ctk.CTkFrame(url_frame, fg_color="transparent")
            url_inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                url_inner,
                text="🔗 Link đọc sách:",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                url_inner,
                text=borrow_info['url_tai_lieu'],
                text_color=("#2e7d32", "#81c784"),
                font=ctk.CTkFont(size=12),
                wraplength=400
            ).pack(anchor="w", pady=(5, 0))
        
        # Hint
        if borrow_info['trang_thai_phieu'] == 'DANG_MUON' and not is_online:
            hint_frame = ctk.CTkFrame(frame, fg_color=("#fff3e0", "#3d2e1a"), corner_radius=8)
            hint_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                hint_frame,
                text="💡 Để trả sách, vui lòng mang sách đến thư viện và liên hệ nhân viên.",
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
            width=100,
            fg_color="gray"
        ).pack(side="left")
        
        # Nút đọc online nếu là sách online
        if is_online and borrow_info.get('url_tai_lieu'):
            def open_link():
                import webbrowser
                webbrowser.open(borrow_info['url_tai_lieu'])
            
            ctk.CTkButton(
                btn_frame,
                text="🌐 Đọc ngay",
                command=open_link,
                width=130,
                fg_color="#17a2b8",
                hover_color="#138496",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="right")
        
        # Tính toán kích thước và căn giữa
        center_window(dialog, 500, 480)
        
        # Hiện dialog
        dialog.deiconify()
        dialog.grab_set()
        dialog.focus_force()
