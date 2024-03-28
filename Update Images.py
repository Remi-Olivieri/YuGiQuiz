import json
import requests
from bs4 import BeautifulSoup
from PIL import Image

with open('cardinfo.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

def format_jpg(carte):
    carte = carte.replace("/", "")
    carte = carte.replace("\\", "")
    carte = carte.replace(":", "")
    carte = carte.replace("*", "")
    carte = carte.replace("?", "")
    carte = carte.replace('"', "")
    carte = carte.replace("<", "")
    carte = carte.replace(">", "")
    carte = carte.replace("|", "")
    
    carte = carte.replace("  ", " ")
    carte = carte.replace("   ", " ")
    
    carte = carte.rstrip('-')
    carte = carte.rstrip(' ')
    
    return(carte)

def telecharger_image(url, nom_fichier):
    
    reponse = requests.get(url)
    try:
        if reponse.status_code == 200:
            with open(nom_fichier, 'wb') as f:
                f.write(reponse.content)
            print("L'image a été téléchargée avec succès sous le nom", nom_fichier)
        else:
            print("Impossible de télécharger l'image ", nom_fichier)
    except Exception:
        print("Pas téléchargé : ", nom_fichier)

for item in data["data"]:
    item_id = item["id"]
    item_name = item["name"]
    
    url = "https://images.ygoprodeck.com/images/cards/" + str(item_id) + ".jpg"
    carte = "Images test/" + format_jpg(item_name) + ".jpg"
    try:
        with Image.open(carte) as img:
            largeur, hauteur = img.size
    except Exception:
        telecharger_image(url, carte)
    

