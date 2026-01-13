# Gói utils (tiện ích)
import customtkinter as ctk
import threading


def center_window(window, width=None, height=None):
    """
    Center một window/dialog trên màn hình
    - window: CTkToplevel hoặc CTk window
    - width, height: Kích thước (nếu None sẽ lấy từ geometry hiện tại)
    """
    window.update_idletasks()
    
    if width is None:
        width = window.winfo_width()
    if height is None:
        height = window.winfo_height()
    
    # Lấy kích thước màn hình
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    # Tính toán vị trí center
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")


def treeview_sort_column(tree, col, reverse):
    """
    Sắp xếp Treeview theo cột
    - tree: Treeview widget
    - col: Tên cột cần sắp xếp
    - reverse: True = giảm dần, False = tăng dần
    """
    # Lấy tất cả dữ liệu
    data = [(tree.set(child, col), child) for child in tree.get_children('')]
    
    # Thử sắp xếp theo số, nếu không được thì sắp xếp theo chuỗi
    try:
        data.sort(key=lambda x: float(x[0].replace(',', '').replace('đ', '').replace('∞', '999999')), reverse=reverse)
    except (ValueError, TypeError):
        data.sort(key=lambda x: x[0].lower() if isinstance(x[0], str) else str(x[0]).lower(), reverse=reverse)
    
    # Di chuyển items theo thứ tự mới
    for index, (val, child) in enumerate(data):
        tree.move(child, '', index)
    
    # Đảo ngược cho lần click tiếp theo
    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))


class LoadingDialog(ctk.CTkToplevel):
    """Dialog hiển thị loading indicator"""
    
    def __init__(self, parent, message="Đang tải..."):
        super().__init__(parent)
        
        self.title("")
        self.geometry("250x100")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Bỏ title bar trên Windows
        self.overrideredirect(True)
        
        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 125
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 50
        self.geometry(f"250x100+{x}+{y}")
        
        # Frame với border
        frame = ctk.CTkFrame(self, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Biểu tượng loading (chấm hoạt ảnh)
        self.loading_label = ctk.CTkLabel(
            frame,
            text="⏳",
            font=ctk.CTkFont(size=24)
        )
        self.loading_label.pack(pady=(15, 5))
        
        # Message
        ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=13)
        ).pack(pady=(0, 15))
        
        # Animation
        self.dots = 0
        self.animate()
        
    def animate(self):
        """Hoạt ảnh cho biểu tượng loading"""
        icons = ["⏳", "⌛"]
        self.loading_label.configure(text=icons[self.dots % 2])
        self.dots += 1
        self.after(500, self.animate)


def run_with_loading(parent, task_func, callback=None, message="Đang tải..."):
    """
    Chạy một task trong background thread với loading indicator
    
    Args:
        parent: Widget cha
        task_func: Hàm cần chạy (không có tham số)
        callback: Hàm callback sau khi hoàn thành (nhận kết quả làm tham số)
        message: Thông báo hiển thị
    """
    loading = LoadingDialog(parent, message)
    result = [None]
    error = [None]
    
    def run_task():
        try:
            result[0] = task_func()
        except Exception as e:
            error[0] = e
        finally:
            parent.after(0, finish)
    
    def finish():
        loading.destroy()
        if error[0]:
            from tkinter import messagebox
            messagebox.showerror("Lỗi", str(error[0]))
        elif callback:
            callback(result[0])
    
    thread = threading.Thread(target=run_task, daemon=True)
    thread.start()


class PaginationFrame(ctk.CTkFrame):
    """Frame phân trang"""
    
    def __init__(self, parent, total_items=0, items_per_page=20, on_page_change=None):
        super().__init__(parent, fg_color="transparent")
        
        self.total_items = total_items
        self.items_per_page = items_per_page
        self.current_page = 1
        self.on_page_change = on_page_change
        
        self.create_widgets()
        self.update_display()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Nhãn thông tin
        self.info_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.info_label.pack(side="left", padx=10)
        
        # Nút điều hướng
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(side="right", padx=10)
        
        self.first_btn = ctk.CTkButton(
            nav_frame,
            text="⏮",
            width=35,
            command=self.go_first
        )
        self.first_btn.pack(side="left", padx=2)
        
        self.prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=35,
            command=self.go_prev
        )
        self.prev_btn.pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(
            nav_frame,
            text="1 / 1",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80
        )
        self.page_label.pack(side="left", padx=10)
        
        self.next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=35,
            command=self.go_next
        )
        self.next_btn.pack(side="left", padx=2)
        
        self.last_btn = ctk.CTkButton(
            nav_frame,
            text="⏭",
            width=35,
            command=self.go_last
        )
        self.last_btn.pack(side="left", padx=2)
        
        # Items per page selector
        ctk.CTkLabel(nav_frame, text="Hiển thị:").pack(side="left", padx=(20, 5))
        
        self.per_page_var = ctk.StringVar(value=str(self.items_per_page))
        per_page_combo = ctk.CTkComboBox(
            nav_frame,
            values=["10", "20", "50", "100"],
            variable=self.per_page_var,
            width=70,
            command=self.on_per_page_change
        )
        per_page_combo.pack(side="left", padx=2)
        
    @property
    def total_pages(self):
        """Tính tổng số trang"""
        if self.total_items == 0:
            return 1
        return (self.total_items + self.items_per_page - 1) // self.items_per_page
    
    def update_display(self):
        """Cập nhật hiển thị"""
        start = (self.current_page - 1) * self.items_per_page + 1
        end = min(self.current_page * self.items_per_page, self.total_items)
        
        if self.total_items == 0:
            self.info_label.configure(text="Không có dữ liệu")
        else:
            self.info_label.configure(text=f"Hiển thị {start}-{end} / {self.total_items}")
        
        self.page_label.configure(text=f"{self.current_page} / {self.total_pages}")
        
        # Enable/disable buttons
        self.first_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        self.last_btn.configure(state="normal" if self.current_page < self.total_pages else "disabled")
        
    def set_total(self, total):
        """Cập nhật tổng số items"""
        self.total_items = total
        if self.current_page > self.total_pages:
            self.current_page = max(1, self.total_pages)
        self.update_display()
        
    def go_first(self):
        """Về trang đầu"""
        if self.current_page != 1:
            self.current_page = 1
            self.update_display()
            if self.on_page_change:
                self.on_page_change(self.current_page, self.items_per_page)
    
    def go_prev(self):
        """Trang trước"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_display()
            if self.on_page_change:
                self.on_page_change(self.current_page, self.items_per_page)
    
    def go_next(self):
        """Trang sau"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_display()
            if self.on_page_change:
                self.on_page_change(self.current_page, self.items_per_page)
    
    def go_last(self):
        """Về trang cuối"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.update_display()
            if self.on_page_change:
                self.on_page_change(self.current_page, self.items_per_page)
                
    def on_per_page_change(self, value):
        """Xử lý khi thay đổi số items/trang"""
        self.items_per_page = int(value)
        self.current_page = 1
        self.update_display()
        if self.on_page_change:
            self.on_page_change(self.current_page, self.items_per_page)
            
    def get_offset(self):
        """Lấy offset cho query"""
        return (self.current_page - 1) * self.items_per_page
    
    def get_limit(self):
        """Lấy limit cho query"""
        return self.items_per_page