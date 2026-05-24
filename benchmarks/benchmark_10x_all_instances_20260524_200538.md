# Benchmark Results - 10x ACO per Parameter Combination + 1x Local Search per Instance

- Timeout per run: `120s`
- Time budget per instance: `300s` for easier instances, `900s` for larger instances
- Policy: 3 parameter combinations, 10 runs each (30 total ACO runs), then local search once on best ACO run

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| youtube_gold.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| youtube_premium.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
| us_iptv.json | 0 | 0.0 | 0 | ants=2, iter=3 | 0 | - |
