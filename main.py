from parser.file_selector import select_file
from parser.parser import Parser
from serializer.serializer import SolutionSerializer
from scheduler.beam_search_scheduler import BeamSearchScheduler
from utils.utils import Utils
import argparse


def main():
    parser_arg = argparse.ArgumentParser(description="Run TV scheduling algorithms")
    parser_arg.add_argument("--input", "-i", dest="input_file", help="Path to input JSON (optional)")
    parser_arg.add_argument("--seed", type=int, default=42, help="Random seed for reproducible randomized local search")
    parser_arg.add_argument("--explore-prob", type=float, default=0.15, help="Probability of random exploration in local search")
    parser_arg.add_argument("--top-k", type=int, default=3, help="Top-k candidates for random exploration")
    
    args = parser_arg.parse_args()
    file_path = args.input_file if args.input_file else select_file()
    parser = Parser(file_path)
    instance = parser.parse()
    Utils.set_current_instance(instance)

    print("\nOpening time:", instance.opening_time)
    print("Closing time:", instance.closing_time)
    print(f"Total Channels: {len(instance.channels)}")

    print('\nRunning Beam Search Scheduler')
    
    # Default optimized parameters
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

    solution = scheduler.generate_solution()
    print(f"\n✓ Generated solution with total score: {solution.total_score}")

    algorithm_name = type(scheduler).__name__.lower()
    serializer = SolutionSerializer(input_file_path=file_path, algorithm_name=algorithm_name)
    serializer.serialize(solution)

    print(f"✓ Solution saved to output file")


if __name__ == "__main__":
    main()
