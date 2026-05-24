"""
Local Search Scheduler - Optimizimi i një zgjidhje me kërkimin lokal
Merr zgjidhjen më të mirë nga ACO dhe e përmirëson përmes kërkimit lokal.
"""

from typing import List, Dict, Tuple, Optional, Set
import random

from models.instance_data import InstanceData
from models.solution import Solution
from models.schedule import Schedule
from models.program import Program


class LocalSearchScheduler:
    """
    Local Search Optimizer - përmirëson një zgjidhje ekzistuese
    përmes kërkimit lokal me levizje të programeve dhe ricalkim të score-it.
    """
    
    def __init__(
        self,
        instance_data: InstanceData,
        initial_solution: Solution,
        max_iterations: int = 100,
        neighborhood_size: int = 50,
        verbose: bool = True,
        random_seed: Optional[int] = None,
    ):
        self.instance_data = instance_data
        self.initial_solution = initial_solution
        self.max_iterations = max(1, max_iterations)
        self.neighborhood_size = max(1, neighborhood_size)
        self.verbose = verbose
        self.rng = random.Random(random_seed)
        self.min_d = instance_data.min_duration
        self._preprocess()

    def _preprocess(self):
        """Përgatitje indeksesh për vëzim të shpejtë"""
        self.ch_progs: List[List[Program]] = []
        self.prog_by_id: Dict[str, Tuple[Program, int]] = {}
        
        for ch_idx, channel in enumerate(self.instance_data.channels):
            progs = sorted(channel.programs, key=lambda p: p.start)
            self.ch_progs.append(progs)
            for prog in progs:
                self.prog_by_id[prog.unique_id] = (prog, ch_idx)

        self.priority_at: Dict[int, Set[int]] = {}
        for block in self.instance_data.priority_blocks:
            allowed = set(block.allowed_channels)
            for t in range(block.start, block.end):
                if t not in self.priority_at:
                    self.priority_at[t] = allowed.copy()
                else:
                    self.priority_at[t] &= allowed

    def optimize(self) -> Solution:
        """Kryej kërkimin lokal"""
        current_solution = self._normalize_schedule(self.initial_solution)
        current_score = current_solution.total_score
        
        if self.verbose:
            print(f"\n[Local Search] Zgjidhje fillestare: {current_score}")
        
        no_improvement_count = 0
        for iteration in range(self.max_iterations):
            neighbor = self._search_for_improvement(current_solution)
            if neighbor is None:
                no_improvement_count += 1
                if self.verbose:
                    print(f"[Local Search] Iteracion {iteration + 1}: pa përmirësim")
            else:
                current_solution = neighbor
                current_score = current_solution.total_score
                no_improvement_count = 0
                if self.verbose:
                    print(f"[Local Search] Iteracion {iteration + 1}: {current_score}")

            if no_improvement_count > 10:
                if self.verbose:
                    print(f"[Local Search] Ndalesa - nuk ka përmirësim")
                break
        
        if self.verbose:
            print(f"[Local Search] Zgjidhje përfundimtare: {current_solution.total_score}")
        
        return current_solution

    def _search_for_improvement(self, solution: Solution) -> Optional[Solution]:
        current_score = solution.total_score
        best_neighbor: Optional[Solution] = None
        best_score = current_score

        for _ in range(self.neighborhood_size):
            neighbor = self._generate_neighbor(solution)
            if neighbor is None:
                continue
            if neighbor.total_score > best_score:
                best_score = neighbor.total_score
                best_neighbor = neighbor

        return best_neighbor

    def _generate_neighbor(self, solution: Solution) -> Optional[Solution]:
        if not solution.scheduled_programs:
            return None

        if self.rng.random() < 0.4:
            return self._generate_swap_neighbor(solution)
        return self._generate_move_neighbor(solution)

    def _generate_move_neighbor(self, solution: Solution) -> Optional[Solution]:
        scheduled = solution.scheduled_programs
        selected_idx = self.rng.randint(0, len(scheduled) - 1)
        selected = scheduled[selected_idx]
        prog_info = self.prog_by_id.get(selected.unique_program_id)
        if not prog_info:
            return None

        program, _ = prog_info
        moves = []
        new_start = self._find_alternative_time(selected, scheduled)
        if new_start is not None:
            moves.append((new_start, selected.channel_id))

        new_channel = self._find_alternative_channel(selected, scheduled)
        if new_channel is not None:
            moves.append((selected.start, new_channel))
            if new_start is None:
                alternate_start = self._find_alternative_time(selected, scheduled, target_channel=new_channel)
                if alternate_start is not None:
                    moves.append((alternate_start, new_channel))

        self.rng.shuffle(moves)
        for new_start, new_channel in moves:
            if not self._is_valid_move(selected, new_start, new_channel, scheduled):
                continue
            return self._build_neighbor_solution(solution, selected_idx, selected, new_start, new_channel)

        return None

    def _generate_swap_neighbor(self, solution: Solution) -> Optional[Solution]:
        scheduled = solution.scheduled_programs
        if len(scheduled) < 2:
            return None

        idx1 = self.rng.randrange(len(scheduled))
        idx2 = self.rng.randrange(len(scheduled))
        if idx1 == idx2:
            idx2 = (idx1 + 1) % len(scheduled)

        first = scheduled[idx1]
        second = scheduled[idx2]
        if first.unique_program_id == second.unique_program_id:
            return None

        first_prog_info = self.prog_by_id.get(first.unique_program_id)
        second_prog_info = self.prog_by_id.get(second.unique_program_id)
        if not first_prog_info or not second_prog_info:
            return None

        first_prog, _ = first_prog_info
        second_prog, _ = second_prog_info

        candidate1 = (second.start, second.channel_id)
        candidate2 = (first.start, first.channel_id)

        reduced_schedule = [item for item in scheduled if item.unique_program_id not in {first.unique_program_id, second.unique_program_id}]
        if not self._is_valid_move(first, candidate1[0], candidate1[1], reduced_schedule):
            return None
        if not self._is_valid_move(second, candidate2[0], candidate2[1], reduced_schedule):
            return None

        swapped_schedule = scheduled.copy()
        swapped_schedule[idx1] = Schedule(
            program_id=first.program_id,
            channel_id=candidate1[1],
            start=candidate1[0],
            end=candidate1[0] + (first_prog.end - first_prog.start),
            fitness=first.fitness,
            unique_program_id=first.unique_program_id,
        )
        swapped_schedule[idx2] = Schedule(
            program_id=second.program_id,
            channel_id=candidate2[1],
            start=candidate2[0],
            end=candidate2[0] + (second_prog.end - second_prog.start),
            fitness=second.fitness,
            unique_program_id=second.unique_program_id,
        )

        swapped_schedule = self._normalize_schedule(Solution(swapped_schedule, 0)).scheduled_programs
        total_score = self._calculate_score(swapped_schedule)
        if total_score <= solution.total_score:
            return None
        return Solution(swapped_schedule, total_score)

    def _build_neighbor_solution(
        self,
        solution: Solution,
        selected_idx: int,
        selected: Schedule,
        new_start: int,
        new_channel_id: str,
    ) -> Solution:
        prog_info = self.prog_by_id.get(selected.unique_program_id)
        if not prog_info:
            return solution

        program, _ = prog_info
        new_schedule = Schedule(
            program_id=selected.program_id,
            channel_id=new_channel_id,
            start=new_start,
            end=new_start + (program.end - program.start),
            fitness=selected.fitness,
            unique_program_id=selected.unique_program_id,
        )

        new_scheduled = solution.scheduled_programs.copy()
        new_scheduled[selected_idx] = new_schedule
        new_scheduled = self._normalize_schedule(Solution(new_scheduled, 0)).scheduled_programs
        total_score = self._calculate_score(new_scheduled)
        return Solution(new_scheduled, total_score)

    def _find_alternative_time(
        self,
        selected: Schedule,
        scheduled: List[Schedule],
        target_channel: Optional[str] = None,
    ) -> Optional[int]:
        prog_info = self.prog_by_id.get(selected.unique_program_id)
        if not prog_info:
            return None

        program, _ = prog_info
        channel_id = target_channel if target_channel is not None else selected.channel_id
        duration = program.end - program.start
        valid_starts = []

        for start in range(self.instance_data.opening_time, self.instance_data.closing_time - duration + 1):
            if start == selected.start and channel_id == selected.channel_id:
                continue
            if self._is_valid_move(selected, start, channel_id, scheduled):
                valid_starts.append(start)

        if not valid_starts:
            return None
        return self.rng.choice(valid_starts)

    def _find_alternative_channel(self, selected: Schedule, scheduled: List[Schedule]) -> Optional[str]:
        valid_channels = []
        for channel in self.instance_data.channels:
            if channel.channel_id == selected.channel_id:
                continue
            if self._is_valid_move(selected, selected.start, channel.channel_id, scheduled):
                valid_channels.append(channel.channel_id)

        if not valid_channels:
            return None
        return self.rng.choice(valid_channels)

    def _is_valid_move(
        self,
        selected: Schedule,
        new_start: int,
        new_channel_id: str,
        scheduled: List[Schedule],
    ) -> bool:
        prog_info = self.prog_by_id.get(selected.unique_program_id)
        if not prog_info:
            return False

        program, _ = prog_info
        new_end = new_start + (program.end - program.start)
        if new_end > self.instance_data.closing_time:
            return False
        if not self._can_place_on_channel(program, new_start, new_channel_id):
            return False

        for item in scheduled:
            if item.unique_program_id == selected.unique_program_id:
                continue
            if item.channel_id != new_channel_id:
                continue
            if new_start < item.end and new_end > item.start:
                return False

        return True

    def _normalize_schedule(self, solution: Solution) -> Solution:
        normalized = sorted(solution.scheduled_programs, key=lambda s: (s.start, s.channel_id))
        total_score = self._calculate_score(normalized)
        return Solution(normalized, total_score)

    def _calculate_score(self, scheduled_list: List[Schedule]) -> int:
        total_score = 0
        previous_channel = None
        previous_genre = None

        for schedule in sorted(scheduled_list, key=lambda s: (s.start, s.channel_id)):
            prog_info = self.prog_by_id.get(schedule.unique_program_id)
            if not prog_info:
                continue
            program, _ = prog_info
            item_score = self._score_for_schedule(program, schedule, previous_channel, previous_genre)
            total_score += item_score
            previous_channel = schedule.channel_id
            previous_genre = program.genre

        return total_score

    def _score_for_schedule(
        self,
        program: Program,
        schedule: Schedule,
        previous_channel: Optional[str],
        previous_genre: Optional[str],
    ) -> int:
        score = program.score
        if previous_channel is not None and previous_channel != schedule.channel_id:
            score -= self.instance_data.switch_penalty

        for pref in self.instance_data.time_preferences:
            if program.genre == pref.preferred_genre:
                overlap_start = max(schedule.start, pref.start)
                overlap_end = min(schedule.end, pref.end)
                if overlap_end - overlap_start >= self.min_d:
                    score += pref.bonus
                    break

        if schedule.start > program.start:
            score -= self.instance_data.termination_penalty
        if schedule.end < program.end:
            score -= self.instance_data.termination_penalty

        return score

    def _can_place_on_channel(self, program: Program, start_time: int, channel_id: str) -> bool:
        for t in range(start_time, start_time + (program.end - program.start)):
            if t in self.priority_at and channel_id not in self.priority_at[t]:
                return False
        return True

    def _is_valid_placement(self, program: Program, start_time: int, channel_id: str) -> bool:
        if start_time + (program.end - program.start) > self.instance_data.closing_time:
            return False
        if not self._can_place_on_channel(program, start_time, channel_id):
            return False
        return True
