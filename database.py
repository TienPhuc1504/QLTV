"""
Database module - Quản lý kết nối và khởi tạo cơ sở dữ liệu SQLite
"""
import sqlite3
from datetime import datetime, timedelta
import hashlib
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "library.db")


def get_connection():
    """Tạo kết nối đến database"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password: str) -> str:
    """Mã hóa mật khẩu bằng SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_database():
    """Khởi tạo cơ sở dữ liệu và các bảng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Bảng NGUOI_DUNG (Người dùng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NGUOI_DUNG (
            ma_nd INTEGER PRIMARY KEY AUTOINCREMENT,
            ho_ten VARCHAR(100) NOT NULL,
            dia_chi VARCHAR(255),
            so_dt VARCHAR(15),
            email VARCHAR(100),
            loai_nguoi_dung VARCHAR(20) NOT NULL CHECK(loai_nguoi_dung IN ('ADMIN', 'NHAN_VIEN', 'DOC_GIA'))
        )
    """)
    
    # Bảng ADMIN
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ADMIN (
            ma_nd INTEGER PRIMARY KEY,
            FOREIGN KEY (ma_nd) REFERENCES NGUOI_DUNG(ma_nd) ON DELETE CASCADE
        )
    """)
    
    # Bảng DOC_GIA (Độc giả)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DOC_GIA (
            ma_nd INTEGER PRIMARY KEY,
            ma_doc_gia VARCHAR(20) UNIQUE NOT NULL,
            ngay_dk DATE NOT NULL,
            FOREIGN KEY (ma_nd) REFERENCES NGUOI_DUNG(ma_nd) ON DELETE CASCADE
        )
    """)
    
    # Bảng NHAN_VIEN (Nhân viên)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NHAN_VIEN (
            ma_nd INTEGER PRIMARY KEY,
            ma_nhan_vien VARCHAR(20) UNIQUE NOT NULL,
            FOREIGN KEY (ma_nd) REFERENCES NGUOI_DUNG(ma_nd) ON DELETE CASCADE
        )
    """)
    
    # Bảng TAI_KHOAN (Tài khoản)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TAI_KHOAN (
            ten_tk VARCHAR(50) PRIMARY KEY,
            mat_khau VARCHAR(255) NOT NULL,
            ma_nd INTEGER UNIQUE NOT NULL,
            FOREIGN KEY (ma_nd) REFERENCES NGUOI_DUNG(ma_nd) ON DELETE CASCADE
        )
    """)
    
    # Bảng THE_DOC_GIA (Thẻ đọc giả)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS THE_DOC_GIA (
            ma_the INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_nd_doc_gia INTEGER UNIQUE NOT NULL,
            ngay_cap DATE NOT NULL,
            ngay_het_han DATE NOT NULL,
            trang_thai_the VARCHAR(20) NOT NULL CHECK(trang_thai_the IN ('HOAT_DONG', 'HET_HAN', 'KHOA')),
            FOREIGN KEY (ma_nd_doc_gia) REFERENCES DOC_GIA(ma_nd) ON DELETE CASCADE
        )
    """)
    
    # Bảng THE_LOAI_SACH (Thể loại sách)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS THE_LOAI_SACH (
            ma_the_loai INTEGER PRIMARY KEY AUTOINCREMENT,
            ten_the_loai VARCHAR(100) NOT NULL UNIQUE
        )
    """)
    
    # Bảng SACH (Sách)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SACH (
            ma_sach INTEGER PRIMARY KEY AUTOINCREMENT,
            tieu_de VARCHAR(255) NOT NULL,
            tac_gia VARCHAR(100),
            trang_thai_sach VARCHAR(20) NOT NULL CHECK(trang_thai_sach IN ('CO_SAN', 'DA_MUON', 'HONG', 'MAT')),
            ma_the_loai INTEGER,
            loai_sach VARCHAR(20) NOT NULL CHECK(loai_sach IN ('SACH_GIAY', 'SACH_ONLINE')),
            FOREIGN KEY (ma_the_loai) REFERENCES THE_LOAI_SACH(ma_the_loai)
        )
    """)
    
    # Bảng SACH_GIAY (Sách giấy)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SACH_GIAY (
            ma_sach INTEGER PRIMARY KEY,
            so_luong INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach) ON DELETE CASCADE
        )
    """)
    
    # Bảng SACH_ONLINE (Sách online)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS SACH_ONLINE (
            ma_sach INTEGER PRIMARY KEY,
            url_tai_lieu VARCHAR(500),
            dinh_dang VARCHAR(50),
            FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach) ON DELETE CASCADE
        )
    """)
    
    # Bảng PHIEU_MUON_TRA (Phiếu mượn trả)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PHIEU_MUON_TRA (
            ma_phieu INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_nd_doc_gia INTEGER NOT NULL,
            ma_nd_nhan_vien INTEGER NOT NULL,
            ma_sach INTEGER NOT NULL,
            ngay_muon DATE NOT NULL,
            ngay_hen_tra DATE NOT NULL,
            ngay_tra_thuc DATE,
            trang_thai_phieu VARCHAR(20) NOT NULL CHECK(trang_thai_phieu IN ('DANG_MUON', 'DA_TRA', 'QUA_HAN')),
            tien_phat REAL DEFAULT 0,
            FOREIGN KEY (ma_nd_doc_gia) REFERENCES DOC_GIA(ma_nd),
            FOREIGN KEY (ma_nd_nhan_vien) REFERENCES NHAN_VIEN(ma_nd),
            FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach)
        )
    """)
    
    conn.commit()
    conn.close()


