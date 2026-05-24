<table border="0">
 <tr>
    <td><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/University_of_Prishtina_logo.svg/500px-University_of_Prishtina_logo.svg.png" width="150" alt="University Logo" /></td>
    <td>
      <p>Universiteti i Prishtinës</p>
      <p>Fakulteti i Inxhinierisë Elektrike dhe Kompjuterike</p>
      <p>Inxhinieri Kompjuterike dhe Softuerike - Programi Master</p>
      <p>Profesor: Prof. Dr. Kadri Sylejmani</p>
      <p>Asistent: MSc. Labeat Arbneshi</p>
    </td>
 </tr>
</table>


## Përshkrimi i Projektit: Optimizimi i Orarit Televiziv

Ky projekt adreson **Problemin e Planifikimit Televiziv për Hapësira Publike** (TV Channel Scheduling Optimization for Public Spaces) në kuadër të lëndës **Algoritmet e Avancuara**. Objektivi primar është përzgjedhja dhe planifikimi optimal i një nënbashkësie të programeve televizive në kanale të shumta, me qëllim maksimizimin e pikëve totale të shikueshmërisë.

**Kufizimet dhe Qëllimet Kryesore:**

Përveç kufizimeve bazë kohore, problemi përfshin rregulla specifike për të siguruar një përvojë cilësore shikimi:

*   **Time Window Constraint:** Programet duhet të planifikohen strikt brenda intervalit kohor global të përcaktuar (Hapja dhe Mbyllja).
*   **No Overlap Constraint:** Ndalohet rreptësisht mbivendosja kohore e programeve në të njëjtin kanal.
*   **Minimum Duration:** Programet duhet të kenë një kohëzgjatje minimale për t'u konsideruar të vlefshme.
*   **Genre Repetition:** Për të siguruar shumëllojshmëri, ka një kufizim në numrin e programeve të njëpasnjëshme të të njëjtit zhanër.
*   **Priority Blocks:** Blloqe kohore specifike ku vetëm kanale të caktuara kanë prioritet ose lejohen të transmetojnë.
*   **Time Preferences:** Bonuse pikësh për transmetimin e zhanreve të caktuara në orare të preferuara.
*   **Optimization Goal:** Maksimizimi i funksionit objektiv, duke balancuar pikët e programeve me penalitetet e mundshme.

## Beam Search Scheduler

 **Beam Search Scheduler**, është një algoritëm **deterministik** që tejkalon kufizimet e qasjeve standarde **Greedy** përmes eksplorimit paralel të hapësirës së zgjidhjeve.

**Metodologjia:**

1.  **Beam Search Strategy:** Në vend të ndjekjes së një rruge të vetme, algoritmi mirëmban një bashkësi prej $N$ zgjidhjesh të pjesshme më premtuese në çdo hap (**Beam Width**). Kjo mundëson shmangien e minimumeve lokale dhe rikuperimin nga vendimet sub-optimale të hershme.
2.  **Lookahead Mechanism:** Përtej vlerësimit të menjëhershëm, algoritmi implementon një mekanizëm **Lookahead** me thellësi të konfiguruar. Kjo analizon impaktin e vendimeve aktuale në mundësitë e ardhshme, duke parandaluar bllokimin e programeve me vlerë të lartë.
3.  **Density Heuristic:** Për vlerësimin e potencialit të intervaleve kohore të mbetura, përdoret një heuristikë e bazuar në dendësinë e pikëve (pikë/minutë).

**Konfigurimi i Parametrave:**
*   **Beam Width:** 100. Ruan 100 degëzimet më të mira të pemës së kërkimit në çdo iteracion.
*   **Lookahead:** 4 hapa. Vlerëson pasojat e vendimeve deri në 4 nivele thellësi.
*   **Density Percentile:** Fokusohet në 25% të programeve më të mira për vlerësim heuristik)

Ky kombinim i eksplorimit **Beam Search** dhe heuristikave të avancuara **Lookahead** mundëson gjetjen e zgjidhjeve të cilësisë së lartë në mënyrë efikase.

## Ant Colony Optimization (ACO) Scheduler

**Ant Colony Optimization**, është një algoritëm **stokastik** që imiton sjelljen e milingonave që kërkojnë ushqim.

**Metodologjia:**

1.  **Pheromone-based Search:** Algoritmi mirëmban një rrjetë feromonesh që përfaqeson cilësinë e vendimeve të mëparshme. Milingonave kanë gjasë më të larta të zgjedhin rrugë me feromon më të lartë.
2.  **Stochastic Construction:** Çdo milingonë ndërton një zgjidhje në mënyrë stokastike, duke balancuar eksplorimin e rastit me shfrytëzimin e rrugëve të mira.
3.  **Pheromone Update:** Pas çdo iteracioni, feromonet azhurnohen bazuar në cilësinë e zgjidhjeve të gjetura. Feromonet më të larta për vendime më të mira, më të ulëta për vendime më të këqija (evaporim).

