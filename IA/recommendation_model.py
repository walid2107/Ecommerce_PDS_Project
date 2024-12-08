import pandas as pd
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split

# Charger les données
def load_data(file_path="interactions.csv"):
    df = pd.read_csv(file_path)
    print("Données chargées avec succès.")
    
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

# Entraîner le modèle de recommandation
def train_model(data):
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data[["clientId", "produitId", "rating"]], reader)
    
    # Séparer en ensembles d'entraînement et de test
    trainset, testset = train_test_split(dataset, test_size=0.25)
    
    # Utiliser SVD (Singular Value Decomposition)
    model = SVD()
    model.fit(trainset)
    
    print("Modèle entraîné avec succès.")
    return model, testset

# Générer des recommandations pour un utilisateur
def recommend(user_id, data, model, n=5):
    produits = data["produitId"].unique()
    already_interacted = data[data["clientId"] == user_id]["produitId"].tolist()
    
    # Exclure les produits déjà vus par l'utilisateur
    produits = [p for p in produits if p not in already_interacted]
    
    # Calculer les scores de prédiction pour chaque produit
    recommendations = [(p, model.predict(user_id, p).est) for p in produits]
    
    # Trier les recommandations par score décroissant
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)
    return recommendations[:n]

# Tester le modèle
if __name__ == "__main__":
    import sys

    # Charger les données
    file_path = "interactions.csv"
    data = load_data(file_path)
    
    # Entraîner le modèle
    model, testset = train_model(data)

    # Vérifier si un user_id est fourni en ligne de commande
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        print(f"Recommandations pour l'utilisateur {user_id}:")
        recommendations = recommend(user_id, data, model)
        for i, (prod, score) in enumerate(recommendations, start=1):
            print(f"{i}. Produit ID: {prod}, Score: {score:.2f}")
    else:
        print("Veuillez fournir un user_id en argument pour tester les recommandations.")
