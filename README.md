# Flow Free Game Solver
## Artificial Intelligence, 3rd year, FII
### @authors: Coteanu Andra, Marele Carina, Mihaes Antonio, Rotariu Cosmin (grupa 3A4)

----------------------------------------------------------------
### Cerinta

Un agent care rezolva puzzle-ul Flow.
- Flow are loc pe o grila 2D cu n linii și m coloane.
- Fiecare puzzle are un număr de C culori.
- In starea initiala sunt 2 * C pozitii colorate, cate doua pentru fiecare culoare.
- Scopul este sa conectati pozițiile de aceeași culoare.
- Drumurile care fac legăturile sunt formate din segmente paralele cu axele.
- Drumurile nu se pot intersecta.
- Este preferabil sa puteți procesa o imagine a unei stări inițiale din Flow pentru a construi datele de intrare.
- Legături relevante:
https://www.microsoft.com/de-de/p/flow-free/9wzdncrdqvpj

----------------------------------------------------------------

## Generare de puzzle-uri
### @author: Antonio M.

Pentru a se genera puzzle-urile s-a creat un script folosind limbajul python "screen_scan.py" care:
- va crea folderul "puzzles" daca acesta nu exista deja, daca exista va ignora acest pas si va continua sa adauge fisiere de tip json in el
- utilizatorul va trebui apoi sa introduca numele pachetului din care fac parte puzzle-urile pe care vrea sa le salveze
- utlizatorul acestui scrip va fi intrebat ce dimensiune au acest tip de puzzle pe care vrea sa le converteasca in json
- utilizatorul va trebui apoi sa pozitioneze cursorul peste butonul "next" (pentru a putea fi salvate coordonatele acestuia)
- utilizatorul va introduce cate puzzle-uri vrea sa obtina
- pentru fiecare puzzle se va crea un nou fisier json in care se vor pune culorile pentru fiecare "casuta" din puzzle
- daca inca nu s-a atins numarul cerut de puzzle-uri atunci se va da click automat pe butonul de next folosind coordonatele

----------------------------------------------------------------

Dupa mai mult research si analiza in mediul online a acestui tip de puzzle am ajuns la concluzia ca 2 posibili algoritmi de rezolvare care ar fi foarte eficienti sunt reducerea problemei la SAT si folosirea unei euristici cu A*. 

Euristici aplicabile pot fi folosind algoritmul lui Djikstra, BFS, DFS, etc. 

Un alt algoritm care ar putea rezolva acest tip de problema este backtracking, dar pentru ca el genereaza si incearca toate posibilitatile pana o gaseste pe cea corecta putem deduce ca nu este eficient ca timp.

----------------------------------------------------------------

## Reducere la SAT
### @author: Antonio M. , Andra C.

----------------------------------------------------------------

## A*
### @author: Carina M. , Cosmin R.

