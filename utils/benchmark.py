"""
Benchmarking Framework - Metrikimi i performancës
Ekzekuton 10 herë çdo algoritëm me matje rezultatesh para dhe pas local search
"""

import json
import time
import sys
from typing import Dict, List, Tuple
from datetime import datetime
import os

from parser.parser import Parser
from scheduler.ant_colony_scheduler import AntColonyScheduler
from scheduler.beam_search_scheduler import BeamSearchScheduler
from scheduler.local_search_scheduler import LocalSearchScheduler
from serializer.serializer import SolutionSerializer
from utils.utils import Utils


class BenchmarkRunner:
    """Menaxhues për benchmark-e dhe matje"""
    
    def __init__(self, input_file: str, max_time_per_execution: int = 300):
        """
        Args:
            input_file: Path i fajlit input
            max_time_per_execution: Max sekonda për ekzekutim (default 5 minuta = 300 sekonda)
        """
        self.input_file = input_file
        self.max_time_per_execution = max_time_per_execution
        self.results = {
            "input_file": os.path.basename(input_file),
            "timestamp": datetime.now().isoformat(),
            "executions": []
        }
        
    def run_benchmark(self, num_executions: int = 10) -> Dict:
        """
        Kryej benchmark për algoritme të ndryshme
        
        Args:
            num_executions: Numri i ekzekutimeve (default 10)
        
        Returns:
            Rezultatet e benchmark-ut
        """
        print(f"\n{'='*70}")
        print(f"BENCHMARK: {os.path.basename(self.input_file)}")
        print(f"Ekzekutime: {num_executions} për algoritëm")
        print(f"Max kohë: {self.max_time_per_execution} sekonda per instance")
        print(f"{'='*70}\n")
        
        # Parse input file
        parser = Parser(self.input_file)
        instance = parser.parse()
        Utils.set_current_instance(instance)
        
        print(f"Kanalet: {len(instance.channels)}")
        print(f"Hapje: {instance.opening_time}, Mbyllje: {instance.closing_time}")
        print(f"Blloqet e prioritetit: {len(instance.priority_blocks)}\n")
        
        # Ant Colony Optimization
        print(f"\nFAZA 1: ANT COLONY OPTIMIZATION")
        print(f"-" * 70)
        aco_results = self._run_aco_executions(instance, num_executions)
        
        # Beam Search
        print(f"\nFAZA 2: BEAM SEARCH")
        print(f"-" * 70)
        beam_results = self._run_beam_executions(instance, num_executions)
        
        # Local Search (mbi zgjidhjen më të mirë të ACO)
        print(f"\nFAZA 3: LOCAL SEARCH (ACO + Local Search)")
        print(f"-" * 70)
        aco_local_results = self._run_aco_with_local_search(instance, aco_results["best_solution"])
        
        # Përmbledhje
        self._print_summary(aco_results, beam_results, aco_local_results)
        
        self.results["aco"] = aco_results
        self.results["beam"] = beam_results
        self.results["aco_with_local_search"] = aco_local_results
        
        return self.results
    
    def _run_aco_executions(self, instance, num_exec: int) -> Dict:
        """Kryej ekzekutime të ACO"""
        results = {
            "algorithm": "ACO",
            "executions": [],
            "scores": [],
            "times": [],
            "best_score": 0,
            "worst_score": float('inf'),
            "avg_score": 0,
            "best_solution": None,
            "failed_executions": 0
        }
        
        ants = 20
        iterations = 50
        
        print(f"Parametra: ants={ants}, iterations={iterations}")
        print(f"Ekzekuto {num_exec} herë...\n")
        
        for i in range(num_exec):
            print(f"  [{i+1}/{num_exec}] ", end="", flush=True)
            
            try:
                start_time = time.time()
                
                scheduler = AntColonyScheduler(
                    instance_data=instance,
                    ants=ants,
                    iterations=iterations,
                    verbose=False,
                    random_seed=None  # Përpara-rastësi
                )
                
                solution = scheduler.generate_solution()
                elapsed = time.time() - start_time
                
                if elapsed > self.max_time_per_execution:
                    print(f"TIMEOUT ({elapsed:.1f}s > {self.max_time_per_execution}s)")
                    results["failed_executions"] += 1
                    continue
                
                score = solution.total_score
                results["scores"].append(score)
                results["times"].append(elapsed)
                results["executions"].append({
                    "execution": i + 1,
                    "score": score,
                    "time": elapsed
                })
                
                if score > results["best_score"]:
                    results["best_score"] = score
                    results["best_solution"] = solution
                
                results["worst_score"] = min(results["worst_score"], score)
                
                print(f"Pikë: {score}, Kohë: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"GABIM: {str(e)}")
                results["failed_executions"] += 1
        
        if results["scores"]:
            results["avg_score"] = sum(results["scores"]) / len(results["scores"])
        
        return results
    
    def _run_beam_executions(self, instance, num_exec: int) -> Dict:
        """Kryej ekzekutime të Beam Search"""
        results = {
            "algorithm": "Beam Search",
            "executions": [],
            "scores": [],
            "times": [],
            "best_score": 0,
            "worst_score": float('inf'),
            "avg_score": 0,
            "best_solution": None,
            "failed_executions": 0
        }
        
        beam_width = 100
        lookahead = 4
        percentile = 25
        
        print(f"Parametra: beam_width={beam_width}, lookahead={lookahead}, percentile={percentile}")
        print(f"Ekzekuto {num_exec} herë...\n")
        
        for i in range(num_exec):
            print(f"  [{i+1}/{num_exec}] ", end="", flush=True)
            
            try:
                start_time = time.time()
                
                scheduler = BeamSearchScheduler(
                    instance_data=instance,
                    beam_width=beam_width,
                    lookahead_limit=lookahead,
                    density_percentile=percentile,
                    verbose=False,
                    random_seed=None
                )
                
                solution = scheduler.generate_solution()
                elapsed = time.time() - start_time
                
                if elapsed > self.max_time_per_execution:
                    print(f"TIMEOUT ({elapsed:.1f}s > {self.max_time_per_execution}s)")
                    results["failed_executions"] += 1
                    continue
                
                score = solution.total_score
                results["scores"].append(score)
                results["times"].append(elapsed)
                results["executions"].append({
                    "execution": i + 1,
                    "score": score,
                    "time": elapsed
                })
                
                if score > results["best_score"]:
                    results["best_score"] = score
                    results["best_solution"] = solution
                
                results["worst_score"] = min(results["worst_score"], score)
                
                print(f"Pikë: {score}, Kohë: {elapsed:.2f}s")
                
            except Exception as e:
                print(f"GABIM: {str(e)}")
                results["failed_executions"] += 1
        
        if results["scores"]:
            results["avg_score"] = sum(results["scores"]) / len(results["scores"])
        
        return results
    
    def _run_aco_with_local_search(self, instance, aco_solution) -> Dict:
        """Kryej local search mbi zgjidhjen më të mirë të ACO"""
        results = {
            "algorithm": "ACO + Local Search",
            "aco_score": aco_solution.total_score if aco_solution else 0,
            "local_search_score": 0,
            "improvement": 0,
            "time": 0
        }
        
        if not aco_solution:
            print("Nuk ka zgjidhje ACO për local search")
            return results
        
        print(f"Zgjidhje fillestare ACO: {aco_solution.total_score}")
        print(f"Aplikim Local Search...\n")
        
        try:
            start_time = time.time()
            
            optimizer = LocalSearchScheduler(
                instance_data=instance,
                initial_solution=aco_solution,
                max_iterations=100,
                neighborhood_size=20,
                verbose=True,
                random_seed=None
            )
            
            improved_solution = optimizer.optimize()
            elapsed = time.time() - start_time
            
            results["local_search_score"] = improved_solution.total_score
            results["improvement"] = improved_solution.total_score - aco_solution.total_score
            results["time"] = elapsed
            
            improvement_pct = (results["improvement"] / aco_solution.total_score * 100) if aco_solution.total_score > 0 else 0
            print(f"\nPërmirësim: {results['improvement']} pikë ({improvement_pct:.2f}%)")
            print(f"Kohë Local Search: {elapsed:.2f}s")
            
        except Exception as e:
            print(f"Gabim në Local Search: {str(e)}")
        
        return results
    
    def _print_summary(self, aco_results: Dict, beam_results: Dict, aco_local_results: Dict):
        """Shtyp përmbledhjen e rezultateve"""
        print(f"\n{'='*70}")
        print(f"PËRMBLEDHJE REZULTATESH")
        print(f"{'='*70}\n")
        
        print(f"ACO:")
        print(f"  Pikë më të mira:     {aco_results['best_score']}")
        print(f"  Pikë më të këqija:   {aco_results['worst_score']}")
        print(f"  Pikë mesatare:       {aco_results['avg_score']:.2f}")
        print(f"  Ekzekutime të dështuara: {aco_results['failed_executions']}")
        
        print(f"\nBeam Search:")
        print(f"  Pikë më të mira:     {beam_results['best_score']}")
        print(f"  Pikë më të këqija:   {beam_results['worst_score']}")
        print(f"  Pikë mesatare:       {beam_results['avg_score']:.2f}")
        print(f"  Ekzekutime të dështuara: {beam_results['failed_executions']}")
        
        print(f"\nACO + Local Search:")
        print(f"  Pikë ACO:            {aco_local_results['aco_score']}")
        print(f"  Pikë pas Local Search: {aco_local_results['local_search_score']}")
        print(f"  Përmirësim:          {aco_local_results['improvement']}")
        
        print(f"\n{'='*70}\n")


def main():
    """Kryej benchmark"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Schedulers")
    parser.add_argument("--input", "-i", dest="input_file", help="Path i input fajlit")
    parser.add_argument("--executions", "-e", type=int, default=10, help="Numri i ekzekutimeve")
    parser.add_argument("--timeout", "-t", type=int, default=300, help="Max kohë në sekonda")
    
    args = parser.parse_args()
    
    if not args.input_file:
        from parser.file_selector import select_file
        args.input_file = select_file()
    
    runner = BenchmarkRunner(args.input_file, args.timeout)
    results = runner.run_benchmark(args.executions)
    
    # Ruaj rezultatet në JSON
    output_file = f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nRezultatet ruajtur në: {output_file}")


if __name__ == "__main__":
    main()
