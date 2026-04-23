const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        await mongoose.connect('mongodb://localhost:27017/product_db');
        console.log('Kết nối tới MongoDB thành công (product_db)');
    } catch (err) {
        console.error('Lỗi kết nối MongoDB:', err.message);
        process.exit(1);
    }
};

module.exports = connectDB;
