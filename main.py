"""
Phần mềm Quản lý Thư viện Số
============================
- Python + CustomTkinter
- Cơ sở dữ liệu SQLite
- Xuất PDF bằng ReportLab

Tác giả: Hệ thống Quản lý Thư viện
Ngày tạo: 2026
"""
import sys
import os

# Thêm thư mục gốc vào path
sys.path.insert(0, os.path.dirname(__file__))

from views.login_view import LoginView


def main():
    """Khởi chạy ứng dụng"""
    app = LoginView()
    app.mainloop()


if __name__ == "__main__":
    main()
