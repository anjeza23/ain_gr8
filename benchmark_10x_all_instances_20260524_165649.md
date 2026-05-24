# Benchmark Results - 10x ACO per Parameter Combination + 1x Local Search per Instance

- Timeout per run: `25s`
- Time budget per instance: `300s` for easier instances, `900s` for larger instances
- Policy: 3 parameter combinations, 10 runs each (30 total ACO runs), then local search once on best ACO run

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
