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
    
    # Bảng SACH (Đầu sách - thông tin chung)
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
    
    # Bảng QUYEN_SACH (Quyển sách - từng bản sao riêng biệt cho sách giấy)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS QUYEN_SACH (
            ma_quyen INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_sach INTEGER NOT NULL,
            ma_quyen_sach VARCHAR(50) UNIQUE NOT NULL,
            trang_thai VARCHAR(20) NOT NULL DEFAULT 'CO_SAN' 
                CHECK(trang_thai IN ('CO_SAN', 'DANG_MUON', 'HONG', 'MAT', 'KHONG_CO_SAN')),
            vi_tri VARCHAR(100),
            ghi_chu TEXT,
            ngay_nhap DATE NOT NULL,
            FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach) ON DELETE CASCADE
        )
    """)
    
    # Bảng SACH_GIAY (Sách giấy - thông tin bổ sung)
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
    
    # Bảng YEU_CAU_MUON (Yêu cầu mượn sách từ đọc giả)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS YEU_CAU_MUON (
            ma_yeu_cau INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_nd_doc_gia INTEGER NOT NULL,
            ma_sach INTEGER NOT NULL,
            ngay_yeu_cau DATE NOT NULL,
            so_ngay_muon_de_xuat INTEGER NOT NULL,
            ghi_chu TEXT,
            trang_thai VARCHAR(20) NOT NULL CHECK(trang_thai IN ('CHO_DUYET', 'CHO_LAY_SACH', 'DA_LAY', 'TU_CHOI', 'DA_HUY')),
            ma_nd_xu_ly INTEGER,
            ngay_xu_ly DATE,
            ly_do_tu_choi TEXT,
            so_ngay_muon_chinh_thuc INTEGER,
            FOREIGN KEY (ma_nd_doc_gia) REFERENCES DOC_GIA(ma_nd),
            FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach),
            FOREIGN KEY (ma_nd_xu_ly) REFERENCES NGUOI_DUNG(ma_nd)
        )
    """)
    
    # Thêm cột so_ngay_muon_chinh_thuc nếu chưa có (cho database cũ)
    try:
        cursor.execute("ALTER TABLE YEU_CAU_MUON ADD COLUMN so_ngay_muon_chinh_thuc INTEGER")
    except:
        pass  # Cột đã tồn tại
    
    # Thêm cột han_lay_sach (hạn lấy sách - 3 ngày sau khi duyệt)
    try:
        cursor.execute("ALTER TABLE YEU_CAU_MUON ADD COLUMN han_lay_sach DATETIME")
    except:
        pass  # Cột đã tồn tại
    
    # Thêm cột ma_quyen vào PHIEU_MUON_TRA (cho migration)
    try:
        cursor.execute("ALTER TABLE PHIEU_MUON_TRA ADD COLUMN ma_quyen INTEGER REFERENCES QUYEN_SACH(ma_quyen)")
    except:
        pass  # Cột đã tồn tại
    
    # Thêm cột ma_quyen vào YEU_CAU_MUON (cho migration)
    try:
        cursor.execute("ALTER TABLE YEU_CAU_MUON ADD COLUMN ma_quyen INTEGER REFERENCES QUYEN_SACH(ma_quyen)")
    except:
        pass  # Cột đã tồn tại
    
    # Migration: Cập nhật constraint cho bảng QUYEN_SACH để hỗ trợ KHONG_CO_SAN
    try:
        # Kiểm tra xem bảng có constraint cũ không bằng cách thử update
        cursor.execute("UPDATE QUYEN_SACH SET trang_thai = 'KHONG_CO_SAN' WHERE 1=0")
    except:
        # Nếu lỗi, cần migrate bảng
        try:
            # Tạo bảng tạm với constraint mới
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS QUYEN_SACH_NEW (
                    ma_quyen INTEGER PRIMARY KEY AUTOINCREMENT,
                    ma_sach INTEGER NOT NULL,
                    ma_quyen_sach VARCHAR(50) UNIQUE NOT NULL,
                    trang_thai VARCHAR(20) NOT NULL DEFAULT 'CO_SAN' 
                        CHECK(trang_thai IN ('CO_SAN', 'DANG_MUON', 'HONG', 'MAT', 'KHONG_CO_SAN')),
                    vi_tri VARCHAR(100),
                    ghi_chu TEXT,
                    ngay_nhap DATE NOT NULL,
                    FOREIGN KEY (ma_sach) REFERENCES SACH(ma_sach) ON DELETE CASCADE
                )
            """)
            
            # Copy dữ liệu
            cursor.execute("""
                INSERT INTO QUYEN_SACH_NEW (ma_quyen, ma_sach, ma_quyen_sach, trang_thai, vi_tri, ghi_chu, ngay_nhap)
                SELECT ma_quyen, ma_sach, ma_quyen_sach, trang_thai, vi_tri, ghi_chu, ngay_nhap FROM QUYEN_SACH
            """)
            
            # Xóa bảng cũ và đổi tên bảng mới
            cursor.execute("DROP TABLE QUYEN_SACH")
            cursor.execute("ALTER TABLE QUYEN_SACH_NEW RENAME TO QUYEN_SACH")
            
            conn.commit()
        except Exception as e:
            pass  # Bỏ qua nếu đã migrate rồi
    
    # Bảng THONG_BAO (Thông báo)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS THONG_BAO (
            ma_thong_bao INTEGER PRIMARY KEY AUTOINCREMENT,
            ma_nd INTEGER NOT NULL,
            tieu_de VARCHAR(200) NOT NULL,
            noi_dung TEXT NOT NULL,
            loai_thong_bao VARCHAR(30) NOT NULL CHECK(loai_thong_bao IN (
                'YEU_CAU_DUYET', 'YEU_CAU_TU_CHOI', 'SAP_HET_HAN', 'QUA_HAN', 
                'SACH_CO_SAN', 'HE_THONG', 'YEU_CAU_MOI', 'CHO_LAY_SACH'
            )),
            da_doc INTEGER DEFAULT 0,
            ngay_tao DATETIME NOT NULL,
            link_lien_quan TEXT,
            FOREIGN KEY (ma_nd) REFERENCES NGUOI_DUNG(ma_nd) ON DELETE CASCADE
        )
    """)
    
        # Bảng YEU_CAU_THE (Yêu cầu in/cấp lại thẻ đọc giả)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS YEU_CAU_THE (
                ma_yeu_cau INTEGER PRIMARY KEY AUTOINCREMENT,
                ma_nd_doc_gia INTEGER NOT NULL,
                ngay_yeu_cau DATETIME NOT NULL,
                trang_thai VARCHAR(20) NOT NULL CHECK(trang_thai IN ('CHO_DUYET', 'DANG_XU_LY', 'DA_IN', 'TU_CHOI', 'DA_HUY')),
                ma_nd_xu_ly INTEGER,
                ngay_xu_ly DATETIME,
                ly_do_tu_choi TEXT,
                FOREIGN KEY (ma_nd_doc_gia) REFERENCES DOC_GIA(ma_nd),
                FOREIGN KEY (ma_nd_xu_ly) REFERENCES NGUOI_DUNG(ma_nd)
            )
        """)
    # Migration: thêm cột da_nhan để đánh dấu đọc giả đã nhận thẻ (0/1)
    try:
        cursor.execute("ALTER TABLE YEU_CAU_THE ADD COLUMN da_nhan INTEGER DEFAULT 0")
    except:
        pass
    
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
            # Tạo từng quyển sách
            for i in range(1, so_luong + 1):
                ma_quyen_sach = f"S{ma_sach:04d}-Q{i:03d}"
                cursor.execute("""
                    INSERT INTO QUYEN_SACH (ma_sach, ma_quyen_sach, trang_thai, ngay_nhap)
                    VALUES (?, ?, 'CO_SAN', ?)
                """, (ma_sach, ma_quyen_sach, datetime.now().strftime('%Y-%m-%d')))
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


def register_user(username: str, password: str, ho_ten: str, dia_chi: str = None,
                  so_dt: str = None, email: str = None, loai_nguoi_dung: str = 'DOC_GIA'):
    """Đăng ký người dùng mới. Trả về ma_nd nếu thành công, hoặc raise Exception nếu lỗi."""
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra username đã tồn tại chưa
    cursor.execute("SELECT ten_tk FROM TAI_KHOAN WHERE ten_tk = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise Exception("Tên đăng nhập đã tồn tại!")

    # Chèn vào NGUOI_DUNG
    cursor.execute("""
        INSERT INTO NGUOI_DUNG (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung)
        VALUES (?, ?, ?, ?, ?)
    """, (ho_ten, dia_chi, so_dt, email, loai_nguoi_dung))

    ma_nd = cursor.lastrowid

    # Nếu là độc giả, tạo bản ghi DOC_GIA và mã độc giả
    if loai_nguoi_dung == 'DOC_GIA':
        ma_doc_gia = f"DG{ma_nd:04d}"
        cursor.execute("INSERT INTO DOC_GIA (ma_nd, ma_doc_gia, ngay_dk) VALUES (?, ?, ?)",
                       (ma_nd, ma_doc_gia, datetime.now().strftime('%Y-%m-%d')))

        # Tạo thẻ độc giả (mặc định hoạt động, hạn 1 năm)
        ngay_cap = datetime.now()
        ngay_het_han = ngay_cap + timedelta(days=365)
        cursor.execute("INSERT INTO THE_DOC_GIA (ma_nd_doc_gia, ngay_cap, ngay_het_han, trang_thai_the) VALUES (?, ?, ?, 'HOAT_DONG')",
                       (ma_nd, ngay_cap.strftime('%Y-%m-%d'), ngay_het_han.strftime('%Y-%m-%d')))

    # Nếu là nhân viên hoặc admin, tạo record tương ứng (ma mã code đơn giản)
    if loai_nguoi_dung == 'NHAN_VIEN':
        ma_nhan_vien = f"NV{ma_nd:04d}"
        cursor.execute("INSERT INTO NHAN_VIEN (ma_nd, ma_nhan_vien) VALUES (?, ?)", (ma_nd, ma_nhan_vien))
    if loai_nguoi_dung == 'ADMIN':
        cursor.execute("INSERT INTO ADMIN (ma_nd) VALUES (?)", (ma_nd,))

    # Tạo tài khoản
    hashed = hash_password(password)
    cursor.execute("INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) VALUES (?, ?, ?)",
                   (username, hashed, ma_nd))

    conn.commit()
    conn.close()
    return ma_nd


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

def get_all_books(search_term: str = "", category_id: int = None, limit: int = None, offset: int = None):
    """Lấy danh sách tất cả sách"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT s.ma_sach, s.tieu_de, s.tac_gia, s.trang_thai_sach, 
                   s.loai_sach, s.ma_the_loai, tl.ten_the_loai,
                   COALESCE(sg.so_luong, 0) as so_luong,
                   so.url_tai_lieu, so.dinh_dang,
                   (SELECT COUNT(*) FROM QUYEN_SACH q WHERE q.ma_sach = s.ma_sach AND q.trang_thai = 'CO_SAN') as so_quyen_co_san,
                   (SELECT COUNT(*) FROM QUYEN_SACH q WHERE q.ma_sach = s.ma_sach) as tong_so_quyen
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
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
        
        cursor.execute(query, params)
        books = [dict(row) for row in cursor.fetchall()]
        return books
    except Exception as e:
        raise Exception(f"Lỗi khi lấy danh sách sách: {str(e)}")
    finally:
        if conn:
            conn.close()


