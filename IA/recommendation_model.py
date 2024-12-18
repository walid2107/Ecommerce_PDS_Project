import pandas as pd
import numpy as np
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
from config.mongodb_connection import get_db_connection
import json
import sys

# Fonction pour convertir les ObjectId en chaîne
def convert_objectid_to_str(obj):
    if isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(i) for i in obj]
    elif isinstance(obj, pd.Series):
        return obj.apply(lambda x: str(x) if isinstance(x, pd._libs.tslibs.np_datetime._datetime) else x)
    elif isinstance(obj, (bytes, bytearray)):  # On pourrait rencontrer d'autres types spécifiques de MongoDB
        return str(obj)
    else:
        return obj

# Charger les données depuis MongoDB
def load_data():
    db = get_db_connection()
    if db is None:
        sys.stderr.write([])
        sys.exit()
    
    # Charger les données d'interaction depuis la collection "interactiontypes"
    interactions_collection = db["interactiontypes"]
     
        # Si la collection est vide, retourner un tableau vide
    if not list(interactions_collection.find()):
        print([])
        sys.exit()
    

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
    
    # Convertir les ObjectId en chaînes avant de retourner le dataframe
    df = convert_objectid_to_str(df)
    return df

# Construire une matrice de similarité basée sur le contenu
def build_content_similarity(data):
    # print("Construction de la matrice de similarité basée sur le contenu...")

    product_features = data[["produitId", "ProduitPrix", "ProduitCategorie", "brand"]].drop_duplicates()

    # Vérifier s'il y a des valeurs manquantes et les gérer
    product_features["ProduitCategorie"] = product_features["ProduitCategorie"].fillna('')
    product_features["brand"] = product_features["brand"].fillna('')

    # Encodage TF-IDF pour les colonnes textuelles
    vectorizer_category = TfidfVectorizer()
    vectorizer_brand = TfidfVectorizer()

    category_matrix = vectorizer_category.fit_transform(product_features["ProduitCategorie"])
    brand_matrix = vectorizer_brand.fit_transform(product_features["brand"])

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
    # print("Entraînement du modèle collaboratif...")
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[["clientId", "produitId", "rating"]], reader)
    
    # Séparer en ensembles d'entraînement et de test
    trainset, testset = train_test_split(dataset, test_size=0.25)
    
    # Utiliser SVD (Singular Value Decomposition)
    model = SVD(n_factors=100, n_epochs=50, lr_all=0.005, reg_all=0.02)
    model.fit(trainset)
    
    return model, testset

# Générer des recommandations pour un utilisateur
def recommend(user_id, data, model, content_similarities, n=5):
    produits = data["produitId"].unique()
    already_interacted = data[data["clientId"] == user_id]["produitId"].tolist()
    
    # Exclure les produits déjà vus par l'utilisateur
    produits = [p for p in produits if p not in already_interacted]
    
    # Calculer les scores de prédiction collaboratifs
    collaborative_scores = []
    for p in produits:
        pred = model.predict(user_id, p)
        # print(f"Predicted score for user {user_id} and product {p}: {pred.est}")  # Affichage de la prédiction
        collaborative_scores.append((p, pred.est))
    
    # Calculer les scores de similarité contenus
    content_scores = []
    for p in produits:
        if p in content_similarities.columns:
            score = content_similarities.loc[already_interacted, p].mean()
            # Remplacer NaN par 0 si nécessaire
            if np.isnan(score):
                score = 0
            # print(f"Content similarity score for product {p}: {score}")  # Affichage de la similarité
        else:
            score = 0
        content_scores.append((p, score))
    
    # Fusionner les scores (pondération 50/50 pour cet exemple)
    recommendations = []
    for i, (prod, collab_score) in enumerate(collaborative_scores):
        content_score = content_scores[i][1]
        final_score = 0.5 * collab_score + 0.5 * content_score
        
        # Assurer que le score ne soit jamais NaN
        if np.isnan(final_score):
            final_score = 0
        
        recommendations.append({"ProduitID": str(prod), "Score": final_score})  # Assurez-vous que le produit est une chaîne
    
    # Trier les recommandations par score décroissant
    recommendations = sorted(recommendations, key=lambda x: x["Score"], reverse=True)
    
    return recommendations[:n]

# Tester le modèle
if __name__ == "__main__":
    import sys

    # Charger les données depuis MongoDB
    data = load_data()
    
    if data is None:
        sys.stderr.write([])
        sys.exit()

    # Construire la matrice de similarité basée sur le contenu
    content_similarities = build_content_similarity(data)
    
    # Entraîner le modèle collaboratif
    model, testset = train_model(data)

    # Vérifier si un user_id est fourni en ligne de commande
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        recommendations = recommend(user_id, data, model, content_similarities)
        
        if recommendations:
            # Convertir les recommandations en JSON
            recommendations = convert_objectid_to_str(recommendations)  # Assurez-vous de convertir toutes les données
            print(json.dumps(recommendations, indent=4))  # Cela convertit les données en JSON et les imprime
        else:
            sys.stderr.write("Aucune recommandation disponible pour cet utilisateur.\n")
    else:
        sys.stderr.write("Veuillez fournir un user_id en argument pour tester les recommandations.\n")
