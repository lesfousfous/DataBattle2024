# DataBattle2024

## Setup le venv
```bash
cd .. # Se placer un dossier au dessus du repo
python3 -m venv .venv
source .venv/bin/activate
cd DataBattle2024 # retourner dans le repo
pip install -r requirements.txt # Attention à bien se placer pour que le requirement.txt soit dans le dossier où l'on exec cette commande

```

## Setup la dase de donnée
Créer/mettre son config.ini dans `src`:
```ini
[mysqlDB]
db = kerdos
host = 127.0.0.1
password = your_sql_password
user = your_sql_username
```

Ouvrir le shell sql: 
```bash 
mysql -u User -p  # Il faut remplacer le User par votre username sql 
```
Puis lancer les commandes:
```sql
use nom_db; # Il faut remplacer nom_db par le nom de la base de donnée
source database.sql; # Nécessaire une nouvelle table a été ajouté
``` 

## Ajouter les embeddings à la BDD

Lancer le script `add_new_solution_embedding.py`.

```bash
cd src
python3 -m utils.add_new_solution_embedding #  Un installer va souvrir pour installer nltk, le fermer une fois l'instalation faite. Le programme va se lancer ensuite, attention ça peut prend  jusqu'à 10-15min.
```

##  Exécution

On peut lancer le script `streamlit_main_page.py`.

```bash
cd src
python3 streamlit_main_page.py
```