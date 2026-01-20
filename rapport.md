<div align="center">

# Compte rendu - TP Big Data Hadoop
## Module: Big Data / Hadoop
### TP: Word Count avec Hadoop Streaming (MapReduce)

**Etudiant(s):** Youssef  khalfa, Prenom NOM  
**Encadrant:** Mme Lamia Derrode  
**Date:** 20/01/2026  
**Etablissement:** Ecole Centrale de Lyon 

</div>

<div style="page-break-after: always;"></div>

## Objectif
Mettre en place un comptage de mots (Word Count) sur un gros fichier texte en
utilisant le paradigme MapReduce via des scripts Python en streaming Hadoop.

## Structure du projet
Le projet se limite a trois fichiers, chacun avec un role clair :
- `wc_mapper.py` : mapper Python qui emet `(mot, 1)` pour chaque mot lu.
- `wc_reducer.py` : reducer Python qui additionne les occurrences par mot.
- `dracula.txt` : corpus de test utilise pour valider le flux.

## Points-cles du code
### Mapper (`wc_mapper.py`)
Le mapper lit chaque ligne depuis STDIN, la decoupe en mots avec `split()`, puis
emet un couple `(mot, 1)` pour chaque occurrence. Cette sortie sert d'entree
au tri puis au reducer.

### Reducer (`wc_reducer.py`)
Le reducer lit un flux trie par cle (mot), convertit le compteur en entier et
aggrege les occurrences. A chaque changement de mot, il ecrit `(mot, total)`,
et pense a emettre le dernier mot en fin de flux.

## Execution
### Test local (PowerShell)
Depuis un terminal, se placer dans le dossier de travail (`cd ...`).
Verifier que la premiere ligne des scripts est bien :
```text
#!/usr/bin/env python3
```

Execution du mapper seul :
```powershell
Get-Content dracula.txt | py wc_mapper.py
```

Execution complete (mapper + tri + reducer) :
```powershell
Get-Content dracula.txt | py wc_mapper.py | Sort-Object -CaseSensitive |
  py wc_reducer.py | Select-Object -First 20
```

Remarque Windows : si `py` n'est pas disponible, utiliser `python.exe` (ou
ajouter Python au `PATH`).

### Test local (Linux/Mac)
```bash
cat dracula.txt | python3 wc_mapper.py
cat dracula.txt | python3 wc_mapper.py | sort | python3 wc_reducer.py | head -n 20
```

### Hadoop Streaming (exemple)
```bash
hadoop jar /path/to/hadoop-streaming.jar \
  -input /user/etu/dracula.txt \
  -output /user/etu/wc_out \
  -mapper "python3 wc_mapper.py" \
  -reducer "python3 wc_reducer.py" \
  -file wc_mapper.py -file wc_reducer.py
```

## Comparaison des sorties (mapper)
### Script initial
Commande :
```powershell
Get-Content dracula.txt | py wc_mapper.py | Select-Object -First 12
```
Extrait :
```text
1897 	 1
DRACULA 	 1
by 	 1
Bram 	 1
Stoker 	 1
CHAPTER 	 1
I. 	 1
JONATHAN 	 1
HARKER'S 	 1
JOURNAL. 	 1
(Kept 	 1
in 	 1
```

### Script improved
Commande :
```powershell
Get-Content dracula.txt | py wc_mapper_improved.py | Select-Object -First 12
```
Extrait :
```text
dracula 	 1
by 	 1
bram 	 1
stoker 	 1
chapter 	 1
i 	 1
jonathan 	 1
harker 	 1
s 	 1
journal 	 1
kept 	 1
in 	 1
```

Commentaire :

## Comparaison des sorties (reducer)
### Script initial
Commande :
```powershell
Get-Content dracula.txt | py wc_mapper.py | Sort-Object -CaseSensitive |
  py wc_reducer.py | Select-Object -First 12
```
Extrait :
```text
"  	 1
"1  	 2
"12  	 1
"17  	 3
"17,  	 1
"18  	 1
"2  	 2
"20  	 1
"21  	 1
"24  	 2
"25  	 4
"27  	 1
```

### Script improved
Commande :
```powershell
Get-Content dracula.txt | py wc_mapper_improved.py | Sort-Object -CaseSensitive |
  py wc_reducer_improved.py | Select-Object -First 12
```
Extrait :
```text
a 	 2949
aback 	 1
abaft 	 2
abandon 	 1
abandoned 	 2
abasement 	 1
abated 	 1
abating 	 2
abbey 	 9
abed 	 1
abhorred 	 2
abide 	 1
```

