const mongoose = require('mongoose');

const InteractionSchema = new mongoose.Schema({
  clientId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  produitId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Product',
    required: true
  },
  type: {
    type: String,
    enum: ['clic', 'vue', 'panier', 'achat','aime','panier abandonné',"n'aime plus"], // Types d'interactions possibles
    required: true
  },
  date: {
    type: Date,
    default: Date.now
  }
});


module.exports = mongoose.model('InteractionType', InteractionSchema);
