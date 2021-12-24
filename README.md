# Documentatie[^1] - Flow Free Game Solver 
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

## Generare de puzzle-uri[^2]
### @author: Antonio M.

Pentru a se genera puzzle-urile s-a creat un script folosind limbajul python "screen_scan.py" care:
- va crea folderul "puzzles" daca acesta nu exista deja, daca exista va ignora acest pas si va continua sa adauge fisiere de tip json in el
- utilizatorul va trebui apoi sa introduca numele pachetului din care fac parte puzzle-urile pe care vrea sa le salveze
- utlizatorul acestui scrip va fi intrebat ce dimensiune au acest tip de puzzle pe care vrea sa le converteasca in json
- utilizatorul va trebui apoi sa pozitioneze cursorul peste butonul "next" (pentru a putea fi salvate coordonatele acestuia)
- utilizatorul va introduce cate puzzle-uri vrea sa obtina
- pentru fiecare puzzle se va crea un nou fisier json in care se vor pune culorile pentru fiecare "casuta" din puzzle
- daca inca nu s-a atins numarul cerut de puzzle-uri atunci se va da click automat pe butonul de next folosind coordonatele[^3]

----------------------------------------------------------------
## Caracteristicile jocului Flow Free[^4]

Flow Free este un joc bazat in jurul rezolvarii unui puzzle: arata ca o matrice cu dimensiuni de n x n pe care se afla mai multe perechi de cate 2 puncte colorate. Scopul jocului si al acestui proiect este rezolvarea unor astfel de puzzle-uri astfel incat:
- toate punctele de aceeasi culoare sa fie unite de un singur drum neintrerupt de alte drumuri
- toate drumurile sa ocupe toate spatiile de pe tabla afisata

