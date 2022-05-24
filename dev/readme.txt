Travail présenté par:
- Jean-Christophe Caron
- Samuel Horvath
- Déric Marchand
- Karl Robillard Marchand

Il consiste à analyser des images et déterminer leur forme avec les concepts suivants :
-On analyse des images de "training" avec 3 de nos paramètres.
-Notre analyse génère des coordonnées à 3 dimensions.
-Par la suite, lorsqu'on doit analyser une image qui ne fait pas partie du "training", on trouve la distance la plus courte
entre ce nouveau point analysé et nos points de "training" pour déterminer sa forme.

Nos 3 descripteurs de forme sont :

1-Le ratio "beigne":  le ratio du rayon entre le centroide et le pixel le plus petit de celui-ci et le rayon de celui le plus loin.

2-Le nombre de pixel sur le périmetre:  on prend la distance entre le centroide et le pixel le plus loin sur la forme pour ensuite compter tous les pixel qui en font parti.

3-L'index de complexité : c'est l'aire de la forme divisé par son périmetre à la puissance de deux.

Plus précisément, ce laboratoire permet de mettre en pratique les notions de :
Le principe d'encapsulation et de modularité du code
Numpy
Acceder à des données d'une base de donnée
Réaliser une interface d'utilisateur
Implementer un algorithme générique d'analyse d'image


Un effort d'abstraction a été fait pour ces points :
Le Knn
Le shapeanalyzer
Finalement, l’ensemble de données le plus complexe que nous avons été capable de résoudre est:
Zoo Large
