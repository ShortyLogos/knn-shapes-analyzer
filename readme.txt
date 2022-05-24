Travail présenté par:
- Jean-Christophe Caron
- Samuel Horvath
- Déric Marchand
- Karl Robillard Marchand

Ce projet consiste à analyser des images et déterminer leurs formes respectives à partir des concepts suivants :
+ On analyse des images de "training" avec 3 métriques d'analyse au moyen de la classe ShapeAnalyzer.
+ Notre analyse génère ainsi un ensembe à 3 dimensions.
+ Par la suite, lorsqu'on doit analyser une image qui ne fait pas partie du "training data", on détermine la distance la plus courte
entre ce nouveau point analysé et un ensemble de points du "training data" (les voisins) pour déterminer sa forme. En d'autres mots,
nous faisons appel à l'algorithme de classification KNN.

Nos 3 descripteurs de forme sont :

1-Le ratio "beigne" (donut ratio): Le ratio entre le rayon inscrit et le rayon circonscrit.
2-Ratio de pixels sur le périmetre: On prend la distance entre le centroide et le pixel le plus éloigné à partir de lui, pour ensuite pour ensuite compter tous les pixel qui en font parti
et normaliser le résultat selon le ratio d'un cercle.
3-L'index de complexité : Il s'agit de l'aire de la forme divisée par son périmetre à la puissance de deux.

Plus précisément, ce laboratoire permet de mettre en pratique les notions suivantes :
- Principe d'encapsulation de la programmation OOJ (ShapeAnalyzer)
- Importance de la modularité du code (KNN générique)
- Puissance de calcul de la librairie numpy
- Manipuler une base de données externe (dump)
- Réaliser une interface d'utilisateur pertinente
- Développer une classe d'analyse d'image
- Implémenter un algorithme générique de KNN


Un effort d'abstraction a été fait pour ces éléments :
Généricité du KNN (en majeure partie)
ShapeAnalyzer

Finalement, l’ensemble de données le plus complexe que nous avons été capable de résoudre est:
Zoo Large !