**Konfigurimi i Parametrave:**
*   **Ants (milingona):** 20. Numri i zgjidhjeve të ndërtuara paralelisht në çdo iteracion.
*   **Iterations:** 50. Numri i iteracioneve të optimizmit.
*   **Alpha:** 1.0. Peshë për influencën e feromoneve në zgjedhje.
*   **Beta:** 2.0. Peshë për influencën e cilësisë heuristike.
*   **Evaporation:** 0.15. Sasia e feromoneve që avaporohen në çdo iteracion.
*   **Q0:** 0.2. Probabiliteti i eksploitimit ndaj eksplorimit.

**Përparësi ACO:**
- Gjen zgjidhje shumë të mira për problemet komplekse
- Kapërcen minimume lokale përmes stokasticitetit
- Paralelizim natyror përmes milingonave

## Local Search Optimizer

**Local Search**, është një faza e dytë optimizimi që përmirëson zgjidhjen më të mirë të gjetjehur asogna fazës së parë.

**Metodologjia:**

1.  **Neighborhood Exploration:** Duke nisur nga zgjidhja më e mirë e ACO, algoritmi eksploro zgjidhjet e afërta (fqinjës):
   - **Move Neighborhood:** Zhvendosja e një programi në kohë ose kanal tjetër
   - **Random Restart:** Nëse bllokohemi në minimum lokal, provoje kërkime të reja

2.  **Hill Climbing:** Pranojmë çdo përmirësim, edhe i vogël, dhe vazhdojmë kërkimin derisa nuk ka më përmirësime.

3.  **Termination Criteria:** Ndalojmë kur:
   - Arrihet maksimumi i iteracioneve
   - Nuk ka përmirësim për shumë iteracione të radhës
   - Arrihet një pikë objektivi

**Përparësi Local Search:**
- Përmirëson zgjidhjet ekzistuese në mënyrë sistematike
- Shpejtëzi e mirë pasi fillon nga zgjidhje e mirë
- Thjeshtësi në implementim dhe kontroll


## Benchmarking - Matja e Performancës

Për të matur performancën e algoritmeve në më shumë ekzekutime:

**Parametra:**
- `--input` (`-i`): Path i fajlit input
- `--executions` (`-e`): Numri i ekzekutimeve (default 10)
- `--timeout` (`-t`): Max koha në sekonda për ekzekutim (default 300 = 5 minuta)

**Rezultatet e benchmark-ut përfshijnë:**
- Pikët më të mira, më të këqija dhe mesatare për secilin algoritëm
- Koha e ekzekutimit për çdo ekzekutim
- Përmirësim gjatë Local Search
- Krahasim midis ACO, Beam Search, dhe ACO + Local Search



## Rezultatet e Benchmark-ut Aktual

Për të ekzekutuar benchmark-un me 10 ekzekutime për secilën kombinim parametrash (të paktën 3 kombinime):

```bash
python utils/run_10_tests.py
```

Ky script ekzekuton të gjitha instancat në `data/input/` (përjashton `toy.json`) në rendin e lehtë deri në të vështirë, bazuar në madhësinë e skedarit.


### Rregulla të ekzekutimit
- Për instancat më të vogla, bëhet `10x` ACO dhe pastaj 1x Local Search në zgjidhjen më të mirë të ACO.
- Për instancat e mëdha, përdoret kohë buxhet deri në 15 minuta për instancë.
- Local Search merr zgjidhjen më të mirë të ACO dhe përpiqet të përmirësojë atë përmes levizjeve të programeve dhe ricalimit të pikëve.

### Rezultate dhe analiza
- Local Search është projektuar të punojë mbi zgjidhjen më të mirë të ACO dhe të përmirësojë rezultatet nëse një vendosje alternative ul penalitetet ose rrit përfitimet.
- Në testet tona, për kombinimet standarde të ACO, modeli që mbajti më mirë balancën score/kohë ishte `ants=20, iterations=50` për instancat mesatare.
- Instancat shumë të mëdha shpesh lehtësohen nga profilet më të lehta të ACO (`ants=2..4`, `iterations=3..5`) për të respektuar kufirin kohor dhe më pas të rafinohen me Local Search.

## BENCHMARK REZULTATE - 10 EKZEKUTIME PER INSTANCE

### Metodologjia e ekzekutimit

- Për secilën instancë janë bërë **10 ekzekutime ACO** me parametra të ndryshëm (`ants`, `iterations`).
- Kufizimi i kohës është respektuar me buxhet **maksimum 5 minuta për instancë**.
-Rezultatet e fundit jane ruajtur ne C:\Users\HP\ain_gr8\benchmark_10x_all_instances_20260524_165649.json

