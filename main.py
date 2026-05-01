from parser.file_selector import select_file
from parser.parser import Parser
from serializer.serializer import SolutionSerializer
from scheduler.ant_colony_scheduler import AntColonyScheduler
from scheduler.beam_search_scheduler import BeamSearchScheduler
from scheduler.local_search_scheduler import LocalSearchScheduler
from utils.utils import Utils
import argparse
import time


def main():
    parser_arg = argparse.ArgumentParser(description="Run TV scheduling algorithms")
    parser_arg.add_argument("--input", "-i", dest="input_file", help="Path to input JSON (optional)")
    parser_arg.add_argument("--algorithm", "-a", choices=["beam", "aco"], default="aco",
                            help="Scheduler algorithm to run")
    parser_arg.add_argument("--seed", type=int, default=None, help="Optional seed; omit to randomize every run")
    parser_arg.add_argument("--explore-prob", type=float, default=0.15, help="Probability of random exploration in local search (beam only)")
    parser_arg.add_argument("--top-k", type=int, default=3, help="Top-k candidates for random exploration (beam only)")
    parser_arg.add_argument("--ants", type=int, default=20, help="Number of ants for ACO")
    parser_arg.add_argument("--iterations", type=int, default=50, help="Number of ACO iterations")
    parser_arg.add_argument("--local-search", action="store_true", help="Apply local search optimization after initial algorithm")
    parser_arg.add_argument("--ls-iterations", type=int, default=100, help="Max iterations for local search")
    parser_arg.add_argument("--ls-neighborhood", type=int, default=20, help="Neighborhood size for local search")
    
    args = parser_arg.parse_args()
    file_path = args.input_file if args.input_file else select_file()
    parser = Parser(file_path)
    instance = parser.parse()
    Utils.set_current_instance(instance)

    print("\nOpening time:", instance.opening_time)
    print("Closing time:", instance.closing_time)
    print(f"Total Channels: {len(instance.channels)}")

    print(f"\nRunning {args.algorithm.upper()} Scheduler")

    if args.algorithm == "beam":
        beam_width = 100
        lookahead = 4
        percentile = 25
        scheduler = BeamSearchScheduler(
            instance_data=instance,
            beam_width=beam_width,
            lookahead_limit=lookahead,
            density_percentile=percentile,
            verbose=False,
            random_seed=args.seed,
            random_explore_prob=args.explore_prob,
            random_top_k=args.top_k
        )
    else:
        scheduler = AntColonyScheduler(
            instance_data=instance,
            ants=args.ants,
            iterations=args.iterations,
            alpha=1.0,
            beta=2.0,
            evaporation=0.15,
            q0=0.2,
            verbose=False,
            random_seed=args.seed
        )

    start_time = time.time()
    solution = scheduler.generate_solution()
    initial_time = time.time() - start_time
    print(f"\n[OK] Generated solution with total score: {solution.total_score}")
    print(f"  Time: {initial_time:.2f} seconds")

    # Apply Local Search if requested
    if args.local_search:
        print(f"\nApplying Local Search Optimization...")
        ls_start = time.time()
        
        local_searcher = LocalSearchScheduler(
            instance_data=instance,
            initial_solution=solution,
            max_iterations=args.ls_iterations,
            neighborhood_size=args.ls_neighborhood,
            verbose=True,
            random_seed=args.seed
        )
        
        solution = local_searcher.optimize()
        ls_time = time.time() - ls_start
        
        print(f"\n[OK] Local Search completed")
        print(f"  Time: {ls_time:.2f} seconds")

    algorithm_name = type(scheduler).__name__.lower()
    if args.local_search:
        algorithm_name += "_with_ls"
    
    serializer = SolutionSerializer(input_file_path=file_path, algorithm_name=algorithm_name)
    serializer.serialize(solution)

    print(f"[OK] Solution saved to output file")


if __name__ == "__main__":
    main()
