const mongoose = require('mongoose');
const Schema = mongoose.Schema;

// Định nghĩa cấu trúc document Product theo sát chuẩn của openapi.yaml
const productSchema = new Schema({
  name: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true
  }
});

// Tạo model từ schema
// Lưu ý: MongoDB sẽ tự động thêm trường _id (ObjectId) vào Model này
const Product = mongoose.model('Product', productSchema);

module.exports = Product;