def insert_sample_data():
    """Thêm dữ liệu mẫu vào database"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra đã có dữ liệu chưa
    cursor.execute("SELECT COUNT(*) FROM NGUOI_DUNG")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Thêm Admin
    cursor.execute("""
        INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
        VALUES ('Quản Trị Viên', 'Hà Nội', '0901234567', 'admin@library.com', 'ADMIN')
    """)
    admin_id = cursor.lastrowid
    cursor.execute("INSERT INTO ADMIN (ma_nd) VALUES (?)", (admin_id,))
    cursor.execute("""
        INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) 
        VALUES ('admin', ?, ?)
    """, (hash_password('admin123'), admin_id))
    
    # Thêm Nhân viên
    cursor.execute("""
        INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
        VALUES ('Nguyễn Văn A', 'Hà Nội', '0912345678', 'nva@library.com', 'NHAN_VIEN')
    """)
    nv_id = cursor.lastrowid
    cursor.execute("INSERT INTO NHAN_VIEN (ma_nd, ma_nhan_vien) VALUES (?, 'NV001')", (nv_id,))
    cursor.execute("""
        INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) 
        VALUES ('nhanvien', ?, ?)
    """, (hash_password('nv123'), nv_id))
    
    # Thêm Đọc giả
    cursor.execute("""
        INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
        VALUES ('Trần Thị B', 'Hồ Chí Minh', '0923456789', 'ttb@email.com', 'DOC_GIA')
    """)
    dg_id = cursor.lastrowid
    cursor.execute("""
        INSERT INTO DOC_GIA (ma_nd, ma_doc_gia, ngay_dk) 
        VALUES (?, 'DG001', ?)
    """, (dg_id, datetime.now().strftime('%Y-%m-%d')))
    cursor.execute("""
        INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) 
        VALUES ('docgia', ?, ?)
    """, (hash_password('dg123'), dg_id))
    
    # Thêm thẻ đọc giả
    ngay_cap = datetime.now()
    ngay_het_han = ngay_cap + timedelta(days=365)
    cursor.execute("""
        INSERT INTO THE_DOC_GIA (ma_nd_doc_gia, ngay_cap, ngay_het_han, trang_thai_the)
        VALUES (?, ?, ?, 'HOAT_DONG')
    """, (dg_id, ngay_cap.strftime('%Y-%m-%d'), ngay_het_han.strftime('%Y-%m-%d')))
    
    # Thêm thể loại sách
    the_loai = ['Văn học', 'Khoa học', 'Công nghệ', 'Kinh tế', 'Lịch sử', 'Thiếu nhi', 'Tâm lý']
    for tl in the_loai:
        cursor.execute("INSERT INTO THE_LOAI_SACH (ten_the_loai) VALUES (?)", (tl,))
    
    # Thêm sách mẫu
    sach_mau = [
        ('Truyện Kiều', 'Nguyễn Du', 'CO_SAN', 1, 'SACH_GIAY', 10),
        ('Số đỏ', 'Vũ Trọng Phụng', 'CO_SAN', 1, 'SACH_GIAY', 5),
        ('Python cơ bản', 'John Smith', 'CO_SAN', 3, 'SACH_GIAY', 8),
        ('AI và Machine Learning', 'Andrew Ng', 'CO_SAN', 3, 'SACH_ONLINE', None),
        ('Kinh tế học vĩ mô', 'Nguyễn Văn X', 'CO_SAN', 4, 'SACH_GIAY', 3),
        ('Lịch sử Việt Nam', 'Trần Quốc V', 'CO_SAN', 5, 'SACH_GIAY', 6),
        ('Đắc nhân tâm', 'Dale Carnegie', 'CO_SAN', 7, 'SACH_GIAY', 15),
    ]
    
    for tieu_de, tac_gia, trang_thai, ma_the_loai, loai_sach, so_luong in sach_mau:
        cursor.execute("""
            INSERT INTO SACH (tieu_de, tac_gia, trang_thai_sach, ma_the_loai, loai_sach)
            VALUES (?, ?, ?, ?, ?)
        """, (tieu_de, tac_gia, trang_thai, ma_the_loai, loai_sach))
        ma_sach = cursor.lastrowid
        
        if loai_sach == 'SACH_GIAY':
            cursor.execute("INSERT INTO SACH_GIAY (ma_sach, so_luong) VALUES (?, ?)", 
                          (ma_sach, so_luong))
        else:
            cursor.execute("""
                INSERT INTO SACH_ONLINE (ma_sach, url_tai_lieu, dinh_dang) 
                VALUES (?, 'https://library.com/ebook', 'PDF')
            """, (ma_sach,))
    
    conn.commit()
    conn.close()


# Các hàm truy vấn dữ liệu

def authenticate_user(username: str, password: str):
    """Xác thực người dùng đăng nhập"""
    conn = get_connection()
    cursor = conn.cursor()
    
    hashed_pw = hash_password(password)
    cursor.execute("""
        SELECT tk.ten_tk, tk.ma_nd, nd.ho_ten, nd.loai_nguoi_dung
        FROM TAI_KHOAN tk
        JOIN NGUOI_DUNG nd ON tk.ma_nd = nd.ma_nd
        WHERE tk.ten_tk = ? AND tk.mat_khau = ?
    """, (username, hashed_pw))
    
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def change_password(ma_nd: int, old_password: str, new_password: str) -> bool:
    """Đổi mật khẩu người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    old_hashed = hash_password(old_password)
    cursor.execute("""
        SELECT ten_tk FROM TAI_KHOAN 
        WHERE ma_nd = ? AND mat_khau = ?
    """, (ma_nd, old_hashed))
    
    if not cursor.fetchone():
        conn.close()
        return False
    
    new_hashed = hash_password(new_password)
    cursor.execute("""
        UPDATE TAI_KHOAN SET mat_khau = ? WHERE ma_nd = ?
    """, (new_hashed, ma_nd))
    
    conn.commit()
    conn.close()
    return True


