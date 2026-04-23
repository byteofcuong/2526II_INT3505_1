const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
    id: { type: Number, required: true, unique: true }, // The unique identifier of the product
    name: { type: String, required: true }, // The name of the product
    price: { type: Number, required: true }, // The price of the product
    category: { type: String }, // Category the product belongs to
    stock: { type: Number }, // The quantity of the product currently in stock
    description: { type: String } // A detailed description of the product
});

module.exports = mongoose.model('Product', productSchema);
