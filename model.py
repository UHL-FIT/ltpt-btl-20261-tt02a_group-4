import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

# =====================================================================
# LỚP XỬ LÝ DỮ LIỆU (SALARY MODEL): QUẢN LÝ DATABASE & TÍNH TOÁN NUMPY
# =====================================================================
class SalaryModel:
    def __init__(self):
        self.db_name = "data.db"  # Định nghĩa tên tệp cơ sở dữ liệu SQLite
        self.don_gia_ot = 150000  # Đơn giá 1 giờ tăng ca (Single Source of Truth)
        self.create_table()  # Tự động gọi hàm tạo bảng khi khởi tạo Model

    def create_table(self):
        """ Khởi tạo cấu trúc bảng và tự động nâng cấp thêm cột nếu tệp DB cũ thiếu trường """
        with sqlite3.connect(self.db_name) as conn:
            # Tạo bảng nhanvien nếu chưa tồn tại trong hệ thống
            conn.execute('''CREATE TABLE IF NOT EXISTS nhanvien (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, ten TEXT,
                            luong_cb REAL, thuong REAL, phat REAL,
                            gio_tang_ca REAL DEFAULT 0, thang TEXT)''')
            
            # Kiểm tra danh sách các cột thực tế đang có trong cơ sở dữ liệu
            cursor = conn.execute("PRAGMA table_info(nhanvien)")
            existing_cols = [col[1] for col in cursor.fetchall()]  # Lấy mảng tên cột
            
            # Rút ngắn: Duyệt vòng lặp tự động nâng cấp cột thiếu thay vì viết nhiều câu lệnh if
            for col_name, col_type in [('gio_tang_ca', 'REAL DEFAULT 0'), ('thang', 'TEXT')]:
                if col_name not in existing_cols:
                    conn.execute(f"ALTER TABLE nhanvien ADD COLUMN {col_name} {col_type}")

    def get_all(self):
        """ Đọc toàn bộ bảng nhân viên chuyển thẳng thành một cấu trúc DataFrame của Pandas """
        with sqlite3.connect(self.db_name) as conn:
            return pd.read_sql_query("SELECT * FROM nhanvien", conn)

    def add(self, ten, luong, thuong, phat, ot):
        """ Ghi nhận và lưu thông tin một nhân viên mới kèm theo tháng hiện tại """
        thang_hien_tai = datetime.now().strftime("%Y-%m")  # Định dạng thời gian dạng Năm-Tháng (Ví dụ: 2026-05)
        with sqlite3.connect(self.db_name) as conn:
            # Thực thi câu lệnh SQL chèn hàng loạt tham số dạng tuple an toàn chống SQL Injection
            conn.execute("INSERT INTO nhanvien (ten, luong_cb, thuong, phat, gio_tang_ca, thang) VALUES (?,?,?,?,?,?)", 
                         (ten, float(luong), float(thuong), float(phat), float(ot), thang_hien_tai))

    def update(self, id_nv, ten, luong, thuong, phat, ot):
        """ Cập nhật chỉnh sửa các thông số lương của nhân viên theo mã định danh ID """
        with sqlite3.connect(self.db_name) as conn:
            # Thực thi câu lệnh UPDATE sửa đổi thông tin chính xác theo ID bộ lọc WHERE
            conn.execute("UPDATE nhanvien SET ten=?, luong_cb=?, thuong=?, phat=?, gio_tang_ca=? WHERE id=?", 
                         (ten, float(luong), float(thuong), float(phat), float(ot), id_nv))

    def delete(self, id_nv):
        """ Xóa hoàn toàn hồ sơ của một nhân viên ra khỏi cơ sở dữ liệu dựa vào mã ID """
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM nhanvien WHERE id=?", (id_nv,))  # Thực thi lệnh DELETE xóa hàng dữ liệu

    def tinh_toan_thong_ke(self):
        """ Sử dụng sức mạnh mảng Numpy để tính toán thực nhận và xuất số liệu thống kê siêu tốc """
        df = self.get_all()  # Gọi hàm lấy toàn bộ dữ liệu hiện tại lên
        if df.empty: return 0, 0, 0, 0, 0  # Trả về mảng số 0 mặc định nếu cơ sở dữ liệu chưa có ai
            
        # Rút ngắn: Chuyển đổi và làm sạch giá trị rỗng (NaN thành 0) của toàn bộ các cột sang mảng Numpy array
        arrs = {col: df[col].fillna(0).values for col in ['luong_cb', 'thuong', 'phat', 'gio_tang_ca']}
        
        # Áp dụng công thức tính Lương thực nhận đồng loạt trên mảng vector (Vectorized Operation)
        thuc_nhan = arrs['luong_cb'] + arrs['thuong'] - arrs['phat'] + (arrs['gio_tang_ca'] * self.don_gia_ot)
        
        # Tính toán siêu tốc các chỉ số: Tổng quỹ lương, trung bình lương, tổng số giờ tăng ca
        si_so = len(df)                  # Tổng số lượng hàng (nhân viên)
        tb_luong = np.mean(thuc_nhan)    # Hàm numpy tính giá trị trung bình lương thực nhận
        tong_quy = np.sum(thuc_nhan)    # Hàm numpy tính tổng toàn bộ quỹ lương phải trả
        tong_ot = np.sum(arrs['gio_tang_ca'])  # Hàm numpy tính tổng số giờ tăng ca của toàn công ty
                     
        # Trả về các thông số kết quả kèm số 0 ở cuối để giữ đúng cấu trúc tương thích với file Controller cũ
        return si_so, tb_luong, tong_quy, tong_ot, 0