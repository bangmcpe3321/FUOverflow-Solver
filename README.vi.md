# FUOverflow Vision (Tiếng Việt)

FUOverflow Vision là một ứng dụng máy tính để bàn với hai chức năng chính:
1.  **Trình tải xuống (Downloader)**: Tự động hóa việc tải xuống các tệp dạng hình ảnh (như ghi chú bài giảng hoặc bộ đề) từ các diễn đàn trên trang web FUOverflow.
2.  **Trình xử lý (Processor)**: Sử dụng Google Gemini AI để phân tích các hình ảnh này, tự động trích xuất bất kỳ câu hỏi nào tìm thấy và cung cấp câu trả lời.

## Tính năng

- **Tải xuống tự động**: Tìm và tải xuống các tệp tuần tự từ một chủ đề diễn đàn FUOverflow được chỉ định.
- **Hỏi và Đáp bằng AI**: Đọc câu hỏi trực tiếp từ hình ảnh đã tải xuống và tạo câu trả lời.
- **Quản lý phiên**: Lưu cookie `xf_user` và `xf_session` của bạn để đơn giản hóa việc đăng nhập trong tương lai.
- **Đầu ra có tổ chức**: Lưu hình ảnh đã tải xuống vào các thư mục được đặt tên theo tiêu đề của chủ đề và lưu kết quả Hỏi & Đáp vào một tệp `.txt`.

## Cách sử dụng

### 1. Tab Trình tải xuống (Image Downloader)

Tab này dùng để lấy hình ảnh từ FUOverflow.

1.  **Mã môn học (Subject Code)**: Nhập mã của diễn đàn bạn muốn tải xuống (ví dụ: `ITE302c`).
2.  **Tổng số tệp (Total Files)**: Nhập số lượng hình ảnh bạn dự kiến sẽ tải xuống.
3.  **Cookie xf_user / Cookie xf_session**: Nhập cookie đăng nhập của bạn từ trang web FUOverflow. Chúng sẽ được lưu lại sau lần chạy đầu tiên.
4.  **Nhấp vào "Fetch URL and Start Download"**: Ứng dụng sẽ đăng nhập, tìm chủ đề mới nhất và bắt đầu tải hình ảnh vào thư mục `downloaded_images`.

### 2. Tab Trình xử lý (Gemini Processor)

Tab này dùng để phân tích các hình ảnh bạn đã tải xuống.

1.  **Khóa API Gemini (Gemini API Key)**: Nhập khóa API của bạn từ Google AI Studio. Khóa này sẽ được lưu trong tệp `config.txt`.
2.  **Thư mục hình ảnh (Image Directory)**: Nhấp vào "Browse..." và chọn thư mục chứa hình ảnh bạn muốn xử lý (ví dụ: thư mục được tạo bởi trình tải xuống).
3.  **Nhấp vào "Start Processing"**: Công cụ sẽ gửi từng hình ảnh đến Gemini, lưu các câu hỏi và câu trả lời đã trích xuất vào một tệp văn bản mới được đặt tên theo thư mục.

---
*Lưu ý: Vui lòng sử dụng công cụ này một cách có trách nhiệm. Cookie và khóa API của bạn là thông tin nhạy cảm.*