# ============ QUẢN LÝ SÁCH ============

def get_all_books(search_term: str = "", category_id: int = None):
    """Lấy danh sách tất cả sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT s.ma_sach, s.tieu_de, s.tac_gia, s.trang_thai_sach, 
               s.loai_sach, tl.ten_the_loai,
               COALESCE(sg.so_luong, 0) as so_luong,
               so.url_tai_lieu, so.dinh_dang
        FROM SACH s
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        LEFT JOIN SACH_GIAY sg ON s.ma_sach = sg.ma_sach
        LEFT JOIN SACH_ONLINE so ON s.ma_sach = so.ma_sach
        WHERE 1=1
    """
    params = []
    
    if search_term:
        query += " AND (s.tieu_de LIKE ? OR s.tac_gia LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    if category_id:
        query += " AND s.ma_the_loai = ?"
        params.append(category_id)
    
    query += " ORDER BY s.ma_sach DESC"
    
    cursor.execute(query, params)
    books = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return books


def get_book_by_id(ma_sach: int):
    """Lấy thông tin sách theo mã"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, tl.ten_the_loai,
               COALESCE(sg.so_luong, 0) as so_luong,
               so.url_tai_lieu, so.dinh_dang
        FROM SACH s
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        LEFT JOIN SACH_GIAY sg ON s.ma_sach = sg.ma_sach
        LEFT JOIN SACH_ONLINE so ON s.ma_sach = so.ma_sach
        WHERE s.ma_sach = ?
    """, (ma_sach,))
    
    book = cursor.fetchone()
    conn.close()
    return dict(book) if book else None