### Rezultatet (ACO 10x + Local Search 1x)

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| germany_tv_input.json | 1456 | 1378.3 | 1324 | ants=15, iter=40 | 1921 | 465 |
| kosovo_tv_input.json | 2428 | 2262.7 | 2127 | ants=20, iter=50 | 2969 | 541 |
| netherlands_tv_input.json | 2404 | 2158.7 | 1990 | ants=25, iter=60 | 2989 | 585 |
| croatia_tv_input.json | 1922 | 1603.2 | 1167 | ants=25, iter=60 | 2207 | 285 |
| uk_tv_input.json | 1397 | 596.9 | 129 | ants=25, iter=60 | 1397 | - |
| singapore_pw.json | 1523 | 1131.2 | 810 | ants=4, iter=5 | 2129 | 606 |
| spain_iptv.json | 1780 | 1345.2 | 979 | ants=3, iter=4 | 2545 | 765 |
| france_iptv.json | 1525 | 1161.5 | 915 | ants=4, iter=5 | 2111 | 586 |
| australia_iptv.json | 1969 | 1639.8 | 1401 | ants=4, iter=5 | 2427 | 458 |
| canada_pw.json | 2102 | 1651.8 | 1287 | ants=2, iter=3 | 2843 | 741 |
| uk_iptv.json | 1869 | 1566.2 | 1235 | ants=2, iter=3 | 2478 | 609 |
| usa_tv_input.json | 2515 | 2030.4 | 1494 | ants=6, iter=12 | 2755 | 240 |
| china_pw.json | 1256 | 999.6 | 753 | ants=3, iter=4 | 2241 | 985 |
| youtube_gold.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_premium.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| us_iptv.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |

Ky tabelë përdor të dhënat reale të benchmark-ut të plotë: 10 run-e ACO për secilën instancë dhe një ekzekutim Local Search mbi zgjidhjen më të mirë ACO.

### Analiza e parametrave

- Në instancat `germany_tv_input.json`, `kosovo_tv_input.json`, `netherlands_tv_input.json`, dhe `croatia_tv_input.json`, Local Search sjell përmirësime të konsiderueshme mbi ACO.
- `uk_tv_input.json` nuk përfitoi nga Local Search në këtë konfigurim, pasi zgjidhja më e mirë ACO ishte tashmë e mirë e optimizuar.
- Në grupin `*_pw.json` dhe `*_iptv.json`, ACO me parametra të lehtë (`ants=2-4`, `iterations=3-5`) jep zgjidhje të vlefshme brenda buxhetit të kohës, dhe Local Search rrit rezultatet në mënyrë domethënëse.
- `youtube_gold.json`, `youtube_premium.json`, dhe `us_iptv.json` nuk prodhuan zgjidhje valide me timeout-in standard (25s). I kemi rikthyer këto tre instanca me timeout të rritur në `120s` për çdo ACO run (30 run-e totale) dhe Local Search.

- **Rezultati i ekzekutimit me `--timeout 120 --instances youtube_gold.json,youtube_premium.json,us_iptv.json`:**
  - Edhe me `timeout=120s` për çdo run, këto instanca përfunduan me `score=0` (best ACO = 0).

- **Përfundim:** Pavarësisht rritjes së timeout-it në 120s, këto tre instanca nuk arritën një zgjidhje valide.


### Rekomandimi kryesor i algoritmit

Për problemin tonë praktik rekomandohet:

1. **Faza 1 (Global Search):** `Ant Colony Optimization (ACO)` me tuning të parametrave sipas instancës.
2. **Faza 2 (Refinement):** `Local Search` mbi zgjidhjen më të mirë të ACO (1 ekzekutim).



## Konkluzioni

Në bazë të testimeve që kemi kryer (benchmark-e me shumë ekzekutime dhe tuning parametrash), ne konstatuam se një qasje hibride — kombinimi i **Ant Colony Optimization (ACO)** për eksplorim global, **Beam Search** për kërkim paralel dhe **Local Search** për rafinim lokal — ofron balancën më të mirë midis cilësisë së zgjidhjes dhe kohës së ekzekutimit për shumicën e instanceve që testuam. Në praktikë, ACO gjeneron zgjidhje premtuese, Beam Search rrit stabilitetin dhe riprodhueshmërinë e rezultateve, dhe Local Search shpesh sjell përmirësime të mëtejshme duke korrigjuar minima lokale.

Nga rezultatet tona: për instance mesatare dhe të mëdha, konfigurime me më shumë milingona dhe iteracione tendencë të japin rezultate më të mira, ndërsa për instance shumë të mëdha përdorimi i profileve ultra-light mund të jetë i nevojshëm për të respektuar kufijtë kohorë. Rekomandojmë që të tune-ni parametrat sipas madhësisë së instanceve dhe të ekzekutoni benchmark-e përpara zbatimit në mjedise reale.

## Authors
- *Anjeza Sfishta*
- *Erza Merovci*
- *Fortesa Cena*
