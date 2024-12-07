const mongoose = require('mongoose');

const SegmentSchema = new mongoose.Schema({
  nom: {
    type: String,
    required: true,
    unique: true
  },
  description: {
    type: String,
    required: true
  },
  criteres: {
    type: Object, 
    required: true
  },
  dateCreation: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Segment', SegmentSchema);