def count_books(search_term: str = "", category_id: int = None):
    """Đếm tổng số sách"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) as total FROM SACH s WHERE 1=1"
        params = []
        
        if search_term:
            query += " AND (s.tieu_de LIKE ? OR s.tac_gia LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        
        if category_id:
            query += " AND s.ma_the_loai = ?"
            params.append(category_id)
        
        cursor.execute(query, params)
        return cursor.fetchone()['total']
    except Exception:
        return 0
    finally:
        if conn:
            conn.close()


def get_book_by_id(ma_sach: int):
    """Lấy thông tin sách theo mã"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, tl.ten_the_loai,
               COALESCE(sg.so_luong, 0) as so_luong,
               so.url_tai_lieu, so.dinh_dang,
               (SELECT COUNT(*) FROM QUYEN_SACH q WHERE q.ma_sach = s.ma_sach AND q.trang_thai = 'CO_SAN') as so_quyen_co_san,
               (SELECT COUNT(*) FROM QUYEN_SACH q WHERE q.ma_sach = s.ma_sach) as tong_so_quyen
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
        # Tạo các quyển sách
        for i in range(1, so_luong + 1):
            ma_quyen_sach = f"S{ma_sach:04d}-Q{i:03d}"
            cursor.execute("""
                INSERT INTO QUYEN_SACH (ma_sach, ma_quyen_sach, trang_thai, ngay_nhap)
                VALUES (?, ?, 'CO_SAN', ?)
            """, (ma_sach, ma_quyen_sach, datetime.now().strftime('%Y-%m-%d')))
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
    """Cập nhật thông tin đầu sách và trạng thái quyển sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Chỉ cập nhật thông tin cơ bản, không thay đổi trang_thai_sach
    cursor.execute("""
        UPDATE SACH SET tieu_de = ?, tac_gia = ?, ma_the_loai = ?
        WHERE ma_sach = ?
    """, (tieu_de, tac_gia, ma_the_loai, ma_sach))
    
    # Xử lý cập nhật trạng thái quyển sách hàng loạt (chỉ cho sách giấy)
    cursor.execute("SELECT loai_sach FROM SACH WHERE ma_sach = ?", (ma_sach,))
    sach = cursor.fetchone()
    
    if sach and sach['loai_sach'] == 'SACH_GIAY':
        if trang_thai == 'KHONG_CO_SAN':
            # Chuyển tất cả quyển CO_SAN sang KHONG_CO_SAN
            cursor.execute("""
                UPDATE QUYEN_SACH SET trang_thai = 'KHONG_CO_SAN' 
                WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
            """, (ma_sach,))
        elif trang_thai == 'CO_SAN':
            # Chuyển tất cả quyển KHONG_CO_SAN sang CO_SAN
            cursor.execute("""
                UPDATE QUYEN_SACH SET trang_thai = 'CO_SAN' 
                WHERE ma_sach = ? AND trang_thai = 'KHONG_CO_SAN'
            """, (ma_sach,))
    
    # Cập nhật URL cho sách online
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
    
    # Kiểm tra có quyển sách đang được mượn không
    cursor.execute("""
        SELECT COUNT(*) as count FROM QUYEN_SACH 
        WHERE ma_sach = ? AND trang_thai = 'DANG_MUON'
    """, (ma_sach,))
    
    if cursor.fetchone()['count'] > 0:
        conn.close()
        raise Exception("Không thể xóa sách có quyển đang được mượn!")
    
    # Kiểm tra có yêu cầu mượn đang chờ xử lý không
    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_MUON 
        WHERE ma_sach = ? AND trang_thai IN ('CHO_DUYET', 'CHO_LAY_SACH')
    """, (ma_sach,))
    
    if cursor.fetchone()['count'] > 0:
        conn.close()
        raise Exception("Không thể xóa sách có yêu cầu mượn đang chờ xử lý!")
    
    # Xóa các quyển sách trước
    cursor.execute("DELETE FROM QUYEN_SACH WHERE ma_sach = ?", (ma_sach,))
    
    cursor.execute("DELETE FROM SACH WHERE ma_sach = ?", (ma_sach,))
    
    conn.commit()
    conn.close()


# =====================================================
# CÁC HÀM QUẢN LÝ QUYỂN SÁCH
# =====================================================

def get_book_copies(ma_sach: int):
    """Lấy danh sách các quyển sách của một đầu sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT q.*, s.tieu_de, s.tac_gia
        FROM QUYEN_SACH q
        JOIN SACH s ON q.ma_sach = s.ma_sach
        WHERE q.ma_sach = ?
        ORDER BY q.ma_quyen_sach
    """, (ma_sach,))
    
    copies = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return copies


def get_copy_by_id(ma_quyen: int):
    """Lấy thông tin quyển sách theo mã"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT q.*, s.tieu_de, s.tac_gia, s.loai_sach, tl.ten_the_loai
        FROM QUYEN_SACH q
        JOIN SACH s ON q.ma_sach = s.ma_sach
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        WHERE q.ma_quyen = ?
    """, (ma_quyen,))
    
    copy = cursor.fetchone()
    conn.close()
    return dict(copy) if copy else None


def get_copy_by_code(ma_quyen_sach: str):
    """Lấy thông tin quyển sách theo mã quyển"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT q.*, s.tieu_de, s.tac_gia, s.loai_sach, tl.ten_the_loai
        FROM QUYEN_SACH q
        JOIN SACH s ON q.ma_sach = s.ma_sach
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        WHERE q.ma_quyen_sach = ?
    """, (ma_quyen_sach,))
    
    copy = cursor.fetchone()
    conn.close()
    return dict(copy) if copy else None


