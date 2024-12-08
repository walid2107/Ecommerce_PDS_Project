import pymongo
import pandas as pd

# Connexion à MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["votre_base_de_donnees"]
collection = db["interactions"]

# Extraction des données
data = list(collection.find())
df = pd.DataFrame(data)

# Nettoyage des données
df = df[["_id", "clientId", "produitId", "type", "date"]]
df.to_csv("interactions.csv", index=False)
print("Données exportées avec succès!")