Commentaire :

## Analyse et ameliorations
Les deux comparaisons racontent la meme chose a deux niveaux. Au mapper, la
version initiale conserve la casse et la ponctuation, ce qui fragmente un meme
mot en plusieurs cles (par exemple `DRACULA` et `dracula`, ou encore `JOURNAL.`).
Au reducer, ce bruit devient plus visible : le tri lexicographique fait remonter
des cles parasites (guillemets, chiffres isoles), ce qui fausse l'analyse des
frequences si l'on ne nettoie pas le texte en amont.

La version improved applique une normalisation simple mais efficace : passage
en minuscules et filtrage des caracteres non alphabetiques. Le resultat est un
vocabulaire plus propre et stable, mieux adapte a un comptage fiable. Cette
approche se paie par une separation des apostrophes (`HARKER'S` devient `harker`
et `s`), un choix acceptable pour un premier traitement mais ajustable selon
les objectifs (par exemple en conservant les contractions).

## Resultats (extrait, version initiale)
```text
a  	 2849
a'  	 2
A  	 46
a.m.-  	 5
aback  	 1
abaft  	 2
abandon  	 1
abandoned  	 2
abasement.  	 1
abated  	 1
abating;  	 2
abbey  	 3
```

## Contexte d'installation (Docker Hadoop)
Dans le cadre du TP, un cluster Hadoop local peut etre lance via Docker
avec un noeud maitre et deux noeuds esclaves. Ce reglage est utile pour
reproduire un environnement distribue, mais les exercices peuvent aussi
etre realises en local si la machine est limitee.

## Execution Hadoop (cluster Docker)
Apres l'installation des conteneurs, on entre dans le noeud maitre
(`docker exec -it hadoop-master bash`). La premiere fois, il faut formater
le HDFS avec la commande suivante (a faire une seule fois) :
```bash
/usr/local/hadoop/bin/hdfs namenode -format
```

Ensuite, on lance les services Hadoop sur le master :
```bash
start-dfs.sh
start-yarn.sh
```

Les fichiers de travail restent dans le systeme Linux du conteneur, mais
les gros fichiers sont places dans HDFS. On copie donc le fichier `dracula`
dans HDFS avant le traitement :
```bash
cd TP_Hadoop/wordcount
hadoop fs -mkdir -p input
hadoop fs -put dracula input
hadoop fs -ls input
```

### Preparation des fichiers pour wordcount
Le terminal du conteneur utilise un systeme Linux. Les scripts Python restent
sur cet espace Linux, tandis que les gros fichiers sont places dans HDFS. On se
place dans le dossier du TP, puis on copie `dracula` dans HDFS :
```bash
cd TP_Hadoop/wordcount
hadoop fs -mkdir -p input
hadoop fs -put dracula input
hadoop fs -ls input
```

### Wordcount avec Hadoop
On declare d'abord la librairie de streaming, puis on lance le job :
```bash
export STREAMINGJAR='/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar'
hadoop jar $STREAMINGJAR -files wc_mapper.py,wc_reducer.py \
  -mapper wc_mapper.py -reducer wc_reducer.py \
  -input input/dracula -output sortie
```

Le resultat est stocke dans HDFS. On peut verifier la presence des fichiers
et lire la fin du resultat :
```bash
hadoop fs -ls sortie/
hadoop fs -tail sortie/part-00000
```

Extrait obtenu :
```text
1
yelping          1
yer      9
yer,     1
yes!     3
yes!"    1
yes,     5
yes;     1
yesterday        16
yesterday!       1
yesterday,       7
yesterday.       2
yet      122
yet!     1
yet,     13
yet,"    1
yet-     3
yet.     8
yet.'    1
yet..."          1
yet;     5
yew      1
yew,     1
yew-tree,        2
yew-trees        1
yews     1
yield    3
yield.           1
yield;           1
yielded          3
yielded,         1
yielding         1
yields           2
yoke,    1
you      1002
you!     4
you!"    5
you!'    1
you'     1
you'd    2
you'll           2
you're           2
you've           4
you,     94
you,"    2
you,'says        1
you-     10
you.     38
you."    13
you:     3
you;     5
you?     8
you?"    3
young    45
young,           3
young,-          1
young-           1
young.           2
young;           1
younger          3
younger,         1
younger;         1
your     273
your's           1
yours    2
yours!"          2
yours,           5
yours.           3
yours."          1
yours;           1
yourself         8
yourself,        4
yourself,"       1
yourself.        6
yourself?"       2
yourself?'       1
yourselves       2
youth    5
youthful         2
zeal;    1
zealous          1
zoophagous       3
zoophagous,      1
zoophagy!"       1
```

