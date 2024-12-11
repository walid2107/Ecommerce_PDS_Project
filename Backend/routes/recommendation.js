const {getRecommandations} = require("../controller/recommandationsCtrl");
const { authMiddleware } = require("../middlewares/authMiddleware");
const express = require("express");
const router = express.Router();

router.get('/',authMiddleware, getRecommandations)


module.exports = router;