# QUICKSTART - PARAMETRI TUNING DHE BENCHMARKING

## Fillim i Shpejtë (5 minuta)

### 1. Ekzekuto algoritmin bazik
```bash
# Me default parameters
python3 main.py --input data/input/toy.json
```

### 2. Me Local Search
```bash
# Merr zgjidhjen më të mirë dhe e përmirëson më tutje
python3 main.py --input data/input/toy.json --local-search
```

### 3. Matje performancës (10 ekzekutime)
```bash
# Testuese ndryshueshmërinë në 10 ekzekutime
python3 utils/benchmark.py --input data/input/toy.json --executions 10
```

---

## Punë e Thellë - Parameter Tuning

### Hapi 1: Identifikimi i Parametrave Optimal

#### ACO Tuning
```bash
# Testuese kombinacione të ants dhe iterations
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm aco --runs 3
```

Parametrat e testuar:
- Ants: 10, 15, 20, 25, 30
- Iterations: 30, 50, 70

Shembull rezultati:
```
TOP 5 KONFIGURACIONET:
1. Max Score: 880
   ants: 25
   iterations: 70
   avg_score: 850.50
   avg_time: 12.34

2. Max Score: 870
   ants: 20
   iterations: 50
   avg_score: 840.32
   avg_time: 9.87
...
```

#### Beam Search Tuning
```bash
# Testuese kombinacione të beam_width dhe lookahead
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm beam --runs 3
```

Parametrat e testuar:
- Beam Width: 50, 100, 150
- Lookahead: 2, 4, 6

### Hapi 2: Ekzekutim me Parametrat Optimal

Pasi të grurpsosh parametrat më të mirë:

```bash
# Perdor parametrat optimal te ACO
python3 main.py --input data/input/toy.json --ants 25 --iterations 70

# Me Local Search
python3 main.py --input data/input/toy.json --ants 25 --iterations 70 --local-search
```

### Hapi 3: Benchmarking me Parametrat Optimal

```bash
# 10 ekzekutime me parametrat optimal
python3 utils/benchmark.py --input data/input/toy.json --executions 10
```

---

## Plotësimi i Plotë - Workflow për Një Instance

### Sekvenca e Rekomanduar:

```bash
# 1. HAPI 1: TUNING (10-15 minuta)
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm aco --runs 5

# 2. HAPI 2: ANALIZA (lexo rezultatet, zgjidh 2-3 më të mirë)
# Rezultatet janë në: tuning_results_XXXXXXXX.json

# 3. HAPI 3: BENCHMARK (15-20 minuta)
python3 utils/benchmark.py --input data/input/toy.json --executions 10 --timeout 300

# 4. HAPI 4: PRODUCTION RUN me parametrat optimal
python3 main.py --input data/input/toy.json --ants 25 --iterations 70 --local-search
```

---

## Shembull Seneriu

### Skenario 1: Instance e vogël (toy.json)

```bash
# 1. Tuning i pozë
python3 utils/parameter_tuner.py --input data/input/toy.json --algorithm aco --runs 3

# 2. Parametrat optimal të gjetura: ants=20, iterations=50
# 3. Benchmark me këto parametra
python3 utils/benchmark.py --input data/input/toy.json --executions 10

# 4. Production
python3 main.py --input data/input/toy.json --ants 20 --iterations 50 --local-search
```

### Skenario 2: Instance më e madhe (usa_tv_input.json)

```bash
# 1. Tuning me më shumë iterations
python3 utils/parameter_tuner.py --input data/input/usa_tv_input.json --algorithm aco --runs 3

# Parametrat optimal të gjetura: ants=30, iterations=100

# 2. Benchmark
python3 utils/benchmark.py --input data/input/usa_tv_input.json --executions 5 --timeout 600

# 3. Production run
python3 main.py --input data/input/usa_tv_input.json --ants 30 --iterations 100 --local-search --ls-iterations 150
```

---

## Interpretimi i Rezultateve

### Benchmark Results File

Output per çdo algoritëm përfshin:

```json
{
  "aco": {
    "best_score": 850,          // Pikpë më të mirë të gjetura
    "worst_score": 720,         // Pikë më të këqija
    "avg_score": 792.5,         // Mesatarja
    "executions": [             // Detaje për çdo ekzekutim
      {
        "execution": 1,
        "score": 850,
        "time": 12.34
      }
    ]
  }
}
```

### Cka do të këtohen:

```
- Best score (Pikë më të mirë): Zgjidhja më e mirë e gjetura (për krahasim)
- Avg score (Mesatarja): Cilësia mesatare e algoritmit
- Zeit (Koha): Sa zgjat algoritmi (importante për deadline-t)
```

### Përmirësim nga Local Search:

Prisni përmirësim tipik:
- ACO: +2% deri +8% mejorësim
- Beam Search: +1% deri +5% mejorësim

Nëse nuk ka përmirësim, çekoni:
1. Nëse zgjidhja fillestare është e prë-optimizuar?
2. Nëse iterations për local search janë të mjaftueshme?

---

## Tips dhe Tricks

### 1. Koha e Computimit
- Ants 10-20: Më shpejtë, më pak i saktë
- Ants 20-30: Balansim më i mirë
- Ants 30+: Më i saktë, më i ngadalshëm

### 2. Për Instanca të Mëdha
```bash
# I shpejtë por më pak i plotë
python3 main.py --ants 15 --iterations 30

# Balansim
python3 main.py --ants 20 --iterations 50

# Kompleks dhe koha e rëndësishme
python3 main.py --ants 30 --iterations 100 --local-search
```

### 3. Reproducibility
Përdorni `--seed` për rezultate reproducible:
```bash
python3 main.py --input data/input/toy.json --seed 42
```

### 4. Debug Mode
Për të parë detaje të algoritmit:
```bash
# Zbukimi i verbose output (modifiko `verbose=True` në kod)
python3 main.py --input data/input/toy.json
```

---

## Fajlla të Prodhuar

### Pas Benchmark:
```
benchmark_results_20260430_125034.json
```

### Pas Parameter Tuning:
```
tuning_results_20260430_123056.json
```

### Pas Main Execution:
```
data/output/toy_output_antcolonyscheduler_380.json
```

---

## Kontakt dhe Ndihmë

Nëse keni pyetje:
1. Lexoni `README.md` për dokumentacion të plotë
2. Shikoni `example_*.json` në `data/input/`
3. Kontaktoni profesorin ose asistentin
