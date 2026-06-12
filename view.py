import customtkinter as ctk
from tkinter import ttk, messagebox

# =====================================================================
# LỚP CỬA SỔ PHỤ (POPUP): DÙNG ĐỂ THÊM HOẶC SỬA THÔNG TIN NHÂN VIÊN
# =====================================================================
class SubWindow(ctk.CTkToplevel):
    def __init__(self, title, callback, data=None):
        super().__init__()
        self.title(title)  # Đặt tiêu đề cho cửa sổ phụ
        self.geometry("460x620")  # Cấu hình kích thước khung cửa sổ cố định
        self.callback = callback  # Lưu lại hàm phản hồi để truyền dữ liệu về Controller
        self.attributes("-topmost", True)  # Ép cửa sổ này luôn nằm trên cùng màn hình
        self.configure(fg_color="#1e1e1e")  # Đổi màu nền cửa sổ thành xám tối

        # Nếu không có dữ liệu (Thêm mới) -> Chữ màu xanh, nếu có dữ liệu (Sửa) -> Chữ màu vàng
        header_color = "#3b8ed0" if not data else "#f1c40f"
        ctk.CTkLabel(self, text=title.upper(), font=("Segoe UI", 20, "bold"), text_color=header_color).pack(pady=30)

        # Tạo khung chứa (Frame) trong suốt để gom các ô nhập liệu thẳng hàng
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(fill="both", expand=True, padx=45)

        # Mảng cấu trúc ánh xạ tên biến cơ sở dữ liệu và nhãn tiếng Việt tương ứng
        fields = [
            ("ten", "Tên nhân viên"), ("luong_cb", "Lương cơ bản (VNĐ)"),
            ("thuong", "Tiền thưởng"), ("phat", "Tiền phạt"), ("gio_tang_ca", "Số giờ tăng ca")
        ]
        
        # VÒNG LẶP TỰ ĐỘNG: Tạo nhãn và ô Entry nhanh chóng, lưu vào từ điển self.vars
        self.vars = {}
        for key, label in fields:
            ctk.CTkLabel(form_frame, text=label, font=("Segoe UI", 13, "bold"), text_color="#aaaaaa").pack(anchor="w", pady=(10, 2))
            self.vars[key] = ctk.CTkEntry(form_frame, width=370, height=38, corner_radius=10, border_width=1, border_color="#333333")
            self.vars[key].pack(pady=(0, 5))

        # ĐỔ DỮ LIỆU CŨ (Nếu ở chế độ Sửa thông tin): Tự động xóa dấu phẩy tiền tệ khi nạp vào ô nhập
        if data:
            self.vars["ten"].insert(0, data[1])  # Chèn dữ liệu Tên gốc vào ô đầu tiên
            for idx, key in enumerate(["luong_cb", "thuong", "phat", "gio_tang_ca"], start=2):
                self.vars[key].insert(0, str(data[idx]).replace(",", ""))  # Đồng loạt xóa dấu phẩy tiền tệ

        # Tạo nút xác nhận, liên kết hành động click chuột với hàm self.submit
        ctk.CTkButton(self, text="XÁC NHẬN", font=("Segoe UI", 14, "bold"), height=48, width=220, corner_radius=24,
                      fg_color=header_color, hover_color="#2c76ad", command=self.submit).pack(pady=35)

    def submit(self):
        try:
            # Dictionary Comprehension: Quét toàn bộ ô nhập, lấy giá trị và xóa khoảng trắng thừa bằng .strip()
            res = {k: v.get().strip() for k, v in self.vars.items()}
            if not res["ten"]: raise ValueError()  # Nếu bỏ trống tên, chủ động kích hoạt lỗi sang khối except
            
            # Ép kiểu dữ liệu chuỗi chữ thành số thực float, nếu ô trống thì mặc định điền số 0
            num_vals = [float(res[k] or 0) for k in ["luong_cb", "thuong", "phat", "gio_tang_ca"]]
            self.callback(res["ten"], *num_vals)  # Giải nén mảng số (*) gửi ngược về hàm xử lý chính ở Controller
            self.destroy()  # Đóng và giải phóng bộ nhớ của cửa sổ phụ
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng kiểm tra dữ liệu và nhập đúng định dạng số!")