def add_book_copy(ma_sach: int, vi_tri: str = None, ghi_chu: str = None):
    """Thêm quyển sách mới cho đầu sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Lấy số thứ tự quyển tiếp theo
    cursor.execute("""
        SELECT COUNT(*) as count FROM QUYEN_SACH WHERE ma_sach = ?
    """, (ma_sach,))
    next_num = cursor.fetchone()['count'] + 1
    
    ma_quyen_sach = f"S{ma_sach:04d}-Q{next_num:03d}"
    
    cursor.execute("""
        INSERT INTO QUYEN_SACH (ma_sach, ma_quyen_sach, trang_thai, vi_tri, ghi_chu, ngay_nhap)
        VALUES (?, ?, 'CO_SAN', ?, ?, ?)
    """, (ma_sach, ma_quyen_sach, vi_tri, ghi_chu, datetime.now().strftime('%Y-%m-%d')))
    
    ma_quyen = cursor.lastrowid
    
    # Cập nhật số lượng trong SACH_GIAY
    cursor.execute("""
        UPDATE SACH_GIAY SET so_luong = so_luong + 1 WHERE ma_sach = ?
    """, (ma_sach,))
    
    conn.commit()
    conn.close()
    return ma_quyen, ma_quyen_sach


def update_book_copy(ma_quyen: int, trang_thai: str = None, vi_tri: str = None, ghi_chu: str = None):
    """Cập nhật thông tin quyển sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    
    if trang_thai is not None:
        updates.append("trang_thai = ?")
        params.append(trang_thai)
    if vi_tri is not None:
        updates.append("vi_tri = ?")
        params.append(vi_tri)
    if ghi_chu is not None:
        updates.append("ghi_chu = ?")
        params.append(ghi_chu)
    
    if updates:
        params.append(ma_quyen)
        cursor.execute(f"""
            UPDATE QUYEN_SACH SET {', '.join(updates)} WHERE ma_quyen = ?
        """, params)
    
    conn.commit()
    conn.close()


