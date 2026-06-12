import threading
from tkinter import messagebox
from view import SubWindow  # Đảm bảo bạn đã có class này trong view.py

# =====================================================================
# LỚP ĐIỀU KHIỂN (SALARY CONTROLLER): KẾT NỐI VÀ ĐIỀU PHỐI MODEL & VIEW
# =====================================================================
class SalaryController:
    def __init__(self, model, view):
        self.model = model  # Liên kết với tầng xử lý dữ liệu (Model)
        self.view = view    # Liên kết với tầng hiển thị giao diện (View)
        self.setup_events() # Cài đặt kết nối các sự kiện nút bấm
        self.refresh_data() # Tải dữ liệu lên bảng ngay khi khởi động chương trình

    def setup_events(self):
        """ Kết nối các nút bấm chức năng trên giao diện với các hàm xử lý logic tương ứng """
        self.view.btn_add.configure(command=self.handle_add)        # Nút Thêm nhân viên
        self.view.btn_edit.configure(command=self.handle_edit)      # Nút Sửa thông tin
        self.view.btn_del.configure(command=self.handle_delete)     # Nút Xóa hồ sơ
        self.view.btn_export.configure(command=self.export_csv)     # Nút Xuất báo cáo
        self.view.search_entry.bind("<KeyRelease>", self.handle_search)  # Sự kiện gõ phím tìm kiếm
        
        # Bắt sự kiện click vào thanh tiêu đề cột "STT" để kích hoạt tính năng chọn/bỏ chọn tất cả hàng loạt
        self.view.tree.heading("STT", command=self.toggle_select_all)

    def refresh_data(self, search_term=""):
        """ Làm sạch bảng lương, nạp lại dữ liệu mới từ Database và đồng bộ lên các ô Dashboard """
        # 1. Làm sạch nhanh toàn bộ các hàng dữ liệu cũ hiện có trên bảng Treeview
        self.view.tree.delete(*self.view.tree.get_children())
        
        # 2. Truy vấn dữ liệu từ Database lên DataFrame Pandas
        df = self.model.get_all()
        if search_term:  # Lọc lọc tên theo từ khóa tìm kiếm (chấp nhận cả chữ hoa và chữ thường)
            df = df[df['ten'].str.contains(search_term, case=False)]

        # 3. Duyệt mảng đổ dữ liệu lên Treeview, tiền tệ tự động ép kiểu int để xóa dấu chấm thập phân .0
        don_gia = self.model.don_gia_ot
        for index, (_, row) in enumerate(df.iterrows(), start=1):
            thuc_nhan = row['luong_cb'] + row['thuong'] - row['phat'] + (row['gio_tang_ca'] * don_gia)
            
            # Khóa ẩn iid lưu mã định danh ID gốc, giá trị hiển thị gồm icon ô vuông trống ☐ kết hợp số thứ tự
            self.view.tree.insert("", "end", iid=int(row['id']), values=(
                f"☐  {index}", row['ten'], f"{int(row['luong_cb']):,}", 
                f"{int(row['thuong']):,}", f"{int(row['phat']):,}", 
                row['gio_tang_ca'], f"{int(thuc_nhan):,}"
            ))

        # Reset thanh tiêu đề STT quay về trạng thái icon trống ban đầu khi bảng tải lại dữ liệu
        self.view.all_selected = False
        self.view.tree.heading("STT", text="☐  STT")

        # 4. Gọi Model tính toán và nạp số liệu đã xóa dấu chấm lên 3 ô Card Dashboard ở đáy màn hình
        si_so, _, tong_quy, tong_ot, _ = self.model.tinh_toan_thong_ke()
        self.view.update_dashboard(int(si_so), int(tong_quy), tong_ot)

    def _set_checkbox_state(self, all_items, select_all=True):
        """ HÀM RÚT NGẮN: Khối dùng chung để quét duyệt hàng loạt hàng, hoán đổi icon checkbox ☐ và ☑ """
        for item in all_items:
            current_values = list(self.view.tree.item(item, "values"))
            if current_values:
                pure_stt = current_values[0].split()[-1]  # Tách chuỗi thu về số thứ tự gốc
                current_values[0] = f"{'☑' if select_all else '☐'}  {pure_stt}"  # Đổi icon theo logic gán
                self.view.tree.item(item, values=current_values)

    def toggle_select_all(self):
        """ Xử lý đảo trạng thái chọn tất cả / bỏ chọn toàn bộ các hàng khi click nhãn STT tiêu đề cột """
        all_items = self.view.tree.get_children()
        if not all_items: return  # Nếu bảng trống rỗng thì kết thúc hàm xử lý luôn

        # Đảo trạng thái biến logic kiểm soát tổng thể True/False trên View
        self.view.all_selected = not self.view.all_selected

        if self.view.all_selected:
            self.view.tree.selection_set(all_items)  # Kích hoạt bôi xanh toàn bộ dải màu các dòng
            self.view.tree.heading("STT", text="☑  STT")  # Đổi tiêu đề cột thành dấu tích xanh
            self._set_checkbox_state(all_items, select_all=True)  # Chuyển toàn bộ ô vuông dòng thành dấu ☑
        else:
            self.view.tree.selection_clear()  # Xóa bỏ trạng thái bôi xanh toàn bộ các dòng
            self.view.tree.heading("STT", text="☐  STT")  # Trả tiêu đề cột về dấu vuông trống
            self._set_checkbox_state(all_items, select_all=False)  # Trả toàn bộ ô vuông dòng về dạng ☐

    # --- CÁC HÀM TIẾP NHẬN XỬ LÝ SỰ KIỆN ---

    def handle_add(self):
        """ Khởi tạo và bật mở hộp cửa sổ phụ điền thông tin thêm nhân viên mới """
        SubWindow("Thêm Nhân Viên", self.add_callback)

    def add_callback(self, ten, luong, thuong, phat, ot):
        """ Hàm callback nhận dữ liệu phản hồi từ cửa sổ con thêm mới để chuyển tiếp lưu vào Database """
        self.model.add(ten, luong, thuong, phat, ot)
        self.refresh_data()  # Làm mới lại giao diện hiển thị

    def handle_edit(self):
        """ Thu thập dòng bôi chọn duy nhất, lấy dữ liệu gốc từ DB ra để bật cửa sổ chỉnh sửa """
        selected = self.view.tree.selection()
        if not selected:
            return messagebox.showwarning("Chú ý", "Vui lòng chọn nhân viên cần sửa!")
        if len(selected) > 1:
            return messagebox.showwarning("Chú ý", "Hệ thống chỉ hỗ trợ sửa thông tin cho từng nhân viên một. Vui lòng không chọn nhiều ô cùng lúc!")
        
        db_id = int(selected[0])  # Lấy ID thực tế được lưu ẩn trong iid của hàng được chọn
        df_all = self.model.get_all()
        row_data = df_all[df_all['id'] == db_id].iloc[0]  # Truy vấn chính xác bản ghi gốc trong Database
        
        # Đóng gói mảng dữ liệu gốc và mở cửa sổ phụ "Sửa Thông Tin"
        item_data = [row_data['id'], row_data['ten'], row_data['luong_cb'], row_data['thuong'], row_data['phat'], row_data['gio_tang_ca']]
        SubWindow("Sửa Thông Tin", lambda t, l, th, p, o: self.edit_callback(db_id, t, l, th, p, o), data=item_data)

    def edit_callback(self, id_nv, ten, luong, thuong, phat, ot):
        """ Hàm callback nhận dữ liệu sửa đổi từ cửa sổ con chuyển giao cho Model cập nhật DB """
        self.model.update(id_nv, ten, luong, thuong, phat, ot)
        self.refresh_data()  # Làm mới giao diện bảng lương

    def handle_delete(self):
        """ Tiếp nhận và thực hiện xóa hàng loạt toàn bộ các nhân viên đang được bôi xanh tích chọn """
        selected = self.view.tree.selection()
        if not selected: 
            return messagebox.showwarning("Chú ý", "Vui lòng tích chọn nhân viên cần xóa!")
        
        # Hiển thị thông báo hộp cảnh báo xác nhận, nếu đồng ý sẽ chạy vòng lặp gọi Model xóa theo ID gốc
        if messagebox.askyesno("Xác nhận", f"Bạn có chắc chắn muốn xóa {len(selected)} nhân viên đã chọn khỏi cơ sở dữ liệu?"):
            for item in selected:
                self.model.delete(int(item))  # Mã iid của hàng đại diện trực tiếp cho mã khóa ID chính trong SQLite
            self.refresh_data()  # Tải lại bảng dữ liệu sau khi xóa thành công

    def handle_search(self, event):
        """ Tìm kiếm và lọc dữ liệu thời gian thực (Real-time Search) trực tiếp ngay khi người dùng gõ phím """
        self.refresh_data(self.view.search_entry.get().strip())

    def export_csv(self):
        """ Kết xuất toàn bộ Database ra tệp BaoCaoLuong.csv (Chạy luồng phụ Threading để tránh đơ đứng ứng dụng) """
        def task():
            try:
                df = self.model.get_all()
                df.to_csv("BaoCaoLuong.csv", index=False, encoding='utf-8-sig')  # Mã hóa 'utf-8-sig' chống lỗi font Excel tiếng Việt
                messagebox.showinfo("Thành công", "Đã xuất file BaoCaoLuong.csv thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể xuất file báo cáo: {e}")
        
        threading.Thread(target=task).start()  # Kích hoạt luồng chạy ngầm riêng biệt