# AuraScent ERP — Quản lý Đơn hàng

Hệ thống quản lý đơn hàng theo yêu cầu bài test vị trí Lập trình viên ERP/CRM.

- Backend: Django 4.2 + Django REST Framework + django-unfold Admin

## 1. Cài đặt & Chạy dự án

```bash
# 1. Tạo và kích hoạt môi trường ảo
python3 -m venv venv
source venv/bin/activate

# 2. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 3. Khởi tạo cấu trúc cơ sở dữ liệu
python manage.py migrate

# 4. Tạo tài khoản Quản trị viên (Superuser)
# Tài khoản này dùng để đăng nhập vào giao diện Django Admin
# (Quản lý danh sách đơn hàng, đổi trạng thái và xem Báo cáo doanh thu)
python manage.py createsuperuser

# 5. Khởi động server phát triển
python manage.py runserver
```

Truy cập:
- Admin Dashboard: http://127.0.0.1:8000/admin/
- Quản lý đơn hàng: http://127.0.0.1:8000/admin/orders/order/
- Báo cáo doanh thu: http://127.0.0.1:8000/admin/orders/order/revenue-report/
- API Báo cáo JSON: http://127.0.0.1:8000/api/orders/revenue-report/

## 2. Chạy Kiểm thử tự động (Unit Test)

```bash
python manage.py test orders -v 2
```

Đã bao phủ 16 test cases:
- Tự động tính `amount = qty * rate`.
- Validate `qty > 0` và `rate > 0`.
- Chặn sửa/đổi trạng thái đơn đã "Đã giao" hoặc "Hủy".
- Chặn xóa đơn "Đã giao" hoặc "Hủy" trên Admin.
- API báo cáo doanh thu theo ngày chỉ tính đơn "Đã giao".

## 3. Các giả định & Thiết kế tối ưu (Best Practices)

- **Toàn vẹn dữ liệu:** Tự động tính thành tiền `amount = qty * rate` ở tầng backend để chống làm giả dữ liệu từ client.
- **Tính bất biến (Immutability):** Khóa cứng trạng thái và toàn bộ thông tin đơn hàng một khi đã chuyển sang "Đã giao" hoặc "Hủy". Chặn xóa trên Admin nhằm đảm bảo tính toàn vẹn của sổ sách kế toán.
- **Tối ưu hóa Database (Indexing):** Thiết lập Composite Index trên `["status", "created_at"]` để tối ưu hóa hiệu năng truy vấn của trang Báo cáo doanh thu khi dữ liệu lớn.
- **Khuyến nghị Production (Idempotency Key):** Đối với môi trường thực tế khi lượng giao dịch lớn và mạng chập chờn, đề xuất tích hợp thêm cơ chế `Idempotency-Key` (header UUID lưu tạm ở Redis) tại API tạo đơn để ngăn chặn triệt để tình trạng tạo trùng đơn hàng khi client bấm submit/retry nhiều lần.