def delete_book_copy(ma_quyen: int):
    """Xóa quyển sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra quyển sách có đang được mượn không
    cursor.execute("""
        SELECT trang_thai, ma_sach FROM QUYEN_SACH WHERE ma_quyen = ?
    """, (ma_quyen,))
    copy = cursor.fetchone()
    
    if not copy:
        conn.close()
        raise Exception("Không tìm thấy quyển sách!")
    
    if copy['trang_thai'] == 'DANG_MUON':
        conn.close()
        raise Exception("Không thể xóa quyển sách đang được mượn!")
    
    ma_sach = copy['ma_sach']
    
    cursor.execute("DELETE FROM QUYEN_SACH WHERE ma_quyen = ?", (ma_quyen,))
    
    # Cập nhật số lượng trong SACH_GIAY
    cursor.execute("""
        UPDATE SACH_GIAY SET so_luong = so_luong - 1 WHERE ma_sach = ? AND so_luong > 0
    """, (ma_sach,))
    
    conn.commit()
    conn.close()


def get_available_copy(ma_sach: int):
    """Lấy một quyển sách có sẵn của đầu sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM QUYEN_SACH 
        WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
        ORDER BY ma_quyen
        LIMIT 1
    """, (ma_sach,))
    
    copy = cursor.fetchone()
    conn.close()
    return dict(copy) if copy else None


def count_available_copies(ma_sach: int):
    """Đếm số quyển sách có sẵn của một đầu sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM QUYEN_SACH 
        WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
    """, (ma_sach,))
    
    count = cursor.fetchone()['count']
    conn.close()
    return count


def count_copies_by_status(ma_sach: int):
    """Đếm số quyển sách theo từng trạng thái"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT trang_thai, COUNT(*) as count 
        FROM QUYEN_SACH 
        WHERE ma_sach = ?
        GROUP BY trang_thai
    """, (ma_sach,))
    
    result = {row['trang_thai']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return result
    
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

def get_all_readers(search_term: str = "", limit: int = None, offset: int = None):
    """Lấy danh sách đọc giả"""
    conn = None
    try:
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
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
        
        cursor.execute(query, params)
        readers = [dict(row) for row in cursor.fetchall()]
        return readers
    except Exception as e:
        raise Exception(f"Lỗi khi lấy danh sách đọc giả: {str(e)}")
    finally:
        if conn:
            conn.close()


def count_readers(search_term: str = ""):
    """Đếm tổng số đọc giả"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) as total 
            FROM NGUOI_DUNG nd
            JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
            WHERE nd.loai_nguoi_dung = 'DOC_GIA'
        """
        params = []
        
        if search_term:
            query += " AND (nd.ho_ten LIKE ? OR dg.ma_doc_gia LIKE ? OR nd.so_dt LIKE ?)"
            params.extend([f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"])
        
        cursor.execute(query, params)
        return cursor.fetchone()['total']
    except Exception:
        return 0
    finally:
        if conn:
            conn.close()


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

def get_staff_by_id(ma_nd: int):
    """Lấy thông tin nhân viên theo mã người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT nd.*, nv.ma_nhan_vien
        FROM NGUOI_DUNG nd
        JOIN NHAN_VIEN nv ON nd.ma_nd = nv.ma_nd
        WHERE nd.ma_nd = ?
    """, (ma_nd,))
    
    staff = cursor.fetchone()
    conn.close()
    return dict(staff) if staff else None


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


def add_staff(ho_ten: str, dia_chi: str, so_dt: str, email: str, ma_nhan_vien: str,
              create_account: bool = True, username: str = None, password: str = None):
    """Thêm nhân viên mới. Nếu create_account True, tạo tài khoản với username/password.
    Nếu username/password bỏ trống, mặc định dùng ma_nhan_vien (lower) cho cả hai."""
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

        if create_account:
            user = username.strip().lower() if username else ma_nhan_vien.lower()
            pwd = password if password else ma_nhan_vien.lower()
            cursor.execute("""
                INSERT INTO TAI_KHOAN (ten_tk, mat_khau, ma_nd) VALUES (?, ?, ?)
            """, (user, hash_password(pwd), ma_nd))
        
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

def get_all_borrows(search_term: str = "", status: str = None, limit: int = None, offset: int = None):
    """Lấy danh sách phiếu mượn"""
    conn = None
    try:
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
        
        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)
        
        cursor.execute(query, params)
        borrows = [dict(row) for row in cursor.fetchall()]
        return borrows
    except Exception as e:
        raise Exception(f"Lỗi khi lấy danh sách phiếu mượn: {str(e)}")
    finally:
        if conn:
            conn.close()


def count_borrows(search_term: str = "", status: str = None):
    """Đếm tổng số phiếu mượn"""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT COUNT(*) as total
            FROM PHIEU_MUON_TRA p
            JOIN DOC_GIA dg ON p.ma_nd_doc_gia = dg.ma_nd
            JOIN NGUOI_DUNG nd_dg ON dg.ma_nd = nd_dg.ma_nd
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
        
        cursor.execute(query, params)
        return cursor.fetchone()['total']
    except Exception:
        return 0
    finally:
        if conn:
            conn.close()


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
    
    # Kiểm tra loại sách
    cursor.execute("""
        SELECT s.loai_sach
        FROM SACH s
        WHERE s.ma_sach = ?
    """, (ma_sach,))
    
    sach = cursor.fetchone()
    if not sach:
        conn.close()
        raise Exception("Không tìm thấy sách!")
    
    ma_quyen = None
    
    if sach['loai_sach'] == 'SACH_GIAY':
        # Tìm quyển sách có sẵn
        cursor.execute("""
            SELECT ma_quyen FROM QUYEN_SACH 
            WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
            ORDER BY ma_quyen LIMIT 1
        """, (ma_sach,))
        quyen = cursor.fetchone()
        
        if not quyen:
            conn.close()
            raise Exception("Sách đã hết! Vui lòng chọn sách khác.")
        
        ma_quyen = quyen['ma_quyen']
    
    ngay_muon = datetime.now()
    ngay_hen_tra = ngay_muon + timedelta(days=so_ngay_muon)
    
    # Đảm bảo ma_nd_nhan_vien tồn tại trong bảng NHAN_VIEN để tránh lỗi FOREIGN KEY
    cursor.execute("SELECT ma_nd FROM NHAN_VIEN WHERE ma_nd = ?", (ma_nd_nhan_vien,))
    if not cursor.fetchone():
        ma_nv_code = f"NV{ma_nd_nhan_vien:04d}"
        cursor.execute("INSERT OR IGNORE INTO NHAN_VIEN (ma_nd, ma_nhan_vien) VALUES (?, ?)", (ma_nd_nhan_vien, ma_nv_code))

    cursor.execute("""
        INSERT INTO PHIEU_MUON_TRA 
        (ma_nd_doc_gia, ma_nd_nhan_vien, ma_sach, ma_quyen, ngay_muon, ngay_hen_tra, trang_thai_phieu)
        VALUES (?, ?, ?, ?, ?, ?, 'DANG_MUON')
    """, (ma_nd_doc_gia, ma_nd_nhan_vien, ma_sach, ma_quyen,
          ngay_muon.strftime('%Y-%m-%d'), ngay_hen_tra.strftime('%Y-%m-%d')))
    
    ma_phieu = cursor.lastrowid
    
    # Cập nhật trạng thái quyển sách
    if ma_quyen:
        cursor.execute("""
            UPDATE QUYEN_SACH SET trang_thai = 'DANG_MUON' WHERE ma_quyen = ?
        """, (ma_quyen,))
    
    conn.commit()
    conn.close()
    return ma_phieu


def return_book(ma_phieu: int, tien_phat: float = 0):
    """Trả sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    ngay_tra = datetime.now().strftime('%Y-%m-%d')
    
    # Lấy thông tin phiếu mượn
    cursor.execute("SELECT ma_sach, ma_quyen FROM PHIEU_MUON_TRA WHERE ma_phieu = ?", (ma_phieu,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return False
    
    ma_sach = result['ma_sach']
    ma_quyen = result['ma_quyen']
    
    # Cập nhật phiếu mượn
    cursor.execute("""
        UPDATE PHIEU_MUON_TRA 
        SET ngay_tra_thuc = ?, trang_thai_phieu = 'DA_TRA', tien_phat = ?
        WHERE ma_phieu = ?
    """, (ngay_tra, tien_phat, ma_phieu))
    
    # Cập nhật trạng thái quyển sách về có sẵn
    if ma_quyen:
        cursor.execute("""
            UPDATE QUYEN_SACH SET trang_thai = 'CO_SAN' WHERE ma_quyen = ?
        """, (ma_quyen,))
    
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


# ==================== YÊU CẦU MƯỢN SÁCH ====================

def create_borrow_request(ma_nd_doc_gia: int, ma_sach: int, so_ngay_muon_de_xuat: int, ghi_chu: str = None):
    """Tạo yêu cầu mượn sách từ đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Giới hạn số sách mượn đồng thời
    MAX_ACTIVE_BORROWS = 5
    
    # Kiểm tra số ngày hợp lệ
    if so_ngay_muon_de_xuat <= 0 or so_ngay_muon_de_xuat > 30:
        conn.close()
        raise Exception("Số ngày mượn phải từ 1-30 ngày!")
    
    # Kiểm tra số sách đang mượn
    cursor.execute("""
        SELECT COUNT(*) as count FROM PHIEU_MUON_TRA 
        WHERE ma_nd_doc_gia = ? AND trang_thai_phieu = 'DANG_MUON'
    """, (ma_nd_doc_gia,))
    
    active_borrows = cursor.fetchone()['count']
    
    # Kiểm tra số yêu cầu đang chờ xử lý
    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_MUON 
        WHERE ma_nd_doc_gia = ? AND trang_thai IN ('CHO_DUYET', 'CHO_LAY_SACH')
    """, (ma_nd_doc_gia,))
    
    pending_requests = cursor.fetchone()['count']
    
    if active_borrows + pending_requests >= MAX_ACTIVE_BORROWS:
        conn.close()
        raise Exception(f"Bạn chỉ có thể mượn tối đa {MAX_ACTIVE_BORROWS} sách cùng lúc!\n"
                       f"Hiện tại: {active_borrows} đang mượn, {pending_requests} đang chờ xử lý.")
    
    # Kiểm tra đọc giả đã mượn sách này chưa (và chưa trả)
    cursor.execute("""
        SELECT COUNT(*) as count FROM PHIEU_MUON_TRA 
        WHERE ma_nd_doc_gia = ? AND ma_sach = ? AND trang_thai_phieu = 'DANG_MUON'
    """, (ma_nd_doc_gia, ma_sach))
    
    if cursor.fetchone()['count'] > 0:
        conn.close()
        raise Exception("Bạn đang mượn sách này! Vui lòng trả sách trước khi mượn lại.")
    
    # Kiểm tra đã có yêu cầu chờ duyệt hoặc chờ lấy sách cho sách này chưa
    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_MUON 
        WHERE ma_nd_doc_gia = ? AND ma_sach = ? AND trang_thai IN ('CHO_DUYET', 'CHO_LAY_SACH')
    """, (ma_nd_doc_gia, ma_sach))
    
    if cursor.fetchone()['count'] > 0:
        conn.close()
        raise Exception("Bạn đã có yêu cầu mượn sách này đang chờ xử lý!")
    
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
    
    if sach['trang_thai_sach'] in ['HONG', 'MAT']:
        conn.close()
        raise Exception("Sách không khả dụng (hỏng hoặc mất)!")
    
    if sach['loai_sach'] == 'SACH_GIAY':
        if sach['so_luong'] is None or sach['so_luong'] <= 0:
            conn.close()
            raise Exception("Sách đã hết! Vui lòng chọn sách khác.")
    
    ngay_yeu_cau = datetime.now().strftime('%Y-%m-%d')
    
    cursor.execute("""
        INSERT INTO YEU_CAU_MUON 
        (ma_nd_doc_gia, ma_sach, ngay_yeu_cau, so_ngay_muon_de_xuat, ghi_chu, trang_thai)
        VALUES (?, ?, ?, ?, ?, 'CHO_DUYET')
    """, (ma_nd_doc_gia, ma_sach, ngay_yeu_cau, so_ngay_muon_de_xuat, ghi_chu))
    
    ma_yeu_cau = cursor.lastrowid
    # Nếu là sách giấy, cố gắng "đặt trước" một quyển (đánh dấu KHONG_CO_SAN)
    if sach['loai_sach'] == 'SACH_GIAY':
        cursor.execute("""
            SELECT ma_quyen FROM QUYEN_SACH 
            WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
            ORDER BY ma_quyen LIMIT 1
        """, (ma_sach,))
        quyen = cursor.fetchone()
        if quyen:
            try:
                # Đánh dấu quyển được đặt trước để tránh người khác mượn cùng lúc
                cursor.execute("UPDATE QUYEN_SACH SET trang_thai = 'KHONG_CO_SAN' WHERE ma_quyen = ?", (quyen['ma_quyen'],))
                # Ghi lại mã quyển vào yêu cầu để theo dõi (nếu cột tồn tại)
                try:
                    cursor.execute("UPDATE YEU_CAU_MUON SET ma_quyen = ? WHERE ma_yeu_cau = ?", (quyen['ma_quyen'], ma_yeu_cau))
                except Exception:
                    # Nếu cột ma_quyen không tồn tại, bỏ qua (migration khác)
                    pass
            except Exception:
                # Nếu không thể đặt trước (race), bỏ qua và để nhân viên xử lý sau
                pass
    
    # Lấy thông tin để tạo thông báo cho nhân viên
    cursor.execute("SELECT tieu_de FROM SACH WHERE ma_sach = ?", (ma_sach,))
    sach_info = cursor.fetchone()
    ten_sach = sach_info['tieu_de'] if sach_info else 'Sách'
    
    cursor.execute("SELECT ho_ten FROM NGUOI_DUNG WHERE ma_nd = ?", (ma_nd_doc_gia,))
    doc_gia_info = cursor.fetchone()
    ten_doc_gia = doc_gia_info['ho_ten'] if doc_gia_info else 'Đọc giả'
    
    # Tạo thông báo cho tất cả nhân viên và admin
    cursor.execute("""
        SELECT ma_nd FROM NGUOI_DUNG WHERE loai_nguoi_dung IN ('NHAN_VIEN', 'ADMIN')
    """)
    staff_list = cursor.fetchall()
    
    for staff in staff_list:
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'YEU_CAU_MOI', ?, ?)
        """, (
            staff['ma_nd'],
            "📬 Yêu cầu mượn sách mới",
            f"Đọc giả {ten_doc_gia} yêu cầu mượn sách \"{ten_sach}\" trong {so_ngay_muon_de_xuat} ngày.",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau:{ma_yeu_cau}"
        ))
    
    conn.commit()
    conn.close()
    
    return ma_yeu_cau


def get_all_borrow_requests(status: str = None, search_term: str = ""):
    """Lấy danh sách yêu cầu mượn sách (cho nhân viên/admin)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT yc.*, 
               nd.ho_ten as ten_doc_gia, nd.so_dt, nd.email,
               dg.ma_doc_gia,
               s.tieu_de, s.tac_gia, s.loai_sach,
               tl.ten_the_loai,
               nd2.ho_ten as nguoi_xu_ly
        FROM YEU_CAU_MUON yc
        JOIN NGUOI_DUNG nd ON yc.ma_nd_doc_gia = nd.ma_nd
        JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
        JOIN SACH s ON yc.ma_sach = s.ma_sach
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        LEFT JOIN NGUOI_DUNG nd2 ON yc.ma_nd_xu_ly = nd2.ma_nd
        WHERE 1=1
    """
    params = []
    
    if status:
        query += " AND yc.trang_thai = ?"
        params.append(status)
    
    if search_term:
        query += """ AND (nd.ho_ten LIKE ? OR s.tieu_de LIKE ? OR dg.ma_doc_gia LIKE ?)"""
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern, search_pattern, search_pattern])
    
    query += " ORDER BY yc.ngay_yeu_cau DESC, yc.ma_yeu_cau DESC"
    
    cursor.execute(query, params)
    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return requests