def add_book(tieu_de: str, tac_gia: str, ma_the_loai: int, loai_sach: str, 
             so_luong: int = 1, url_tai_lieu: str = None, dinh_dang: str = None):
    """Thêm sách mới"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO SACH (tieu_de, tac_gia, trang_thai_sach, ma_the_loai, loai_sach)
        VALUES (?, ?, 'CO_SAN', ?, ?)
    """, (tieu_de, tac_gia, ma_the_loai, loai_sach))
    
    ma_sach = cursor.lastrowid
    
    if loai_sach == 'SACH_GIAY':
        cursor.execute("INSERT INTO SACH_GIAY (ma_sach, so_luong) VALUES (?, ?)", 
                      (ma_sach, so_luong))
    else:
        cursor.execute("""
            INSERT INTO SACH_ONLINE (ma_sach, url_tai_lieu, dinh_dang) 
            VALUES (?, ?, ?)
        """, (ma_sach, url_tai_lieu, dinh_dang))
    
    conn.commit()
    conn.close()
    return ma_sach


def update_book(ma_sach: int, tieu_de: str, tac_gia: str, ma_the_loai: int, 
                trang_thai: str, so_luong: int = None, url_tai_lieu: str = None, 
                dinh_dang: str = None):
    """Cập nhật thông tin sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE SACH SET tieu_de = ?, tac_gia = ?, ma_the_loai = ?, trang_thai_sach = ?
        WHERE ma_sach = ?
    """, (tieu_de, tac_gia, ma_the_loai, trang_thai, ma_sach))
    
    if so_luong is not None:
        cursor.execute("UPDATE SACH_GIAY SET so_luong = ? WHERE ma_sach = ?", 
                      (so_luong, ma_sach))
    
    if url_tai_lieu is not None:
        cursor.execute("""
            UPDATE SACH_ONLINE SET url_tai_lieu = ?, dinh_dang = ? WHERE ma_sach = ?
        """, (url_tai_lieu, dinh_dang, ma_sach))
    
    conn.commit()
    conn.close()


def delete_book(ma_sach: int):
    """Xóa sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM SACH WHERE ma_sach = ?", (ma_sach,))
    
    conn.commit()
    conn.close()


def get_all_categories():
    """Lấy danh sách thể loại sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM THE_LOAI_SACH ORDER BY ten_the_loai")
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return categories


