# 📱 Project DjangoWeb - Website Cửa Hàng Công Nghệ (MyShop)

Chào mừng bạn đến với **MyShop** - một dự án website thương mại điện tử chuyên cung cấp thiết bị công nghệ (điện thoại di động, máy tính bảng, v.v.) được xây dựng và phát triển trên nền tảng **Django (Python)**. Dự án được thiết kế trực quan, tối ưu và tích hợp đầy đủ các tính năng của một trang bán hàng hiện đại cùng hệ thống API bảo mật cao.

---

## 🚀 Các Tính Năng Chính

### 🛍️ Dành Cho Khách Hàng (Front-end Website)
- **Trang chủ & Danh mục**: Duyệt sản phẩm trực quan, phân loại linh hoạt theo thương hiệu (Brand) hoặc danh mục sản phẩm (Category).
- **Thông số kỹ thuật chi tiết**: Hiển thị đầy đủ thông số kỹ thuật chi tiết của thiết bị như chip xử lý, RAM, dung lượng bộ nhớ, camera, pin, sạc,...
- **Giỏ hàng trực tuyến (Shopping Cart)**:
  - Thêm sản phẩm nhanh vào giỏ hàng.
  - Tự động tính toán số tiền và áp dụng ưu đãi khuyến mãi nếu có.
  - Cập nhật số lượng sản phẩm trực tiếp hoặc xóa sản phẩm khỏi giỏ hàng.
- **Tiến trình đặt hàng (Checkout)**: Quy trình thanh toán đơn giản, nhập thông tin giao hàng (địa chỉ, số điện thoại) nhanh chóng.
- **Quản lý tài khoản**: Đăng ký thành viên mới, đăng nhập hệ thống và đăng xuất bảo mật.
- **Đánh giá & Xếp hạng (Product Reviews)**: Người dùng có thể bình luận và chấm điểm sản phẩm từ 1 đến 5 sao giúp tăng tương tác.
- **Chương trình khuyến mãi (Promotion)**: Tự động tính toán giá ưu đãi dựa trên thời gian bắt đầu và kết thúc của chương trình giảm giá.

### 🔌 Dành Cho Nhà Phát Triển (Back-end & API)
- **Trang quản trị (Django Admin)**: Đầy đủ giao diện quản lý cơ sở dữ liệu chuyên nghiệp cho Admin.
- **Tích hợp API RESTful**: Hệ thống REST API hoàn chỉnh cho phép phát triển ứng dụng di động hoặc bên thứ ba.
- **Xác thực bảo mật JWT**: Sử dụng `djangorestframework-simplejwt` để cấp quyền truy cập qua Access/Refresh token.

---

## 🛠️ Công Nghệ Sử Dụng

- **Ngôn ngữ**: Python 3.13+
- **Framework**: Django 6.0+
- **API Engine**: Django REST Framework (DRF)
- **Authentication**: Simple JWT (JSON Web Token)
- **Cơ sở dữ liệu**: SQLite (Nhẹ nhàng, không cần cấu hình phức tạp)
- **Các thư viện bổ trợ**: Numpy (phục vụ tính toán), v.v.

---

## 💾 Kiến Trúc Cơ Sở Dữ Liệu (Database Schema)

Hệ thống được thiết kế với cơ sở dữ liệu quan hệ chặt chẽ bao gồm các bảng:

| Bảng dữ liệu | Model | Mô tả chức năng |
| :--- | :--- | :--- |
| **Category** | Danh mục | Phân loại sản phẩm (ví dụ: Điện thoại, Phụ kiện), hỗ trợ phân cấp cha-con. |
| **Brand** | Thương hiệu | Quản lý thông tin nhà sản xuất (Apple, Samsung, Xiaomi,...). |
| **Detail** | Thông số kỹ thuật | Lưu trữ chi tiết cấu hình phần cứng (Màn hình, Hệ điều hành, RAM, Camera, Pin,...). |
| **Product** | Sản phẩm | Lưu tên, giá bán, số lượng tồn kho, trạng thái kinh doanh và liên kết cấu hình. |
| **ProductImage** | Bộ ảnh sản phẩm | Chứa các hình ảnh phụ bổ sung cho sản phẩm. |
| **Promotion** | Khuyến mãi | Thiết lập tỷ lệ phần trăm giảm giá theo thời hạn định sẵn. |
| **Order** | Đơn hàng | Quản lý giỏ hàng của thành viên, thông tin giao hàng và trạng thái thanh toán. |
| **OrderDetail**| Chi tiết đơn hàng | Lưu số lượng và giá của từng sản phẩm trong mỗi đơn hàng. |
| **Review** | Đánh giá | Lưu trữ xếp hạng sao (1-5★) cùng bình luận từ người mua. |

---

## 🏃 Hướng Dẫn Cài Đặt và Khởi Chạy Dự Án

Làm theo các bước dưới đây để chạy thử website trên máy tính của bạn:

### Bước 1: Di chuyển vào thư mục dự án
Mở terminal hoặc cửa sổ dòng lệnh và di chuyển tới thư mục chứa file `manage.py`:
```bash
cd django_web/myweb
```

### Bước 2: Cài đặt các thư viện phụ thuộc
Đảm bảo máy của bạn đã cài đặt Python 3. Hãy cài đặt các thư viện cần thiết bằng lệnh:
```bash
pip install django djangorestframework djangorestframework-simplejwt numpy
```

### Bước 3: Đồng bộ cơ sở dữ liệu (Nếu có thay đổi)
Do dự án đã đi kèm cơ sở dữ liệu sqlite được đồng bộ sẵn, bạn có thể bỏ qua bước này. Tuy nhiên, nếu bạn tạo mới cơ sở dữ liệu hoặc thay đổi Models, hãy chạy:
```bash
python manage.py migrate
```

### Bước 4: Khởi chạy máy chủ phát triển (Development Server)
Khởi động máy chủ cục bộ bằng lệnh:
```bash
python manage.py runserver
```

Khi màn hình xuất hiện thông báo:
```text
Watching for file changes with StatReloader
System check identified no issues (0 silenced).
Django version 6.0.5, using settings 'myweb.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
Máy chủ của bạn đã sẵn sàng!

---

## 🌐 Địa Chỉ Truy Cập Mặc Định

Sau khi khởi chạy thành công, bạn có thể truy cập dự án thông qua các địa chỉ:

- **Trang chủ Website MyShop**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Trang quản trị hệ thống (Django Admin)**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Điểm cuối API xác thực JWT**:
  - Lấy mã token: `/api/token/`
  - Làm mới token: `/api/token/refresh/`

---
*Chúc bạn có trải nghiệm tuyệt vời khi phát triển và sử dụng **MyShop**!*
