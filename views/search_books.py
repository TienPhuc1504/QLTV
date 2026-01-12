"""
Search Books - Tìm và mượn sách (dành cho đọc giả) - Giao diện trực quan
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import (get_reader_by_id, get_all_books, create_borrow_request, 
                      get_book_by_id, get_all_categories)
from utils import center_window


class BookCard(ctk.CTkFrame):
    """Widget card hiển thị thông tin sách"""
    
    def __init__(self, parent, book, on_click, on_borrow, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.book = book
        self.on_click = on_click
        self.on_borrow = on_borrow
        self._is_hovered = False
        self._last_click_time = 0  # Timestamp của click cuối
        self._hover_after_id = None  # ID của after callback để debounce
        
        self.configure(
            corner_radius=12,
            border_width=2,
            border_color=("#e0e0e0", "#404040"),
            fg_color=("#ffffff", "#2b2b2b")
        )
        
        self.create_widgets()
        
        # Bind events cho card và tất cả widget con
        self._bind_hover_recursive(self)
        self._bind_click_recursive(self)
        
    def create_widgets(self):
        book = self.book
        is_online = book['loai_sach'] == 'SACH_ONLINE'
        
        # Kiểm tra sách có khả dụng không
        # - Sách online: luôn có sẵn
        # - Sách giấy: cần có quyển có sẵn
        if is_online:
            is_available = True
        else:
            # Sử dụng so_quyen_co_san thay vì so_luong
            so_quyen_co_san = book.get('so_quyen_co_san', book.get('so_luong', 0))
            is_available = so_quyen_co_san > 0
        
        # Header với loại sách và trạng thái
        header = ctk.CTkFrame(self, fg_color="transparent", height=30)
        header.pack(fill="x", padx=10, pady=(10, 5))
        header.pack_propagate(False)
        
        # Badge loại sách
        if is_online:
            type_badge = ctk.CTkLabel(
                header,
                text="🌐 ONLINE",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#17a2b8",
                text_color="white",
                corner_radius=8,
                width=70,
                height=22
            )
        else:
            type_badge = ctk.CTkLabel(
                header,
                text="📚 GIẤY",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#6c757d",
                text_color="white",
                corner_radius=8,
                width=60,
                height=22
            )
        type_badge.pack(side="left")
        
        # Badge miễn phí cho sách online
        if is_online:
            free_badge = ctk.CTkLabel(
                header,
                text="✨ MIỄN PHÍ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color="#28a745",
                text_color="white",
                corner_radius=8,
                width=75,
                height=22
            )
            free_badge.pack(side="left", padx=5)
        
        # Badge trạng thái
        if is_available:
            if is_online:
                status_badge = ctk.CTkLabel(
                    header,
                    text="✅ Có sẵn",
                    font=ctk.CTkFont(size=10),
                    text_color="#28a745"
                )
            else:
                so_quyen_co_san = book.get('so_quyen_co_san', book.get('so_luong', 0))
                status_badge = ctk.CTkLabel(
                    header,
                    text=f"✅ Còn {so_quyen_co_san}",
                    font=ctk.CTkFont(size=10),
                    text_color="#28a745"
                )
        else:
            status_badge = ctk.CTkLabel(
                header,
                text="❌ Hết",
                font=ctk.CTkFont(size=10),
                text_color="#dc3545"
            )
        status_badge.pack(side="right")
        
        # Tiêu đề sách
        title_label = ctk.CTkLabel(
            self,
            text=book['tieu_de'],
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=220,
            justify="left",
            anchor="w"
        )
        title_label.pack(fill="x", padx=10, pady=(5, 2))
        
        # Tác giả
        author_label = ctk.CTkLabel(
            self,
            text=f"✍️ {book['tac_gia'] or 'Chưa cập nhật'}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        author_label.pack(fill="x", padx=10)
        
        # Thể loại
        category_label = ctk.CTkLabel(
            self,
            text=f"📂 {book['ten_the_loai'] or 'Chưa phân loại'}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        )
        category_label.pack(fill="x", padx=10, pady=(0, 8))
        
        # Nút mượn
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        if is_online:
            # Sách online - Đọc ngay (miễn phí)
            if is_available:
                self.action_btn = ctk.CTkButton(
                    btn_frame,
                    text="📖 Đọc ngay",
                    command=lambda: self.on_borrow(book, is_premium=False),
                    width=100,
                    height=28,
                    fg_color="#17a2b8",
                    hover_color="#138496",
                    font=ctk.CTkFont(size=11, weight="bold")
                )
            else:
                self.action_btn = ctk.CTkButton(
                    btn_frame,
                    text="Không khả dụng",
                    width=100,
                    height=28,
                    fg_color="#6c757d",
                    state="disabled",
                    font=ctk.CTkFont(size=11)
                )
            self.action_btn.pack(side="left")
        else:
            # Sách giấy - Yêu cầu mượn
            if is_available:
                self.action_btn = ctk.CTkButton(
                    btn_frame,
                    text="📥 Mượn sách",
                    command=lambda: self.on_borrow(book, is_premium=False),
                    width=100,
                    height=28,
                    fg_color="#28a745",
                    hover_color="#218838",
                    font=ctk.CTkFont(size=11, weight="bold")
                )
            else:
                self.action_btn = ctk.CTkButton(
                    btn_frame,
                    text="Hết sách",
                    width=100,
                    height=28,
                    fg_color="#6c757d",
                    state="disabled",
                    font=ctk.CTkFont(size=11)
                )
            self.action_btn.pack(side="left")
    
    def _bind_hover_recursive(self, widget):
        """Bind hover events cho tất cả widget con"""
        widget.bind("<Enter>", self._on_enter, add="+")
        widget.bind("<Leave>", self._on_leave, add="+")
        
        for child in widget.winfo_children():
            self._bind_hover_recursive(child)
    
    def _bind_click_recursive(self, widget, inside_button=False):
        """Bind click events cho widget và tất cả widget con"""
        # Kiểm tra nếu widget là button
        widget_class = widget.winfo_class()
        is_button = widget_class in ['CTkButton', 'Button'] or 'button' in str(type(widget)).lower()
        
        # Chỉ bind click nếu không phải button và không ở trong button
        if not inside_button and not is_button:
            widget.bind("<Button-1>", self._on_widget_click, add="+")
        
        # Bind cho tất cả widget con
        for child in widget.winfo_children():
            self._bind_click_recursive(child, inside_button=inside_button or is_button)
    
    def _is_mouse_inside_card(self):
        """Kiểm tra xem chuột có đang ở trong card không"""
        try:
            # Lấy vị trí chuột trên màn hình
            mouse_x = self.winfo_pointerx()
            mouse_y = self.winfo_pointery()
            
            # Lấy vị trí và kích thước của card
            card_x = self.winfo_rootx()
            card_y = self.winfo_rooty()
            card_width = self.winfo_width()
            card_height = self.winfo_height()
            
            # Kiểm tra chuột có nằm trong card không
            return (card_x <= mouse_x <= card_x + card_width and 
                    card_y <= mouse_y <= card_y + card_height)
        except:
            return False
    
    def _is_widget_inside_button(self, widget):
        """Kiểm tra xem widget có nằm trong button không"""
        parent = widget
        while parent:
            try:
                parent_class = parent.winfo_class()
                if parent_class in ['CTkButton', 'Button'] or 'button' in str(type(parent)).lower():
                    return True
                if parent == self:
                    return False
                parent = parent.master
            except:
                return False
        return False
    
    def _on_widget_click(self, event):
        """Xử lý click trên card - dùng timestamp để tránh duplicate"""
        import time
        
        # Kiểm tra không phải button hoặc widget bên trong button
        if self._is_widget_inside_button(event.widget):
            return
        
        # Dùng timestamp để tránh xử lý cùng 1 click nhiều lần
        current_time = time.time() * 1000
        if current_time - self._last_click_time < 500:
            return
            
        self._last_click_time = current_time
        
        # Reset hover state
        self._is_hovered = False
        self.configure(border_color=("#e0e0e0", "#404040"))
        
        # Gọi callback
        self.on_click(self.book)
        
    def _on_enter(self, event):
        """Xử lý khi chuột vào card hoặc widget con"""
        # Hủy bỏ timer leave đang chờ (nếu có)
        if self._hover_after_id:
            self.after_cancel(self._hover_after_id)
            self._hover_after_id = None
        
        # Set hover state ngay lập tức
        if not self._is_hovered:
            import time
            current_time = time.time() * 1000
            if current_time - self._last_click_time > 200:
                self._is_hovered = True
                self.configure(border_color=("#1f538d", "#5294e2"))
        
    def _on_leave(self, event):
        """Xử lý khi chuột rời khỏi widget - dùng delay để tránh flicker"""
        # Hủy timer cũ nếu có
        if self._hover_after_id:
            self.after_cancel(self._hover_after_id)
        
        # Đặt timer ngắn để kiểm tra xem chuột có thực sự rời khỏi card không
        self._hover_after_id = self.after(10, self._check_and_reset_hover)
    
    def _check_and_reset_hover(self):
        """Kiểm tra và reset hover state nếu chuột đã rời khỏi card"""
        self._hover_after_id = None
        
        # Chỉ reset hover nếu chuột thực sự ở ngoài card
        if not self._is_mouse_inside_card():
            self._is_hovered = False
            self.configure(border_color=("#e0e0e0", "#404040"))


class SearchBooks(ctk.CTkFrame):
    """Giao diện tìm và mượn sách cho đọc giả - Phiên bản trực quan"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_book = None
        self.book_cards = []
        self.current_view = "grid"  # grid or list
        
        self.create_widgets()
        self.load_books()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="📚 Tìm và Mượn sách",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Quick stats
        stats_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        stats_frame.pack(side="right")
        
        self.stats_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.stats_label.pack()
        
        # Search and Filter frame
        filter_frame = ctk.CTkFrame(self, fg_color=("#f0f0f0", "#333333"), corner_radius=10)
        filter_frame.pack(fill="x", padx=20, pady=10)
        
        filter_inner = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_inner.pack(fill="x", padx=15, pady=12)
        
        # Search
        self.search_entry = ctk.CTkEntry(
            filter_inner,
            placeholder_text="🔍 Tìm theo tên sách, tác giả...",
            width=280,
            height=35
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.filter_books())
        
        # Category filter
        ctk.CTkLabel(filter_inner, text="Thể loại:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(20, 5))
        
        self.categories = get_all_categories()
        category_names = ["📁 Tất cả"] + [c['ten_the_loai'] for c in self.categories]
        
        self.category_var = ctk.StringVar(value="📁 Tất cả")
        self.category_combo = ctk.CTkComboBox(
            filter_inner,
            values=category_names,
            variable=self.category_var,
            command=lambda e: self.filter_books(),
            width=140,
            height=35
        )
        self.category_combo.pack(side="left")
        
        # Book type filter
        ctk.CTkLabel(filter_inner, text="Loại:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15, 5))
        
        self.book_type_var = ctk.StringVar(value="Tất cả")
        self.book_type_combo = ctk.CTkComboBox(
            filter_inner,
            values=["Tất cả", "🌐 Sách online", "📚 Sách giấy"],
            variable=self.book_type_var,
            command=lambda e: self.filter_books(),
            width=130,
            height=35
        )
        self.book_type_combo.pack(side="left")
        
        # Status filter
        ctk.CTkLabel(filter_inner, text="Trạng thái:", font=ctk.CTkFont(size=12)).pack(side="left", padx=(15, 5))
        
        self.status_var = ctk.StringVar(value="Tất cả")
        self.status_combo = ctk.CTkComboBox(
            filter_inner,
            values=["Tất cả", "✅ Có sẵn", "❌ Hết sách"],
            variable=self.status_var,
            command=lambda e: self.filter_books(),
            width=120,
            height=35
        )
        self.status_combo.pack(side="left")
        
        # Reset button
        ctk.CTkButton(
            filter_inner,
            text="🔄 Đặt lại",
            command=self.reset_filters,
            width=80,
            height=35,
            fg_color="transparent",
            border_width=1,
            text_color=("gray", "white"),
            hover_color=("#e0e0e0", "#404040")
        ).pack(side="right")
        
        # View toggle buttons
        view_frame = ctk.CTkFrame(filter_inner, fg_color="transparent")
        view_frame.pack(side="right", padx=10)
        
        self.grid_btn = ctk.CTkButton(
            view_frame,
            text="⊞",
            width=35,
            height=35,
            command=lambda: self.toggle_view("grid"),
            fg_color=("#1f538d", "#1f538d")
        )
        self.grid_btn.pack(side="left", padx=2)
        
        self.list_btn = ctk.CTkButton(
            view_frame,
            text="☰",
            width=35,
            height=35,
            command=lambda: self.toggle_view("list"),
            fg_color="transparent",
            border_width=1,
            text_color=("gray", "white")
        )
        self.list_btn.pack(side="left", padx=2)
        
        # Books container (scrollable)
        self.books_container = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.books_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Grid frame inside scrollable
        self.grid_frame = ctk.CTkFrame(self.books_container, fg_color="transparent")
        self.grid_frame.pack(fill="both", expand=True)
        
        # Note at bottom
        note_frame = ctk.CTkFrame(self, fg_color=("#e8f5e9", "#1b3d1b"), corner_radius=8)
        note_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        ctk.CTkLabel(
            note_frame,
            text="💡 Sách online có thể đọc ngay miễn phí. Sách giấy cần gửi yêu cầu mượn và nhân viên sẽ xác nhận.",
            text_color=("#2e7d32", "#81c784"),
            font=ctk.CTkFont(size=12)
        ).pack(pady=8, padx=15)
        
    def toggle_view(self, view_type):
        """Chuyển đổi giữa grid và list view"""
        self.current_view = view_type
        
        if view_type == "grid":
            self.grid_btn.configure(fg_color=("#1f538d", "#1f538d"), border_width=0)
            self.list_btn.configure(fg_color="transparent", border_width=1)
        else:
            self.list_btn.configure(fg_color=("#1f538d", "#1f538d"), border_width=0)
            self.grid_btn.configure(fg_color="transparent", border_width=1)
        
        self.filter_books()
        
    def load_books(self):
        """Tải danh sách sách"""
        self.filter_books()
    
    def reset_filters(self):
        """Reset bộ lọc"""
        self.search_entry.delete(0, 'end')
        self.category_var.set("📁 Tất cả")
        self.book_type_var.set("Tất cả")
        self.status_var.set("Tất cả")
        self.filter_books()
            
    def filter_books(self):
        """Lọc và hiển thị sách"""
        # Clear current cards
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self.book_cards.clear()
        
        books = get_all_books()
        
        search_term = self.search_entry.get().lower()
        category_filter = self.category_var.get()
        book_type_filter = self.book_type_var.get()
        status_filter = self.status_var.get()
        
        filtered_books = []
        
        for book in books:
            # Lọc theo từ khóa
            if search_term:
                if (search_term not in book['tieu_de'].lower() and 
                    search_term not in (book['tac_gia'] or '').lower() and
                    search_term not in (book['ten_the_loai'] or '').lower()):
                    continue
            
            # Lọc theo thể loại
            if category_filter != "📁 Tất cả":
                if book['ten_the_loai'] != category_filter:
                    continue
            
            # Lọc theo loại sách
            if "online" in book_type_filter.lower() and book['loai_sach'] != 'SACH_ONLINE':
                continue
            elif "giấy" in book_type_filter.lower() and book['loai_sach'] != 'SACH_GIAY':
                continue
            
            # Lọc theo trạng thái
            is_available = book['so_luong'] > 0
            if "Có sẵn" in status_filter and not is_available:
                continue
            elif "Hết" in status_filter and is_available:
                continue
            
            filtered_books.append(book)
        
        # Update stats
        total_online = sum(1 for b in filtered_books if b['loai_sach'] == 'SACH_ONLINE')
        total_paper = len(filtered_books) - total_online
        self.stats_label.configure(
            text=f"📊 Tìm thấy {len(filtered_books)} sách ({total_online} online, {total_paper} giấy)"
        )
        
        # Display based on view type
        if self.current_view == "grid":
            self._display_grid(filtered_books)
        else:
            self._display_list(filtered_books)
            
    def _display_grid(self, books):
        """Hiển thị sách dạng grid"""
        cols = 4  # 4 cột
        
        for idx, book in enumerate(books):
            row = idx // cols
            col = idx % cols
            
            card = BookCard(
                self.grid_frame,
                book,
                on_click=self.view_book_detail,
                on_borrow=self.handle_borrow_action,
                width=250,
                height=180
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.book_cards.append(card)
        
        # Configure grid weights
        for i in range(cols):
            self.grid_frame.columnconfigure(i, weight=1)
            
    def _display_list(self, books):
        """Hiển thị sách dạng list"""
        for book in books:
            card = self._create_list_item(book)
            card.pack(fill="x", pady=4)
            self.book_cards.append(card)
            
    def _create_list_item(self, book):
        """Tạo item cho list view"""
        is_online = book['loai_sach'] == 'SACH_ONLINE'
        is_available = book['so_luong'] > 0
        
        frame = ctk.CTkFrame(
            self.grid_frame, 
            corner_radius=8,
            border_width=1,
            border_color=("#e0e0e0", "#404040"),
            height=60
        )
        frame.pack_propagate(False)
        
        # Bind click event vào frame list item
        def on_list_item_click(event):
            if event.widget.winfo_class() not in ['CTkButton', 'Button']:
                self.view_book_detail(book)
        
        frame.bind("<Button-1>", on_list_item_click, add="+")
        
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=15, pady=8)
        inner.bind("<Button-1>", on_list_item_click, add="+")
        
        # Left: Info
        info_frame = ctk.CTkFrame(inner, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)
        info_frame.bind("<Button-1>", on_list_item_click, add="+")
        
        # Title row with badges
        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(fill="x")
        title_row.bind("<Button-1>", on_list_item_click, add="+")
        
        # Badge loại sách
        if is_online:
            ctk.CTkLabel(
                title_row,
                text="🌐",
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=(0, 5))
            
            ctk.CTkLabel(
                title_row,
                text="MIỄN PHÍ",
                font=ctk.CTkFont(size=9, weight="bold"),
                fg_color="#28a745",
                text_color="white",
                corner_radius=4,
                width=55,
                height=16
            ).pack(side="left", padx=(0, 8))
        else:
            ctk.CTkLabel(
                title_row,
                text="📚",
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=(0, 5))
        
        ctk.CTkLabel(
            title_row,
            text=book['tieu_de'],
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w"
        ).pack(side="left")
        
        # Author & Category
        ctk.CTkLabel(
            info_frame,
            text=f"✍️ {book['tac_gia'] or 'N/A'} | 📂 {book['ten_the_loai'] or 'N/A'}",
            font=ctk.CTkFont(size=11),
            text_color="gray",
            anchor="w"
        ).pack(fill="x")
        
        # Right: Status & Action
        action_frame = ctk.CTkFrame(inner, fg_color="transparent")
        action_frame.pack(side="right")
        
        # Status
        if is_available:
            ctk.CTkLabel(
                action_frame,
                text=f"✅ Còn {book['so_luong']}",
                font=ctk.CTkFont(size=11),
                text_color="#28a745"
            ).pack(side="left", padx=10)
        else:
            ctk.CTkLabel(
                action_frame,
                text="❌ Hết",
                font=ctk.CTkFont(size=11),
                text_color="#dc3545"
            ).pack(side="left", padx=10)
        
        # Action button
        if is_online:
            ctk.CTkButton(
                action_frame,
                text="📖 Đọc",
                command=lambda b=book: self.handle_borrow_action(b, is_premium=False),
                width=70,
                height=30,
                fg_color="#17a2b8",
                hover_color="#138496"
            ).pack(side="left", padx=5)
        elif is_available:
            ctk.CTkButton(
                action_frame,
                text="📥 Mượn",
                command=lambda b=book: self.handle_borrow_action(b, is_premium=False),
                width=70,
                height=30,
                fg_color="#28a745",
                hover_color="#218838"
            ).pack(side="left", padx=5)
        else:
            ctk.CTkButton(
                action_frame,
                text="Hết",
                width=70,
                height=30,
                fg_color="#6c757d",
                state="disabled"
            ).pack(side="left", padx=5)
        
        # Detail button
        ctk.CTkButton(
            action_frame,
            text="👁️",
            command=lambda b=book: self.view_book_detail(b),
            width=35,
            height=30,
            fg_color="transparent",
            border_width=1,
            text_color=("gray", "white")
        ).pack(side="left", padx=2)
        
        return frame
    
    def handle_borrow_action(self, book, is_premium=False):
        """Xử lý action mượn/đọc sách"""
        from datetime import datetime
        
        if book['loai_sach'] == 'SACH_ONLINE':
            # Sách online - show read dialog
            self.show_online_book_dialog(book, is_premium)
        else:
            # Sách giấy - kiểm tra và gửi yêu cầu mượn
            self.selected_book = book['ma_sach']
            self.request_borrow_book(book)
    
    def show_online_book_dialog(self, book, is_premium=False):
        """Hiển thị dialog đọc sách online"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📖 Đọc sách Online")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 500, 480)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="#17a2b8", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📖 " + book['tieu_de'],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white",
            wraplength=450
        ).pack(expand=True)
        
        # Content - scrollable
        frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Free badge
        badge_frame = ctk.CTkFrame(frame, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            badge_frame,
            text="✨ MIỄN PHÍ",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#28a745",
            text_color="white",
            corner_radius=8,
            width=100,
            height=30
        ).pack(side="left")
        
        # Book info
        info_items = [
            ("✍️ Tác giả:", book['tac_gia'] or 'Chưa cập nhật'),
            ("📂 Thể loại:", book['ten_the_loai'] or 'Chưa phân loại'),
        ]
        
        for label, value in info_items:
            row = ctk.CTkFrame(frame, fg_color="transparent")
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(row, text=label, font=ctk.CTkFont(weight="bold"), width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=value, anchor="w").pack(side="left", padx=10)
        
        # URL
        if book.get('url_tai_lieu'):
            url_frame = ctk.CTkFrame(frame, fg_color=("#e3f2fd", "#1a3a5c"), corner_radius=8)
            url_frame.pack(fill="x", pady=15)
            
            url_inner = ctk.CTkFrame(url_frame, fg_color="transparent")
            url_inner.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                url_inner,
                text="🔗 Link đọc sách:",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w")
            
            ctk.CTkLabel(
                url_inner,
                text=book['url_tai_lieu'],
                text_color="#1976d2",
                font=ctk.CTkFont(size=12),
                wraplength=430
            ).pack(anchor="w", pady=(5, 0))
            
            def open_link():
                import webbrowser
                webbrowser.open(book['url_tai_lieu'])
                
            ctk.CTkButton(
                url_inner,
                text="🌐 Mở trong trình duyệt",
                command=open_link,
                width=160,
                fg_color="#1976d2",
                hover_color="#1565c0"
            ).pack(anchor="w", pady=(10, 0))
        
        # Premium option (for future)
        premium_frame = ctk.CTkFrame(frame, fg_color=("#fff3e0", "#3d2e1a"), corner_radius=8)
        premium_frame.pack(fill="x", pady=10)
        
        premium_inner = ctk.CTkFrame(premium_frame, fg_color="transparent")
        premium_inner.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            premium_inner,
            text="⭐ Tùy chọn Premium",
            font=ctk.CTkFont(weight="bold"),
            text_color=("#e65100", "#ffb74d")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            premium_inner,
            text="Nâng cấp lên Premium để có thêm các tính năng:",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(anchor="w")
        
        features = ["• Tải xuống PDF", "• Đọc offline", "• Không quảng cáo"]
        for f in features:
            ctk.CTkLabel(
                premium_inner,
                text=f,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w")
        
        ctk.CTkButton(
            premium_inner,
            text="⭐ Nâng cấp Premium (Sắp ra mắt)",
            width=200,
            fg_color="#ff9800",
            hover_color="#f57c00",
            state="disabled"
        ).pack(anchor="w", pady=(8, 0))
        
        # Button frame cố định ở cuối
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame,
            text="Đóng",
            command=dialog.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left")
        
        # Nút mở link nếu có URL
        if book.get('url_tai_lieu'):
            def open_link_btn():
                import webbrowser
                webbrowser.open(book['url_tai_lieu'])
                
            ctk.CTkButton(
                btn_frame,
                text="🌐 Mở đọc sách",
                command=open_link_btn,
                width=130,
                fg_color="#17a2b8",
                hover_color="#138496"
            ).pack(side="right")
            
    def view_book_detail(self, book):
        """Xem chi tiết sách - Thiết kế giống dialog Yêu cầu mượn sách"""
        # Lấy thông tin đầy đủ từ database
        full_book = get_book_by_id(book['ma_sach'])
        if full_book:
            book = full_book
        
        is_online = book['loai_sach'] == 'SACH_ONLINE'
        is_available = book['so_luong'] > 0
        
        # Xác định màu header và icon
        if is_online:
            header_color = "#17a2b8"
            book_icon = "🌐"
            type_text = "SÁCH ONLINE"
            type_color = "#17a2b8"
        else:
            header_color = "#1f538d"
            book_icon = "📚"
            type_text = "SÁCH GIẤY"
            type_color = "#6c757d"
        
        # Tạo dialog với cấu hình tối ưu
        dialog = ctk.CTkToplevel(self)
        dialog.title("📖 Chi tiết sách")
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
            text="📖 Chi tiết sách",
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
        
        # Book title
        ctk.CTkLabel(
            book_inner,
            text=f"{book_icon} {book['tieu_de']}",
            font=ctk.CTkFont(size=15, weight="bold"),
            wraplength=420,
            anchor="w"
        ).pack(fill="x")
        
        # Author & Category
        ctk.CTkLabel(
            book_inner,
            text=f"✍️ {book['tac_gia'] or 'Chưa cập nhật'}",
            text_color="gray",
            anchor="w"
        ).pack(fill="x", pady=(5, 0))
        
        # Badges row
        badge_frame = ctk.CTkFrame(frame, fg_color="transparent")
        badge_frame.pack(fill="x", pady=(0, 10))
        
        # Type badge
        ctk.CTkLabel(
            badge_frame,
            text=type_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=type_color,
            text_color="white",
            corner_radius=8,
            width=90,
            height=24
        ).pack(side="left", padx=(0, 8))
        
        # Free badge for online books
        if is_online:
            ctk.CTkLabel(
                badge_frame,
                text="✨ MIỄN PHÍ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#28a745",
                text_color="white",
                corner_radius=8,
                width=85,
                height=24
            ).pack(side="left", padx=(0, 8))
        
        # Status badge
        if is_available:
            status_text = f"✅ Còn {book['so_luong']}" if not is_online else "✅ Có sẵn"
            status_color = "#28a745"
        else:
            status_text = "❌ Hết sách"
            status_color = "#dc3545"
        
        ctk.CTkLabel(
            badge_frame,
            text=status_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=status_color,
            text_color="white",
            corner_radius=8,
            width=75,
            height=24
        ).pack(side="left")
        
        # Info grid
        info_frame = ctk.CTkFrame(frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=10)
        
        info_data = [
            ("📌 Mã sách:", str(book['ma_sach'])),
            ("📂 Thể loại:", book['ten_the_loai'] or 'Chưa phân loại'),
            ("📊 Loại sách:", "Sách online" if is_online else "Sách giấy"),
        ]
        
        if not is_online:
            info_data.append(("📦 Số lượng:", str(book['so_luong'])))
        
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
        
        # URL box for online books
        if is_online and book.get('url_tai_lieu'):
            url_frame = ctk.CTkFrame(frame, fg_color=("#e3f2fd", "#1a3a5c"), corner_radius=8)
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
                text=book['url_tai_lieu'],
                text_color=("#1976d2", "#64b5f6"),
                font=ctk.CTkFont(size=12),
                wraplength=400
            ).pack(anchor="w", pady=(5, 0))
        
        # Info hint based on book type
        if is_online:
            hint_frame = ctk.CTkFrame(frame, fg_color=("#e8f5e9", "#1b3d1b"), corner_radius=8)
            hint_frame.pack(fill="x", pady=10)
            
            ctk.CTkLabel(
                hint_frame,
                text="💡 Đây là sách online miễn phí. Bạn có thể đọc ngay mà không cần đăng ký mượn.",
                text_color=("#2e7d32", "#81c784"),
                font=ctk.CTkFont(size=11),
                wraplength=420
            ).pack(padx=12, pady=10)
        else:
            if is_available:
                hint_frame = ctk.CTkFrame(frame, fg_color=("#e8f5e9", "#1b3d1b"), corner_radius=8)
                hint_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    hint_frame,
                    text="💡 Nhấn \"Mượn sách\" để gửi yêu cầu. Sau khi được duyệt, bạn có 3 ngày để đến thư viện lấy sách.",
                    text_color=("#2e7d32", "#81c784"),
                    font=ctk.CTkFont(size=11),
                    wraplength=420
                ).pack(padx=12, pady=10)
            else:
                hint_frame = ctk.CTkFrame(frame, fg_color=("#fff3e0", "#3d2e1a"), corner_radius=8)
                hint_frame.pack(fill="x", pady=10)
                
                ctk.CTkLabel(
                    hint_frame,
                    text="⚠️ Sách hiện đã hết. Vui lòng quay lại sau hoặc chọn sách khác.",
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
        
        if is_online:
            def open_read_dialog():
                dialog.destroy()
                self.show_online_book_dialog(book)
            
            ctk.CTkButton(
                btn_frame,
                text="📖 Đọc ngay",
                command=open_read_dialog,
                width=130,
                fg_color="#17a2b8",
                hover_color="#138496",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="right")
        elif is_available:
            def borrow_and_close():
                dialog.destroy()
                self.selected_book = book['ma_sach']
                self.request_borrow_book(book)
                
            ctk.CTkButton(
                btn_frame,
                text="📥 Mượn sách",
                command=borrow_and_close,
                width=130,
                fg_color="#28a745",
                hover_color="#218838",
                font=ctk.CTkFont(weight="bold")
            ).pack(side="right")
        
        # Tính toán kích thước và căn giữa sau khi build xong UI
        center_window(dialog, 480, 450)
        
        # Hiện dialog và grab focus
        dialog.deiconify()
        dialog.grab_set()
        dialog.focus_force()
            
    def request_borrow_book(self, book=None):
        """Gửi yêu cầu mượn sách"""
        from datetime import datetime
        
        if book is None:
            if not self.selected_book:
                messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách!")
                return
            book = get_book_by_id(self.selected_book)
            
        if not book:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin sách!")
            return
        
        # Kiểm tra thẻ đọc giả
        reader = get_reader_by_id(self.user['ma_nd'])
        if not reader:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin đọc giả!")
            return
            
        if reader.get('trang_thai_the') != 'HOAT_DONG':
            messagebox.showwarning("Cảnh báo", "Thẻ đọc giả của bạn không hoạt động!\nVui lòng liên hệ thư viện để gia hạn.")
            return
        
        # Kiểm tra thẻ đọc giả hết hạn
        if reader.get('ngay_het_han'):
            try:
                ngay_het_han = datetime.strptime(reader['ngay_het_han'], '%Y-%m-%d').date()
                if ngay_het_han < datetime.now().date():
                    messagebox.showwarning(
                        "Cảnh báo", 
                        f"Thẻ đọc giả của bạn đã hết hạn ngày {reader['ngay_het_han']}!\n"
                        "Vui lòng liên hệ thư viện để gia hạn thẻ."
                    )
                    return
            except:
                pass
        
        # Hiện dialog nhập số ngày mượn
        self.show_borrow_request_dialog(book)
    
    def show_borrow_request_dialog(self, book):
        """Hiện dialog yêu cầu mượn sách"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📝 Yêu cầu mượn sách")
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog, 480, 450)
        
        # Header
        header = ctk.CTkFrame(dialog, fg_color="#28a745", height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        ctk.CTkLabel(
            header,
            text="📝 Yêu cầu mượn sách",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="white"
        ).pack(expand=True)
        
        # Content
        frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Book info card
        book_card = ctk.CTkFrame(frame, fg_color=("#f8f9fa", "#2d2d2d"), corner_radius=8)
        book_card.pack(fill="x", pady=(0, 15))
        
        book_inner = ctk.CTkFrame(book_card, fg_color="transparent")
        book_inner.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(
            book_inner,
            text="📚 " + book['tieu_de'],
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=400,
            anchor="w"
        ).pack(fill="x")
        
        ctk.CTkLabel(
            book_inner,
            text=f"✍️ {book['tac_gia'] or 'N/A'}",
            text_color="gray",
            anchor="w"
        ).pack(fill="x")
        
        # Số ngày muốn mượn
        ctk.CTkLabel(
            frame,
            text="📅 Số ngày muốn mượn: *",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(10, 5))
        
        days_frame = ctk.CTkFrame(frame, fg_color="transparent")
        days_frame.pack(fill="x", pady=(0, 10))
        
        days_entry = ctk.CTkEntry(days_frame, width=100, placeholder_text="1-30")
        days_entry.insert(0, "14")
        days_entry.pack(side="left")
        
        ctk.CTkLabel(days_frame, text="ngày (tối đa 30)", text_color="gray").pack(side="left", padx=10)
        
        # Quick select
        quick_frame = ctk.CTkFrame(frame, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(quick_frame, text="Chọn nhanh:", text_color="gray").pack(side="left")
        
        for days in [7, 14, 21, 30]:
            def set_days(d=days):
                days_entry.delete(0, 'end')
                days_entry.insert(0, str(d))
                
            ctk.CTkButton(
                quick_frame,
                text=f"{days} ngày",
                width=60,
                height=25,
                fg_color="transparent",
                border_width=1,
                text_color=("gray", "white"),
                hover_color=("#e0e0e0", "#404040"),
                command=set_days
            ).pack(side="left", padx=3)
        
        # Ghi chú
        ctk.CTkLabel(
            frame,
            text="📝 Ghi chú (tùy chọn):",
            font=ctk.CTkFont(weight="bold"),
            anchor="w"
        ).pack(fill="x", pady=(0, 5))
        
        note_textbox = ctk.CTkTextbox(frame, height=70)
        note_textbox.pack(fill="x", pady=(0, 10))
        
        # Info
        info_frame = ctk.CTkFrame(frame, fg_color=("#e8f5e9", "#1b3d1b"), corner_radius=8)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="💡 Nhân viên sẽ xác nhận yêu cầu và quyết định số ngày mượn chính thức.\n"
                 "    Bạn có 3 ngày để đến thư viện lấy sách sau khi được duyệt.",
            text_color=("#2e7d32", "#81c784"),
            font=ctk.CTkFont(size=11),
            justify="left"
        ).pack(padx=12, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        # Tạo nút submit trước để có thể reference trong hàm submit_request
        submit_btn = ctk.CTkButton(
            btn_frame, 
            text="📤 Gửi yêu cầu", 
            command=lambda: None,  # Sẽ set command sau
            fg_color="#28a745",
            hover_color="#218838",
            width=130,
            font=ctk.CTkFont(weight="bold")
        )
        
        def submit_request():
            # Disable button ngay khi click để tránh double-submit
            submit_btn.configure(state="disabled", text="⏳ Đang xử lý...")
            
            try:
                so_ngay = int(days_entry.get())
                if so_ngay <= 0 or so_ngay > 30:
                    messagebox.showwarning("Cảnh báo", "Số ngày mượn phải từ 1-30 ngày!")
                    submit_btn.configure(state="normal", text="📤 Gửi yêu cầu")
                    return
            except:
                messagebox.showwarning("Cảnh báo", "Số ngày phải là số!")
                submit_btn.configure(state="normal", text="📤 Gửi yêu cầu")
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
                    "✅ Thành công", 
                    f"Đã gửi yêu cầu mượn sách thành công!\n\n"
                    f"📖 {book['tieu_de']}\n"
                    f"📅 Số ngày đề xuất: {so_ngay} ngày\n\n"
                    f"Vui lòng chờ nhân viên thư viện xác nhận."
                )
                
                self.filter_books()
                
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
                # Enable lại button nếu có lỗi
                submit_btn.configure(state="normal", text="📤 Gửi yêu cầu")
        
        # Set command cho submit button
        submit_btn.configure(command=submit_request)
        
        ctk.CTkButton(
            btn_frame, 
            text="Hủy", 
            command=dialog.destroy, 
            fg_color="gray",
            width=100
        ).pack(side="left")
        
        submit_btn.pack(side="right")