def get_reader_borrow_requests(ma_nd_doc_gia: int):
    """Lấy danh sách yêu cầu mượn của đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT yc.*, 
               s.tieu_de, s.tac_gia, s.loai_sach,
               tl.ten_the_loai,
               nd.ho_ten as nguoi_xu_ly
        FROM YEU_CAU_MUON yc
        JOIN SACH s ON yc.ma_sach = s.ma_sach
        LEFT JOIN THE_LOAI_SACH tl ON s.ma_the_loai = tl.ma_the_loai
        LEFT JOIN NGUOI_DUNG nd ON yc.ma_nd_xu_ly = nd.ma_nd
        WHERE yc.ma_nd_doc_gia = ?
        ORDER BY yc.ngay_yeu_cau DESC
    """, (ma_nd_doc_gia,))
    
    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return requests


def create_card_request(ma_nd_doc_gia: int):
    """Tạo yêu cầu in/cấp lại thẻ cho đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()

    # Kiểm tra đã có yêu cầu đang chờ xử lý không
    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_THE
        WHERE ma_nd_doc_gia = ? AND trang_thai IN ('CHO_DUYET', 'DANG_XU_LY')
    """, (ma_nd_doc_gia,))
    if cursor.fetchone()['count'] > 0:
        conn.close()
        raise Exception("Bạn đã có yêu cầu in thẻ đang chờ xử lý!")

    ngay_yeu_cau = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        INSERT INTO YEU_CAU_THE (ma_nd_doc_gia, ngay_yeu_cau, trang_thai)
        VALUES (?, ?, 'CHO_DUYET')
    """, (ma_nd_doc_gia, ngay_yeu_cau))

    ma_yeu_cau = cursor.lastrowid

    # Tạo thông báo cho tất cả nhân viên và admin
    cursor.execute("SELECT ma_nd FROM NGUOI_DUNG WHERE loai_nguoi_dung IN ('NHAN_VIEN', 'ADMIN')")
    staff_list = cursor.fetchall()

    cursor.execute("SELECT ho_ten FROM NGUOI_DUNG WHERE ma_nd = ?", (ma_nd_doc_gia,))
    doc_gia_info = cursor.fetchone()
    ten_doc_gia = doc_gia_info['ho_ten'] if doc_gia_info else 'Đọc giả'

    for staff in staff_list:
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'YEU_CAU_MOI', ?, ?)
        """, (
            staff['ma_nd'],
            "📬 Yêu cầu in thẻ mới",
            f"Đọc giả {ten_doc_gia} yêu cầu in/cấp lại thẻ đọc giả.",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau_the:{ma_yeu_cau}"
        ))

    conn.commit()
    conn.close()
    return ma_yeu_cau


def get_all_card_requests(status: str = None, search_term: str = ""):
    """Lấy danh sách yêu cầu in/cấp thẻ (cho nhân viên/admin)"""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT yt.*, nd.ho_ten as ten_doc_gia, dg.ma_doc_gia, nd2.ho_ten as nguoi_xu_ly
        FROM YEU_CAU_THE yt
        JOIN NGUOI_DUNG nd ON yt.ma_nd_doc_gia = nd.ma_nd
        LEFT JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
        LEFT JOIN NGUOI_DUNG nd2 ON yt.ma_nd_xu_ly = nd2.ma_nd
        WHERE 1=1
    """
    params = []

    if status:
        query += " AND yt.trang_thai = ?"
        params.append(status)

    if search_term:
        query += " AND (nd.ho_ten LIKE ? OR dg.ma_doc_gia LIKE ? )"
        pattern = f"%{search_term}%"
        params.extend([pattern, pattern])

    query += " ORDER BY yt.ngay_yeu_cau DESC, yt.ma_yeu_cau DESC"

    cursor.execute(query, params)
    reqs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reqs


def get_card_request_by_id(ma_yeu_cau: int):
    """Lấy chi tiết một yêu cầu in thẻ theo id"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT yt.*, nd.ho_ten as ten_doc_gia, dg.ma_doc_gia, nd2.ho_ten as nguoi_xu_ly
        FROM YEU_CAU_THE yt
        JOIN NGUOI_DUNG nd ON yt.ma_nd_doc_gia = nd.ma_nd
        LEFT JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd
        LEFT JOIN NGUOI_DUNG nd2 ON yt.ma_nd_xu_ly = nd2.ma_nd
        WHERE yt.ma_yeu_cau = ?
    """, (ma_yeu_cau,))

    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_reader_card_requests(ma_nd_doc_gia: int):
    """Lấy danh sách yêu cầu in thẻ của đọc giả"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT yc.* , nd.ho_ten as nguoi_xu_ly
        FROM YEU_CAU_THE yc
        LEFT JOIN NGUOI_DUNG nd ON yc.ma_nd_xu_ly = nd.ma_nd
        WHERE yc.ma_nd_doc_gia = ?
        ORDER BY yc.ngay_yeu_cau DESC
    """, (ma_nd_doc_gia,))

    requests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return requests



def approve_borrow_request(ma_yeu_cau: int, ma_nd_xu_ly: int, so_ngay_muon: int):
    """Duyệt yêu cầu mượn sách (nhân viên/admin) - chuyển sang chờ lấy sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Kiểm tra số ngày hợp lệ
    if so_ngay_muon <= 0 or so_ngay_muon > 30:
        conn.close()
        raise Exception("Số ngày mượn phải từ 1-30 ngày!")
    
    # Lấy thông tin yêu cầu
    cursor.execute("""
        SELECT yc.*, s.loai_sach
        FROM YEU_CAU_MUON yc
        JOIN SACH s ON yc.ma_sach = s.ma_sach
        WHERE yc.ma_yeu_cau = ?
    """, (ma_yeu_cau,))
    
    yeu_cau = cursor.fetchone()
    if not yeu_cau:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu!")
    
    if yeu_cau['trang_thai'] != 'CHO_DUYET':
        conn.close()
        raise Exception("Yêu cầu này đã được xử lý!")
    
    # Kiểm tra sách còn khả dụng không (cho sách giấy)
    if yeu_cau['loai_sach'] == 'SACH_GIAY':
        cursor.execute("SELECT COUNT(*) as count FROM QUYEN_SACH WHERE ma_sach = ? AND trang_thai = 'CO_SAN'", (yeu_cau['ma_sach'],))
        if cursor.fetchone()['count'] <= 0:
            # Nếu không còn CO_SAN, nhưng yêu cầu này đã đặt trước một quyển, coi là hợp lệ
            try:
                if yeu_cau.get('ma_quyen'):
                    cursor.execute("SELECT trang_thai FROM QUYEN_SACH WHERE ma_quyen = ?", (yeu_cau['ma_quyen'],))
                    q = cursor.fetchone()
                    if q and q['trang_thai'] in ('KHONG_CO_SAN', 'CO_SAN'):
                        pass  # vẫn cho duyệt vì đã có quyển đặt trước
                    else:
                        conn.close()
                        raise Exception("Sách đã hết!")
                else:
                    conn.close()
                    raise Exception("Sách đã hết!")
            except Exception:
                conn.close()
                raise
    
    # Cập nhật trạng thái yêu cầu sang CHO_LAY_SACH
    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d')
    # Hạn lấy sách: 3 ngày sau khi duyệt
    han_lay_sach = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        UPDATE YEU_CAU_MUON 
        SET trang_thai = 'CHO_LAY_SACH', ma_nd_xu_ly = ?, ngay_xu_ly = ?, 
            so_ngay_muon_chinh_thuc = ?, han_lay_sach = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, so_ngay_muon, han_lay_sach, ma_yeu_cau))
    
    # Xóa tất cả thông báo YEU_CAU_MOI liên quan đến yêu cầu này
    cursor.execute("""
        DELETE FROM THONG_BAO WHERE link_lien_quan = ? AND loai_thong_bao = 'YEU_CAU_MOI'
    """, (f"yeu_cau:{ma_yeu_cau}",))
    
    # Lấy thông tin sách để tạo thông báo
    cursor.execute("SELECT tieu_de FROM SACH WHERE ma_sach = ?", (yeu_cau['ma_sach'],))
    sach = cursor.fetchone()
    ten_sach = sach['tieu_de'] if sach else 'Sách'
    
    # Tính ngày hết hạn lấy sách
    han_lay_str = (datetime.now() + timedelta(days=3)).strftime('%d/%m/%Y')
    
    # Tạo thông báo cho đọc giả
    cursor.execute("""
        INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
        VALUES (?, ?, ?, 'YEU_CAU_DUYET', ?, ?)
    """, (
        yeu_cau['ma_nd_doc_gia'],
        "✅ Yêu cầu mượn sách đã được duyệt!",
        f"Yêu cầu mượn sách \"{ten_sach}\" đã được duyệt với thời hạn {so_ngay_muon} ngày.\n⏰ Vui lòng đến thư viện lấy sách trước ngày {han_lay_str}.",
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        f"yeu_cau:{ma_yeu_cau}"
    ))
    
    conn.commit()
    conn.close()
    
    return ma_yeu_cau


