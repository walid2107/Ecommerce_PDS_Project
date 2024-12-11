const asyncHandler = require("express-async-handler");
const slugify = require("slugify");
const validateMongoDbId = require("../utils/validateMongodbId");
const { spawn } = require('child_process');
const path = require('path');
const Product = require("../models/productModel");

const getRecommandations = asyncHandler(async (req, res) => {
    const userId = req.user._id;
    const scriptPath = path.join(__dirname, '..', '..', 'IA', 'recommendation_model.py');
    let options = {
      mode: 'text',
      pythonPath: 'python', // ou 'python' selon votre environnement
      args: [userId]
    };
  
  // Appeler le script Python pour obtenir des recommandations
     const python = spawn('python', [scriptPath, userId]);
  
     python.stdout.on('data', async (data) => {
      const recommendedProductsData = JSON.parse(data.toString());
      // Récupération des produits recommandés avec Promise.all
      const productsRecommanded = await Promise.all(
        recommendedProductsData.map(async (element) => {
          return  {product: await Product.findById(element.ProduitID), score:element.Score };
        })
      );
      res.json(productsRecommanded);
    });
    python.stderr.on('data', (data) => {
      console.error(`Erreur : ${data}`);
      res.status(500).send("Erreur lors de l'exécution du modèle.");
    });
  });


  module.exports={
    getRecommandations
  }