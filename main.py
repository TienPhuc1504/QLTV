"""
Phần mềm Quản lý Thư viện Số
============================
- Python + CustomTkinter
- SQLite Database
- ReportLab PDF Export

Tác giả: Library Management System
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
