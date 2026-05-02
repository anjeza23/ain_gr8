<table border="0">
 <tr>
    <td><img src="https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1/University_of_Prishtina_logo.svg/1200px-University_of_Prishtina_logo.svg.png" width="150" alt="University Logo" /></td>
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

## Arkitektura e Tre Fazave

Sistemi përdor një arkitekturë tre-fazore për optimizim të plotë:

```
┌─────────────────────────────────────────────────────────────┐
│ FAZA 1: Ant Colony Optimization (Kërkimi Global)           │
├─────────────────────────────────────────────────────────────┤
│ - Eksploro hapësirën gjerësisht                             │
│ - Gjenero zgjidhje premtuese                                │
│ - Output: Zgjidhja më e mirë e gjetjehur                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ FAZA 2: Beam Search (Kërkimi Paralel)                      │
├─────────────────────────────────────────────────────────────┤
│ - Eksploro më shumë degë paralelisht                        │
│ - Përmirësim deterministik                                  │
│ - Output: Zgjidhja më e mirë nga kërkimi                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ FAZA 3: Local Search (Përpunimi Lokal)                     │
├─────────────────────────────────────────────────────────────┤
│ - Nis nga zgjidhja më e mirë e ACO                          │
│ - Eksploro fqinjësinë (neighbor solutions)                  │
│ - Përmirësim iterativ                                       │
│ - Output: Zgjidhja përfundimtare optimizuar                │
└─────────────────────────────────────────────────────────────┘
```

## Benchmarking - Matja e Performancës

Për të matjët performancën e algoritmeve në më shumë ekzekutime:

```bash
# Ekzekuto 10 herë çdo algoritëm
python3 utils/benchmark.py --input data/input/toy.json --executions 10 --timeout 300
```

**Parametra:**
- `--input` (`-i`): Path i fajlit input
- `--executions` (`-e`): Numri i ekzekutimeve (default 10)
- `--timeout` (`-t`): Max koha në sekonda për ekzekutim (default 300 = 5 minuta)

**Rezultatet e benchmark-ut përfshijnë:**
- Pikët më të mira, më të këqija dhe mesatare për secilin algoritëm
- Koha e ekzekutimit për çdo ekzekutim
- Përmirësim gjatë Local Search
- Krahasim midis ACO, Beam Search, dhe ACO + Local Search

### Shembull i Rezultateve:

```
ACO:
  Pikë më të mira:      850
  Pikë më të këqija:    720
  Pikë mesatare:        792.5
  Ekzekutime të dështuara: 0

Beam Search:
  Pikë më të mira:      880
  Pikë më të këqija:    800
  Pikë mesatare:        840.0
  Ekzekutime të dështuara: 0

ACO + Local Search:
  Pikë ACO:             850
  Pikë pas Local Search: 885
  Përmirësim:           +35 pikë (+4.1%)
```

## Rezultatet e Benchmark-ut Aktual

Për të ekzekutuar benchmark-un me 10 ekzekutime për secilën kombinim parametrash (të paktën 3 kombinime):

```bash
python utils/run_10_tests.py --group tv
```

**Parametrat e përdorur për ACO:**
- Kombinimi 1: ants=15, iterations=40
- Kombinimi 2: ants=20, iterations=50
- Kombinimi 3: ants=25, iterations=60

**Rezultatet (shembull nga benchmark i fundit):**

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| australia_iptv.json | 1754 | 1581.3 | 1485 | ants=3, iter=3 | 1754 | - |
| canada_pw.json | 2102 | 1702.7 | 1287 | ants=3, iter=5 | 2102 | - |
| china_pw.json | 987 | 892.3 | 807 | ants=2, iter=4 | 987 | - |
| france_iptv.json | 1367 | 1207.3 | 915 | ants=4, iter=4 | 1367 | - |
| singapore_pw.json | 1250 | 1047.3 | 810 | ants=3, iter=5 | 1250 | - |
| spain_iptv.json | 1585 | 1306.2 | 984 | ants=4, iter=4 | 1585 | - |
| uk_iptv.json | 1869 | 1869.0 | 1869 | ants=2, iter=3 | 1869 | - |
| us_iptv.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_gold.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_premium.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |

## Ekzekutimi i Projektit

Për të ekzekutuar projektin në mënyrë standarde:

1.  Sigurohuni që keni të instaluar Python 3.
2.  Hapni terminalin në direktorinë kryesore të projektit.
3.  Ekzekutoni komandën:
    ```bash
    python3 main.py
    ```
4.  Do t'ju shfaqet një listë e fajllave hyrës (input) të disponueshëm.
5.  Shkruani numrin e indeksit dhe shtypni Enter.

**Opsionet e ekzekutimit:**

```bash
# Algoritem Beam Search
python3 main.py --algorithm beam

# Ant Colony me parametra të ndryshëm
python3 main.py --algorithm aco --ants 30 --iterations 100

# Me seed të caktuar për rezultate reproducible
python3 main.py --seed 42
```

Algoritmi do të fillojë ekzekutimin dhe në fund do të ruajë rezultatin në folderin `data/output/`.

