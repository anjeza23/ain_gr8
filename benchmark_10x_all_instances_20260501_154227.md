# Benchmark Results - 10x ACO + 1x Local Search per Instance

- Timeout per run: `25s`
- Time budget per instance: `300s`
- Policy: 10 ACO runs (different parameters), then local search once on best ACO run

| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |
|---|---:|---:|---:|---|---:|---:|
| usa_tv_input.json | 2019 | 1925.0 | 1831 | ants=6, iter=12 | 2019 | - |
