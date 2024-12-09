const { PythonShell } = require('python-shell');
const { spawn } = require('child_process');
const express = require("express");
const path = require('path');
const router = express.Router();

router.post('/', (req, res) => {
  const userId = req.body.userId;
  const scriptPath = path.join(__dirname, '..', '..', 'IA', 'recommendation_model.py');
console.log(scriptPath);
  let options = {
    mode: 'text',
    pythonPath: 'python', // ou 'python' selon votre environnement
    args: [userId]
  };

// Appeler le script Python pour obtenir des recommandations
   const python = spawn('python', [scriptPath, userId]);

   python.stdout.on('data', (data) => {
    res.send(JSON.parse(data.toString()));
  });

  python.stderr.on('data', (data) => {
    console.error(`Erreur : ${data}`);
    res.status(500).send("Erreur lors de l'exécution du modèle.");
  });
});


module.exports = router;