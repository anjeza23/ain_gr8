"""
Run 10 ACO executions per instance, then 1 local-search run on best ACO state.
Generates JSON + Markdown tables ready for README.
"""

import json
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List


class BenchmarkExecutor:
    """Benchmark all input instances except toy.json."""

    ACO_TESTS = [
        {"ants": 10, "iterations": 30},
        {"ants": 15, "iterations": 40},
        {"ants": 20, "iterations": 50},
        {"ants": 25, "iterations": 60},
        {"ants": 30, "iterations": 70},
        {"ants": 12, "iterations": 50},
        {"ants": 18, "iterations": 60},
        {"ants": 22, "iterations": 70},
        {"ants": 28, "iterations": 80},
        {"ants": 35, "iterations": 90},
    ]
    USA_ACO_TESTS = [
        {"ants": 5, "iterations": 10},
        {"ants": 6, "iterations": 12},
        {"ants": 7, "iterations": 12},
        {"ants": 8, "iterations": 15},
        {"ants": 10, "iterations": 15},
        {"ants": 5, "iterations": 20},
        {"ants": 8, "iterations": 20},
        {"ants": 10, "iterations": 20},
        {"ants": 12, "iterations": 20},
        {"ants": 15, "iterations": 20},
    ]
    LARGE_ACO_TESTS = [
        {"ants": 2, "iterations": 3},
        {"ants": 2, "iterations": 4},
        {"ants": 3, "iterations": 3},
        {"ants": 3, "iterations": 4},
        {"ants": 3, "iterations": 5},
        {"ants": 4, "iterations": 3},
        {"ants": 4, "iterations": 4},
        {"ants": 5, "iterations": 3},
        {"ants": 5, "iterations": 4},
        {"ants": 6, "iterations": 3},
    ]

    def __init__(self, timeout_seconds: int = 25, instance_budget_seconds: int = 300):
        self.timeout_seconds = timeout_seconds
        self.instance_budget_seconds = instance_budget_seconds
        self.results: Dict[str, object] = {
            "timestamp": datetime.now().isoformat(),
            "timeout_seconds_per_run": timeout_seconds,
            "instance_budget_seconds": instance_budget_seconds,
            "instances": [],
        }

    @staticmethod
    def _extract_score(stdout: str) -> int:
        for line in stdout.splitlines():
            if "Generated solution with total score" in line:
                try:
                    return int(line.split(":")[-1].strip())
                except ValueError:
                    return 0
        return 0

    @staticmethod
    def _extract_local_final_score(stdout: str) -> int:
        # Local Search logs: [Local Search] Zgjidhje përfundimtare: <score>
        for line in stdout.splitlines():
            if "Zgjidhje përfundimtare" in line:
                try:
                    return int(line.split(":")[-1].strip())
                except ValueError:
                    continue
        return 0

    def _run_single_aco(self, input_path: str, run_id: int, params: Dict[str, int]) -> Dict[str, object]:
        cmd = [
            "python",
            "main.py",
            "--input",
            input_path,
            "--algorithm",
            "aco",
            "--ants",
            str(params["ants"]),
            "--iterations",
            str(params["iterations"]),
            "--seed",
            str(run_id),
        ]

        start = time.time()
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            elapsed = time.time() - start
            score = self._extract_score(completed.stdout)
            return {
                "run": run_id,
                "params": params,
                "score": score,
                "time_sec": elapsed,
                "timeout": False,
                "ok": score > 0 and completed.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "run": run_id,
                "params": params,
                "score": 0,
                "time_sec": self.timeout_seconds,
                "timeout": True,
                "ok": False,
            }

    def _run_local_search_once(
        self,
        input_path: str,
        best_aco: Dict[str, object],
    ) -> Dict[str, object]:
        seed = int(best_aco["run"])
        ants = int(best_aco["params"]["ants"])
        iterations = int(best_aco["params"]["iterations"])
        aco_score = int(best_aco["score"])

        cmd = [
            "python",
            "main.py",
            "--input",
            input_path,
            "--algorithm",
            "aco",
            "--ants",
            str(ants),
            "--iterations",
            str(iterations),
            "--seed",
            str(seed),
            "--local-search",
        ]

        start = time.time()
        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
            )
            elapsed = time.time() - start

            initial_score = self._extract_score(completed.stdout) or aco_score
            final_score = self._extract_local_final_score(completed.stdout)
            if final_score == 0:
                final_score = initial_score

            return {
                "ok": completed.returncode == 0,
                "params": {"ants": ants, "iterations": iterations, "seed": seed},
                "initial_aco_score": initial_score,
                "local_search_score": final_score,
                "improvement": final_score - initial_score,
                "time_sec": elapsed,
                "timeout": False,
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "params": {"ants": ants, "iterations": iterations, "seed": seed},
                "initial_aco_score": aco_score,
                "local_search_score": aco_score,
                "improvement": 0,
                "time_sec": self.timeout_seconds,
                "timeout": True,
            }

    def _instance_files(self, group: str = "tv") -> List[Path]:
        all_inputs = sorted(Path("data/input").glob("*.json"))
        if group == "large":
            return [p for p in all_inputs if not p.name.endswith("_tv_input.json") and p.name != "toy.json"]
        if group == "all":
            return [p for p in all_inputs if p.name != "toy.json"]
        return [p for p in all_inputs if p.name.endswith("_tv_input.json") and p.name != "toy.json"]

    def _tests_for_instance(self, instance_name: str) -> List[Dict[str, int]]:
        if instance_name == "usa_tv_input.json":
            return self.USA_ACO_TESTS
        if (
            instance_name.endswith("_iptv.json")
            or instance_name.endswith("_pw.json")
            or instance_name.startswith("youtube_")
        ):
            return self.LARGE_ACO_TESTS
        return self.ACO_TESTS

    def run_all(self, only_instance: str = "", group: str = "tv") -> Dict[str, object]:
        instances = self._instance_files(group=group)
        if only_instance:
            instances = [p for p in instances if p.name == only_instance]
        print(f"Running benchmark for {len(instances)} instances (excluding toy.json)")

        for instance_path in instances:
            print(f"\n{'=' * 90}")
            print(f"INSTANCE: {instance_path.name}")
            print(f"{'=' * 90}")

            tests = self._tests_for_instance(instance_path.name)
            runs = []
            for idx, params in enumerate(tests, start=1):
                result = self._run_single_aco(str(instance_path), idx, params)
                runs.append(result)
                status = "TIMEOUT" if result["timeout"] else ("OK" if result["ok"] else "FAIL")
                print(
                    f"[{idx:02d}/10] ants={params['ants']:2d} iter={params['iterations']:3d} "
                    f"-> score={result['score']:5d} time={result['time_sec']:.2f}s {status}"
                , flush=True)

            valid_runs = [r for r in runs if r["ok"]]
            if valid_runs:
                best_aco = sorted(valid_runs, key=lambda x: (-int(x["score"]), float(x["time_sec"])))[0]
                avg_score = sum(int(r["score"]) for r in valid_runs) / len(valid_runs)
                worst_score = min(int(r["score"]) for r in valid_runs)
            else:
                best_aco = {"run": 1, "params": tests[0], "score": 0, "time_sec": self.timeout_seconds}
                avg_score = 0.0
                worst_score = 0

            instance_elapsed = sum(float(r["time_sec"]) for r in runs)
            if instance_elapsed >= self.instance_budget_seconds:
                ls_result = {
                    "ok": False,
                    "params": {
                        "ants": best_aco["params"]["ants"],
                        "iterations": best_aco["params"]["iterations"],
                        "seed": best_aco["run"],
                    },
                    "initial_aco_score": int(best_aco["score"]),
                    "local_search_score": int(best_aco["score"]),
                    "improvement": 0,
                    "time_sec": 0.0,
                    "timeout": False,
                    "skipped_reason": "instance_budget_exceeded_before_local_search",
                }
            else:
                ls_result = self._run_local_search_once(str(instance_path), best_aco)

            instance_result = {
                "instance": instance_path.name,
                "aco_runs": runs,
                "aco_best": best_aco,
                "aco_avg_score": avg_score,
                "aco_worst_score": worst_score,
                "aco_successful_runs": len(valid_runs),
                "local_search": ls_result,
            }
            self.results["instances"].append(instance_result)

            print(
                f"BEST ACO: score={best_aco['score']} (ants={best_aco['params']['ants']}, "
                f"iter={best_aco['params']['iterations']}, run={best_aco['run']})"
            )
            print(
                f"LOCAL SEARCH: final={ls_result['local_search_score']} "
                f"improvement={ls_result['improvement']} time={ls_result['time_sec']:.2f}s"
            )

        return self.results

    def save_outputs(self) -> Dict[str, str]:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_path = Path(f"benchmark_10x_all_instances_{timestamp}.json")
        md_path = Path(f"benchmark_10x_all_instances_{timestamp}.md")

        with json_path.open("w", encoding="utf-8") as fp:
            json.dump(self.results, fp, indent=2, ensure_ascii=False)

        md_content = self._build_markdown_report()
        md_path.write_text(md_content, encoding="utf-8")

        return {"json": str(json_path), "markdown": str(md_path)}

    def _build_markdown_report(self) -> str:
        lines: List[str] = []
        lines.append("# Benchmark Results - 10x ACO + 1x Local Search per Instance")
        lines.append("")
        lines.append(f"- Timeout per run: `{self.timeout_seconds}s`")
        lines.append(f"- Time budget per instance: `{self.instance_budget_seconds}s`")
        lines.append("- Policy: 10 ACO runs (different parameters), then local search once on best ACO run")
        lines.append("")
        lines.append("| Instance | ACO Best | ACO Avg | ACO Worst | Best Params | LS Final | LS Improvement |")
        lines.append("|---|---:|---:|---:|---|---:|---:|")

        for item in self.results["instances"]:
            best = item["aco_best"]
            ls = item["local_search"]
            best_params = f"ants={best['params']['ants']}, iter={best['params']['iterations']}"
            improvement_display = ls["improvement"] if ls["improvement"] > 0 else "-"
            lines.append(
                f"| {item['instance']} | {best['score']} | {item['aco_avg_score']:.1f} | "
                f"{item['aco_worst_score']} | {best_params} | {ls['local_search_score']} | {improvement_display} |"
            )

        lines.append("")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run 10x ACO tests + 1x Local Search")
    parser.add_argument("--instance", default="", help="Run only one instance file name (e.g. usa_tv_input.json)")
    parser.add_argument("--group", choices=["tv", "large", "all"], default="tv",
                        help="Instance group to benchmark")
    args = parser.parse_args()

    executor = BenchmarkExecutor(timeout_seconds=25, instance_budget_seconds=300)
    executor.run_all(only_instance=args.instance.strip(), group=args.group)
    output_paths = executor.save_outputs()
    print("\nSaved files:")
    print(f"- JSON: {output_paths['json']}")
    print(f"- Markdown: {output_paths['markdown']}")


if __name__ == "__main__":
    main()