def approve_card_request(ma_yeu_cau: int, ma_nd_xu_ly: int):
    """Nhân viên đánh dấu yêu cầu in thẻ đang xử lý"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM YEU_CAU_THE WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
    yc = cursor.fetchone()
    if not yc:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu in thẻ!")

    if yc['trang_thai'] != 'CHO_DUYET':
        conn.close()
        raise Exception("Yêu cầu này đã được xử lý!")

    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE YEU_CAU_THE SET trang_thai = 'DANG_XU_LY', ma_nd_xu_ly = ?, ngay_xu_ly = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, ma_yeu_cau))

    # Xóa thông báo YEU_CAU_MOI liên quan
    cursor.execute("DELETE FROM THONG_BAO WHERE link_lien_quan = ? AND loai_thong_bao = 'YEU_CAU_MOI'", (f"yeu_cau_the:{ma_yeu_cau}",))

    # Thông báo cho đọc giả
    cursor.execute("SELECT nd.ma_nd, nd.ho_ten FROM NGUOI_DUNG nd JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd JOIN YEU_CAU_THE yt ON yt.ma_nd_doc_gia = dg.ma_nd WHERE yt.ma_yeu_cau = ?", (ma_yeu_cau,))
    reader = cursor.fetchone()
    if reader:
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'YEU_CAU_DUYET', ?, ?)
        """, (
            reader['ma_nd'],
            "✅ Yêu cầu in thẻ đang được xử lý",
            "Yêu cầu in thẻ của bạn đã được nhân viên tiếp nhận và đang xử lý.",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau_the:{ma_yeu_cau}"
        ))

    conn.commit()
    conn.close()
    return ma_yeu_cau


def mark_card_printed(ma_yeu_cau: int, ma_nd_xu_ly: int):
    """Đánh dấu yêu cầu đã in thẻ và tạo/ cập nhật THE_DOC_GIA"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM YEU_CAU_THE WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
    yc = cursor.fetchone()
    if not yc:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu in thẻ!")

    if yc['trang_thai'] not in ('CHO_DUYET', 'DANG_XU_LY'):
        conn.close()
        raise Exception("Yêu cầu này không ở trạng thái có thể in!")

    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE YEU_CAU_THE SET trang_thai = 'DA_IN', ma_nd_xu_ly = ?, ngay_xu_ly = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, ma_yeu_cau))

    # Tạo hoặc cập nhật THE_DOC_GIA
    ma_nd_doc = yc['ma_nd_doc_gia']
    cursor.execute("SELECT ma_the FROM THE_DOC_GIA WHERE ma_nd_doc_gia = ?", (ma_nd_doc,))
    existing = cursor.fetchone()
    ngay_cap = datetime.now()
    ngay_het_han = (ngay_cap + timedelta(days=365)).strftime('%Y-%m-%d')
    if existing:
        cursor.execute("UPDATE THE_DOC_GIA SET ngay_cap = ?, ngay_het_han = ?, trang_thai_the = 'HOAT_DONG' WHERE ma_nd_doc_gia = ?",
                       (ngay_cap.strftime('%Y-%m-%d'), ngay_het_han, ma_nd_doc))
    else:
        cursor.execute("INSERT INTO THE_DOC_GIA (ma_nd_doc_gia, ngay_cap, ngay_het_han, trang_thai_the) VALUES (?, ?, ?, 'HOAT_DONG')",
                       (ma_nd_doc, ngay_cap.strftime('%Y-%m-%d'), ngay_het_han))

    # Xóa các thông báo cũ liên quan
    cursor.execute("DELETE FROM THONG_BAO WHERE link_lien_quan = ?", (f"yeu_cau_the:{ma_yeu_cau}",))

    # Thông báo cho đọc giả
    cursor.execute("SELECT nd.ma_nd FROM NGUOI_DUNG nd JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd JOIN YEU_CAU_THE yt ON yt.ma_nd_doc_gia = dg.ma_nd WHERE yt.ma_yeu_cau = ?", (ma_yeu_cau,))
    reader = cursor.fetchone()
    if reader:
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'HE_THONG', ?, ?)
        """, (
            reader['ma_nd'],
            "✅ Thẻ độc giả đã được in",
            "Thẻ độc giả của bạn đã được in và kích hoạt. Vui lòng đến thư viện nhận thẻ.",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau_the:{ma_yeu_cau}"
        ))

    conn.commit()
    conn.commit()
    conn.close()
    return ma_yeu_cau


def confirm_card_pickup(ma_yeu_cau: int, ma_nd_xu_ly: int):
    """Xác nhận đọc giả đã lấy thẻ: đánh dấu da_nhan = 1 và ghi nhận người xử lý"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM YEU_CAU_THE WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
    yc = cursor.fetchone()
    if not yc:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu in thẻ!")

    # Phải in thẻ trước khi xác nhận lấy thẻ
    if yc['trang_thai'] != 'DA_IN':
        conn.close()
        raise Exception("Chỉ có thể xác nhận lấy thẻ khi thẻ đã được in!")

    # Nếu đã được đánh dấu là đã nhận
    try:
        if yc.get('da_nhan') and yc['da_nhan'] == 1:
            conn.close()
            raise Exception("Yêu cầu đã được xác nhận lấy trước đó.")
    except Exception:
        # một số sqlite Row có thể không hỗ trợ .get trên các phiên bản cũ, dùng phương án thay thế
        pass

    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE YEU_CAU_THE SET da_nhan = 1, ma_nd_xu_ly = ?, ngay_xu_ly = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, ma_yeu_cau))

    # Thông báo cho đọc giả
    cursor.execute("SELECT nd.ma_nd FROM NGUOI_DUNG nd JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd JOIN YEU_CAU_THE yt ON yt.ma_nd_doc_gia = dg.ma_nd WHERE yt.ma_yeu_cau = ?", (ma_yeu_cau,))
    reader = cursor.fetchone()
    if reader:
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'HE_THONG', ?, ?)
        """, (
            reader['ma_nd'],
            "🎉 Đã nhận thẻ",
            "Bạn đã nhận thẻ độc giả tại thư viện. Cảm ơn!",
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau_the:{ma_yeu_cau}"
        ))

    conn.commit()
    conn.close()
    return ma_yeu_cau


def reject_card_request(ma_yeu_cau: int, ma_nd_xu_ly: int, ly_do: str = None):
    """Từ chối yêu cầu in thẻ"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM YEU_CAU_THE WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
    yc = cursor.fetchone()
    if not yc:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu in thẻ!")

    if yc['trang_thai'] != 'CHO_DUYET':
        conn.close()
        raise Exception("Chỉ có thể từ chối yêu cầu ở trạng thái Chờ duyệt")

    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        UPDATE YEU_CAU_THE SET trang_thai = 'TU_CHOI', ma_nd_xu_ly = ?, ngay_xu_ly = ?, ly_do_tu_choi = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, ly_do, ma_yeu_cau))

    # Xóa thông báo YEU_CAU_MOI liên quan
    cursor.execute("DELETE FROM THONG_BAO WHERE link_lien_quan = ? AND loai_thong_bao = 'YEU_CAU_MOI'", (f"yeu_cau_the:{ma_yeu_cau}",))

    # Thông báo cho đọc giả
    cursor.execute("SELECT nd.ma_nd FROM NGUOI_DUNG nd JOIN DOC_GIA dg ON nd.ma_nd = dg.ma_nd JOIN YEU_CAU_THE yt ON yt.ma_nd_doc_gia = dg.ma_nd WHERE yt.ma_yeu_cau = ?", (ma_yeu_cau,))
    reader = cursor.fetchone()
    if reader:
        noi_dung = "Yêu cầu in thẻ của bạn đã bị từ chối."
        if ly_do:
            noi_dung += f" Lý do: {ly_do}"
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'YEU_CAU_TU_CHOI', ?, ?)
        """, (
            reader['ma_nd'],
            "❌ Yêu cầu in thẻ bị từ chối",
            noi_dung,
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau_the:{ma_yeu_cau}"
        ))

    conn.commit()
    conn.close()
    return ma_yeu_cau


