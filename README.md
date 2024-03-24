# DataBattle2024

1. Setup le venv
   a) Se placer un dossier au dessus du repo
   b) python3 -m venv .venv
   c) source ./bin/activate
   d) pip install -r requirements.txt (Attention à bien se placer pour que le requirement.txt soit dans le dossier où l'on exec cette commande)

2. Setup la db

a) mysql -u User -p (Il faut remplacer le User par votre truc et se placer dans le dossier qui contient le config.ini)
b) source database.sql (J'ai rajouté un tableau à la BDD)

3. Ajouter les embeddings à la BDD

a) Il faut run la fonction fill_embeddings_table_from_scratch() du script add_new_solution_embedding.py
(ça prend 10-15min)

4. C bon tu peux run le main.py