def add_category(ten_the_loai: str):
    """Thêm thể loại sách mới"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO THE_LOAI_SACH (ten_the_loai) VALUES (?)", (ten_the_loai,))
    
    conn.commit()
    ma_the_loai = cursor.lastrowid
    conn.close()
    return ma_the_loai


# ============ QUẢN LÝ ĐỌC GIẢ ============

def get_all_readers(search_term: str = ""):
    """Lấy danh sách đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT nd.*, dg.ma_doc_gia, dg.ngay_dk,
               tdg.ma_the, tdg.ngay_cap, tdg.ngay_het_han, tdg.trang_thai_the
        FROM NGUOI_DUNG nd
        JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
        LEFT JOIN THE_DOC_GIA tdg ON dg.ma_nd = tdg.ma_nd_doc_gia
        WHERE nd.loai_nguoi_dung = 'DOC_GIA'
    """
    params = []
    
    if search_term:
        query += " AND (nd.ho_ten LIKE ? OR dg.ma_doc_gia LIKE ? OR nd.so_dt LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
    
    query += " ORDER BY nd.ma_nd DESC"
    
    cursor.execute(query, params)
    readers = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return readers


def get_reader_by_id(ma_nd: int):
    """Lấy thông tin đọc giả theo mã"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT nd.*, dg.ma_doc_gia, dg.ngay_dk,
               tdg.ma_the, tdg.ngay_cap, tdg.ngay_het_han, tdg.trang_thai_the
        FROM NGUOI_DUNG nd
        JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
        LEFT JOIN THE_DOC_GIA tdg ON dg.ma_nd = tdg.ma_nd_doc_gia
        WHERE nd.ma_nd = ?
    """, (ma_nd,))
    
    reader = cursor.fetchone()
    conn.close()
    return dict(reader) if reader else None


def add_reader(ho_ten: str, dia_chi: str, so_dt: str, email: str, 
               ma_doc_gia: str, thoi_han_the: int = 365):
    """Thêm đọc giả mới"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Thêm người dùng
        cursor.execute("""
            INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
            VALUES (?, ?, ?, ?, 'DOC_GIA')
        """, (ho_ten, dia_chi, so_dt, email))
        
        ma_nd = cursor.lastrowid
        ngay_dk = datetime.now().strftime('%Y-%m-%d')
        
        # Thêm đọc giả
        cursor.execute("""
            INSERT INTO DOC_GIA (ma_nd, ma_doc_gia, ngay_dk) VALUES (?, ?, ?)
        """, (ma_nd, ma_doc_gia, ngay_dk))
        
        # Tạo thẻ đọc giả
        ngay_cap = datetime.now()
        ngay_het_han = ngay_cap + timedelta(days=thoi_han_the)
        cursor.execute("""
            INSERT INTO THE_DOC_GIA (ma_nd_doc_gia, ngay_cap, ngay_het_han, trang_thai_the)
            VALUES (?, ?, ?, 'HOAT_DONG')
        """, (ma_nd, ngay_cap.strftime('%Y-%m-%d'), ngay_het_han.strftime('%Y-%m-%d')))
        
        # Tạo tài khoản mặc định (username = ma_doc_gia, password = ma_doc_gia)
        cursor.execute("""
            INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) VALUES (?, ?, ?)
        """, (ma_doc_gia.lower(), hash_password(ma_doc_gia.lower()), ma_nd))
        
        conn.commit()
        conn.close()
        return ma_nd
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


def update_reader(ma_nd: int, ho_ten: str, dia_chi: str, so_dt: str, email: str):
    """Cập nhật thông tin đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE NGUOI_DUNG SET ho_ten = ?, dia_chi = ?, so_dt = ?, email = ?
        WHERE ma_nd = ?
    """, (ho_ten, dia_chi, so_dt, email, ma_nd))
    
    conn.commit()
    conn.close()


def update_reader_card(ma_nd: int, trang_thai: str, extend_days: int = 0):
    """Cập nhật thẻ đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    if extend_days > 0:
        cursor.execute("""
            UPDATE THE_DOC_GIA 
            SET ngay_het_han = date(ngay_het_han, '+' || ? || ' days'),
                trang_thai_the = ?
            WHERE ma_nd_doc_gia = ?
        """, (extend_days, trang_thai, ma_nd))
    else:
        cursor.execute("""
            UPDATE THE_DOC_GIA SET trang_thai_the = ? WHERE ma_nd_doc_gia = ?
        """, (trang_thai, ma_nd))
    
    conn.commit()
    conn.close()


def delete_reader(ma_nd: int):
    """Xóa đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM NGUOI_DUNG WHERE ma_nd = ?", (ma_nd,))
    
    conn.commit()
    conn.close()


# ============ QUẢN LÝ NHÂN VIÊN ============

def get_all_staff(search_term: str = ""):
    """Lấy danh sách nhân viên"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT nd.*, nv.ma_nhan_vien
        FROM NGUOI_DUNG nd
        JOIN NHAN_VIEN nv ON nd.ma_nd = nv.ma_nd
        WHERE nd.loai_nguoi_dung = 'NHAN_VIEN'
    """
    params = []
    
    if search_term:
        query += " AND (nd.ho_ten LIKE ? OR nv.ma_nhan_vien LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%"])
    
    query += " ORDER BY nd.ma_nd DESC"
    
    cursor.execute(query, params)
    staff = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return staff


