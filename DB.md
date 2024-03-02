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
    - `sol` : Solution
    - `solcout` : Coût d’une solution
    - `solgain` : Gain d’une solution
    - `tec` : Technologie
    - `tecenj`
    - `tecnor`
    - `sec`
    - `secchi`
    - `seccon`
    - `secenj`
    - `fin`
    - `finrex`
    - `finsol`
    - `rex`
    - `rexcout`
    - `rexgain`
    - `ref`
    - `autodiag`
    - `opp`
    - `chart`
    - `chartVal`
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
