import customtkinter as ctk
from model import SalaryModel
from view import SalaryView
from controller import SalaryController

if __name__ == "__main__":
    # 1. Cấu hình giao diện hệ thống (Ép buộc chế độ tối/sáng đồng bộ)
    ctk.set_appearance_mode("Dark")  # Giữ giao diện Dark Mode sâu giống hình ảnh thực tế của bạn
    ctk.set_default_color_theme("blue")

    # 2. Khởi tạo các thành phần theo mô hình kiến trúc MVC
    model = SalaryModel()
    view = SalaryView()
    
    # 3. Khởi tạo bộ điều phối để kết nối dữ liệu Model lên giao diện View
    controller = SalaryController(model, view)

    # 4. Kích hoạt vòng lặp chạy ứng dụng (Main Event Loop)
    try:
        view.mainloop()
    except KeyboardInterrupt:
        # Xử lý ngoại lệ thoát an toàn khi dev bấm Ctrl+C trong Terminal
        print("\n[Hệ thống] Ứng dụng quản lý lương đã được đóng an toàn.")