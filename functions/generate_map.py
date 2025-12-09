import os
from datetime import datetime
import json

# verifie si le dossier de la map existe sinon créer un
if (not os.path.isdir('map')):
    os.mkdir("map")

dateNowRaw = datetime.now()  # récup temps
# crée nom de fichier sous forme (année-mois-jour-microsecondes)
dateNow = f"{dateNowRaw.strftime("%Y")}-{dateNowRaw.strftime("%m")}-{dateNowRaw.strftime("%d")}-{dateNowRaw.strftime("%f")}"

with open(f"./map/{dateNow}.json", 'w') as map:
    mapDict = {}
    mapDict["player"] = {
        "coordinates": "(0,0,0)",
    }

    mapDict["world"] = {
        "plants": {
            "flowers": {},
            "grass": {},
        }
    }

    json.dump(mapDict, map)
