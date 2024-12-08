const express = require('express');
const router = express.Router();
const { spawn } = require('child_process');

router.get('/recommend/:userId', (req, res) => {
  const userId = req.params.userId;

  // Appeler le script Python pour obtenir des recommandations
  const python = spawn('python', ['recommendation_model.py', userId]);

  python.stdout.on('data', (data) => {
    res.send(JSON.parse(data.toString()));
  });

  python.stderr.on('data', (data) => {
    console.error(`Erreur : ${data}`);
    res.status(500).send("Erreur lors de l'exécution du modèle.");
  });
});

module.exports = router;
