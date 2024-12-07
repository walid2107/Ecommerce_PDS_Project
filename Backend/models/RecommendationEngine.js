const mongoose = require('mongoose');

const RecommendationSchema = new mongoose.Schema({
  clientId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  recommendations: [
    {
      produitId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Produit',
        required: true
      },
      score: {
        type: Number, // Score de pertinence de la recommandation
        required: true
      },
      date: {
        type: Date,
        default: Date.now
      }
    }
  ],
  date: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Recommendation', RecommendationSchema);