# =====================================================================
# LỚP GIAO DIỆN CHÍNH (MAIN VIEW): CHỨA SIDEBAR, BẢNG LƯƠNG & DASHBOARD
# =====================================================================
class SalaryView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Quản Lý Lương Nhân Viên")
        self.geometry("1300x850")
        self.configure(fg_color="#0f0f10")  # Màu nền tổng thể đen sâu sang trọng

        # Cấu hình lưới (Grid): Giúp vùng hiển thị chính bên phải tự co giãn rộng ra khi phóng to màn hình
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- THANH DIỀU KHIỂN (SIDEBAR) BÊN TRÁI ---
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#161618", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="", height=40).pack()  # Tạo khoảng trống phía trên cùng sidebar
        
        # Tạo cấu hình giao diện chung cho các nút bấm để tránh viết lặp code
        btn_config = {"height": 45, "corner_radius": 12, "font": ("Segoe UI", 13, "bold"), "anchor": "w"}
        buttons_data = [
            ("btn_add", "  ➕  Thêm Nhân Viên", "#1d8a42", "#145a2d", "top"),
            ("btn_edit", "  📝  Sửa Thông Tin", "#d4ac0d", "#a6860a", "top"),
            ("btn_del", "  🗑️  Xóa Hồ Sơ", "#a93226", "#7b241c", "top"),
            ("btn_export", "  📥  Xuất Báo Cáo", "#21618c", "#1a5276", "bottom")
        ]
        
        # VÒNG LẶP KHỞI TẠO NÚT: Dùng hàm setattr để biến chuỗi chữ thành tên biến chính thức (self.btn_add,...)
        for attr, text, fg, hover, side in buttons_data:
            btn = ctk.CTkButton(self.sidebar, text=text, fg_color=fg, hover_color=hover, text_color="black" if fg=="#d4ac0d" else "white", **btn_config)
            btn.pack(pady=10 if side == "top" else 40, padx=22, fill="x", side=side)
            setattr(self, attr, btn)

        # --- VÙNG NỘI DUNG CHÍNH (MAIN CONTENT) BÊN PHẢI ---
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, padx=35, pady=35, sticky="nsew")

        # Khởi tạo thanh tìm kiếm nhanh bo tròn cao góc lớn
        self.search_entry = ctk.CTkEntry(self.content_frame, placeholder_text="🔍 Tìm kiếm nhân viên nhanh...", 
                                         width=520, height=48, corner_radius=24, border_width=1, border_color="#333333", fg_color="#1c1c1e")
        self.search_entry.pack(anchor="w", pady=(0, 25))

        # --- CẤU HÌNH STYLE CHO BẢNG TREEVIEW (CHỮ TO & THOÁNG) ---
        style = ttk.Style()
        style.theme_use("default")
        # Chỉnh chữ nội dung to lên 13px và nới cao dòng lên 50px giúp các hàng không bị dính sát dải đường kẻ
        style.configure("Treeview", background="#161618", foreground="#e1e1e1", fieldbackground="#161618", borderwidth=0, rowheight=50, font=("Segoe UI", 13))
        # Chỉnh chữ thanh tiêu đề to lên 13px và in đậm
        style.configure("Treeview.Heading", background="#222224", foreground="white", relief="flat", font=("Segoe UI", 13, "bold"))
        style.map("Treeview", background=[('selected', '#21618c')], foreground=[('selected', 'white')])  # Màu nền bôi xanh hàng được chọn
        
        # Thùng chứa bảng dữ liệu bo góc
        table_container = ctk.CTkFrame(self.content_frame, fg_color="#161618", corner_radius=15, border_width=1, border_color="#222224")
        table_container.pack(fill="both", expand=True)

        cols = ("STT", "Tên", "Lương CB", "Thưởng", "Phạt", "Giờ OT", "Thực Nhận")
        # selectmode="extended" kích hoạt tính năng thông minh cho phép giữ Ctrl/Shift bôi xanh chọn nhiều hàng loạt dòng
        self.tree = ttk.Treeview(table_container, columns=cols, show="headings", selectmode="extended")
        
        # VÒNG LẶP DỰNG TIÊU ĐỀ: Gán biểu tượng ô vuông trống ☐ cho STT, nới rộng các cột lên 135px để số tiền to không bị khuất
        for col in cols:
            self.tree.heading(col, text="☐  STT" if col == "STT" else col.upper())
            self.tree.column(col, width=110 if col == "STT" else 135, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.all_selected = False 
        self.tree.bind("<ButtonRelease-1>", self.on_row_click)  # Bắt sự kiện thả chuột trái để cập nhật dấu tích Checkbox công việc

        # --- KHU VỰC THỐNG KÊ (DASHBOARD) ĐÁY MÀNH HÌNH ---
        self.dashboard = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.dashboard.pack(fill="x", pady=(25, 0))
        self.dashboard.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")  # Chia đều kích thước 3 cột bằng nhau

        # VÒNG LẶP TẠO CARD THỐNG KÊ: Khởi tạo nhanh 3 ô chức năng và lưu tập trung vào từ điển self.cards
        self.cards = {}
        for idx, (title, color) in enumerate([("NHÂN VIÊN", "white"), ("QUỸ LƯƠNG", "#3b8ed0"), ("TỔNG GIỜ OT", "#f1c40f")]):
            card = ctk.CTkFrame(self.dashboard, fg_color="#1c1c1e", height=120, corner_radius=16, border_width=1, border_color="#333333")
            card.grid(row=0, column=idx, sticky="nsew", padx=10)
            ctk.CTkLabel(card, text=title, font=("Segoe UI", 13, "bold"), text_color="#777777").pack(pady=(18, 0))
            self.cards[title] = ctk.CTkLabel(card, text="--", font=("Segoe UI", 26, "bold"), text_color=color)
            self.cards[title].pack(pady=(5, 18))

    def update_table(self, data_list):
        """ Hàm làm mới và đẩy toàn bộ danh sách dữ liệu từ Database lên bảng giao diện """
        self.tree.delete(*self.tree.get_children())  # Giải nén toán tử dấu sao (*) dọn sạch nhanh toàn bộ các dòng cũ
        for index, row in enumerate(data_list, start=1):
            # insert từng dòng nhân viên, tự động điền icon ô trống "☐" trước STT, lồng định dạng lồng {:,} phân tách hàng nghìn
            self.tree.insert("", "end", iid=row[0], values=(f"☐  {index}", row[1], f"{row[2]:,}", f"{row[3]:,}", f"{row[4]:,}", row[5], f"{row[6]:,}"))
        self.all_selected = False
        self.tree.heading("STT", text="☐  STT")  # Trả icon thanh tiêu đề về trạng thái trống ban đầu

    def on_row_click(self, event):
        """ Hàm xử lý logic tự động đảo ngược biểu tượng Checkbox dựa trên trạng thái dòng được bôi chọn xanh """
        selected = self.tree.selection()  # Thu thập mảng chứa các mã ID dòng đang được người dùng bôi chọn
        for item in self.tree.get_children():
            vals = list(self.tree.item(item, "values"))
            if vals:
                stt = vals[0].split()[-1]  # Tách chuỗi loại bỏ icon cũ, chỉ giữ lại số thứ tự gốc (Ví dụ: "☑  5" -> "5")
                # Toán tử điều kiện: Nếu hàng nằm trong danh sách bôi xanh thì đổi sang tích chọn ☑, ngược lại trả về ☐
                vals[0] = f"☑  {stt}" if item in selected else f"☐  {stt}"
                self.tree.item(item, values=vals)  # Thực thi ghi đè giá trị có nhãn tích mới lên dòng bảng bảng lương

    def update_dashboard(self, count, total_salary, total_ot):
        """ Hàm nhận thông số tính toán từ tệp xử lý chính và cập nhật số liệu trực tiếp lên các ô Card dưới đáy """
        self.cards["NHÂN VIÊN"].configure(text=f"Sĩ số: {count} người")
        self.cards["QUỸ LƯƠNG"].configure(text=f"{total_salary:,} VNĐ")  # Định dạng tiền tệ có dấu phẩy ngăn cách hàng nghìn
        self.cards["TỔNG GIỜ OT"].configure(text=f"{total_ot:.1f} giờ")  # Định dạng số thực làm tròn lấy 1 chữ số thập phân