def add_staff(ho_ten: str, dia_chi: str, so_dt: str, email: str, ma_nhan_vien: str):
    """Thêm nhân viên mới"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
            VALUES (?, ?, ?, ?, 'NHAN_VIEN')
        """, (ho_ten, dia_chi, so_dt, email))
        
        ma_nd = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO NHAN_VIEN (ma_nd, ma_nhan_vien) VALUES (?, ?)
        """, (ma_nd, ma_nhan_vien))
        
        # Tạo tài khoản
        cursor.execute("""
            INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) VALUES (?, ?, ?)
        """, (ma_nhan_vien.lower(), hash_password(ma_nhan_vien.lower()), ma_nd))
        
        conn.commit()
        conn.close()
        return ma_nd
    except Exception as e:
        conn.rollback()
        conn.close()
        raise e


def update_staff(ma_nd: int, ho_ten: str, dia_chi: str, so_dt: str, email: str):
    """Cập nhật thông tin nhân viên"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE NGUOI_DUNG SET ho_ten = ?, dia_chi = ?, so_dt = ?, email = ?
        WHERE ma_nd = ?
    """, (ho_ten, dia_chi, so_dt, email, ma_nd))
    
    conn.commit()
    conn.close()


def delete_staff(ma_nd: int):
    """Xóa nhân viên"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM NGUOI_DUNG WHERE ma_nd = ?", (ma_nd,))
    
    conn.commit()
    conn.close()


# ============ QUẢN LÝ MƯỢN TRẢ SÁCH ============

def get_all_borrows(search_term: str = "", status: str = None):
    """Lấy danh sách phiếu mượn"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT p.*, 
               nd_dg.ho_ten as ten_doc_gia, dg.ma_doc_gia,
               nd_nv.ho_ten as ten_nhan_vien, nv.ma_nhan_vien,
               s.tieu_de, s.tac_gia
        FROM PHIEU_MUON_TRA p
        JOIN DOC_GIA dg ON p.ma_nd_doc_gia = dg.ma_nd
        JOIN NGUOI_DUNG nd_dg ON dg.ma_nd = nd_dg.ma_nd
        JOIN NHAN_VIEN nv ON p.ma_nd_nhan_vien = nv.ma_nd
        JOIN NGUOI_DUNG nd_nv ON nv.ma_nd = nd_nv.ma_nd
        JOIN SACH s ON p.ma_sach = s.ma_sach
        WHERE 1=1
    """
    params = []
    
    if search_term:
        query += " AND (nd_dg.ho_ten LIKE ? OR dg.ma_doc_gia LIKE ? OR s.tieu_de LIKE ?)"
        params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
    
    if status:
        query += " AND p.trang_thai_phieu = ?"
        params.append(status)
    
    query += " ORDER BY p.ma_phieu DESC"
    
    cursor.execute(query, params)
    borrows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return borrows


def get_borrow_by_id(ma_phieu: int):
    """Lấy thông tin phiếu mượn theo mã"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, 
               nd_dg.ho_ten as ten_doc_gia, nd_dg.dia_chi, nd_dg.so_dt, nd_dg.email,
               dg.ma_doc_gia,
               nd_nv.ho_ten as ten_nhan_vien, nv.ma_nhan_vien,
               s.tieu_de, s.tac_gia, tl.ten_the_loai
        FROM PHIEU_MUON_TRA p
        JOIN DOC_GIA dg ON p.ma_nd_doc_gia = dg.ma_nd
        JOIN NGUOI_DUNG nd_dg ON dg.ma_nd = nd_dg.ma_nd
        JOIN NHAN_VIEN nv ON p.ma_nd_nhan_vien = nv.ma_nd
        JOIN NGUOI_DUNG nd_nv ON nv.ma_nd = nd_nv.ma_nd
        JOIN SACH s ON p.ma_sach = s.ma_sach
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        WHERE p.ma_phieu = ?
    """, (ma_phieu,))
    
    borrow = cursor.fetchone()
    conn.close()
    return dict(borrow) if borrow else None