def confirm_book_pickup(ma_yeu_cau: int, ma_nd_nhan_vien: int):
    """Xác nhận đọc giả đã lấy sách - tạo phiếu mượn"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Lấy thông tin yêu cầu
    cursor.execute("""
        SELECT yc.*, s.loai_sach
        FROM YEU_CAU_MUON yc
        JOIN SACH s ON yc.ma_sach = s.ma_sach
        WHERE yc.ma_yeu_cau = ?
    """, (ma_yeu_cau,))
    
    yeu_cau = cursor.fetchone()
    if not yeu_cau:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu!")
    
    if yeu_cau['trang_thai'] != 'CHO_LAY_SACH':
        conn.close()
        raise Exception("Yêu cầu này chưa được duyệt hoặc đã lấy sách!")
    
    ma_quyen = None
    
    # Kiểm tra và lấy quyển sách có sẵn (cho sách giấy)
    if yeu_cau['loai_sach'] == 'SACH_GIAY':
        # Nếu trước đó đã đặt trước một quyển (ma_quyen trong yêu cầu), dùng nó
        if yeu_cau.get('ma_quyen'):
            cursor.execute("SELECT ma_quyen, trang_thai FROM QUYEN_SACH WHERE ma_quyen = ?", (yeu_cau['ma_quyen'],))
            q = cursor.fetchone()
            if not q:
                conn.close()
                raise Exception("Quyển sách đặt trước không tồn tại!")
            # Nếu trạng thái không phải KHONG_CO_SAN hoặc CO_SAN, nghĩa là không thể lấy
            if q['trang_thai'] not in ('KHONG_CO_SAN', 'CO_SAN'):
                conn.close()
                raise Exception("Quyển sách đã không còn sẵn để lấy.")
            ma_quyen = q['ma_quyen']
        else:
            cursor.execute("""
                SELECT ma_quyen FROM QUYEN_SACH 
                WHERE ma_sach = ? AND trang_thai = 'CO_SAN'
                ORDER BY ma_quyen LIMIT 1
            """, (yeu_cau['ma_sach'],))
            quyen = cursor.fetchone()
            
            if not quyen:
                conn.close()
                raise Exception("Sách đã hết!")
            
            ma_quyen = quyen['ma_quyen']
    
    # Cập nhật trạng thái yêu cầu sang DA_LAY
    cursor.execute("""
        UPDATE YEU_CAU_MUON SET trang_thai = 'DA_LAY', ma_quyen = ? WHERE ma_yeu_cau = ?
    """, (ma_quyen, ma_yeu_cau))
    
    # Xóa thông báo YEU_CAU_DUYET liên quan đến yêu cầu này (đã lấy sách rồi)
    cursor.execute("""
        DELETE FROM THONG_BAO WHERE link_lien_quan = ? AND loai_thong_bao IN ('YEU_CAU_DUYET', 'CHO_LAY_SACH')
    """, (f"yeu_cau:{ma_yeu_cau}",))
    
    # Lấy số ngày mượn chính thức
    so_ngay_muon = yeu_cau['so_ngay_muon_chinh_thuc'] or yeu_cau['so_ngay_muon_de_xuat']
    
    # Tạo thông báo cho đọc giả xác nhận đã lấy sách
    cursor.execute("SELECT tieu_de FROM SACH WHERE ma_sach = ?", (yeu_cau['ma_sach'],))
    sach_info = cursor.fetchone()
    ten_sach = sach_info['tieu_de'] if sach_info else 'Sách'
    
    ngay_tra = (datetime.now() + timedelta(days=so_ngay_muon)).strftime('%d/%m/%Y')
    cursor.execute("""
        INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
        VALUES (?, ?, ?, 'HE_THONG', ?, ?)
    """, (
        yeu_cau['ma_nd_doc_gia'],
        "📚 Bạn đã lấy sách thành công!",
        f"Bạn đã mượn sách \"{ten_sach}\". Hạn trả: {ngay_tra}. Vui lòng trả sách đúng hạn!",
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        f"phieu_muon:new"
    ))
    
    # Tạo phiếu mượn
    ngay_muon = datetime.now()
    ngay_hen_tra = ngay_muon + timedelta(days=so_ngay_muon)
    
    # Đảm bảo ma_nd_nhan_vien tồn tại trong bảng NHAN_VIEN để tránh lỗi FOREIGN KEY
    cursor.execute("SELECT ma_nd FROM NHAN_VIEN WHERE ma_nd = ?", (ma_nd_nhan_vien,))
    if not cursor.fetchone():
        ma_nv_code = f"NV{ma_nd_nhan_vien:04d}"
        cursor.execute("INSERT OR IGNORE INTO NHAN_VIEN (ma_nd, ma_nhan_vien) VALUES (?, ?)", (ma_nd_nhan_vien, ma_nv_code))

    cursor.execute("""
        INSERT INTO PHIEU_MUON_TRA 
        (ma_nd_doc_gia, ma_nd_nhan_vien, ma_sach, ma_quyen, ngay_muon, ngay_hen_tra, trang_thai_phieu)
        VALUES (?, ?, ?, ?, ?, ?, 'DANG_MUON')
    """, (yeu_cau['ma_nd_doc_gia'], ma_nd_nhan_vien, yeu_cau['ma_sach'], ma_quyen,
          ngay_muon.strftime('%Y-%m-%d'), ngay_hen_tra.strftime('%Y-%m-%d')))
    
    ma_phieu = cursor.lastrowid
    
    # Cập nhật trạng thái quyển sách
    if ma_quyen:
        cursor.execute("UPDATE QUYEN_SACH SET trang_thai = 'DANG_MUON' WHERE ma_quyen = ?", (ma_quyen,))
    
    conn.commit()
    conn.close()
    
    return ma_phieu


def reject_borrow_request(ma_yeu_cau: int, ma_nd_xu_ly: int, ly_do: str = None):
    """Từ chối yêu cầu mượn sách"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT yc.trang_thai, yc.ma_nd_doc_gia, yc.ma_sach FROM YEU_CAU_MUON yc WHERE yc.ma_yeu_cau = ?
    """, (ma_yeu_cau,))
    
    yeu_cau = cursor.fetchone()
    if not yeu_cau:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu!")
    
    if yeu_cau['trang_thai'] != 'CHO_DUYET':
        conn.close()
        raise Exception("Yêu cầu này đã được xử lý!")
    
    ngay_xu_ly = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("""
        UPDATE YEU_CAU_MUON 
        SET trang_thai = 'TU_CHOI', ma_nd_xu_ly = ?, ngay_xu_ly = ?, ly_do_tu_choi = ?
        WHERE ma_yeu_cau = ?
    """, (ma_nd_xu_ly, ngay_xu_ly, ly_do, ma_yeu_cau))
    
    # Xóa tất cả thông báo YEU_CAU_MOI liên quan đến yêu cầu này
    cursor.execute("""
        DELETE FROM THONG_BAO WHERE link_lien_quan = ? AND loai_thong_bao = 'YEU_CAU_MOI'
    """, (f"yeu_cau:{ma_yeu_cau}",))
    
    # Lấy thông tin sách để tạo thông báo
    cursor.execute("SELECT tieu_de FROM SACH WHERE ma_sach = ?", (yeu_cau['ma_sach'],))
    sach = cursor.fetchone()
    ten_sach = sach['tieu_de'] if sach else 'Sách'
    
    # Tạo thông báo cho đọc giả
    noi_dung = f"Yêu cầu mượn sách \"{ten_sach}\" của bạn đã bị từ chối."
    if ly_do:
        noi_dung += f" Lý do: {ly_do}"
    
    cursor.execute("""
        INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
        VALUES (?, ?, ?, 'YEU_CAU_TU_CHOI', ?, ?)
    """, (
        yeu_cau['ma_nd_doc_gia'],
        "❌ Yêu cầu mượn sách bị từ chối",
        noi_dung,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        f"yeu_cau:{ma_yeu_cau}"
    ))
    # Nếu trước đó đã đặt trước một quyển, trả lại trạng thái CO_SAN cho quyển đó
    try:
        cursor.execute("SELECT ma_quyen FROM YEU_CAU_MUON WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
        row = cursor.fetchone()
        if row and row['ma_quyen']:
            cursor.execute("UPDATE QUYEN_SACH SET trang_thai = 'CO_SAN' WHERE ma_quyen = ?", (row['ma_quyen'],))
    except Exception:
        pass
    
    conn.commit()
    conn.close()


def cancel_borrow_request(ma_yeu_cau: int, ma_nd_doc_gia: int):
    """Hủy yêu cầu mượn sách (đọc giả tự hủy)"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT trang_thai, ma_nd_doc_gia FROM YEU_CAU_MUON WHERE ma_yeu_cau = ?
    """, (ma_yeu_cau,))
    
    yeu_cau = cursor.fetchone()
    if not yeu_cau:
        conn.close()
        raise Exception("Không tìm thấy yêu cầu!")
    
    if yeu_cau['ma_nd_doc_gia'] != ma_nd_doc_gia:
        conn.close()
        raise Exception("Bạn không có quyền hủy yêu cầu này!")
    
    if yeu_cau['trang_thai'] not in ('CHO_DUYET', 'CHO_LAY_SACH'):
        conn.close()
        raise Exception("Chỉ có thể hủy yêu cầu đang chờ duyệt hoặc chờ lấy sách!")
    
    cursor.execute("""
        UPDATE YEU_CAU_MUON SET trang_thai = 'DA_HUY' WHERE ma_yeu_cau = ?
    """, (ma_yeu_cau,))
    # Nếu trước đó đã đặt trước một quyển, trả lại trạng thái CO_SAN cho quyển đó
    try:
        cursor.execute("SELECT ma_quyen FROM YEU_CAU_MUON WHERE ma_yeu_cau = ?", (ma_yeu_cau,))
        row = cursor.fetchone()
        if row and row['ma_quyen']:
            cursor.execute("UPDATE QUYEN_SACH SET trang_thai = 'CO_SAN' WHERE ma_quyen = ?", (row['ma_quyen'],))
    except Exception:
        pass
    
    conn.commit()
    conn.close()


def get_pending_requests_count():
    """Đếm số yêu cầu đang chờ duyệt"""
    conn = get_connection()
    cursor = conn.cursor()
    # Đếm cả yêu cầu mượn và yêu cầu in thẻ đang chờ duyệt
    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_MUON WHERE trang_thai = 'CHO_DUYET'
    """)
    count_muon = cursor.fetchone()['count']

    cursor.execute("""
        SELECT COUNT(*) as count FROM YEU_CAU_THE WHERE trang_thai = 'CHO_DUYET'
    """)
    count_the = cursor.fetchone()['count']

    count = count_muon + count_the
    conn.close()
    
    return count


