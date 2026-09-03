# Campaign Management API

API quản lý chiến dịch marketing được xây dựng bằng FastAPI. Ứng dụng hỗ trợ
người dùng tạo và quản lý chiến dịch, phân quyền thành viên, theo dõi đầu việc,
trao đổi bình luận và đính kèm tệp tin.

## Tính năng chính

- Đăng ký, đăng nhập và làm mới access token.
- Quản lý thông tin người dùng; quản trị viên có thể tìm kiếm người dùng.
- Tạo, xem, cập nhật và xóa chiến dịch.
- Thêm, xem và xóa thành viên trong chiến dịch.
- Tạo và quản lý đầu việc theo trạng thái, mức độ ưu tiên, hạn hoàn thành và phân trang.
- Thêm và xem bình luận của đầu việc.
- Tải tệp đính kèm lên đầu việc và truy cập tệp qua endpoint storage.
- Phân quyền theo vai trò người dùng, chủ sở hữu và thành viên chiến dịch.
- Giới hạn số lần đăng nhập để tăng an toàn cho API.

## Công nghệ

- Python 3
- FastAPI và Uvicorn
- SQLAlchemy
- Pydantic
- JWT authentication
- SlowAPI rate limiting

## Cài đặt và chạy dự án

```bash
pip install -r requirements.txt
cd app
uvicorn main:app --reload
```

Sau khi chạy, API mặc định có tại `http://127.0.0.1:8000`.

## Tài liệu API

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Các endpoint yêu cầu đăng nhập sử dụng header:

```text
Authorization: Bearer <access_token>
```

## Nhóm endpoint

| Nhóm | Prefix | Mục đích |
| --- | --- | --- |
| Auth | `/auth` | Đăng ký, đăng nhập, làm mới token |
| Users | `/users` | Thông tin tài khoản và tìm kiếm người dùng |
| Campaign | `/campaigns` | Chiến dịch, thành viên và đầu việc |
| Campaign Tasks | `/campaign-task` | Chi tiết đầu việc, bình luận và tệp đính kèm |

## Lưu ý

Tệp tải lên được lưu trong thư mục `app/storage/task_attachment`. Cấu hình cơ sở
dữ liệu và các biến môi trường được quản lý trong `app/core/config.py`.
