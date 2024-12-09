import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from config.mongodb_connection import get_db_connection

# Charger les données depuis MongoDB
def load_data():
    db = get_db_connection()
    if db is None:
        print("Échec de la connexion à la base de données. Impossible de continuer.")
        return None
    
    # Charger les données d'interaction depuis la collection "interactions"
    interactions_collection = db["interactiontypes"]
    df = pd.DataFrame(list(interactions_collection.find()))
    # Mapper les types d'interaction à des notes (scores)
    interaction_mapping = {
        "clic": 1,
        "vue": 1,
        "aime": 3,
        "panier": 4,
        "achat": 5,
        "panier abandonné": 2,
        "n'aime plus": 1
    }
    df["rating"] = df["type"].map(interaction_mapping)
    return df

# Construire une matrice de similarité basée sur le contenu
def build_content_similarity(data):
    # Sélectionner les attributs produits
    product_features = data[["produitId", "ProduitPrix", "ProduitCategorie", "brand"]].drop_duplicates()
    
    # Encodage TF-IDF pour les colonnes textuelles
    vectorizer = TfidfVectorizer()
    category_matrix = vectorizer.fit_transform(product_features["ProduitCategorie"])
    brand_matrix = vectorizer.fit_transform(product_features["brand"])
    
    # Normaliser les prix
    scaler = MinMaxScaler()
    product_features["ProduitPrix"] = scaler.fit_transform(product_features[["ProduitPrix"]])
    
    # Combiner toutes les caractéristiques
    combined_features = np.hstack((
        product_features["ProduitPrix"].values.reshape(-1, 1),
        category_matrix.toarray(),
        brand_matrix.toarray()
    ))
    
    # Calculer la matrice de similarité cosinus
    similarity_matrix = cosine_similarity(combined_features)
    
    # Associer les similarités aux IDs de produits
    product_similarities = pd.DataFrame(similarity_matrix, index=product_features["produitId"], columns=product_features["produitId"])
    return product_similarities

# Entraîner le modèle de recommandation collaboratif
def train_model(data):
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[["clientId", "produitId", "rating"]], reader)
    
    # Séparer en ensembles d'entraînement et de test
    trainset, testset = train_test_split(dataset, test_size=0.25)
    
    # Utiliser SVD (Singular Value Decomposition)
    model = SVD()
    model.fit(trainset)
    
    return model, testset

# Générer des recommandations pour un utilisateur
def recommend(user_id, data, model, content_similarities, n=5):
    produits = data["produitId"].unique()
    already_interacted = data[data["clientId"] == user_id]["produitId"].tolist()
    
    # Exclure les produits déjà vus par l'utilisateur
    produits = [p for p in produits if p not in already_interacted]
    
    # Calculer les scores de prédiction collaboratifs
    collaborative_scores = [(p, model.predict(user_id, p).est) for p in produits]
    
    # Calculer les scores de similarité contenus
    content_scores = [
        (p, content_similarities.loc[already_interacted, p].mean() if p in content_similarities.columns else 0)
        for p in produits
    ]
    
    # Fusionner les scores (pondération 50/50 pour cet exemple)
    recommendations = []
    for i, (prod, collab_score) in enumerate(collaborative_scores):
        content_score = content_scores[i][1]
        final_score = 0.5 * collab_score + 0.5 * content_score
        recommendations.append((prod, final_score))
    
    # Trier les recommandations par score décroissant
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    return recommendations[:n]

# Tester le modèle
if __name__ == "__main__":
    import sys

    # Charger les données depuis MongoDB
    data = load_data()
    
    if data is None:
        print("Impossible de charger les données depuis MongoDB.")
        sys.exit()

    # Construire la matrice de similarité basée sur le contenu
    content_similarities = build_content_similarity(data)
    
    # Entraîner le modèle collaboratif
    model, testset = train_model(data)

    # Vérifier si un user_id est fourni en ligne de commande
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        print(f"\nRecommandations pour l'utilisateur {user_id} :\n")
        
        recommendations = recommend(user_id, data, model, content_similarities)
        
        if recommendations:
            for i, (prod, score) in enumerate(recommendations, start=1):
                print(f"{i}. Produit ID: {prod}, Score: {score:.2f}")
        else:
            print("Aucune recommandation disponible pour cet utilisateur.")
    else:
        print("Veuillez fournir un user_id en argument pour tester les recommandations.")