Note : si un dossier `sortie` existe deja, il faut soit le supprimer, soit
changer le nom de sortie (ex. `sortie2`). Suppression :
```bash
hadoop fs -rm -r -f sortie
```

### Monitoring du cluster et des jobs
Hadoop propose des interfaces web utiles pour verifier l'etat du cluster. Le
Namenode est visible sur `http://localhost:9870` et le ResourceManager (Yarn)
sur `http://localhost:8088`. Ces ports ont ete exposes lors du lancement des
conteneurs Docker.

Sur la page du Namenode, mon instance indique un etat **active** et une version
Hadoop **3.4.1**, ce qui confirme que le service est bien demarre. L'onglet
"Datanodes" montre un seul noeud en service, avec une capacite d'environ
**1006.85 GB** et un usage HDFS tres faible (**~1.42 MB**), ce qui est coherent
avec un petit test sur `dracula`. Le resume affiche aussi `Safemode: off` et
`Security: off`, donc le cluster est operationnel pour les essais du TP.

Enfin, le tableau "Summary" liste **1 Live Node**, **0 Dead Nodes** et un
petit nombre de blocs (5), signe que les fichiers charges dans HDFS sont bien
reconnus. Ces observations confirment que le cluster tourne correctement avant
le lancement des jobs MapReduce.

Du cote Yarn (port `8088`), la page "Nodes of the cluster" montre un seul noeud
en etat **RUNNING**, avec **12 GB** de memoire et **8 vCores** disponibles, et
aucune ressource consommee au repos. La page "All Applications" affiche un job
MapReduce termine avec le statut **SUCCEEDED**, ce qui confirme que l'execution
du wordcount a bien ete prise en compte par le ResourceManager.

## Tests et exercice
### Wordcount improved
Pour reutiliser les scripts ameliores dans le conteneur Hadoop, on ouvre un
second terminal sur la machine hote et on copie les fichiers vers Linux avec
`docker cp`. Cette methode servira aussi pour de futurs scripts :
```powershell
docker cp wc_mapper_improved.py hadoop-master:/root/TP_Hadoop/wordcount/
docker cp wc_reducer_improved.py hadoop-master:/root/TP_Hadoop/wordcount/
```

Dans le premier terminal (dans le conteneur), on verifie la presence des
fichiers, on les rend executables, puis on convertit les fins de ligne Windows
vers Linux avec `dos2unix` :
```bash
cd /root/TP_Hadoop/wordcount
ls
chmod +x wc_mapper_improved.py
chmod +x wc_reducer_improved.py
dos2unix wc_mapper_improved.py
dos2unix wc_reducer_improved.py
```

Remarque : la commande d'exemple `dos2unix fichier.py` affiche une erreur si le
fichier n'existe pas. Dans notre cas, la conversion a bien fonctionne sur les
deux scripts ameliore.

### Multiplication de deux grandes matrices (generation)
On se place dans le repertoire `~/TP_Hadoop/matrice` et on lance le script
`matrice.py`. Il genere deux matrices (matriceA et matriceB), les enregistre
dans `matriceA.txt` et `matriceB.txt`, puis affiche leur produit. Les
dimensions observees sont **20x10** et **10x15**, donc un produit **20x15**.
```bash
cd ~/TP_Hadoop/matrice
python matrice.py
```

Extrait d'affichage :
```text
matriceA =  [[74  7 23 54 96  2 83 66 77 50]
 [ 3 69 98 19 97 46 56 89 91 23]
 ...]
matriceB =  [[66  5 65 41 70 56 23 15 57 64 53 71 94 75  0]
 [83 40 46 16 34 46 69 10  0  7 58 44 27 39  0]
 ...]
Produit des 2 matrices =  [[173 163 204 180 132  15 178 228   4 167  10 131 246 124  33]
 [ 32  96  60  47  60 110   7 160 239 188 154 209 213 241   6]
 ...]
```

Les fichiers generes ont ensuite ete deposes sur HDFS dans le repertoire
`input` :
```bash
hadoop fs -put matriceA.txt input
hadoop fs -put matriceB.txt input
```

## Conclusion
Le traitement MapReduce fonctionne correctement sur un corpus volumineux.
Le tri des donnees avant reduction est indispensable pour agreger les comptes
par mot.
