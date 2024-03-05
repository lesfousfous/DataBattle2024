# Base de données fournie

## Importer la base de données

- Installer MySQL ou MariaDB
- Créer une base de données vide
```sql
create database kerdos;
```
- Importer la base de données
```sh
mysql -u username -p kerdos < db_backup_plateforme_2024-01-10_010001.sql
```

## La plateforme Kerdos
Ne pas hésiter à se connecter sur [la platforme kerdos](https://plateforme.kerdos-energy.com/) pour mieux comprendre la doc.
Login : contact@iapau.org
Mot de passe : Databattle2024
Numéro de licence : Yu3dH7ykUY8EoH3
## Schéma

### Solution `tblsolution`

- `numsolution` : Numéro de la solution

### Dictionnaire `tbldictionnaire`

Contient toutes les chaînes de caractères. 

- `codelangue` : Langue de la description (voir `tbllangue`)
    - 2 : français
    - 3 : anglais
    - 4 : espagnol
- `typedictionnaire` : Type de l’objet
    - `sol` : Toutes les informations sur la solution
    - `tec` : Toutes les infos sur une technologie sauf les Normes et Enjeux
    - `tecenj` : Description des enjeux d'une technologie
    - `tecnor`: Norme, loi et règlementation d'une technologie
    - `sec` : Nom du secteur et descriptions du secteur mélangés
    - `secchi` : Texte décrivant les chiffres clés d'un secteur
    - `seccon` : Texte décrivant la consommation d'énergie dans ce secteur
    - `secenj` : Texte décrivant les enjeux du secteur
    - `fin` : Toutes les infos sur un financement sauf ?
    - `finrex` : ?
    - `rex` : Nom de l'entreprise associé à l'étude de cas (rex = Retour d'experience)
    - `rexcout` : Contient les descriptions des coûts dûs à l'installation d'une solution dans le contexte d'une étude de cas
    - `rexgain` : Contient les descriptions des gains réalisés par l'installation d'une solution dans le contexte d'une étude de cas
    - `ref` : Nom du document référence
    - `autodiag` : Questions liées à l'autodiagnostic (aujourd'hui 02/03/2024 il y a quasi rien)
    - `opp` : Noms des sujets d'étude d'opportunités (Pas encore complètement implémentée sur la platforme Kerdos)
    - `chart` : Légendes des graphiques (ex : Coûts (EUR/kW))
    - `chartVal` : Les données des graphiques
    - `bench` 
    - `benchVal`
- `codeappelobjet` : Numéro de l’objet
- `indexdictionnaire` : Un objet peut avoir plusieurs entrées, la première entrée est sûrement celle qu’on veut
- `traductiondictionnaire` : Description de l’objet

Exemple : récupérer la description de la solution 160.
```sql
select traductiondictionnaire from tbldictionnaire
where codelangue = 2           # français
  and typedictionnaire = 'sol' # solution
  and codeappelobjet = 160     # numéro de la solution
  and indexdictionnaire = 1    # première description
```
| traductiondictionnaire |
| :--- |
| Campagne de détection des fuites sur un réseau d’air comprimé |



### Dictionnaire `tbldictionnairecategories`

Contient toutes les chaînes de caractères liées aux descriptions

- `codelangue` : Langue de la description (voir `tbllangue`)
    - 2 : français
    - 3 : anglais
    - 4 : espagnol
- `typedictionnairecategories` : Type de l’objet
    - `res` : Contient les valeurs [-N/A-, Oui, Non, Partiel] (Je ne sais pas encore à quoi elles servent)
    - `tra` : Contient les valeurs [Neuf/Extension, Renovation/retrofit, Neuf OU Existant] (Je ne sais pas encore à quoi elles servent)
    - `uni` : Contient plein d'unités (ex: EUR / Ah / m.s-1)
    - `reffor`: Contient les types de réferences (Fichier/ Livre ou Internet)
    - `reftyp` : ?
    - `tecgrp` : Contient les grandes catégories de technologies
    - `secgrp` : Contient les grandes catégories de secteurs
    - `solcat` : Contient les 3 grandes catégories de solutions (Comportementale / Exploitation / Investissement)
    - `mec` : Contient les mécanismes de financement
    - `cee` : Contient des numéros d'arrêtés (jsp à quoi ça sert)
    - `ceethm` :
    - `ceegrp` : 
    - `sys` : Correspond aux sous-catégories les plus profondes de solutions sauf que des fois il y a général au lieu du nom qui va bien (let's go la bdd en access)
 
Exemple : récupérer les noms de grandes catégories de technologies.
```sql
SELECT traductiondictionnairecategories  FROM tbldictionnairecategories 
WHERE codelangue = 2 
and typedictionnairecategories  = "tecgrp"
```

- `codeappelobjet` : Numéro de l’objet
- `indexdictionnairecategories` : Un objet peut avoir plusieurs entrées, la première entrée est sûrement celle qu’on veut
- `traductiondictionnairecategories` : Description de l’objet
