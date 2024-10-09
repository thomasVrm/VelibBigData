import requests
from pymongo import MongoClient
from datetime import datetime
import time


# Fonction pour se connecter à MongoDB
def connect_to_mongodb(uri, database_name):
    try:
        client = MongoClient(uri)
        db = client[database_name]
        print(f"Connexion réussie à la base de données: {database_name}")
        return db
    except Exception as e:
        print(f"Erreur lors de la connexion à MongoDB: {e}")
        return None


# Fonction pour récupérer les données depuis l'API
def fetch_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        print(f"Statut de la réponse: {response.status_code}")
        data = response.json().get('results', [])
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP: {http_err}")
        return []
    except Exception as e:
        print(f"Erreur lors de la récupération des données de l'API: {e}")
        return []


# Fonction pour insérer des données dans MongoDB avec timestamp
def insert_data_to_mongodb(db, collection_name, data):
    try:
        collection = db[collection_name]
        timestamped_data = {
            "horodatage": datetime.now(),
            "data": data
        }
        print(f"Insertion des données dans MongoDB : {timestamped_data}")
        collection.insert_one(timestamped_data)
        print(f"Données insérées avec succès dans la collection {collection_name}.")
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans MongoDB: {e}")


# Fonction principale pour automatiser la récupération et insertion des données
def automate_data_insertion(db, api_url, collection_name_base, interval=60):
    while True:
        # Récupérer les données depuis l'API
        gps_points = fetch_data_from_api(api_url)

        if gps_points:
            # Insertion des données dans MongoDB avec un horodatage
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            collection_name = f"{collection_name_base}_{timestamp}"
            insert_data_to_mongodb(db, collection_name, gps_points)
        else:
            print("Aucune donnée récupérée de l'API.")

        # Attendre l'intervalle spécifié avant la prochaine récupération
        time.sleep(interval)


# Usage
if __name__ == "__main__":
    # Connexion à MongoDB
    uri = "mongodb://localhost:27017/"
    database_name = "Velib"
    db = connect_to_mongodb(uri, database_name)

    # URL de l'API Velib
    api_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=100"

    # Nom de base pour la collection
    collection_name_base = "velib_disponibilite"

    # Lancer l'automatisation toutes les 60 secondes
    automate_data_insertion(db, api_url, collection_name_base, interval=60)
