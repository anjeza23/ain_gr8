"""
Parameter Tuning Framework - Eksperimentim me parametra të ndryshëm
Testuese kombinacione të ndryshme parametrash për të gjetur konfigurimin më të mirë
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
from serializer.serializer import SolutionSerializer
from utils.utils import Utils


class ParameterTuner:
    """Menaxhues për eksperimentim me parametra"""
    
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.results = {
            "input_file": os.path.basename(input_file),
            "timestamp": datetime.now().isoformat(),
            "experiments": []
        }
        
        # Parse fajlin input njëherë
        parser = Parser(input_file)
        self.instance = parser.parse()
        Utils.set_current_instance(self.instance)
    
    def tune_aco_parameters(self, ants_range: List[int], iterations_range: List[int], 
                           runs_per_config: int = 3) -> Dict:
        """
        Teste kombinacione të ndryshme të parametrave ACO
        
        Args:
            ants_range: Listë e vlerave për të testuar (p.sh., [10, 20, 30])
            iterations_range: Listë e vlerave për iteracione
            runs_per_config: Numri i ekzekutimeve për secilin kombinacion
        
        Returns:
            Rezultatet e tuning-ut
        """
        print(f"\n{'='*70}")
        print(f"ACO PARAMETER TUNING")
        print(f"{'='*70}\n")
        
        print(f"Input: {os.path.basename(self.input_file)}")
        print(f"Ants të testuara: {ants_range}")
        print(f"Iterations të testuara: {iterations_range}")
        print(f"Ekzekutime për secilin kombinacion: {runs_per_config}\n")
        
        best_config = None
        best_score = 0
        
        total_configs = len(ants_range) * len(iterations_range)
        config_num = 0
        
        for ants in ants_range:
            for iterations in iterations_range:
                config_num += 1
                scores = []
                times = []
                
                print(f"[{config_num}/{total_configs}] Ants={ants}, Iterations={iterations}")
                
                for run in range(runs_per_config):
                    try:
                        start = time.time()
                        
                        scheduler = AntColonyScheduler(
                            instance_data=self.instance,
                            ants=ants,
                            iterations=iterations,
                            verbose=False,
                            random_seed=None
                        )
                        
                        solution = scheduler.generate_solution()
                        elapsed = time.time() - start
                        
                        scores.append(solution.total_score)
                        times.append(elapsed)
                        
                        print(f"  Run {run+1}: {solution.total_score} ({elapsed:.2f}s)")
                        
                    except Exception as e:
                        print(f"  Run {run+1}: GABIM - {str(e)}")
                        continue
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    avg_time = sum(times) / len(times) if times else 0
                    max_score = max(scores)
                    
                    config_result = {
                        "ants": ants,
                        "iterations": iterations,
                        "avg_score": avg_score,
                        "max_score": max_score,
                        "min_score": min(scores),
                        "avg_time": avg_time,
                        "runs": len(scores)
                    }
                    
                    self.results["experiments"].append(config_result)
                    
                    print(f"  Rezultate: avg={avg_score:.0f}, max={max_score}, time={avg_time:.2f}s\n")
                    
                    if max_score > best_score:
                        best_score = max_score
                        best_config = config_result
        
        # Renditu rezultatet
        self._print_tuning_summary(best_config)
        
        return self.results
    
    def tune_beam_parameters(self, beam_widths: List[int], lookaheads: List[int],
                           runs_per_config: int = 3) -> Dict:
        """
        Teste kombinacione të ndryshme të parametrave Beam Search
        
        Args:
            beam_widths: Listë e gjerësive të beam
            lookaheads: Listë të thellësive lookahead
            runs_per_config: Numri i ekzekutimeve për secilin kombinacion
        
        Returns:
            Rezultatet e tuning-ut
        """
        print(f"\n{'='*70}")
        print(f"BEAM SEARCH PARAMETER TUNING")
        print(f"{'='*70}\n")
        
        print(f"Input: {os.path.basename(self.input_file)}")
        print(f"Beam widths të testuara: {beam_widths}")
        print(f"Lookaheads të testuara: {lookaheads}")
        print(f"Ekzekutime për secilin kombinacion: {runs_per_config}\n")
        
        best_config = None
        best_score = 0
        
        total_configs = len(beam_widths) * len(lookaheads)
        config_num = 0
        
        for beam_width in beam_widths:
            for lookahead in lookaheads:
                config_num += 1
                scores = []
                times = []
                
                print(f"[{config_num}/{total_configs}] Beam Width={beam_width}, Lookahead={lookahead}")
                
                for run in range(runs_per_config):
                    try:
                        start = time.time()
                        
                        scheduler = BeamSearchScheduler(
                            instance_data=self.instance,
                            beam_width=beam_width,
                            lookahead_limit=lookahead,
                            density_percentile=25,
                            verbose=False,
                            random_seed=None
                        )
                        
                        solution = scheduler.generate_solution()
                        elapsed = time.time() - start
                        
                        scores.append(solution.total_score)
                        times.append(elapsed)
                        
                        print(f"  Run {run+1}: {solution.total_score} ({elapsed:.2f}s)")
                        
                    except Exception as e:
                        print(f"  Run {run+1}: GABIM - {str(e)}")
                        continue
                
                if scores:
                    avg_score = sum(scores) / len(scores)
                    avg_time = sum(times) / len(times) if times else 0
                    max_score = max(scores)
                    
                    config_result = {
                        "beam_width": beam_width,
                        "lookahead": lookahead,
                        "avg_score": avg_score,
                        "max_score": max_score,
                        "min_score": min(scores),
                        "avg_time": avg_time,
                        "runs": len(scores)
                    }
                    
                    self.results["experiments"].append(config_result)
                    
                    print(f"  Rezultate: avg={avg_score:.0f}, max={max_score}, time={avg_time:.2f}s\n")
                    
                    if max_score > best_score:
                        best_score = max_score
                        best_config = config_result
        
        # Renditu rezultatet
        self._print_tuning_summary(best_config)
        
        return self.results
    
    def _print_tuning_summary(self, best_config: Dict):
        """Shtyp përmbledhjen e tuning-ut"""
        print(f"\n{'='*70}")
        print(f"PËRMBLEDHJA E TUNING-UT")
        print(f"{'='*70}\n")
        
        if best_config:
            print(f"KONFIGURIMI MË I MIR:")
            for key, value in best_config.items():
                if key != "runs":
                    if isinstance(value, float):
                        print(f"  {key}: {value:.2f}")
                    else:
                        print(f"  {key}: {value}")
        
        # Sorto dhe shfaq top 5
        sorted_experiments = sorted(
            self.results["experiments"],
            key=lambda x: x.get("max_score", 0),
            reverse=True
        )
        
        print(f"\nTOP 5 KONFIGURACIONET:")
        for i, config in enumerate(sorted_experiments[:5], 1):
            print(f"\n{i}. Max Score: {config.get('max_score', 'N/A')}")
            for key, value in config.items():
                if key not in ["runs", "max_score"]:
                    if isinstance(value, float):
                        print(f"   {key}: {value:.2f}")
                    else:
                        print(f"   {key}: {value}")
        
        print(f"\n{'='*70}\n")


def main():
    """Krye parameter tuning"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parameter Tuning")
    parser.add_argument("--input", "-i", dest="input_file", required=True, 
                       help="Path i input fajlit")
    parser.add_argument("--algorithm", "-a", choices=["aco", "beam"], default="aco",
                       help="Algoritmi për tuning")
    parser.add_argument("--runs", "-r", type=int, default=3,
                       help="Ekzekutime për secilin kombinacion")
    
    args = parser.parse_args()
    
    tuner = ParameterTuner(args.input_file)
    
    if args.algorithm == "aco":
        # Teste kombinacione të ndryshme
        ants_to_test = [10, 15, 20, 25, 30]
        iterations_to_test = [30, 50, 70]
        
        results = tuner.tune_aco_parameters(
            ants_range=ants_to_test,
            iterations_range=iterations_to_test,
            runs_per_config=args.runs
        )
    else:
        # Beam Search parameter tuning
        beam_widths = [50, 100, 150]
        lookaheads = [2, 4, 6]
        
        results = tuner.tune_beam_parameters(
            beam_widths=beam_widths,
            lookaheads=lookaheads,
            runs_per_config=args.runs
        )
    
    # Ruaj rezultatet
    output_file = f"tuning_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Rezultatet ruajtur në: {output_file}")


if __name__ == "__main__":
    main()
