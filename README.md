# WishDenRing

---

<table style="border: none;">
  <tr style="border: none;">
    <td style="border: none;">
      <h3>Un Dungeon Crawler 3D sous Python</h3>
      <p>
        Développé avec le moteur <strong>Ursina</strong>,  <br/>
        WishDenRing est un jeu d'exploration de donjons. <br/>
        Votre objectif : combattre des monstres redoutables <br/>
        pour nettoyer les différentes zones et progresser <br/>
        à travers les niveaux.
      </p>
    </td>
    <td width="30%" style="border: none;">
      <img src="./assets/icons/eldenwish.png" alt="Logo WishDenRing" width="100%">
    </td>
  </tr>
</table>

<br>

<div align="center">
  <img src="./assets/textures/gameThumbnail.png" alt="Gameplay Screenshot" width="80%">
</div>

---

## 💻 Compatibilité

* [X] Windows
* [X] Linux (Ubuntu, Arch, etc.)
* [ ] MacOS

## Préparation au lancement

Création de l'environnement virtuel python pour pouvoir installer toutes les dépendances nécéssaires

`python -m venv .venv`

Activer l'environnement virtuel python. Méthode qui peut varier selon le système d'exploitation

* Linux/MacOs: `source ./.venv/bin/activate`
* Windows: `./.venv/Scripts/Activate.ps1`

Installer toutes les dépendances nécésaires a tout le projet

`pip install -r requirements.txt`

Executer le projet a travers le launcher

`python main.py`

---

## Arguments de lancement pour le jeu

`python game.py --config configFile.json --multiplayer host/client --ipaddress ws://localhost:3030`

`--config`: prend en paramètre le fichier de configuration pour le jeu
`--multiplayer`: definis le mode de connection pour le mode multijoueur host pour créer le serveur ou client pour s'y connecter
`--ipaddress`: définis l'addresse ip pour se connecter en cas de client pour un multi. Ne sert a rien si le mode de connection est définis sur host

---

## Fichier de configuration

```json
{
    "user": {
        "sensi": 45,
        "renderDistance": 40
    }
}
```


