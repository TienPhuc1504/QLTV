"""
Giao diện thống kê
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_book_statistics, get_borrow_statistics
from utils.report_generator import generate_book_statistics_report, generate_borrow_statistics_report


class StatisticsView(ctk.CTkFrame):
    """Giao diện thống kê"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        
        self.create_widgets()
        self.load_statistics()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
            # Tiêu đề
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📈 Thống kê",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Export buttons
            # Các nút xuất báo cáo
        export_books_btn = ctk.CTkButton(
            header_frame,
            text="📊 Xuất thống kê sách",
            command=self.export_book_stats,
            width=160
        )
        export_books_btn.pack(side="right", padx=5)
        
        export_borrow_btn = ctk.CTkButton(
            header_frame,
            text="📋 Xuất thống kê mượn/trả",
            command=self.export_borrow_stats,
            width=180,
            fg_color="#28a745",
            hover_color="#218838"
        )
        export_borrow_btn.pack(side="right", padx=5)
        
        # Main content - scrollable
            # Nội dung chính - có cuộn
        self.content = ctk.CTkScrollableFrame(self)
        self.content.pack(fill="both", expand=True, padx=20, pady=10)
        
    def load_statistics(self):
        """Tải và hiển thị thống kê"""
        book_stats = get_book_statistics()
        borrow_stats = get_borrow_statistics()
        
        # ================== TỔNG QUAN ==================
        overview_frame = ctk.CTkFrame(self.content)
        overview_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            overview_frame,
            text="📊 TỔNG QUAN",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Cards
            # Các thẻ thông tin
        cards_frame = ctk.CTkFrame(overview_frame, fg_color="transparent")
        cards_frame.pack(fill="x", padx=20, pady=10)
        
        # Card data
            # Dữ liệu thẻ
        card_data = [
            ("📚", "Tổng số sách", str(book_stats.get('total_books', 0)), "#3498db"),
            ("📖", "Đang được mượn", str(borrow_stats.get('by_status', {}).get('DANG_MUON', 0)), "#2ecc71"),
            ("⚠️", "Phiếu quá hạn", str(borrow_stats.get('overdue', 0)), "#e74c3c"),
            ("💰", "Tổng tiền phạt", f"{borrow_stats.get('total_fines', 0):,.0f}đ", "#f39c12"),
        ]
        
        for i, (icon, title, value, color) in enumerate(card_data):
            card = ctk.CTkFrame(cards_frame, fg_color=color, corner_radius=10)
            card.pack(side="left", fill="both", expand=True, padx=5)
            
            ctk.CTkLabel(card, text=icon, font=ctk.CTkFont(size=30), text_color="white").pack(pady=(15, 5))
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=20, weight="bold"), text_color="white").pack()
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="white").pack(pady=(0, 15))
        
        # ================== SÁCH THEO TRẠNG THÁI ==================
        status_frame = ctk.CTkFrame(self.content)
        status_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            status_frame,
            text="📖 SÁCH THEO TRẠNG THÁI",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=20, pady=(0, 15))
        
        by_status = book_stats.get('by_status', {})
        status_map = {
            'CO_SAN': ('Có sẵn', '#28a745'),
            'DA_MUON': ('Đã mượn', '#ffc107'),
            'HONG': ('Hỏng', '#dc3545'),
            'MAT': ('Mất', '#6c757d')
        }
        
        for status, count in by_status.items():
            name, color = status_map.get(status, (status, '#6c757d'))
            
            row = ctk.CTkFrame(status_content, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(row, text=name, width=100, anchor="w").pack(side="left")
            
            # Progress bar simulation
                # Mô phỏng thanh tiến trình
            bar_frame = ctk.CTkFrame(row, fg_color="#e0e0e0", height=20, corner_radius=5)
            bar_frame.pack(side="left", fill="x", expand=True, padx=10)
            bar_frame.pack_propagate(False)
            
            total = book_stats.get('total_books', 1) or 1
            width_percent = (count / total) * 100
            
            if width_percent > 0:
                bar = ctk.CTkFrame(bar_frame, fg_color=color, corner_radius=5)
                bar.place(relx=0, rely=0, relwidth=width_percent/100, relheight=1)
            
            ctk.CTkLabel(row, text=str(count), width=50, anchor="e").pack(side="right")
        
        # ================== SÁCH THEO THỂ LOẠI ==================
        category_frame = ctk.CTkFrame(self.content)
        category_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            category_frame,
            text="📁 SÁCH THEO THỂ LOẠI",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Table
            # Bảng
        table_frame = ctk.CTkFrame(category_frame)
        table_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        columns = ("the_loai", "so_luong", "ty_le")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        
        tree.heading("the_loai", text="Thể loại")
        tree.heading("so_luong", text="Số lượng")
        tree.heading("ty_le", text="Tỷ lệ")
        
        tree.column("the_loai", width=200)
        tree.column("so_luong", width=100, anchor="center")
        tree.column("ty_le", width=100, anchor="center")
        
        tree.pack(fill="x")
        
        by_category = book_stats.get('by_category', [])
        total = book_stats.get('total_books', 1) or 1
        
        for name, count in by_category:
            ty_le = f"{(count / total) * 100:.1f}%"
            tree.insert("", "end", values=(name, count, ty_le))
        
        # ================== SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT ==================
        popular_frame = ctk.CTkFrame(self.content)
        popular_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            popular_frame,
            text="🔥 TOP SÁCH ĐƯỢC MƯỢN NHIỀU NHẤT",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        # Table
            # Bảng
        table_frame2 = ctk.CTkFrame(popular_frame)
        table_frame2.pack(fill="x", padx=20, pady=(0, 15))
        
        columns2 = ("stt", "tieu_de", "tac_gia", "luot_muon")
        tree2 = ttk.Treeview(table_frame2, columns=columns2, show="headings", height=8)
        
        tree2.heading("stt", text="STT")
        tree2.heading("tieu_de", text="Tên sách")
        tree2.heading("tac_gia", text="Tác giả")
        tree2.heading("luot_muon", text="Lượt mượn")
        
        tree2.column("stt", width=50, anchor="center")
        tree2.column("tieu_de", width=300)
        tree2.column("tac_gia", width=150)
        tree2.column("luot_muon", width=100, anchor="center")
        
        tree2.pack(fill="x")
        
        most_borrowed = book_stats.get('most_borrowed', [])
        
        for i, (title, author, count) in enumerate(most_borrowed, 1):
            tree2.insert("", "end", values=(i, title, author or 'N/A', count))
        
        # ================== THỐNG KÊ MƯỢN TRẢ ==================
        borrow_frame = ctk.CTkFrame(self.content)
        borrow_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            borrow_frame,
            text="📋 THỐNG KÊ MƯỢN TRẢ",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 10))
        
        borrow_content = ctk.CTkFrame(borrow_frame, fg_color="transparent")
        borrow_content.pack(fill="x", padx=20, pady=(0, 15))
        
        borrow_by_status = borrow_stats.get('by_status', {})
        borrow_status_map = {
            'DANG_MUON': ('Đang mượn', '#ffc107'),
            'DA_TRA': ('Đã trả', '#28a745'),
            'QUA_HAN': ('Quá hạn', '#dc3545')
        }
        
        borrow_total = borrow_stats.get('total_borrows', 1) or 1
        
        for status, count in borrow_by_status.items():
            name, color = borrow_status_map.get(status, (status, '#6c757d'))
            
            row = ctk.CTkFrame(borrow_content, fg_color="transparent")
            row.pack(fill="x", pady=3)
            
            ctk.CTkLabel(row, text=name, width=100, anchor="w").pack(side="left")
            
            bar_frame = ctk.CTkFrame(row, fg_color="#e0e0e0", height=20, corner_radius=5)
            bar_frame.pack(side="left", fill="x", expand=True, padx=10)
            bar_frame.pack_propagate(False)
            
            width_percent = (count / borrow_total) * 100
            
            if width_percent > 0:
                bar = ctk.CTkFrame(bar_frame, fg_color=color, corner_radius=5)
                bar.place(relx=0, rely=0, relwidth=width_percent/100, relheight=1)
            
            ctk.CTkLabel(row, text=str(count), width=50, anchor="e").pack(side="right")
            
    def export_book_stats(self):
        """Xuất thống kê sách ra PDF"""
        try:
            stats = get_book_statistics()
            output_path = generate_book_statistics_report(stats)
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo:\n{output_path}")
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {str(e)}")
            
    def export_borrow_stats(self):
        """Xuất thống kê mượn trả ra PDF"""
        try:
            stats = get_borrow_statistics()
            output_path = generate_borrow_statistics_report(stats)
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo:\n{output_path}")
            os.startfile(output_path)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất báo cáo: {str(e)}")
