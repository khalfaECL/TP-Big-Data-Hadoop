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
J'ai mis en place un comptage de mots (Word Count) sur un gros fichier texte
en utilisant le paradigme MapReduce via des scripts Python en streaming Hadoop.

## Structure du projet
J'utilise trois fichiers principaux, chacun avec un role clair :
- `wc_mapper.py` : mapper Python qui emet `(mot, 1)` pour chaque mot lu.
- `wc_reducer.py` : reducer Python qui additionne les occurrences par mot.
- `dracula.txt` : corpus de test utilise pour valider le flux.

## Points-cles du code
### Mapper (`wc_mapper.py`)
J'ai code un mapper qui lit chaque ligne depuis STDIN, la decoupe en mots avec
`split()`, puis emet un couple `(mot, 1)` pour chaque occurrence. Cette sortie
sert d'entree au tri puis au reducer.

### Reducer (`wc_reducer.py`)
J'ai code un reducer qui lit un flux trie par cle (mot), convertit le compteur
en entier et agrege les occurrences. A chaque changement de mot, il ecrit
`(mot, total)` et emet le dernier mot en fin de flux.

## Execution
### Test local (PowerShell)
J'ai execute les commandes suivantes en local :
```powershell
Get-Content dracula.txt | py wc_mapper.py
```

```powershell
Get-Content dracula.txt | py wc_mapper.py | Sort-Object -CaseSensitive |
  py wc_reducer.py | Select-Object -First 20
```

## Comparaison des sorties (mapper)
### Script initial
J'ai utilise la commande suivante :
```powershell
Get-Content dracula.txt | py wc_mapper.py | Select-Object -First 12
```
J'ai observe l'extrait suivant :
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
J'ai utilise la commande suivante :
```powershell
Get-Content dracula.txt | py wc_mapper_improved.py | Select-Object -First 12
```
J'ai observe l'extrait suivant :
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

## Comparaison des sorties (reducer)
### Script initial
J'ai utilise la commande suivante :
```powershell
Get-Content dracula.txt | py wc_mapper.py | Sort-Object -CaseSensitive |
  py wc_reducer.py | Select-Object -First 12
```
J'ai observe l'extrait suivant :
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
J'ai utilise la commande suivante :
```powershell
Get-Content dracula.txt | py wc_mapper_improved.py | Sort-Object -CaseSensitive |
  py wc_reducer_improved.py | Select-Object -First 12
```
J'ai observe l'extrait suivant :
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

## Analyse et ameliorations
J'observe la meme difference a deux niveaux. Au mapper, la version initiale
conserve la casse et la ponctuation, ce qui fragmente un meme mot en plusieurs
cles (par exemple `DRACULA` et `dracula`, ou encore `JOURNAL.`). Au reducer, ce
bruit devient plus visible et fausse l'analyse si je ne nettoie pas le texte.

J'ai donc applique une normalisation simple : passage en minuscules et filtrage
des caracteres non alphabetiques. Le resultat donne un vocabulaire plus propre,
adapte a un comptage fiable. Cette approche se paie par la separation des
apostrophes (`HARKER'S` devient `harker` et `s`), ce qui reste acceptable pour
ce TP.

## Resultats (extrait, version initiale)
J'ai obtenu l'extrait suivant :
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
Dans ce TP, j'ai lance un cluster Hadoop local via Docker avec un noeud maitre
et deux noeuds esclaves. Cela me permet de reproduire un environnement
distribue sur ma machine.

## Execution Hadoop (cluster Docker)
Apres l'installation des conteneurs, j'entre dans le noeud maitre
(`docker exec -it hadoop-master bash`). La premiere fois, je formate le HDFS :
```bash
/usr/local/hadoop/bin/hdfs namenode -format
```

Ensuite, je lance les services Hadoop sur le master :
```bash
start-dfs.sh
start-yarn.sh
```

### Preparation des fichiers pour wordcount
Dans le conteneur, j'utilise le systeme Linux et je garde les scripts Python
sur cet espace. Les fichiers volumineux sont places dans HDFS. Je me place dans
le dossier du TP puis je copie `dracula` dans HDFS :
```bash
cd TP_Hadoop/wordcount
hadoop fs -mkdir -p input
hadoop fs -put dracula input
hadoop fs -ls input
```

