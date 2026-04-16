/* eslint-disable no-unused-vars */
const Service = require('./Service');
const Product = require('../models/Product'); // Nhúng Model vào

/**
* Thêm một sản phẩm mới
*
* productInput ProductInput 
* no response value expected for this operation
* */
const createProduct = ({ productInput }) => new Promise(
  async (resolve, reject) => {
    try {
      // Logic MongoDB
      const newProduct = await Product.create(productInput);
      resolve(Service.successResponse(newProduct, 201));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);
/**
* Xoá một sản phẩm
*
* id String ID của sản phẩm (MongoDB ObjectID)
* no response value expected for this operation
* */
const deleteProduct = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      // Logic MongoDB
      await Product.findByIdAndDelete(id);
      resolve(Service.successResponse('Deleted successfully', 204));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);
/**
* Lấy chi tiết thông tin một sản phẩm
*
* id String ID của sản phẩm (MongoDB ObjectID)
* returns Product
* */
const getProductById = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      // Logic MongoDB
      const product = await Product.findById(id);
      if (!product) {
         return reject(Service.rejectResponse('Not Found', 404));
      }
      resolve(Service.successResponse(product));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);
/**
* Lấy danh sách tất cả sản phẩm
*
* returns List
* */
const getProducts = () => new Promise(
  async (resolve, reject) => {
    try {
      // Logic MongoDB
      const products = await Product.find({});
      resolve(Service.successResponse(products));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);
/**
* Chỉnh sửa thông tin sản phẩm
*
* id String ID của sản phẩm (MongoDB ObjectID)
* productInput ProductInput 
* no response value expected for this operation
* */
const updateProduct = ({ id, productInput }) => new Promise(
  async (resolve, reject) => {
    try {
      // Logic MongoDB
      const updatedProduct = await Product.findByIdAndUpdate(id, productInput, { new: true });
      resolve(Service.successResponse(updatedProduct));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 405,
      ));
    }
  },
);

module.exports = {
  createProduct,
  deleteProduct,
  getProductById,
  getProducts,
  updateProduct,
};
