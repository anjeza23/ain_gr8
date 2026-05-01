# Benchmark Results - 10x ACO + 1x Local Search per Instance

- Timeout per run: `25s`
- Time budget per instance: `300s`
- Policy: 10 ACO runs (different parameters), then local search once on best ACO run

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