### Wordcount avec Hadoop
J'ai declare la librairie de streaming puis j'ai lance le job :
```bash
export STREAMINGJAR='/usr/local/hadoop/share/hadoop/tools/lib/hadoop-streaming-3.4.1.jar'
hadoop jar $STREAMINGJAR -files wc_mapper.py,wc_reducer.py \
  -mapper wc_mapper.py -reducer wc_reducer.py \
  -input input/dracula -output sortie
```

J'ai ensuite verifie la presence des fichiers et la fin du resultat :
```bash
hadoop fs -ls sortie/
hadoop fs -tail sortie/part-00000
```

J'ai obtenu l'extrait suivant :
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


### Monitoring du cluster et des jobs
J'ai consulte les interfaces web du Namenode (`http://localhost:9870`) et du
ResourceManager Yarn (`http://localhost:8088`). Sur le Namenode, j'ai observe
un etat **active**, Hadoop **3.4.1**, un seul datanode en service et un usage
HDFS tres faible (**~1.42 MB**). Le resume indique `Safemode: off` et
`Security: off`, ce qui confirme que le cluster est operationnel.

Sur Yarn, la page "Nodes of the cluster" montre un noeud **RUNNING** avec
**12 GB** et **8 vCores** disponibles. La page "All Applications" affiche un
job MapReduce termine avec le statut **SUCCEEDED**, ce qui valide l'execution
du wordcount sur le cluster.

## Tests et exercice
### Wordcount improved
Pour reutiliser les scripts ameliores dans le conteneur Hadoop, j'ai ouvert un
second terminal sur la machine hote et j'ai copie les fichiers vers Linux avec
`docker cp` :
```powershell
docker cp wc_mapper_improved.py hadoop-master:/root/TP_Hadoop/wordcount/
docker cp wc_reducer_improved.py hadoop-master:/root/TP_Hadoop/wordcount/
```

Dans le conteneur, j'ai verifie la presence des fichiers, je les ai rendus
executables, puis j'ai converti les fins de ligne Windows vers Linux :
```bash
cd /root/TP_Hadoop/wordcount
ls
chmod +x wc_mapper_improved.py
chmod +x wc_reducer_improved.py
dos2unix wc_mapper_improved.py
dos2unix wc_reducer_improved.py
```

### Multiplication de deux grandes matrices (generation)
Je me suis place dans le repertoire `~/TP_Hadoop/matrice` et j'ai lance le
script `matrice.py`. Il genere deux matrices (matriceA et matriceB), les enregistre
dans `matriceA.txt` et `matriceB.txt`, puis affiche leur produit. Les
dimensions observees sont **20x10** et **10x15**, donc un produit **20x15**.
```bash
cd ~/TP_Hadoop/matrice
python matrice.py
```

J'ai obtenu l'affichage suivant :
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

J'ai ensuite depose ces fichiers sur HDFS dans le repertoire `input` :
```bash
hadoop fs -put matriceA.txt input
hadoop fs -put matriceB.txt input
```

### Multiplication de deux grandes matrices (MapReduce)
J'ai ecrit un mapper et un reducer pour calculer le produit matriciel a partir
de `matriceA.txt` et `matriceB.txt`. Le mapper identifie la matrice (A ou B) via
le nom du fichier, puis emet des paires pour chaque cellule cible `(i,j)`. Le
reducer regroupe ces valeurs et somme les produits sur l'indice `k`.

Les scripts utilises sont `matrice_mapper.py` et `matrice_reducer.py`. Les
dimensions par defaut correspondent aux matrices generees (A: 20x10, B: 10x15),
et peuvent etre adaptees via `A_ROWS`, `A_COLS`, `B_COLS`.
```bash
hadoop jar $STREAMINGJAR -cmdenv A_ROWS=20 -cmdenv A_COLS=10 -cmdenv B_COLS=15 \
  -files matrice_mapper.py,matrice_reducer.py \
  -mapper "python matrice_mapper.py" -reducer "python matrice_reducer.py" \
  -input input/matriceA.txt,input/matriceB.txt -output sortie_matrice
```

J'ai obtenu le resultat suivant sous HDFS (extrait) :
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
Je conclus que le traitement MapReduce fonctionne correctement sur un corpus
volumineux. Le tri des donnees avant reduction est indispensable pour agreger
les comptes par mot.

<div style="page-break-after: always;"></div>

## Hadoop MapReduce avec MrJob
J'ai utilise la librairie **MrJob** dans le dossier `TP-Big-Data-HadoopMrjob`
pour tester un wordcount en mode local avant la suite.

