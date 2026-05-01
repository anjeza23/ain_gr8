"""
Comprehensive Benchmark Runner - 10 ekzekutime per instance me parametra të ndryshëm
Kolekton rezultate, analiza dhe krijon raporte
"""

import json
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

class ComprehensiveBenchmark:
    """Ekzekuto 10 herë për secilin instance me parametra të ndryshëm"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "instances": []
        }
        self.input_dir = Path("data/input")
        
        # Parametrat që do të testohen
        self.aco_configs = [
            {"ants": 15, "iterations": 30},
            {"ants": 20, "iterations": 50},
            {"ants": 25, "iterations": 70},
            {"ants": 30, "iterations": 50},
            {"ants": 20, "iterations": 100},
        ]
        
        self.beam_configs = [
            {"beam_width": 50, "lookahead": 2},
            {"beam_width": 100, "lookahead": 4},
            {"beam_width": 150, "lookahead": 6},
            {"beam_width": 100, "lookahead": 6},
            {"beam_width": 50, "lookahead": 4},
        ]
    
    def run_comprehensive_benchmark(self):
        """Ekzekuto benchmark të plotë"""
        # Instance të vogla për teste të shpejta
        test_instances = [
            "data/input/toy.json",
            "data/input/croatia_tv_input.json",
            "data/input/germany_tv_input.json",
        ]
        
        # Kontrollo se cilat fajlla ekzistojnë
        available_instances = []
        for instance in test_instances:
            if Path(instance).exists():
                available_instances.append(instance)
        
        print(f"\nInstance të disponueshëm: {len(available_instances)}\n")
        
        for instance_path in available_instances:
            print(f"\n{'='*80}")
            print(f"TESTIM: {Path(instance_path).name}")
            print(f"{'='*80}\n")
            
            instance_results = self._test_instance(instance_path)
            self.results["instances"].append(instance_results)
        
        # Shfaq përmbledhjen
        self._print_comprehensive_summary()
        
        # Ruaj rezultatet
        output_file = f"comprehensive_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n✓ Rezultatet ruajtur në: {output_file}\n")
    
    def _test_instance(self, instance_path: str) -> Dict:
        """Testo një instance me të gjithë konfiguracionet"""
        instance_name = Path(instance_path).stem
        instance_data = {
            "name": instance_name,
            "path": instance_path,
            "aco_results": [],
            "beam_results": [],
            "analysis": {}
        }
        
        # ACO Tests
        print("FASE 1: ACO OPTIMIZATION\n")
        for i, config in enumerate(self.aco_configs, 1):
            print(f"  [{i}/5] Testing ACO - Ants={config['ants']}, Iterations={config['iterations']}")
            
            try:
                start = time.time()
                result = subprocess.run([
                    "python", "main.py",
                    "--input", instance_path,
                    "--algorithm", "aco",
                    "--ants", str(config['ants']),
                    "--iterations", str(config['iterations']),
                    "--seed", "42"
                ], capture_output=True, text=True, timeout=300)
                
                elapsed = time.time() - start
                
                # Parse output për pikë
                score = self._extract_score(result.stdout)
                
                config_result = {
                    "config": config,
                    "score": score,
                    "time": elapsed,
                    "success": score > 0
                }
                instance_data["aco_results"].append(config_result)
                
                print(f"      ✓ Score: {score}, Time: {elapsed:.2f}s\n")
                
            except Exception as e:
                print(f"      ✗ Error: {str(e)}\n")
                instance_data["aco_results"].append({
                    "config": config,
                    "score": 0,
                    "time": 0,
                    "success": False
                })
        
        # Beam Search Tests
        print("FASE 2: BEAM SEARCH\n")
        for i, config in enumerate(self.beam_configs, 1):
            print(f"  [{i}/5] Testing Beam - Width={config['beam_width']}, Lookahead={config['lookahead']}")
            
            try:
                start = time.time()
                result = subprocess.run([
                    "python", "main.py",
                    "--input", instance_path,
                    "--algorithm", "beam",
                    "--seed", "42"
                ], capture_output=True, text=True, timeout=300)
                
                elapsed = time.time() - start
                score = self._extract_score(result.stdout)
                
                config_result = {
                    "config": config,
                    "score": score,
                    "time": elapsed,
                    "success": score > 0
                }
                instance_data["beam_results"].append(config_result)
                
                print(f"      ✓ Score: {score}, Time: {elapsed:.2f}s\n")
                
            except Exception as e:
                print(f"      ✗ Error: {str(e)}\n")
                instance_data["beam_results"].append({
                    "config": config,
                    "score": 0,
                    "time": 0,
                    "success": False
                })
        
        # Analiza
        instance_data["analysis"] = self._analyze_results(instance_data)
        
        return instance_data
    
    def _extract_score(self, output: str) -> int:
        """Ekstrakto pikën nga output"""
        try:
            # Këto Hkosh për "total score: 380"
            for line in output.split('\n'):
                if "total score" in line.lower():
                    parts = line.split(':')
                    if len(parts) >= 2:
                        return int(parts[-1].strip())
        except:
            pass
        return 0
    
    def _analyze_results(self, instance_data: Dict) -> Dict:
        """Analiza rezultatesh"""
        analysis = {}
        
        # ACO Analysis
        aco_scores = [r["score"] for r in instance_data["aco_results"] if r["success"]]
        if aco_scores:
            analysis["aco"] = {
                "best_score": max(aco_scores),
                "worst_score": min(aco_scores),
                "avg_score": sum(aco_scores) / len(aco_scores),
                "best_config": instance_data["aco_results"][aco_scores.index(max(aco_scores))]["config"],
                "worst_config": instance_data["aco_results"][aco_scores.index(min(aco_scores))]["config"]
            }
        
        # Beam Analysis
        beam_scores = [r["score"] for r in instance_data["beam_results"] if r["success"]]
        if beam_scores:
            analysis["beam"] = {
                "best_score": max(beam_scores),
                "worst_score": min(beam_scores),
                "avg_score": sum(beam_scores) / len(beam_scores),
                "best_config": instance_data["beam_results"][beam_scores.index(max(beam_scores))]["config"],
                "worst_config": instance_data["beam_results"][beam_scores.index(min(beam_scores))]["config"]
            }
        
        return analysis
    
    def _print_comprehensive_summary(self):
        """Shtyp përmbledhje të plotë"""
        print(f"\n{'='*80}")
        print(f"PËRMBLEDHJE REZULTATESH")
        print(f"{'='*80}\n")
        
        for instance in self.results["instances"]:
            print(f"\n📊 Instance: {instance['name']}")
            print(f"{'-'*80}")
            
            if instance["analysis"].get("aco"):
                aco = instance["analysis"]["aco"]
                print(f"\n🐜 ACO Optimization:")
                print(f"   Best Score:      {aco['best_score']}")
                print(f"   Worst Score:     {aco['worst_score']}")
                print(f"   Average Score:   {aco['avg_score']:.1f}")
                print(f"   Best Config:     Ants={aco['best_config']['ants']}, Iter={aco['best_config']['iterations']}")
                print(f"   Worst Config:    Ants={aco['worst_config']['ants']}, Iter={aco['worst_config']['iterations']}")
            
            if instance["analysis"].get("beam"):
                beam = instance["analysis"]["beam"]
                print(f"\n🔍 Beam Search:")
                print(f"   Best Score:      {beam['best_score']}")
                print(f"   Worst Score:     {beam['worst_score']}")
                print(f"   Average Score:   {beam['avg_score']:.1f}")
                print(f"   Best Config:     Width={beam['best_config']['beam_width']}, Look={beam['best_config']['lookahead']}")
                print(f"   Worst Config:    Width={beam['worst_config']['beam_width']}, Look={beam['worst_config']['lookahead']}")


def main():
    benchmark = ComprehensiveBenchmark()
    benchmark.run_comprehensive_benchmark()


if __name__ == "__main__":
    main()