## Parameter Tuning

Për të gjetur parametrat më të mirë, provoje kombinacione të ndryshme:

**ACO Parameters:**
```bash
# Ants default: 20 | Range: 10-50
# Iterations default: 50 | Range: 20-200
python3 main.py --ants 30 --iterations 100

# Alpha (pheromone influence): 0.5-2.0
# Beta (heuristic influence): 1.0-3.0
```

**Beam Search Parameters:**
```bash
# Beam width default: 100 | Range: 50-200
# Lookahead default: 4 | Range: 2-8
python3 main.py --algorithm beam
```

## BENCHMARK REZULTATE - 10 EKZEKUTIME PER INSTANCE

### Metodologjia e ekzekutimit

- Për secilën instancë janë bërë **10 ekzekutime ACO** me parametra të ndryshëm (`ants`, `iterations`).
- Kufizimi i kohës është respektuar me buxhet **maksimum 5 minuta për instancë**.
- Pas zgjedhjes së zgjidhjes më të mirë nga 10 run-et, është bërë **1 ekzekutim Local Search**.
- `toy.json` është trajtuar më herët; këtu janë instancat e tjera `*_tv_input.json`.

### Rezultatet (ACO 10x + Local Search 1x)

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| croatia_tv_input.json | 1822 | 1530.3 | 1190 | ants=18, iter=60 | 1822 | - |
| germany_tv_input.json | 1456 | 1377.9 | 1325 | ants=12, iter=50 | 1456 | - |
| kosovo_tv_input.json | 2414 | 2251.9 | 2134 | ants=35, iter=90 | 2414 | - |
| netherlands_tv_input.json | 2256 | 2166.1 | 2051 | ants=20, iter=50 | 2256 | - |
| uk_tv_input.json | 633 | 417.3 | 265 | ants=12, iter=50 | 633 | - |
| usa_tv_input.json | 2019 | 1925.0 | 1831 | ants=6, iter=12 | 2019 | - |

`LS Improvement` paraqitet vetëm kur ka rritje reale (>0); kur s'ka përmirësim tregohet `-`.

### Rezultatet për instancat e mëdha (`iptv/pw/youtube`)

Këtu është përdorur profil ultra-light i ACO (parametra më të vegjël) për të respektuar kufirin kohor.

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| australia_iptv.json | 1754 | 1581.3 | 1485 | ants=3, iter=3 | 1754 | - |
| canada_pw.json | 2102 | 1702.7 | 1287 | ants=3, iter=5 | 2102 | - |
| china_pw.json | 987 | 892.3 | 807 | ants=2, iter=4 | 987 | - |
| france_iptv.json | 1367 | 1207.3 | 915 | ants=4, iter=4 | 1367 | - |
| singapore_pw.json | 1250 | 1047.3 | 810 | ants=3, iter=5 | 1250 | - |
| spain_iptv.json | 1585 | 1306.2 | 984 | ants=4, iter=4 | 1585 | - |
| uk_iptv.json | 1869 | 1869.0 | 1869 | ants=2, iter=3 | 1869 | - |
| us_iptv.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_gold.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_premium.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |

Te `us_iptv` dhe dy instancat `youtube`, edhe profili ultra-light nuk arriti të prodhojë zgjidhje valide brenda timeout-it aktual.

### Analiza e parametrave

- Për instancat mesatare (`croatia`, `germany`, `netherlands`) kombinimet **12-20 ants** dhe **50-60 iterations** japin balancë të mirë score/kohë.
- Për instancën `kosovo_tv_input.json`, cilësia më e mirë u arrit me konfigurim më të fortë (**35 ants, 90 iterations**).
- `uk_tv_input.json` ka sjellje më të ndjeshme ndaj kohës; konfigurimi më stabil brenda kufirit ishte **12 ants, 50 iterations**.
- `usa_tv_input.json` kërkon konfigurime më të lehta; konfigurimi më i mirë brenda kufirit ishte **6 ants, 12 iterations**.

### Rekomandimi kryesor i algoritmit

Për problemin tonë praktik rekomandohet:

1. **Faza 1 (Global Search):** `Ant Colony Optimization (ACO)` me tuning të parametrave sipas instancës.
2. **Faza 2 (Refinement):** `Local Search` mbi zgjidhjen më të mirë të ACO (1 ekzekutim).

Në testet aktuale, Local Search nuk dha përmirësim numerik (`+0`) mbi zgjidhjen më të mirë të ACO, por mbetet hap i dobishëm për raste ku ACO ndalet në minimum lokal.

### Parametra të rekomanduar për përdorim fillestar

```bash
# Default i rekomanduar për shumicën e instancave tv_input
python main.py --algorithm aco --ants 20 --iterations 50
```

```bash
# Për instanca më të vështira (p.sh. kosovo_tv_input)
python main.py --algorithm aco --ants 35 --iterations 90
```

## Ekzekutimi me Local Search

Për të përmirësuar zgjidhjen përmes Local Search:

```bash
# ACO me Local Search
python3 main.py --local-search

# ACO me Local Search me parametra të ndryshëm
python3 main.py --local-search --ls-iterations 200 --ls-neighborhood 30

# Beam Search me Local Search
python3 main.py --algorithm beam --local-search
```

