import os
import pymongo
#from dotenv import load_dotenv

# Charger les variables d'environnement depuis un fichier .env
#load_dotenv()

def get_db_connection():
    """
    Établit une connexion à MongoDB et retourne la base de données.
    """
    try:
        # Récupérer l'URI de connexion MongoDB à partir des variables d'environnement
        #mongo_uri = os.getenv("MONGO_URI")
        mongo_uri="mongodb+srv://PDS:PDS2024@pds.mywkn.mongodb.net/?retryWrites=true&w=majority&appName=PDS"
        if mongo_uri is None:
            raise ValueError("L'URI de MongoDB n'est pas définie dans le fichier .env")
        
        # Créer une connexion à MongoDB
        client = pymongo.MongoClient(mongo_uri)
        
        # Sélectionner la base de données (remplacer "ecommerce_db" par le nom de votre base de données)
        db = client["test"]
        
        print("Connexion à MongoDB réussie")
        return db
    except Exception as e:
        print(f"Erreur de connexion à MongoDB : {e}")
        return None