### Etape 1 - Test local (MrJob)
J'ai execute la commande suivante en local :
```powershell
Get-Content .\dracula.txt | py .\wc_mrjob_1.py | Set-Content .\resultInline.txt
```

J'ai obtenu le fichier `resultInline.txt` dans le dossier du TP.

J'ai extrait cet exemple depuis `resultInline.txt` :
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

### Test MrJob sur le cluster Hadoop
J'ai ensuite lance le meme wordcount sur le cluster Hadoop avec le runner
`-r hadoop`, en lecture depuis STDIN puis depuis HDFS.

J'ai utilise les commandes suivantes :
```bash
python wc_mrjob_1.py -r hadoop < dracula > resultHadoop.txt
python wc_mrjob_1.py -r hadoop hdfs:///user/root/input/dracula > resultHadoop.txt
```

J'ai observe l'extrait suivant (job soumis et termine) :
```text
Running job: job_1768916694477_0003
map 100% reduce 100%
Job job_1768916694477_0003 completed successfully
The url to track the job: http://hadoop-master:8088/proxy/application_1768916694477_0003/
```

### Exercice 1 - Questionner un fichier de ventes
J'ai analyse un gros fichier de ventes pour produire des statistiques. J'ai
utilise `purchases.txt` (plus de 4 000 000 lignes) et un extrait
`purchases_10000.txt` pour des tests rapides. Le fichier est tabule et contient
6 colonnes : date (YYYY-MM-DD), heure (hh:mm), ville, categorie d'achat (Book,
Men's Clothing, DVDs, etc.), somme depensee et moyen de paiement (Amex, Cash,
MasterCard, etc.).

J'ai place les fichiers dans `TP-Big-Data-HadoopMrjob/ventes`. Chaque question
est implemente dans un script MRJob distinct pour garder une trace claire des
traitements.

J'ai traite les analyses suivantes : nombre d'achats par categorie, somme
totale depensee par categorie, depense a San Francisco par moyen de paiement,
ville la plus rentable en Cash pour la categorie Women's Clothing, puis une
requete originale multi-step pour aller au-dela des agregations simples.

Pour structurer ce travail, j'ai associe chaque question a un script MRJob
distinct place dans `TP-Big-Data-HadoopMrjob/ventes` : `count_by_category.py`,
`sum_by_category.py`, `sf_by_payment.py`, `womens_cash_top_city.py`. La requete
originale multi-step est `top_cities_by_sales.py`, qui classe les villes par
chiffre d'affaires et ressort un top 5 par defaut (parametrable).

Dans `count_by_category.py`, j'extrais la categorie et j'emets `(categorie, 1)`.
Le reducer additionne ces valeurs pour obtenir le nombre d'achats par categorie.

Dans `sum_by_category.py`, j'emets `(categorie, montant)` et je somme les
montants pour produire le chiffre d'affaires total par categorie.

Dans `sf_by_payment.py`, je filtre les lignes de la ville "San Francisco" puis
je regroupe les montants par moyen de paiement.

Dans `womens_cash_top_city.py`, je filtre la categorie "Women's Clothing" avec
paiement "Cash", j'agrege par ville, puis je compare les totaux pour garder la
ville la plus rentable sur ce segment.

Dans `top_cities_by_sales.py`, je calcule le chiffre d'affaires par ville puis
je conserve les N villes les plus rentables (top 5 par defaut).

J'ai obtenu les resultats suivants (extraits, `purchases_10000.txt`) :
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
J'ai ecrit un script MapReduce pour detecter les mots qui partagent exactement
les memes lettres (ordre different). Je ne garde que les groupes avec au moins
2 mots et je ne tiens pas compte des voyelles accentuees.

Exemple attendu :
```text
faible, fiable
arbre, barre
devenir, deviner
lemon, melon
```

Pour des tests plus intensifs, j'ai utilise `words_alpha` (anglais) dans le
dossier `TP-Big-Data-HadoopMrjob/anagramme`.

J'ai code le script `TP-Big-Data-HadoopMrjob/anagramme/anagramme.py`. Mon mapper
lit les mots (un par ligne ou separes par des virgules), passe en minuscules,
puis neutralise les accents sur les voyelles avant de calculer une signature
(lettres triees). Mon reducer regroupe les mots ayant la meme signature,
elimine les doublons, puis n'affiche que les groupes de taille superieure ou
egale a 2.
