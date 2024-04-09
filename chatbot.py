from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from joblib import load
import pandas as pd
import numpy as np
import folium
import geopandas
import random
from geopy.geocoders import Nominatim
from matplotlib.patches import Ellipse
from sklearn.cluster import DBSCAN
import matplotlib.colors as colors
from opencage.geocoder import OpenCageGeocode

modele = load('data/decision_tree.joblib')

france = geopandas.read_file('https://github.com/gregoiredavid/france-geojson/raw/master/departements.geojson')

app = Flask(__name__)
CORS(app)

def get_map(latitude_c, longitude_c):
    #Les communes de France et leur géolocalisations
    np.random.seed(0)

    df_communes_original = pd.read_csv('data/to_use.csv')
    df_communes = df_communes_original.copy()
    mask = df_communes_original['code_dep'].apply(lambda x: len(x) > 2)
    communes_france_metro = df_communes.drop(index=df_communes[mask].index)
    communes_france_metro_geo_list = communes_france_metro[['latitude', 'longitude', 'pop']]

    density_sum = communes_france_metro_geo_list['pop'].sum()
    density_probs = communes_france_metro_geo_list['pop'] / density_sum

    sampled_indexes = np.random.choice(communes_france_metro_geo_list.index, size=5434, replace=True, p=density_probs)

    # Les cas COVID de notre jeu de données

    np.random.seed(0)

    df_original = pd.read_csv('data/Covid Dataset.csv')
    df_COVID = df_original[['COVID-19']]

    df_COVID['lat'] = communes_france_metro_geo_list['latitude'][sampled_indexes].tolist()
    df_COVID['lon'] = communes_france_metro_geo_list['longitude'][sampled_indexes].tolist()
    df_ready = df_COVID.copy()
    df_ready = df_ready[df_ready['COVID-19'] == 'Yes']

    X = df_ready[['lon', 'lat']].values
    X = np.radians(X)

    kms_per_radian = 6371.0088
    epsilon = 10 / kms_per_radian

    dbscan = DBSCAN(eps=epsilon, min_samples=3, algorithm='ball_tree', metric='haversine')
    labels = dbscan.fit_predict(X)

    # Les données pour l'affichage des cluster sur une map

    # Nb de cas dans le Cluster
    unique_labels = set(labels)
    unique_labels.remove(-1)
    n_points = [len(labels[labels == label]) for label in unique_labels]

    # Calculs des centroïdes
    centers = []
    for label in unique_labels:
        centers.append(np.mean(X[labels == label], axis=0))

    # Calcul de la distance maximal entre un controïde et son élément le plus éloigné
    max_distances = []
    for center, label in zip(centers, unique_labels):
        distances = np.linalg.norm(X[labels == label] - center, axis=1)
        max_distances.append(np.max(distances))

    centers = np.degrees(centers)

    # Create a Folium map centered at the desired location
    m = folium.Map(location=[latitude_c, longitude_c], zoom_start=10)  #/ ! \ remplace "location" par les coordonnées géographiques que l'internaute renseignera
    folium.Marker(location=[latitude_c, longitude_c]).add_to(m)        #/ ! \ remplace "location" par les coordonnées géographiques que l'internaute renseignera

    folium.GeoJson(data=france, style_function=lambda x: {'fillColor': 'white', 'color': 'black', 'weight': 0.3}).add_to(m)

    # Convert the list of centers to a pandas DataFrame

    all_info = pd.DataFrame(centers, columns=['latitude', 'longitude'])
    all_info['max_distances'] = max_distances
    all_info['n_points'] = n_points

    # Add a circle marker for each center to the map
    for index, row in all_info.iterrows():
        #print(index, row)
        latitude = row['latitude']
        longitude = row['longitude']
        max_distance = row['max_distances']*80
        #print(max_distance)
        color = braket_color(row['n_points'])
        covid_nb = int(row['n_points'])
        folium.Circle(
            location=[longitude, latitude],
            radius=max_distance*50000,
            color=color,
            weight=1,
            fill_opacity=0.5,
            fill_color=color,
            fill=False,
            opacity=1,
            popup="{} cas positifs".format(covid_nb),
        ).add_to(m)

    m.save('templates/map.html')
    return m

def braket_color(nb_points):

    if nb_points >= 3 and nb_points <= 10:
        color = 'orange'
    elif nb_points > 10 and nb_points <= 100:
        color = 'red'
    else:
        color = 'purple'
    
    return color

@app.route('/map', methods=['POST', 'GET'])
def map():
    data = request.get_json()
    code_postal = data.get('postalCode')
    cle_api = '6fef25b5b24742c58be8f17ef944ad98'
    geocoder = OpenCageGeocode(cle_api)

    query = f'{code_postal}, France'
    result = geocoder.geocode(query)

    if result and len(result):
        latitude = result[0]['geometry']['lat']
        longitude = result[0]['geometry']['lng']
        get_map(latitude, longitude)
    else:
        return jsonify({"error": result})
    
    return render_template('map.html')


@app.route('/chatbot', methods=['POST'])
def chatbot_response():
    data = request.get_json()
    
    symptomes_df = pd.DataFrame(data)
    prediction = modele.predict(symptomes_df)

    resultat = "Positif au COVID-19" if prediction[0] == 1 else "Négatif au COVID-19"

    return jsonify({"resultat": resultat})

@app.route('/')
def main():
    return render_template('/chatbot.html')


if __name__ == '__main__':
    app.run(debug=True)