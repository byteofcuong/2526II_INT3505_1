/* eslint-disable no-unused-vars */
const Service = require('./Service');
const Product = require('../models/Product');

/**
* Get all products
* Retrieve a list of all products in the system.
*
* returns List
* */
const productsGET = () => new Promise(
  async (resolve, reject) => {
    try {
      const products = await Product.find({});
      resolve(Service.successResponse(products));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 500,
      ));
    }
  },
);

/**
* Delete a product
* Remove a product from the inventory by its ID.
*
* id Integer The unique identifier of the product.
* no response value expected for this operation
* */
const productsIdDELETE = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      const deletedProduct = await Product.findOneAndDelete({ id: id });
      if (!deletedProduct) {
        return reject(Service.rejectResponse('Product not found', 404));
      }
      resolve(Service.successResponse(null, 204));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 500,
      ));
    }
  },
);

/**
* Get a product by ID
* Retrieve detailed information about a specific product.
*
* id Integer The unique identifier of the product.
* returns Product
* */
const productsIdGET = ({ id }) => new Promise(
  async (resolve, reject) => {
    try {
      const product = await Product.findOne({ id: id });
      if (!product) {
        return reject(Service.rejectResponse('Product not found', 404));
      }
      resolve(Service.successResponse(product));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 500,
      ));
    }
  },
);

/**
* Update a product
* Update the attributes of an existing product.
*
* id Integer The unique identifier of the product.
* productInput ProductInput 
* returns Product
* */
const productsIdPUT = ({ id, productInput }) => new Promise(
  async (resolve, reject) => {
    try {
      const updatedProduct = await Product.findOneAndUpdate(
        { id: id },
        productInput,
        { new: true, runValidators: true }
      );
      if (!updatedProduct) {
        return reject(Service.rejectResponse('Product not found', 404));
      }
      resolve(Service.successResponse(updatedProduct));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 400,
      ));
    }
  },
);

/**
* Create a new product
* Add a new product to the inventory.
*
* productInput ProductInput 
* returns Product
* */
const productsPOST = (params) => new Promise(
  async (resolve, reject) => {
    try {
      const input = params.productInput || params.body || params;
      console.log('DEBUG: productInput received:', input);
      // Find the highest ID and increment it. Default to 1 if no products exist.
      const lastProduct = await Product.findOne().sort({ id: -1 });
      const newId = lastProduct && lastProduct.id ? lastProduct.id + 1 : 1;
      
      const newProduct = new Product({
        ...input,
        id: newId
      });
      await newProduct.save();
      
      // Pass the complete new product and status code 201 Created
      resolve(Service.successResponse(newProduct, 201));
    } catch (e) {
      reject(Service.rejectResponse(
        e.message || 'Invalid input',
        e.status || 400,
      ));
    }
  },
);

module.exports = {
  productsGET,
  productsIdDELETE,
  productsIdGET,
  productsIdPUT,
  productsPOST,
};
