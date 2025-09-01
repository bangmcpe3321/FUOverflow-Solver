[English](https://github.com/bangmcpe3321/FUOverflow-Solver/blob/main/README.en.md)

# Trình tải xuống hình ảnh & xử lý Gemini cho FUOverflow (Tiếng Việt)

Dự án này cung cấp một tiện ích hai phần để tải xuống hình ảnh từ `fuoverflow.com` và xử lý chúng bằng Google Gemini AI để trích xuất và trả lời các câu hỏi có trong hình ảnh.

## Tính năng

- **Giao diện đồ họa người dùng (GUI)**: Một giao diện thân thiện được xây dựng bằng Tkinter để thao tác dễ dàng.
- **Trình tải xuống hình ảnh**: Một tab chuyên dụng để tải hàng loạt hình ảnh, yêu cầu URL bắt đầu và cookie phiên để xác thực.
- **Trình xử lý Gemini AI**: Một tab thứ hai để phân tích một thư mục hình ảnh. Nó sử dụng Gemini AI để xác định câu hỏi trong mỗi hình ảnh và tạo ra câu trả lời.
- **Giao diện dòng lệnh (CLI)**: Logic xử lý AI cũng có thể được chạy dưới dạng một tập lệnh CLI độc lập (`AI.py`).
- **Ghi lại tiến trình**: Cả trình tải xuống và trình xử lý đều ghi lại tiến trình của chúng trong GUI và lưu các câu trả lời cuối cùng do AI tạo ra vào một tệp `.txt`.
- **Quản lý cấu hình**: Tự động tải và lưu khóa API Google Gemini cần thiết từ tệp `config.txt`.

---

## ⚠️ Cảnh báo bảo mật

Dự án này lưu trữ khóa API Google Gemini của bạn trong một tệp văn bản thuần túy (`config.txt`). Để tránh vô tình chia sẻ khóa API bí mật của bạn, **rất khuyến khích** bạn không commit tệp này lên một kho lưu trữ công khai.

Tạo một tệp `.gitignore` trong thư mục gốc của dự án với nội dung sau để loại trừ các tệp nhạy cảm và dữ liệu đã tải xuống khỏi kiểm soát phiên bản:

```
# Môi trường ảo Python
/venv/

# Tệp cấu hình
config.txt
cookies.json

# Hình ảnh đã tải xuống
/downloaded_images/

# Tệp đầu ra
*.txt
```

---

## Điều kiện tiên quyết

- Python 3.12.x
- Các thư viện Python sau:
  - `google-generativeai`
  - `requests`
  - `Pillow`
  - `selenium`
  - `webdriver-manager`

## Cài đặt

**Windows:**
- Chỉ cần chạy `gui.bat` để khởi động ứng dụng.

**Linux:**
1.  **Sao chép kho lưu trữ (hoặc tải xuống các tệp):**
    ```bash
    git clone https://github.com/bangmcpe3321/FUOverflow-image-downloader.git
    
    cd FUOverflow-image-downloader
    ```

2.  **Thiết lập môi trường ảo Python (khuyến nghị):**
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3.  **Cài đặt các gói cần thiết:**
    ```bash
    pip install google-generativeai requests Pillow selenium webdriver-manager
    ```

## Cách sử dụng

### Phương pháp GUI (Khuyến nghị)

Khởi chạy ứng dụng bằng cách chạy tệp batch hoặc tập lệnh Python:

- **Windows**: Nhấp đúp vào `gui.bat`
- **Linux**: Chạy `python gui_app.py` từ terminal của bạn.

#### 1. Tab Trình tải xuống hình ảnh

Tab này dùng để tải hình ảnh từ `fuoverflow.com`.

1.  **Mã môn học**: Nhập mã môn học từ URL diễn đàn (ví dụ: `ITE302c`).
2.  **Tổng số tệp**: Nhập tổng số hình ảnh bạn muốn tải xuống.
3.  **Cookie xf_user**: Nhập giá trị cookie `xf_user` của bạn để xác thực.
4.  **Cookie xf_session**: Nhập giá trị cookie `xf_session` của bạn.
5.  Nhấp vào **Fetch URL and Start Download**. Ứng dụng sẽ tự động tìm URL bắt đầu chính xác và sau đó bắt đầu tải hình ảnh vào một thư mục được đặt tên theo tiêu đề của cuộc thảo luận bên trong thư mục `downloaded_images`.

##### Cách lấy Cookies của bạn

**Chrome:**
Bạn có thể sử dụng một tiện ích mở rộng trình duyệt như [Cookie Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm) để dễ dàng xem và sao chép các giá trị cookie `xf_user` và `xf_session`.

**Firefox:**
1.  Mở `fuoverflow.com` trong Firefox.
2.  Nhấn `F12` để mở công cụ dành cho nhà phát triển.
3.  Đi đến tab **Network**.
4.  Tải lại trang (F5).
5.  Nhấp vào bất kỳ yêu cầu nào đến `fuoverflow.com` trong danh sách.
6.  Trong bảng điều khiển bên phải, đi đến tab **Cookies**.
7.  Tìm và sao chép các giá trị cho `xf_user` và `xf_session`.

#### 2. Tab Trình xử lý Gemini

Tab này dùng để phân tích các hình ảnh đã tải xuống bằng AI.

1.  **Khóa API Gemini**: Khóa của bạn từ `config.txt` sẽ được tải tự động. Bạn cũng có thể dán trực tiếp vào đây.
2.  **Thư mục hình ảnh**: Nhấp vào **Browse...** và chọn thư mục `downloaded_images` (hoặc bất kỳ thư mục nào khác chứa hình ảnh bạn muốn xử lý).
3.  Nhấp vào **Start Processing**. AI sẽ phân tích từng hình ảnh và kết quả sẽ được nối vào một tệp `.txt` được đặt tên theo thư mục hình ảnh (ví dụ: `downloaded_images.txt`).

### Phương pháp dòng lệnh (Chỉ trình xử lý)

Bạn có thể chạy phân tích AI trực tiếp từ dòng lệnh.

1.  Mở terminal của bạn trong thư mục dự án.
2.  Chạy tập lệnh:
    ```bash
    python AI.py
    ```
3.  Tập lệnh sẽ kiểm tra khóa API trong `config.txt` trước. Nếu không tìm thấy, nó sẽ nhắc bạn nhập.
4.  Sau đó, nó sẽ yêu cầu đường dẫn đến thư mục chứa hình ảnh của bạn.
5.  Tập lệnh sẽ xử lý tất cả các hình ảnh trong thư mục và lưu kết quả vào `all_questions_and_answers.txt`.