# ==================== THÔNG BÁO ====================

def create_notification(ma_nd: int, tieu_de: str, noi_dung: str, loai_thong_bao: str, link_lien_quan: str = None):
    """Tạo thông báo mới cho người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ma_nd, tieu_de, noi_dung, loai_thong_bao, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), link_lien_quan))
    
    conn.commit()
    conn.close()


def get_notifications(ma_nd: int, limit: int = 50, unread_only: bool = False):
    """Lấy danh sách thông báo của người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT * FROM THONG_BAO 
        WHERE ma_nd = ?
    """
    
    if unread_only:
        query += " AND da_doc = 0"
    
    query += " ORDER BY ngay_tao DESC LIMIT ?"
    
    cursor.execute(query, (ma_nd, limit))
    notifications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return notifications


def get_unread_notification_count(ma_nd: int) -> int:
    """Đếm số thông báo chưa đọc của người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as count FROM THONG_BAO 
        WHERE ma_nd = ? AND da_doc = 0
    """, (ma_nd,))
    
    count = cursor.fetchone()['count']
    conn.close()
    
    return count


def mark_notification_as_read(ma_thong_bao: int):
    """Đánh dấu thông báo đã đọc"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE THONG_BAO SET da_doc = 1 WHERE ma_thong_bao = ?
    """, (ma_thong_bao,))
    
    conn.commit()
    conn.close()


def mark_all_notifications_as_read(ma_nd: int):
    """Đánh dấu tất cả thông báo đã đọc"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE THONG_BAO SET da_doc = 1 WHERE ma_nd = ?
    """, (ma_nd,))
    
    conn.commit()
    conn.close()


def delete_notification(ma_thong_bao: int):
    """Xóa thông báo"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM THONG_BAO WHERE ma_thong_bao = ?", (ma_thong_bao,))
    
    conn.commit()
    conn.close()


def delete_all_notifications(ma_nd: int):
    """Xóa tất cả thông báo của người dùng"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM THONG_BAO WHERE ma_nd = ?", (ma_nd,))
    
    conn.commit()
    conn.close()


def delete_notifications_by_link(link_pattern: str):
    """Xóa tất cả thông báo có link_lien_quan khớp với pattern"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM THONG_BAO WHERE link_lien_quan = ?", (link_pattern,))
    
    conn.commit()
    conn.close()


def delete_old_notifications(days: int = 30):
    """Xóa thông báo cũ hơn số ngày chỉ định"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        DELETE FROM THONG_BAO WHERE ngay_tao < ? AND da_doc = 1
    """, (cutoff_date,))
    
    conn.commit()
    conn.close()


def check_and_notify_due_books():
    """Kiểm tra và tạo thông báo cho sách sắp hết hạn và quá hạn"""
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.now().date()
    now = datetime.now()
    
    # === KIỂM TRA YÊU CẦU CHỜ LẤY SÁCH QUÁ HẠN ===
    cursor.execute("""
        SELECT yc.*, s.tieu_de, s.loai_sach, sg.so_luong
        FROM YEU_CAU_MUON yc
        JOIN SACH s ON yc.ma_sach = s.ma_sach
        LEFT JOIN SACH_GIAY sg ON s.ma_sach = sg.ma_sach
        WHERE yc.trang_thai = 'CHO_LAY_SACH' 
        AND yc.han_lay_sach IS NOT NULL
        AND datetime(yc.han_lay_sach) < datetime('now', 'localtime')
    """)
    
    expired_requests = cursor.fetchall()
    
    for req in expired_requests:
        # Tự động hủy yêu cầu quá hạn
        cursor.execute("""
            UPDATE YEU_CAU_MUON SET trang_thai = 'DA_HUY' WHERE ma_yeu_cau = ?
        """, (req['ma_yeu_cau'],))
        
        # Tạo thông báo cho đọc giả
        cursor.execute("""
            INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
            VALUES (?, ?, ?, 'HE_THONG', ?, ?)
        """, (
            req['ma_nd_doc_gia'],
            "⏰ Yêu cầu mượn sách đã hết hạn lấy",
            f"Yêu cầu mượn sách \"{req['tieu_de']}\" đã bị hủy do quá hạn 3 ngày lấy sách. Bạn có thể gửi yêu cầu mới nếu cần.",
            now.strftime('%Y-%m-%d %H:%M:%S'),
            f"yeu_cau:{req['ma_yeu_cau']}"
        ))
    
    # === KIỂM TRA SÁCH SẮP HẾT HẠN VÀ QUÁ HẠN ===
    # Lấy các phiếu mượn đang mượn
    cursor.execute("""
        SELECT pm.*, s.tieu_de, nd.ma_nd, nd.ho_ten
        FROM PHIEU_MUON_TRA pm
        JOIN SACH s ON pm.ma_sach = s.ma_sach
        JOIN DOC_GIA dg ON pm.ma_nd_doc_gia = dg.ma_nd
        JOIN NGUOI_DUNG nd ON dg.ma_nd = nd.ma_nd
        WHERE pm.trang_thai_phieu = 'DANG_MUON'
    """)
    
    phieu_muons = cursor.fetchall()
    
    for pm in phieu_muons:
        ngay_hen_tra = datetime.strptime(pm['ngay_hen_tra'], '%Y-%m-%d').date()
        days_until_due = (ngay_hen_tra - today).days
        
        # Kiểm tra đã gửi thông báo chưa (trong ngày hôm nay)
        cursor.execute("""
            SELECT COUNT(*) as count FROM THONG_BAO 
            WHERE ma_nd = ? AND link_lien_quan = ? 
            AND DATE(ngay_tao) = DATE('now', 'localtime')
        """, (pm['ma_nd'], f"phieu_muon:{pm['ma_phieu']}"))
        
        already_notified = cursor.fetchone()['count'] > 0
        
        if already_notified:
            continue
        
        if days_until_due < 0:
            # Quá hạn
            cursor.execute("""
                INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
                VALUES (?, ?, ?, 'QUA_HAN', ?, ?)
            """, (
                pm['ma_nd'],
                "⚠️ Sách đã quá hạn trả!",
                f"Sách \"{pm['tieu_de']}\" đã quá hạn {abs(days_until_due)} ngày. Vui lòng trả sách ngay để tránh phạt.",
                now.strftime('%Y-%m-%d %H:%M:%S'),
                f"phieu_muon:{pm['ma_phieu']}"
            ))
        elif days_until_due <= 3:
            # Sắp hết hạn (còn 1-3 ngày)
            cursor.execute("""
                INSERT INTO THONG_BAO (ma_nd, tieu_de, noi_dung, loai_thong_bao, ngay_tao, link_lien_quan)
                VALUES (?, ?, ?, 'SAP_HET_HAN', ?, ?)
            """, (
                pm['ma_nd'],
                "📅 Sách sắp đến hạn trả",
                f"Sách \"{pm['tieu_de']}\" sẽ đến hạn trả sau {days_until_due} ngày ({ngay_hen_tra.strftime('%d/%m/%Y')}). Hãy chuẩn bị trả sách đúng hạn!",
                now.strftime('%Y-%m-%d %H:%M:%S'),
                f"phieu_muon:{pm['ma_phieu']}"
            ))
    
    conn.commit()
    conn.close()


# Khởi tạo database khi import module
if __name__ == "__main__":
    init_database()
    insert_sample_data()
    print("Database initialized successfully!")
