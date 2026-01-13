"""
Quản lý nhân viên (chỉ Admin)
"""
import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import get_all_staff, add_staff, update_staff, delete_staff
from utils import treeview_sort_column, center_window


class StaffManagement(ctk.CTkFrame):
    """Giao diện quản lý nhân viên"""
    
    def __init__(self, parent, user: dict):
        super().__init__(parent, fg_color="transparent")
        
        self.user = user
        self.selected_staff = None
        
        self.create_widgets()
        self.load_staff()
        
    def create_widgets(self):
        """Tạo các widget"""
        # Tiêu đề
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="👔 Quản lý Nhân viên",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title.pack(side="left")
        
        # Nút thêm
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Thêm nhân viên",
            command=self.show_add_dialog,
            width=140
        )
        add_btn.pack(side="right")
        
        # Khung tìm kiếm
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Tìm kiếm theo tên, mã nhân viên...",
            width=350
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_staff())
        
        refresh_btn = ctk.CTkButton(
            search_frame,
            text="🔄",
            command=self.load_staff,
            width=40
        )
        refresh_btn.pack(side="left", padx=10)
        
        # Khung bảng
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Bảng (Treeview)
        columns = ("ma_nhan_vien", "ho_ten", "so_dt", "email", "dia_chi")
        
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=12)
        
        # Tiêu đề cột có sắp xếp
        headings = {
            "ma_nhan_vien": "Mã NV",
            "ho_ten": "Họ tên",
            "so_dt": "Số điện thoại",
            "email": "Email",
            "dia_chi": "Địa chỉ"
        }
        for col, text in headings.items():
            self.tree.heading(col, text=text, 
                            command=lambda c=col: treeview_sort_column(self.tree, c, False))
        
        # Độ rộng cột
        self.tree.column("ma_nhan_vien", width=100, anchor="center")
        self.tree.column("ho_ten", width=200)
        self.tree.column("so_dt", width=130, anchor="center")
        self.tree.column("email", width=220)
        self.tree.column("dia_chi", width=200)
        
        # Thanh cuộn
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Gắn sự kiện chọn
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # Các nút hành động
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
        
        # Ghi chú
        note_label = ctk.CTkLabel(
            action_frame,
            text="💡 Tài khoản mặc định: mã nhân viên/mã nhân viên",
            text_color="gray",
            font=ctk.CTkFont(size=12)
        )
        note_label.pack(side="right")
        
    def load_staff(self):
        """Tải danh sách nhân viên"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        staff_list = get_all_staff()
        
        for staff in staff_list:
            self.tree.insert("", "end", iid=staff['ma_nd'], values=(
                staff['ma_nhan_vien'],
                staff['ho_ten'],
                staff['so_dt'] or "N/A",
                staff['email'] or "N/A",
                staff['dia_chi'] or "N/A"
            ))
            
    def search_staff(self):
        """Tìm kiếm nhân viên"""
        search_term = self.search_entry.get()
        
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        staff_list = get_all_staff(search_term)
        
        for staff in staff_list:
            self.tree.insert("", "end", iid=staff['ma_nd'], values=(
                staff['ma_nhan_vien'],
                staff['ho_ten'],
                staff['so_dt'] or "N/A",
                staff['email'] or "N/A",
                staff['dia_chi'] or "N/A"
            ))
            
    def on_select(self, event):
        """Xử lý khi chọn item"""
        selection = self.tree.selection()
        if selection:
            self.selected_staff = int(selection[0])  # iid là ma_nd
            self.edit_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")
        else:
            self.selected_staff = None
            self.edit_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")    
    def on_double_click(self, event):
        """Xử lý double-click - chỉ mở dialog nếu click vào dòng dữ liệu"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            self.show_edit_dialog()            
    def show_add_dialog(self):
        """Hiện dialog thêm nhân viên"""
        dialog = StaffDialog(self, "Thêm nhân viên mới")
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                add_staff(**dialog.result)
                messagebox.showinfo("Thành công", "Thêm nhân viên thành công!\nTài khoản: mã NV/mã NV")
                self.load_staff()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể thêm: {str(e)}")
                
    def show_edit_dialog(self):
        """Hiện dialog sửa nhân viên"""
        if not self.selected_staff:
            return
            
        # Lấy thông tin từ tree
        selection = self.tree.selection()
        if not selection:
            return
            
        item = self.tree.item(selection[0])
        values = item['values']
        
        staff_data = {
            'ma_nd': self.selected_staff,
            'ma_nhan_vien': values[0],
            'ho_ten': values[1],
            'so_dt': values[2] if values[2] != "N/A" else "",
            'email': values[3] if values[3] != "N/A" else "",
            'dia_chi': values[4] if values[4] != "N/A" else ""
        }
        
        dialog = StaffDialog(self, "Sửa thông tin nhân viên", staff_data)
        self.wait_window(dialog)
        
        if dialog.result:
            try:
                update_staff(self.selected_staff, **dialog.result)
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
                self.load_staff()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể cập nhật: {str(e)}")
                
    def delete_selected(self):
        """Xóa nhân viên đã chọn"""
        if not self.selected_staff:
            return
            
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa nhân viên này?"):
            try:
                delete_staff(self.selected_staff)
                messagebox.showinfo("Thành công", "Xóa nhân viên thành công!")
                self.load_staff()
                self.selected_staff = None
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xóa: {str(e)}")


