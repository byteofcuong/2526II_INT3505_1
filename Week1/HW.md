# Bài tập Tuần 1: Tìm và phân tích 3 API công khai (GitHub, OpenWeather, v.v.)

## 1. Google Map Platform
Cung cấp thông tin về định vị, định tuyến, bản đồ,...\
Kiến trúc: REST\
Endpoint: https://maps.googleapis.com/maps/api/geocode/json (GET)\
Input - Output: Địa chỉ, API Key - JSON chứa tọa độ\
Chức năng chính: Bản đồ tĩnh và động, tra cứu và đánh giá các địa điểm, tìm đường, định vị vị trí
## 2. Cloundinary
Quản lý ảnh, video,... dựa trên cloud\
Kiến trúc: REST\
Endpoint: https://api.cloudinary.com/v1_1/{cloud_name}/image/upload (POST)\
Output: 201 khi upload ảnh thành công\
Chức năng chính: Tải lên hình ảnh, video. Thay đổi trực tiếp trên url ví dụ như cắt ghép, đổi kích cỡ. Tự động nén dung lượng và chọn định dạng thích hợp tùy loại media
## 3. Spotify Web API
Cho phép dev truy cập được vào nguồn âm nhạc của Spotify\
Kiến trúc: REST\
Endpoint: https://api.spotify.com/v1/albums/{id} (GET)\
(Endpoint này giúp tránh n + 1 problem, client chỉ cần gọi 1 request thì sẽ có thông tin album và danh sách bài hát, không cần gọi 1 request lấy album rồi lại gọi n request lấy từng bài hát) \
Chức năng chính: Thông tin về nhạc, nhạc sĩ, nội dung nhạc. Tạo, chỉnh sửa danh sách phát của người dùng. Điều khiển thiết bị đang sử dụng spotify như dừng, chuyển bài



