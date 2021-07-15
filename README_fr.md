# ASM battle

Ce programme est pour moi le résultat d'un vieux rêve. 
Celui de créer une arène pour explorer (légalement) la rencontre d'apprentis pirates informatiques. 

## Le jeu
Chaque joueur soumet au jeu un programme dans un langage assembleur simplifié. Chacun d'eux est
assemblé et chargé dans sa propre région en mémoire, puis se voit assigné un processeur virtuel.
Chaque espace mémoire et chaque caractère de l'écran écrit durant la partie compte pour un point.

Un micro BIOS fournit une table de branchement pour le lancement de processeur et une fonction 
d'impression de textes terminés par un caractère "null" (00). À vous de la trouver. À titre d'indice, 
le programme Hello World s'en sert.

Ceci est une version très préliminaire. Les améliorations seront apportées sur la base des commentaires
des utilisateurs.

## Marque de reconnaissance
Ce projet est basé sur : « _Simple 8-bit Assembler Simulator_ » par Marco Schweighauser (2015). https://schweigi.github.io/assembler-simulator/ 


_Michel_, 5 juillet 2021

https://www.michelrondeau.com