![image](https://user-images.githubusercontent.com/72747266/147162193-f0e8206a-c073-407f-b3ff-206b84f2bca2.png)

Un prim pas de rezolvare, indiferent de algoritmul folosit, este sa decidem cu care culoare incepem algoritmul. Cel mai eficient este sa incepem cu acele culori care au cele mai putine optiuni de deplasare.

Dupa mai mult research si analiza in mediul online a acestui tip de puzzle am ajuns la concluzia ca 2 posibili algoritmi de rezolvare care ar fi foarte eficienti sunt reducerea problemei la SAT si folosirea unei euristici cu A*. 

Euristici aplicabile pot fi folosind algoritmul lui Djikstra, BFS, DFS, etc. 

Un alt algoritm care ar putea rezolva acest tip de problema este backtracking, dar pentru ca el genereaza si incearca toate posibilitatile pana o gaseste pe cea corecta putem deduce ca nu este eficient ca timp.

----------------------------------------------------------------

## Reducere la SAT[^5]
### @author: Antonio M. , Andra C.

Problema SAT[^6] este problema de a determina daca exista macar o formula din logica booleana care poate fi interpretata astfel incat cel putin odata aceasta sa rezulte TRUE.

Reamintim Forma Normala Conjunctiva (FNC): mai multe disjunctii unite prin conjunctie. Exemplu: ![image](https://user-images.githubusercontent.com/72747266/147168402-95e6e443-2576-428c-92a8-3cf2416b064a.png)

### Reducerea FlowFree la SAT

Pentru a face aceasta reducere vom avea nevoie de FNC pentru ca vom lua fiecare constrangere/cerinta si o vom scrie sub forma de logica booleana respectand FNC.

Pentru a putea demonstra ca acest tip de puzzle poate fi rezolvat cu SAT, mai intai vom face cateva notatii:

- puzzle-ul este de dimensiunea `n x n` => vom avea ![equation](http://www.sciweavers.org/tex2img.php?eq=%20n%5E%7B2%7D%20&bc=Black&fc=White&im=jpg&fs=12&ff=arev&edit=0) patratele
- numarul de culori il vom nota cu `c`
- directiile posibile sunt:
  - sus-jos &emsp; &emsp; &emsp; &emsp; │
  - jos-sus &emsp; &emsp; &emsp; &emsp; │
  - stanga-dreapta  &emsp; ─
  - dreapta-stanga  &emsp; ─
  - sus-stanga &emsp; &emsp; &nbsp;&nbsp; ┘
  - sus-dreapta &emsp; &emsp; └
  - jos-stanga &emsp; &emsp; &nbsp;&nbsp;&nbsp; ┐
  - jos-dreapta &emsp; &emsp;&nbsp; ┌

#### 1. Fiecare patratel are o culoare a sa
- avem `n*n*c` posibilitati de colorare
- fie `i` id-ul patratelelor `(1 <= i <= n*n)`
- avem `c*(c-1)/2` combinatii posibile de culori pentru fiecare patratel care nu este deja colorat de o bulina de start/stop
- pentru cateva patratele avem deja stabilita culoarea deoarece acelea vor fi bulinele de start/stop; pentru un astfel de patrat `i` putem scrie urmatoarea clauza: ![image](https://user-images.githubusercontent.com/72747266/147306787-a288e5b7-7c15-4c9a-9ebe-7476a64346d1.png)
- pentru restul patratelelor pentru care nu au deja culoarea prestabilita putem scrie urmatoarea clauza (pentru un patratel `i`): ![image](https://user-images.githubusercontent.com/72747266/147306585-1ad476b1-8478-4939-a2b0-e9a6016e6630.png)
- fiecare din clauzele de mai sus vin de la: ![image](https://user-images.githubusercontent.com/72747266/147306465-cc62799a-2a17-42d1-8165-e01c777828b6.png) , unde `u` si `u'` sunt doua culori diferite pentru patratelul `i` (in formulele prezentate mai sus aceasta clauza este negata deoarece am adus clauza la forma normala conjunctiva)

#### 2. Fiecare bulina de start/inceput are exact un vecin (drum) cu aceeasi culoare
- fiecare patratel cu bulina de start/stop va avea exact un singur vecin cu drum (cu aceeasi culoare)
- presupunem un patratel cu bulina de start/stop `i` care are culoarea `m` si cei 4 vecini corespunzatori cu punctele cardinale (N,S,E,V) `s, t, u, v`
- pentru ca patratelul `i` are culoarea `m`, atunci putem scrie clauza: ![image](https://user-images.githubusercontent.com/72747266/147349647-0579c2ca-2cc7-47ee-a6c6-44f6a0983b57.png)
- in plus, oricare 2 vecini ai patratelului `i` nu pot avea aceeasi culoare
  - pentru a compara daca 2 patrate au aceeasi culoare putem scrie clauza: ![image](https://user-images.githubusercontent.com/72747266/147349787-9f490b95-1c8c-4d58-aa2c-ec049c1e635b.png)
  - insa pe noi ne intereseaza ca atunci cand 2 patrate au aceeasi culoare sa obtinem rezultatul clauzei FALSE (asa cum e scrisa mai sus clauza, daca 2 patrate au aceeasi culaore returneaza TRUE); pentru a obtine asta va trebui sa negam clauza anterioara, deci vom obtine clauza: ![image](https://user-images.githubusercontent.com/72747266/147350002-dd871b5a-6e3f-40db-8cb0-6f0527339fd4.png)
  - clauza de mai sus este scrisa pentru exemplul dintre patratele `s` si `t` cu culoarea `m`, insa aceeasi clauza se aplica pentru toate combinatiile de cate 2 patrate din `s, t, u, v` cu culoarea `m`: `s si t`, `s si u`, `s si v`, `t si u`, `t si v`, `u si v`
  - nu are rost sa comapram `s si t` si `t si s` deoarece operatiile ^ si v sunt comutative, deci vom obtine practic aceeasi clauza

#### 3. Culoarea bulinelor de start/stop sunt stiute
- putem asigna instant acelor patratele culoarea lor
- deasemenea putem sa eliminam restul culorilor ca o posibilitate pentru patratelul respectiv
- inainte de rezolvarea jocului trebuie sa avem un numar par de patratele ale caror culori le cunoastem, iar numarul lor sa fie dublul numarului de culori

#### 4. Directia drumurilor in casutele care nu sunt buline de start/stop sunt in numar de 8: sus, jos, stanga, dreapta, sus-stanga, sus-dreapta, jos-stanga, jos-dreapta
- fiecare patratel care nu contine o bulina de start/stop va contine, in rezolvarea finala, va avea o singura directie care va indica cu care dintre vecinii sai formeaza un drum
  - faptul ca acest tip de patratel va contine macar o directie poate fi scris ca o clauza pentru fiecare astfel de patratel
  - faptul ca acest tip de patratel nu poate contine mai mult de o singura directie poate fi scris ca `2*nr_directii = 2*8 = 16 clauze` pentru fiecare patratel (daca cele 16 clauze sunt indeplinite atunci este indeplinita si clauza de la subpunctul anterior)
- doua astfel de patratele vecine unite prin directiile pe care le contin vor avea aceeasi culoare
- un astfel de patratel poate avea doar 2 vecini de aceeasi culoare (fie 2 patrate cu directie, fie unul cu directie si unul cu bulina start/stop, fie ambii cu bulina start/stop) 
- toate directiile de aceeas culoare formeaza un drum; drumul trebuie sa inceapa si sa se termine in patratelele cu bulina de aceeasi culoare
- reamintim directiile posibile si cum vor fi aceastea notate:
    - sus-jos &emsp; &emsp; &emsp; &emsp; │
    - jos-sus &emsp; &emsp; &emsp; &emsp; │
    - stanga-dreapta  &emsp; ─
    - dreapta-stanga  &emsp; ─
    - sus-stanga &emsp; &emsp; &nbsp;&nbsp; ┘
    - sus-dreapta &emsp; &emsp; └
    - jos-stanga &emsp; &emsp; &nbsp;&nbsp;&nbsp; ┐
    - jos-dreapta &emsp; &emsp;&nbsp; ┌

#### 5. Vecinul patratelului curent aflat in directia pe care acesta o indica tebuie sa fie de aceeasi culoare
- fiecare patratel trebuie considerat ca o punte intre altele 2, de aceeasi directia pe care o vor contine patratele va simboliza de fapt care 2 patratele vecine le uneste
- pentru orice patratel `i` pe care avem directia `d` vom avea 2 vecini `s si t` care trebuie sa aiba aceeasi culoare ca si patratul `i`
- presupunand ca patratelul `i` are culoarea `m` atunci vom obtine clauza: ![image](https://user-images.githubusercontent.com/72747266/147350782-79ce7488-e3db-4533-bfc3-1f9c7319628a.png)
- pentru ca nu putem traduce acea clauza intr-o secventa de cod asa cum am scris-o mai sus va trebui sa aducem aceasta clauza in forma ei normala conjunctiva
  - clauza de mai sus scrisa in FNC va produce 4 clauze:  
    ![image](https://user-images.githubusercontent.com/72747266/147351220-fcc03cc4-5331-4712-becd-9ef4a90cf3a8.png)

#### 6. Vecinii patratelului curent aflat in oricare alta directie decat cea pe care acesta o indica tebuie sa fie de alta culoare
- toti vecinii ramasi neconectati de drumul din patratel trebuie sa aiba orice alta culoare in afara de culoarea patratelului
- aceasta regula previne ca un drum sa se intercaleze cu el insusi la un moment dat
- pentru un patrat `i` cu directia `d` si culoarea `m`, orice vecin `s` care nu e indicat de directia `d` nu poate avea culoarea `m`: ![image](https://user-images.githubusercontent.com/72747266/147359857-810bd592-ad5f-4dea-8f08-6ec563d0b035.png)
  - formula de mai sus trebuie adusa si ea in FNC si obtinem clauza: ![image](https://user-images.githubusercontent.com/72747266/147359910-df08ba9a-1c7c-49d2-8020-9c929497a76c.png)

Aplicand aceste reguli pe un puzzle cu `n*n` patratele si `c` culori obtinem `n*n*c` variabile pentru culori si aproape `8*n*n` variabile pentru directii (include si patratelele cu buline de start/stop). Vom avea `O(n*n*c*c)` clauze pentru culori si inca `O(n*n*c)` clauze pentru legaturile dintre culori si directii.

Aceste constrangeri ne ofera cel mai scurt si rapid drum pe care il poate gasi ceea ce poate duce la patratele libere ramase care vor fi umplute cu drumuri. Din experienta obtinuta prin rezolvatul manual al astfel de puzzle-uri am observat ca atunci cand se intampla sa fie extra patratele acestea vor avea un numar par atat pe orizontala cat si pe verticala deoarece trebuie sa ofere posibilitatea de a crea drumuri prin ele. Pentru ca vom avea un numar par de patratee libere vecine si pe orizontala si pe verticala inseamna ca algoritmul acesta ba produce niste cicluri care nu contin buline de start/stop.

![image](https://user-images.githubusercontent.com/72747266/147171137-65b30bb2-2473-4bc2-a3cb-ec9233a07404.png)

Pentru a evita aceste scenarii se mai poate adauga o verificare la solutia finala unde cautam daca exista drumuri astfel incat sa se formeze un ciclu. Exemplu: dreapta-jos, stanga-jos, stanga-sus, dreapta sus: 

┌  ┐  
└  ┘

![image](https://user-images.githubusercontent.com/72747266/147171167-66d05ad3-11b7-4aed-bba7-c2671b0eaf21.png)

Problema SAT are in general, in cel mai rau scenariu, un numar exponential de varabile, deci o complexitate exponentiala. Problema SAT a fost deja demonstrata ca fiind NP-completa, dar in anumite situatii ea poate fi redusa la un timp polinomial, deci incadrata ca o problema P-completa.

### Implementare

a = trebuie sa traduc notitele de pe foaie si sa le formulez frumos
To be continued soon . . .


----------------------------------------------------------------

## A*
### @author: Carina M. , Cosmin R.


----------------------------------------------------------------

## Rapoarte finale de analiza. Compararea celor doua implementari
### @author: Andra C. , 

Este clar ca cei doi algoritmi abordeaza diferit acest subiect, deci se vor obtine pasi diferiti, deci timpi diferiti de rezolvare. Dar pentru a obtine pasi diferiti si codul va fi diferit, deci si acesta poate fi un criteriu de comparatie intre cele doua implementari.

#### 1. Eficienta - timp rezolvare

#### 2. Dimensiunea si nivelul de dificultate al codului

----------------------------------------------------------------

##### Resurse si alte link-uri utile:

[^1]: [sintaxa fisierelor .md](https://docs.github.com/en/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) and many more stack**overflow** pages

[^2]: [code](https://github.com/cosminrotariu/Flow_Game/blob/main/screen_scan.py)

[^3]: [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)

[^4]: [FlowFree](https://en.wikipedia.org/wiki/Flow_Free)

[^5]: [code](https://github.com/cosminrotariu/Flow_Game/blob/main/sat_solver.py)

[^6]: [SAT](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem)
