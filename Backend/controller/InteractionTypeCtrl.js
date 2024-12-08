const InteractionType = require("../models/interactionModel");
const asyncHandler = require("express-async-handler");

const createInteractionType = asyncHandler(async (req, res) => {
  try {
    console.log("Interaction controller here !");
    const { _id } = req.user;
    const { produitId, type,ProduitPrix,ProduitCategorie,brand } = req.body;


    const newInteraction = await InteractionType.create({produitId, type,ProduitPrix,ProduitCategorie,brand,clientId:_id});
    res.json(newInteraction);
  } catch (error) {
    throw new Error(error);
  }
});

module.exports={
    createInteractionType
}