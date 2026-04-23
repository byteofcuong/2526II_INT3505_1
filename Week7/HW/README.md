# Hướng dẫn: API Quản lý Product (Node.js & Express)

Dự án này chứa file đặc tả OpenAPI (`product.yaml`) và phần mã nguồn (`target_api`) được sinh tự động thông qua OpenAPI Generator, nhắm tới nền tảng **Node.js Express Server**.

## 1. Lệnh đã sử dụng để sinh code

Để sinh ra thư mục `target_api` từ file `product.yaml`, chúng ta đã sử dụng câu lệnh `npx` của OpenAPI. Câu lệnh cụ thể như sau:

```bash
npx -y @openapitools/openapi-generator-cli generate -i product.yaml -g nodejs-express-server -o target_api
```

- `-i product.yaml`: Chỉ định file đầu vào (input) là file OpenAPI Spec của chúng ta.
- `-g nodejs-express-server`: Chọn generator cho nền tảng Node.js Express.
- `-o target_api`: Thư mục đầu ra chứa code (output).

## 2. Hướng dẫn khởi chạy ứng dụng sinh ra

### Bước 1: Di chuyển vào thư mục dự án
```bash
cd target_api
```

### Bước 2: Cài đặt các thư viện phụ thuộc
Hệ thống được thiết lập sẵn với `package.json`, bạn cài thư viện bằng NPM:
```bash
npm install
```

### Bước 3: Khởi chạy API Server
Sau khi cài đặt xong, khởi chạy server bằng lệnh:
```bash
npm start
```

## 3. Hướng dẫn tích hợp MongoDB & Mongoose sắp tới

Code do OpenAPI Generator sinh ra đang tách logic điều hướng (controllers) và logic nghiệp vụ (services). Để kết nối với **MongoDB** sử dụng **Mongoose**, bạn hãy thực hiện theo các bước sau trong quá trình phát triển tiếp theo:

### 3.1. Cài đặt Mongoose
Tại thư mục `target_api` mà chúng ta vừa sinh ra, hãy chạy lệnh để cài đặt mongoose:
```bash
npm install mongoose
```

### 3.2. Cấu hình Kết nối MongoDB ở Server
Bạn hãy mở file cài đặt Server gốc như `target_api/index.js` (hoặc `expressServer.js`) và thêm đoạn kết nối CSDL cơ bản:
```javascript
const mongoose = require('mongoose');

mongoose.connect('mongodb://localhost:27017/product_db', {
    useNewUrlParser: true,
    useUnifiedTopology: true
}).then(() => {
    console.log("Kết nối tới MongoDB thành công");
}).catch((err) => {
    console.error("Lỗi khi kết nối MongoDB", err);
});
```

### 3.3. Định nghĩa Model của tài nguyên (Product)
Tạo thư mục mới `models` trong `target_api` và tạo file `Product.js`. File này định nghĩa Mongoose Schema khớp đúng 100% với `product.yaml`:
```javascript
const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
    id: { type: Number, required: true, unique: true },
    name: { type: String, required: true },
    price: { type: Number, required: true },
    category: { type: String },
    stock: { type: Number },
    description: { type: String }
});

module.exports = mongoose.model('Product', productSchema);
```

### 3.4. Cập nhật Logic ở DefaultService.js
Kiến trúc NodeJS sinh ra gọi từ Controller (như `DefaultController.js`) sang Service (`DefaultService.js`). Hãy mở file `target_api/services/DefaultService.js`, tại đây hãy tìm các hàm như `productsGET` hay `productsPOST` và thay mã dummy (trả về tĩnh) bằng thao tác database thật cùng Mongoose.

Ví dụ:

```javascript
const Product = require('../models/Product');

/**
 * Get all products
 * Retrieve a list of all products in the system.
 */
const productsGET = () => new Promise(
  async (resolve, reject) => {
    try {
      const products = await Product.find({});
      resolve(Service.successResponse(products));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Lỗi lấy dữ liệu',
        e.status || 500,
      ));
    }
  },
);
```

**Lưu ý**: Áp dụng chiến lược tương tự cho các hàm CREATE, UPDATE, DELETE bằng cách gọi tương ứng `Product.create()`, `Product.findOneAndUpdate()`, và `Product.findOneAndDelete()`.

## 4. Hướng dẫn Kiểm thử (Testing)

Sau khi bạn đã hoàn thiện thiết lập Database và chạy thành công server bằng lệnh `npm start` ở thư mục `target_api`, bạn có thể kiểm thử trực tiếp các API dựa trên cấu trúc đã thiết kế:

### 4.1. Khởi tạo một Sản phẩm mới (POST /products)
**Sử dụng cURL:**
```bash
curl -X POST http://localhost:8080/api/products \
-H "Content-Type: application/json" \
-d '{
  "name": "Bàn phím cơ Keychron",
  "price": 99.5,
  "category": "Electronics",
  "stock": 50,
  "description": "Bàn phím không dây Bluetooth"
}'
```
**Sử dụng Postman / Thunder Client:**
- Method: **POST**
- URL: `http://localhost:8080/api/products`
- Tab **Body** (chọn `raw` và định dạng `JSON`): Sao chép đoạn body JSON ở trên vào.

### 4.2. Lấy danh sách toàn bộ Sản phẩm (GET /products)
**Sử dụng cURL:**
```bash
curl -X GET http://localhost:8080/api/products
```
**Sử dụng Postman / Thunder Client:**
- Method: **GET**
- URL: `http://localhost:8080/api/products`

### 4.3. Lấy chi tiết một Sản phẩm theo ID (GET /products/{id})
Đảm bảo bạn truyền ID dưới dạng số nguyên (Ví dụ: id = 1).
**Sử dụng cURL:**
```bash
curl -X GET http://localhost:8080/api/products/1
```

### 4.4. Cập nhật cấu hình một Sản phẩm (PUT /products/{id})
**Sử dụng cURL:**
```bash
curl -X PUT http://localhost:8080/api/products/1 \
-H "Content-Type: application/json" \
-d '{
  "name": "Bàn phím cơ Keychron Q1 Pro",
  "price": 199.99
}'
```

### 4.5. Xoá Sản phẩm (DELETE /products/{id})
**Sử dụng cURL:**
```bash
curl -X DELETE http://localhost:8080/api/products/1
```