class StaffDialog(ctk.CTkToplevel):
    """Dialog thêm/sửa nhân viên"""
    
    def __init__(self, parent, title: str, staff: dict = None):
        super().__init__(parent)
        
        self.title(title)
        self.transient(parent)
        self.grab_set()
        center_window(self, 400, 380)
        
        self.staff = staff
        self.result = None
        
        self.create_widgets()
        
        if staff:
            self.populate_fields()
            
    def create_widgets(self):
        """Tạo các widget"""
        # Khung chính + nội dung có cuộn để dialog có thể cuộn khi cần
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=12, pady=12)

        content = ctk.CTkScrollableFrame(main_container, fg_color="transparent")
        content.pack(fill="both", expand=True, pady=(0, 10))

        # Mã nhân viên sẽ được tự động sinh khi thêm mới
        # (nên không hiển trường nhập mã)
        # Họ tên
        ctk.CTkLabel(content, text="Họ tên: *", anchor="w").pack(fill="x", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(content)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Địa chỉ
        ctk.CTkLabel(content, text="Địa chỉ:", anchor="w").pack(fill="x", pady=(0, 5))
        self.address_entry = ctk.CTkEntry(content)
        self.address_entry.pack(fill="x", pady=(0, 10))

        # Số điện thoại
        ctk.CTkLabel(content, text="Số điện thoại:", anchor="w").pack(fill="x", pady=(0, 5))
        self.phone_entry = ctk.CTkEntry(content)
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Email
        ctk.CTkLabel(content, text="Email:", anchor="w").pack(fill="x", pady=(0, 5))
        self.email_entry = ctk.CTkEntry(content)
        self.email_entry.pack(fill="x", pady=(0, 10))
        
        # Các nút cố định ở dưới
        btn_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        btn_frame.pack(fill="x", side="bottom")
        ctk.CTkButton(btn_frame, text="Hủy", command=self.destroy, fg_color="gray", width=100).pack(side="left", padx=12, pady=10)
        ctk.CTkButton(btn_frame, text="Lưu", command=self.save, width=100).pack(side="right", padx=12, pady=10)
        
    def populate_fields(self):
        """Điền dữ liệu khi sửa"""
        self.name_entry.insert(0, self.staff['ho_ten'])
        self.address_entry.insert(0, self.staff['dia_chi'] or "")
        self.phone_entry.insert(0, self.staff['so_dt'] or "")
        self.email_entry.insert(0, self.staff['email'] or "")
        # No account fields in this dialog anymore
        
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

        if self.staff:
            # Update existing staff
            self.result = {
                'ho_ten': ho_ten,
                'dia_chi': self.address_entry.get().strip() or None,
                'so_dt': so_dt or None,
                'email': email or None
            }
        else:
            # Auto-generate staff code: find max existing numeric suffix and increment
            staff_list = get_all_staff()
            max_num = 0
            for s in staff_list:
                code = s.get('ma_nhan_vien') or ''
                m = re.search(r"(\d+)$", code)
                if m:
                    try:
                        num = int(m.group(1))
                        if num > max_num:
                            max_num = num
                    except:
                        pass

            next_num = max_num + 1
            ma_nhan_vien = f"NV{next_num:03d}"

            # Account creation is mandatory and will use ma_nhan_vien as default username/password
            self.result = {
                'ho_ten': ho_ten,
                'dia_chi': self.address_entry.get().strip() or None,
                'so_dt': so_dt or None,
                'email': email or None,
                'ma_nhan_vien': ma_nhan_vien,
                'create_account': True,
                'username': None,
                'password': None
            }

        self.destroy()
