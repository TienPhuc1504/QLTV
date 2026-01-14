# 📚 Phần mềm Quản lý Thư viện Số

## Giới thiệu
Phần mềm Quản lý Thư viện Số được phát triển bằng Python với giao diện CustomTkinter, cơ sở dữ liệu SQLite và xuất báo cáo PDF bằng ReportLab.

## Cài đặt

### 1. Yêu cầu hệ thống
- Python 3.8 trở lên
- Windows/macOS/Linux

### 2. Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### 3. Chạy ứng dụng
```bash
python main.py
```

## Tài khoản demo

| Vai trò | Tên đăng nhập | Mật khẩu |
|---------|---------------|----------|
| Admin | admin | admin123 |
| Nhân viên | nhanvien | nv123 |
| Đọc giả | docgia | dg123 |

## Chức năng

### 🔐 Hệ thống
- Đăng nhập/Đăng xuất
- Đổi mật khẩu
- Phân quyền theo vai trò

### 📖 Quản lý Sách (Nhân viên)
- Thêm/Sửa/Xóa sách
- Tìm kiếm sách
- Quản lý thể loại
- Hỗ trợ sách giấy và sách online

### 👥 Quản lý Đọc giả (Nhân viên)
- Thêm/Sửa/Xóa đọc giả
- Quản lý thẻ đọc giả
- Gia hạn thẻ
- Xem lịch sử mượn
- In thẻ đọc giả (PDF)

### 📋 Quản lý Mượn/Trả (Nhân viên)
- Tạo phiếu mượn sách
- Trả sách
- Tính tiền phạt quá hạn
- In phiếu mượn/trả (PDF)

### 👔 Quản lý Nhân viên (Admin)
- Thêm/Sửa/Xóa nhân viên
- Tạo tài khoản nhân viên

### 📈 Thống kê (Nhân viên, Admin)
- Thống kê sách theo trạng thái
- Thống kê sách theo thể loại
- Top sách được mượn nhiều
- Thống kê mượn trả
- Xuất báo cáo PDF

### 📚 Đọc giả
- Xem thông tin cá nhân
- Xem sách đang mượn
- Xem lịch sử mượn
- Tìm kiếm sách

## Cấu trúc dự án

```
QLTV/
├── main.py                 # Entry point
├── database.py             # Database module (SQLite)
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── library.db             # SQLite database (auto-generated)
├── reports/               # Thư mục chứa báo cáo PDF
├── views/
│   ├── __init__.py
│   ├── login_view.py      # Giao diện đăng nhập
│   ├── main_view.py       # Giao diện chính
│   ├── book_management.py # Quản lý sách
│   ├── reader_management.py # Quản lý đọc giả
│   ├── borrow_management.py # Quản lý mượn/trả
│   ├── staff_management.py  # Quản lý nhân viên
│   ├── my_books.py        # Giao diện đọc giả
│   └── statistics_view.py # Thống kê
└── utils/
    ├── __init__.py
    └── report_generator.py # Xuất PDF
```

## Sơ đồ ERD

Hệ thống bao gồm các bảng:
- **NGUOI_DUNG**: Thông tin người dùng (Admin, Nhân viên, Đọc giả)
- **TAI_KHOAN**: Tài khoản đăng nhập
- **SACH**: Thông tin sách
- **THE_LOAI_SACH**: Thể loại sách
- **DOC_GIA**: Thông tin đọc giả
- **THE_DOC_GIA**: Thẻ đọc giả
- **NHAN_VIEN**: Thông tin nhân viên
- **PHIEU_MUON_TRA**: Phiếu mượn trả sách

## Công nghệ sử dụng

- **Python 3.x**: Ngôn ngữ lập trình
- **CustomTkinter**: Framework GUI hiện đại
- **SQLite**: Cơ sở dữ liệu nhúng
- **ReportLab**: Xuất báo cáo PDF

## Tác giả
Library Management System © 2026