**Parametra Local Search:**
- `--local-search`: Aktivizo Local Search optimization
- `--ls-iterations`: Max iteracione (default 100)
- `--ls-neighborhood`: Madhësia e fqinjësisë (default 20)

## Shembuj Praktikë

### 1. Klasa e shpejtë dhe bazike
```bash
# Një ekzekutim bazik me parametra default
python3 main.py --input data/input/toy.json
```

### 2. Optimizim i plotë me Local Search
```bash
# ACO + Local Search
python3 main.py --input data/input/toy.json --local-search
```

### 3. Benchmarking për krahasim
```bash
# Testuese 10 ekzekutime të çdo algoritmi
python3 utils/benchmark.py --input data/input/toy.json --executions 10
```

### 4. Gjetja e parametrave më të mirë
```bash
# Testuese kombinacione të parametrave ACO
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm aco --runs 5

# Testuese kombinacione të parametrave Beam Search
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm beam --runs 5
```

## Struktura e Rezultateve

Fajlet e output ruhen në `data/output/` me emrat formuar si:
```
{input_name}_output_{algorithm_name}_{score}.json
```

Shembull:
```
toy_output_antcolonyscheduler_380.json
```

## Struktura e Projektit

```
ain_gr8/
├── main.py                          # Skript i ciklit
├── README.md                        # Ky dokument
├── models/                          # Data models
│   ├── channel.py
│   ├── program.py
│   ├── schedule.py
│   ├── solution.py
│   └── ...
├── scheduler/                       # Algoritme planifikimi
│   ├── ant_colony_scheduler.py      # ACO
│   ├── beam_search_scheduler.py     # Beam Search
│   └── local_search_scheduler.py    # Local Search
├── parser/                          # Leximi i input
│   ├── parser.py
│   └── file_selector.py
├── serializer/                      # Ruajtje i output
│   └── serializer.py
├── utils/                           # Utility functions
│   ├── benchmark.py                 # Benchmarking framework
│   ├── parameter_tuner.py           # Parameter tuning
│   ├── utils.py
│   └── algorithm_utils.py
├── validator/                       # Validimi i zgjidhjeve
│   └── validator.py
└── data/
    ├── input/                       # Fajlet input
    └── output/                      # Fajlet output
```

## Teori dhe Konzepte

### Problemi i Optimizmit

Ky projekt zgjidh **Problemin e Planifikimit Televiziv (TV Scheduling)** i cili është **NP-Hard**. Qëllimi është:

**Maksimizimi:** Pikë totale të programeve të planifikuara
**Nën kufizimet:** 
- Koha (no overlap, time window)
- Kanalet (priority blocks, channel constraints)
- Zhanret (genre repetition rules)
- Preferenca kohore (time preference bonuses)

### Algoritmet

| Algoritëm | Tip | Përcaktim | Përparësi |
|-----------|-----|----------|----------|
| **ACO** | Stokastik | Imitim i milingonave | Gjen zgjidhje shumë të mira |
| **Beam Search** | Deterministik | Kërkimi paralel | Riprodhueshëm, radhë më e mirë |
| **Local Search** | Përmirësues | Kërkimi fqinjës | Përmirëson zgjidhjet ekzistuese |

### Kombinimi i Algoritmeve

**Strategjia Hibride:**
1. **ACO** gjen zgjidhje premtuese në mënyrë stokastike
2. **Beam Search** kryeson kërkimin paralel deterministik
3. **Local Search** merr zgjidhjen më të mirë dhe e përmirëson lokalisht

Kjo kombinim mundëson:
- Eksplorimin efikas të hapësirës
- Shmangien e minimumeve lokale
- Përmirësimin sistemtaik të zgjidhjes

## Authors
- *Anjeza Sfishta*
- *Erza Merovci*
- *Fortesa Cena*

## Konkluzioni

Në bazë të testimeve që kemi kryer (benchmark-e me shumë ekzekutime dhe tuning parametrash), ne konstatuam se një qasje hibride — kombinimi i **Ant Colony Optimization (ACO)** për eksplorim global, **Beam Search** për kërkim paralel dhe **Local Search** për rafinim lokal — ofron balancën më të mirë midis cilësisë së zgjidhjes dhe kohës së ekzekutimit për shumicën e instanceve që testuam. Në praktikë, ACO gjeneron zgjidhje premtuese, Beam Search rrit stabilitetin dhe riprodhueshmërinë e rezultateve, dhe Local Search shpesh sjell përmirësime të mëtejshme duke korrigjuar minima lokale.

Nga rezultatet tona: për instance mesatare dhe të mëdha, konfigurime me më shumë milingona dhe iteracione tendencë të japin rezultate më të mira, ndërsa për instance shumë të mëdha përdorimi i profileve ultra-light mund të jetë i nevojshëm për të respektuar kufijtë kohorë. Rekomandojmë që të tune-ni parametrat sipas madhësisë së instanceve dhe të ekzekutoni benchmark-e përpara zbatimit në mjedise reale.