def create_borrow(ma_nd_doc_gia: int, ma_nd_nhan_vien: int, ma_sach: int, 
                  so_ngay_muon: int = 14):
    """Tạo phiếu mượn sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra đọc giả đã mượn sách này chưa (và chưa trả)
    cursor.execute("""
        SELECT COUNT(*) as count FROM PHIEU_MUON_TRA 
        WHERE ma_nd_doc_gia = ? AND ma_sach = ? AND trang_thai_phieu = 'DANG_MUON'
    """, (ma_nd_doc_gia, ma_sach))
    
    existing = cursor.fetchone()
    if existing and existing['count'] > 0:
        conn.close()
        raise Exception("Bạn đã mượn sách này rồi! Vui lòng trả sách trước khi mượn lại.")
    
    # Kiểm tra sách có khả dụng không
    cursor.execute("""
        SELECT s.trang_thai_sach, s.loai_sach, sg.so_luong
        FROM SACH s
        LEFT JOIN SACH_GIAY sg ON s.ma_sach = sg.ma_sach
        WHERE s.ma_sach = ?
    """, (ma_sach,))
    
    sach = cursor.fetchone()
    if not sach:
        conn.close()
        raise Exception("Không tìm thấy sách!")
    
    # Kiểm tra trạng thái sách
    if sach['trang_thai_sach'] in ['HONG', 'MAT']:
        conn.close()
        raise Exception("Sách không khả dụng (hỏng hoặc mất)!")
    
    # Kiểm tra số lượng nếu là sách giấy
    if sach['loai_sach'] == 'SACH_GIAY':
        if sach['so_luong'] is None or sach['so_luong'] <= 0:
            conn.close()
            raise Exception("Sách đã hết! Vui lòng chọn sách khác.")
    
    ngay_muon = datetime.now()
    ngay_hen_tra = ngay_muon + timedelta(days=so_ngay_muon)
    
    cursor.execute("""
        INSERT INTO PHIEU_MUON_TRA 
        (ma_nd_doc_gia, ma_nd_nhan_vien, ma_sach, ngay_muon, ngay_hen_tra, trang_thai_phieu)
        VALUES (?, ?, ?, ?, ?, 'DANG_MUON')
    """, (ma_nd_doc_gia, ma_nd_nhan_vien, ma_sach, 
          ngay_muon.strftime('%Y-%m-%d'), ngay_hen_tra.strftime('%Y-%m-%d')))
    
    ma_phieu = cursor.lastrowid
    
    # Cập nhật số lượng sách
    cursor.execute("""
        UPDATE SACH_GIAY SET so_luong = so_luong - 1 WHERE ma_sach = ?
    """, (ma_sach,))
    
    # Cập nhật trạng thái sách nếu hết
    cursor.execute("""
        UPDATE SACH SET trang_thai_sach = 'DA_MUON' 
        WHERE ma_sach = ? AND ma_sach IN (
            SELECT ma_sach FROM SACH_GIAY WHERE so_luong = 0
        )
    """, (ma_sach,))
    
    conn.commit()
    conn.close()
    return ma_phieu


def return_book(ma_phieu: int, tien_phat: float = 0):
    """Trả sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    ngay_tra = datetime.now().strftime('%Y-%m-%d')
    
    # Lấy thông tin phiếu mượn
    cursor.execute("SELECT ma_sach FROM PHIEU_MUON_TRA WHERE ma_phieu = ?", (ma_phieu,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    ma_sach = result['ma_sach']
    
    # Cập nhật phiếu mượn
    cursor.execute("""
        UPDATE PHIEU_MUON_TRA 
        SET ngay_tra_thuc = ?, trang_thai_phieu = 'DA_TRA', tien_phat = ?
        WHERE ma_phieu = ?
    """, (ngay_tra, tien_phat, ma_phieu))
    
    # Cập nhật số lượng sách
    cursor.execute("""
        UPDATE SACH_GIAY SET so_luong = so_luong + 1 WHERE ma_sach = ?
    """, (ma_sach,))
    
    # Cập nhật trạng thái sách
    cursor.execute("""
        UPDATE SACH SET trang_thai_sach = 'CO_SAN' WHERE ma_sach = ?
    """, (ma_sach,))
    
    conn.commit()
    conn.close()
    return True


def calculate_fine(ma_phieu: int, fine_per_day: float = 5000) -> float:
    """Tính tiền phạt quá hạn"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT ngay_hen_tra FROM PHIEU_MUON_TRA WHERE ma_phieu = ?
    """, (ma_phieu,))
    
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return 0
    
    ngay_hen_tra = datetime.strptime(result['ngay_hen_tra'], '%Y-%m-%d')
    ngay_hien_tai = datetime.now()
    
    if ngay_hien_tai > ngay_hen_tra:
        so_ngay_tre = (ngay_hien_tai - ngay_hen_tra).days
        return so_ngay_tre * fine_per_day
    
    return 0


def get_reader_borrow_history(ma_nd_doc_gia: int):
    """Lấy lịch sử mượn sách của đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.*, s.tieu_de, s.tac_gia, s.loai_sach,
               nd_nv.ho_ten as ten_nhan_vien,
               so.url_tai_lieu, so.dinh_dang
        FROM PHIEU_MUON_TRA p
        JOIN SACH s ON p.ma_sach = s.ma_sach
        LEFT JOIN SACH_ONLINE so ON s.ma_sach = so.ma_sach
        JOIN NHAN_VIEN nv ON p.ma_nd_nhan_vien = nv.ma_nd
        JOIN NGUOI_DUNG nd_nv ON nv.ma_nd = nd_nv.ma_nd
        WHERE p.ma_nd_doc_gia = ?
        ORDER BY p.ngay_muon DESC
    """, (ma_nd_doc_gia,))
    
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history


