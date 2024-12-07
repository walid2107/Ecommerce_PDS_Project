const express = require("express");
const router = express.Router();
const { authMiddleware } = require("../middlewares/authMiddleware");
const {createInteractionType} = require("../controller/InteractionTypeCtrl");


router.post("/", authMiddleware , createInteractionType);

module.exports = router;