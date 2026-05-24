# Benchmark Results - 10x ACO + 1x Local Search per Instance

- Timeout per run: `25s`
- Time budget per instance: `300s`
- Policy: 10 ACO runs (different parameters), then local search once on best ACO run

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| croatia_tv_input.json | 1822 | 1530.3 | 1190 | ants=18, iter=60 | 1822 | 0 |
| germany_tv_input.json | 1456 | 1377.9 | 1325 | ants=12, iter=50 | 1456 | 0 |
| kosovo_tv_input.json | 2414 | 2251.9 | 2134 | ants=35, iter=90 | 2414 | 0 |
| netherlands_tv_input.json | 2256 | 2166.1 | 2051 | ants=20, iter=50 | 2256 | 0 |
| uk_tv_input.json | 633 | 417.3 | 265 | ants=12, iter=50 | 633 | 0 |
| usa_tv_input.json | 0 | 0.0 | 0 | ants=10, iter=30 | 0 | 0 |