# ============ THỐNG KÊ ============

def get_book_statistics():
    """Thống kê sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Tổng số sách
    cursor.execute("SELECT COUNT(*) as total FROM SACH")
    stats['total_books'] = cursor.fetchone()['total']
    
    # Sách theo trạng thái
    cursor.execute("""
        SELECT trang_thai_sach, COUNT(*) as count 
        FROM SACH GROUP BY trang_thai_sach
    """)
    stats['by_status'] = {row['trang_thai_sach']: row['count'] for row in cursor.fetchall()}
    
    # Sách theo thể loại
    cursor.execute("""
        SELECT tl.ten_the_loai, COUNT(s.ma_sach) as count
        FROM THE_LOAI_SACH tl
        LEFT JOIN SACH s ON tl.ma_the_loai = s.ma_the_loai
        GROUP BY tl.ma_the_loai
        ORDER BY count DESC
    """)
    stats['by_category'] = [(row['ten_the_loai'], row['count']) for row in cursor.fetchall()]
    
    # Sách được mượn nhiều nhất
    cursor.execute("""
        SELECT s.tieu_de, s.tac_gia, COUNT(p.ma_phieu) as borrow_count
        FROM SACH s
        LEFT JOIN PHIEU_MUON_TRA p ON s.ma_sach = p.ma_sach
        GROUP BY s.ma_sach
        ORDER BY borrow_count DESC
        LIMIT 10
    """)
    stats['most_borrowed'] = [(row['tieu_de'], row['tac_gia'], row['borrow_count']) 
                              for row in cursor.fetchall()]
    
    conn.close()
    return stats


def get_borrow_statistics():
    """Thống kê mượn trả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    stats = {}
    
    # Tổng số phiếu mượn
    cursor.execute("SELECT COUNT(*) as total FROM PHIEU_MUON_TRA")
    stats['total_borrows'] = cursor.fetchone()['total']
    
    # Phiếu theo trạng thái
    cursor.execute("""
        SELECT trang_thai_phieu, COUNT(*) as count 
        FROM PHIEU_MUON_TRA GROUP BY trang_thai_phieu
    """)
    stats['by_status'] = {row['trang_thai_phieu']: row['count'] for row in cursor.fetchall()}
    
    # Phiếu quá hạn
    cursor.execute("""
        SELECT COUNT(*) as count FROM PHIEU_MUON_TRA 
        WHERE trang_thai_phieu = 'DANG_MUON' AND ngay_hen_tra < date('now')
    """)
    stats['overdue'] = cursor.fetchone()['count']
    
    # Tổng tiền phạt
    cursor.execute("SELECT COALESCE(SUM(tien_phat), 0) as total FROM PHIEU_MUON_TRA")
    stats['total_fines'] = cursor.fetchone()['total']
    
    conn.close()
    return stats


# Khởi tạo database khi import module
if __name__ == "__main__":
    init_database()
    insert_sample_data()
    print("Database initialized successfully!")
