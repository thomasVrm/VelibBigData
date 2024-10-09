# VelibBigData

Ce projet s'occupe de récupérer les données provenant de l'API :https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/velib-disponibilite-en-temps-reel/records?limit=20
Les données sont récupérer puis écrite dans une base mongoDB grâce au fichier "data.py".

Le fichier "map.py", quand a lui s'occupe de récupérer les données de la base mongoDB et grâce a un input de l'utilisateur affiche sa position sur une carte "Leaflet" ainsi que les 10 Vélibs les plus proches de sa position.

Avec l'outil "Navicat" j'ai réaliser un "MapReduce" qui permet de récupérer le nombre total de vélos électriques disponibles (ebike) et le nombre total de vélos mécaniques (mechanical) par arrondissement (nom_arrondissement_communes).
