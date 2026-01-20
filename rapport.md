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

### Multiplication de deux grandes matrices (MapReduce)
L'exercice demande d'ecrire un mapper et un reducer pour calculer le produit
matriciel a partir de `matriceA.txt` et `matriceB.txt`. Le mapper identifie la
matrice (A ou B) via le nom du fichier, puis emet des paires pour chaque cellule
cible `(i,j)`. Le reducer regroupe ces valeurs et somme les produits sur l'indice
`k`.

Les scripts proposes sont `matrice_mapper.py` et `matrice_reducer.py`. Les
dimensions par defaut correspondent aux matrices generees (A: 20x10, B: 10x15),
et peuvent etre adaptees via `A_ROWS`, `A_COLS`, `B_COLS`.
```bash
hadoop jar $STREAMINGJAR -cmdenv A_ROWS=20 -cmdenv A_COLS=10 -cmdenv B_COLS=15 \
  -files matrice_mapper.py,matrice_reducer.py \
  -mapper "python matrice_mapper.py" -reducer "python matrice_reducer.py" \
  -input input/matriceA.txt,input/matriceB.txt -output sortie_matrice
```

Resultat sous HDFS (extrait) :
```bash
hadoop fs -ls sortie_matrice_1
hadoop fs -tail sortie_matrice_1/part-00000
```
```text
Found 2 items
-rw-r--r--   2 root supergroup          0 2026-01-20 15:51 sortie_matrice_1/_SUCCESS
-rw-r--r--   2 root supergroup       3124 2026-01-20 15:51 sortie_matrice_1/part-00000
152
3,14    11940
3,2     28447
3,3     22120
3,4     30060
3,5     21063
3,6     26746
3,7     19926
3,8     14163
3,9     29997
4,0     21977
4,1     33934
4,10    28865
4,11    30957
4,12    18286
4,13    23727
4,14    12441
4,2     32849
4,3     25314
4,4     26935
4,5     18806
4,6     35818
4,7     21576
4,8     14763
4,9     30138
5,0     20334
5,1     35618
5,10    35768
5,11    34278
5,12    18303
5,13    31813
5,14    18635
5,2     30745
5,3     32375
5,4     27975
5,5     26968
5,6     36161
5,7     26434
5,8     17880
5,9     37984
6,0     21867
6,1     25053
6,10    24984
6,11    27507
6,12    14806
6,13    22214
6,14    9970
6,2     24911
6,3     20952
6,4     24439
6,5     16278
6,6     27346
6,7     17623
6,8     12495
6,9     26121
7,0     22057
7,1     21534
7,10    22060
7,11    24057
7,12    17224
7,13    22651
7,14    10623
7,2     22438
7,3     18512
7,4     23217
7,5     16868
7,6     23727
7,7     15926
7,8     14315
7,9     24909
8,0     24457
8,1     34757
8,10    40575
8,11    40141
8,12    24009
8,13    32850
8,14    17250
8,2     35031
8,3     33991
8,4     31587
8,5     28281
8,6     39964
8,7     27567
8,8     19234
8,9     40216
9,0     23031
9,1     20891
9,10    28235
9,11    30052
9,12    17694
9,13    24959
9,14    12853
9,2     22584
9,3     22517
9,4     25503
9,5     24390
9,6     25706
9,7     17808
9,8     12640
9,9     25803
```

## Conclusion
Le traitement MapReduce fonctionne correctement sur un corpus volumineux.
Le tri des donnees avant reduction est indispensable pour agreger les comptes
par mot.

<div style="page-break-after: always;"></div>

## Hadoop MapReduce avec MrJob
Cette partie utilise la librairie **MrJob** et se deroule dans le dossier
`TP-Big-Data-HadoopMrjob`. L'objectif est de tester un wordcount en mode local
avant de passer aux etapes suivantes.

### Etape 1 - Test local (MrJob)
Sous PowerShell, la redirection `<` ne fonctionne pas comme sous Linux. La
commande equivalente est :
```powershell
Get-Content .\dracula.txt | py .\wc_mrjob_1.py | Set-Content .\resultInline.txt
```

Resultat : le fichier `resultInline.txt` a bien ete cree dans le dossier du TP.

Extrait de `resultInline.txt` :
```text
"service!"      1
"service"       10
"service,"      1
"service-"      1
"service."      2
"service;"      1
"services"      1
"set"   47
"set,"  9
"set."  6
"setting"       4
"settle"        5
```

Verification : avec `cat resultInline.txt` (alias `Get-Content` sous
PowerShell), on doit voir des lignes au format `mot<TAB>compte`. Pour valider
rapidement, on peut chercher un mot attendu (ex. `service`, `shall`) et verifier
qu'il a un compteur non nul.

### Test MrJob sur le cluster Hadoop
Le meme wordcount a ete lance sur le cluster Hadoop avec le runner `-r hadoop`.
Deux variantes ont ete testees : lecture depuis STDIN et lecture directe depuis
HDFS.

Commandes :
```bash
python wc_mrjob_1.py -r hadoop < dracula > resultHadoop.txt
python wc_mrjob_1.py -r hadoop hdfs:///user/root/input/dracula > resultHadoop.txt
```

Extrait de sortie (job soumis et termine) :
```text
Running job: job_1768916694477_0003
map 100% reduce 100%
Job job_1768916694477_0003 completed successfully
The url to track the job: http://hadoop-master:8088/proxy/application_1768916694477_0003/
```

