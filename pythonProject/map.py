import folium
import webbrowser
from geopy.geocoders import Nominatim
from haversine import haversine, Unit
from pymongo import MongoClient
import time

# Fonction pour parser les coordonnées
def parse_coordinates(coord_data):
    if isinstance(coord_data, dict):  # Les données sont déjà sous forme de dict
        return coord_data.get('lat'), coord_data.get('lon')
    return None, None

# Fonction pour géocoder une adresse
def geocode_address(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    time.sleep(1)  # Délai entre les requêtes pour éviter d'être bloqué par l'API
    if location:
        return location.latitude, location.longitude
    else:
        print("Adresse introuvable.")
        return None, None


def find_closest_points(user_location, gps_points):
    distances = []
    for point in gps_points:
        coord = point.get('coordonnees_geo')

        # Vérifie si les coordonnées sont sous forme de dictionnaire avec 'lat' et 'lon'
        if isinstance(coord, dict) and 'lat' in coord and 'lon' in coord:
            lat = coord['lat']
            lon = coord['lon']

            # Calculer la distance si les coordonnées sont valides
            if lat is not None and lon is not None:
                print(f"Coordonnées du point: ({lat}, {lon}) pour la station {point['name']}")
                try:
                    distance = haversine(user_location, (lat, lon), unit=Unit.METERS)
                    distances.append((point, distance))
                    print(f"Distance calculée: {distance:.2f} m pour {point['name']}")
                except Exception as e:
                    print(f"Erreur lors du calcul de la distance pour {point['name']}: {e}")
            else:
                print(f"Coordonnées manquantes pour la station: {point['name']}")
        else:
            print(f"Données de coordonnées manquantes ou invalides pour le point: {point}")

    # Trier par distance et prendre les 10 plus proches
    distances.sort(key=lambda x: x[1])

    if len(distances) > 0:
        print(f"Stations les plus proches (top 10): {[d[0]['name'] for d in distances[:10]]}")
    else:
        print("Aucune station n'a été trouvée à proximité.")

    return distances[:10]


# Fonction principale pour l'affichage
def display_map(user_address):
    user_lat, user_lon = geocode_address(user_address)
    if user_lat and user_lon:
        user_location = (user_lat, user_lon)
        print(f"Votre position: {user_location}")  # Log de position

        # Connexion à MongoDB
        uri = "mongodb://localhost:27017/"
        database_name = "Velib"
        client = MongoClient(uri)
        db = client[database_name]

        # Récupérer les données depuis la bonne collection
        gps_points = list(db['velib-disponibilite-en-temps-reel'].find())  # Collection correcte
        print(f"Nombre total de points récupérés: {len(gps_points)}")  # Débogage

        # Trouver les 10 points les plus proches
        close_points = find_closest_points(user_location, gps_points)
        print(f"Points les plus proches: {close_points}")  # Débogage

        # Créer la carte centrée sur l'adresse de l'utilisateur
        m = folium.Map(location=[user_lat, user_lon], zoom_start=12)

        # Ajouter le marqueur pour l'adresse de l'utilisateur en rouge
        folium.Marker(
            [user_lat, user_lon],
            popup="Votre adresse",
            icon=folium.Icon(color="red")
        ).add_to(m)

        # Ajouter des marqueurs pour les 10 points les plus proches
        for point, distance in close_points:
            lat, lon = point['coordonnees_geo']['lat'], point['coordonnees_geo']['lon']
            name = point.get('name', 'Nom de rue inconnu')

            # Log pour chaque point ajouté
            print(f"Ajout d'un marqueur pour la station {name} située à {distance:.2f} m")

            if lat and lon:
                popup_content = f"""
                <div style="border-radius: 10px; padding: 10px; background-color: #f9f9f9; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                    <h4 style="margin: 0;">{name}</h4>
                    <p><strong>Coordonnées:</strong> {lat},{lon}<br>
                    <strong>Distance:</strong> {distance:.2f} m</p>
                </div>
                """
                # Ajouter le marqueur pour chaque point trouvé
                folium.Marker(
                    [lat, lon],
                    popup=folium.Popup(popup_content, max_width=300)
                ).add_to(m)

        # Sauvegarder la carte dans un fichier HTML et l'ouvrir
        try:
            m.save('map.html')
            webbrowser.open('map.html')
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la carte: {e}")
    else:
        print("Impossible de géocoder l'adresse.")


# Demander l'adresse à l'utilisateur et afficher la carte
user_address = input("Entrez une adresse: ")
display_map(user_address)