### Exercice 1 - Questionner un fichier de ventes
Dans cette partie, l'objectif est d'analyser un gros fichier de ventes afin de
produire des statistiques. Deux jeux de donnees sont utilises : `purchases.txt`
(plus de 4 000 000 lignes) et un extrait `purchases_10000.txt` pour des tests
rapides. Le fichier est tabule et contient 6 colonnes : date (YYYY-MM-DD),
heure (hh:mm), ville, categorie d'achat (Book, Men's Clothing, DVDs, etc.),
somme depensee et moyen de paiement (Amex, Cash, MasterCard, etc.).

La preparation consiste a creer un repertoire local et y deposer le fichier de
ventes. En Python, la tabulation est representee par `\t`, ce qui permet de
parser facilement les lignes (ex. `avant\tapres`).

Les fichiers ont ete places dans `TP-Big-Data-HadoopMrjob/ventes`, avec
`purchases.txt` pour le traitement complet et `purchases_10000.txt` pour les
tests rapides. Chaque question suivante doit etre implemente dans un script
MRJob distinct afin de garder une trace claire des traitements.

Les analyses demandees sont les suivantes : calculer le nombre d'achats par
categorie, puis la somme totale depensee par categorie. Ensuite, isoler la ville
de San Francisco pour mesurer la depense par moyen de paiement, et determiner
la ville ou la categorie Women's Clothing genere le plus d'argent en Cash.
Enfin, une requete originale et plus complexe (plusieurs steps MRJob) doit etre
proposee pour aller au-dela des agregations simples.

Pour structurer ce travail, chaque question est associee a un script MRJob
distinct place dans `TP-Big-Data-HadoopMrjob/ventes` : `count_by_category.py`,
`sum_by_category.py`, `sf_by_payment.py`, `womens_cash_top_city.py`. La requete
originale multi-step est `top_cities_by_sales.py`, qui classe les villes par
chiffre d'affaires et ressort un top 5 par defaut (parametrable).

`count_by_category.py` lit chaque ligne, valide les 6 champs tabules et ne
garde que la categorie. Le mapper emet `(categorie, 1)` et le reducer additionne
ces valeurs pour obtenir le nombre d'achats par categorie.

`sum_by_category.py` suit la meme logique de parsing, mais conserve le montant.
Le mapper emet `(categorie, montant)` et le reducer calcule la somme afin de
fournir le chiffre d'affaires total par categorie.

`sf_by_payment.py` filtre uniquement les lignes de la ville "San Francisco".
Il regroupe ensuite les montants par moyen de paiement, ce qui permet de
comparer la depense totale par carte, cash, etc. dans cette ville.

`Women's Clothing" avec paiement "Cash" et on agrege par ville,
puis on compare les totaux pour ressortir la ville la plus rentable sur ce
segment precis.

`top_cities_by_sales.py` est la requete multi-step originale. Elle calcule le
chiffre d'affaires par ville, puis conserve les N villes les plus rentables
(top 5 par defaut), ce qui donne un classement synthetique des meilleures
villes.

Resultats (extraits, `purchases_10000.txt`) :
```text
count_by_category.py
"Baby"	515
"Books"	600
"CDs"	555
"Cameras"	518
"Children's Clothing"	554
"Computers"	550
"Consumer Electronics"	564
"Crafts"	556
"DVDs"	539
"Garden"	539
"Health and Beauty"	567
"Men's Clothing"	573

sum_by_category.py
"Baby"	132845.15
"Books"	149213.91
"CDs"	142896.84
"Cameras"	134448.18
"Children's Clothing"	138348.24
"Computers"	141206.54
"Consumer Electronics"	147882.21
"Crafts"	137843.05
"DVDs"	133396.26
"Garden"	134093.76
"Health and Beauty"	143057.23
"Men's Clothing"	145254.71

sf_by_payment.py
"Amex"	4167.34
"Cash"	3511.56
"Discover"	3217.94
"MasterCard"	7117.61
"Visa"	6141.3

womens_cash_top_city.py
"Kansas City"	1322.05

top_cities_by_sales.py (top 5)
"Scottsdale"	31072.38
"Oakland"	31019.55
"Las Vegas"	30266.46
"Santa Ana"	30039.41
"Lubbock"	29440.9
```

### Exercice 2 - Anagramme
Objectif : a partir d'un fichier de mots, detecter les mots qui partagent
exactement les memes lettres (ordre different). La sortie ne garde que les
groupes avec au moins 2 mots, et ne tient pas compte des voyelles accentuees.

Exemple attendu :
```text
faible, fiable
arbre, barre
devenir, deviner
lemon, melon
```

Pour des tests plus intensifs, on peut utiliser `words_alpha` (anglais) ou
`Liste-de-mots-francais-Gutenberg` (francais).

Le script MRJob associe a cet exercice est `TP-Big-Data-HadoopMrjob/anagramme/anagramme.py`.
Le mapper lit les mots (un par ligne ou separes par des virgules), passe en
minuscules, puis neutralise les accents sur les voyelles avant de calculer une
signature (lettres triees). Le reducer regroupe les mots ayant la meme
signature, elimine les doublons, puis n'affiche que les groupes de taille
superieure ou egale a 2.
