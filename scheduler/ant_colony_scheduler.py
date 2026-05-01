from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import bisect
import random

from models.instance_data import InstanceData
from models.solution import Solution
from models.schedule import Schedule
from models.program import Program


class AntColonyScheduler:
    def __init__(
        self,
        instance_data: InstanceData,
        ants: int = 20,
        iterations: int = 50,
        alpha: float = 1.0,
        beta: float = 2.0,
        evaporation: float = 0.15,
        q0: float = 0.2,
        verbose: bool = True,
        random_seed: Optional[int] = None,
    ):
        self.instance_data = instance_data
        self.n_ants = max(1, ants)
        self.n_iterations = max(1, iterations)
        self.alpha = max(0.0, alpha)
        self.beta = max(0.0, beta)
        self.evaporation = min(1.0, max(0.0, evaporation))
        self.q0 = min(1.0, max(0.0, q0))
        self.verbose = verbose
        self.rng = random.Random(random_seed)
        self.min_d = instance_data.min_duration
        self._preprocess()

    def _preprocess(self):
        self.n_channels = len(self.instance_data.channels)
        self.ch_progs: List[List[Program]] = []
        self.ch_starts: List[List[int]] = []
        self.prog_by_id: Dict[str, Tuple[Program, int]] = {}
        self.starts_at = defaultdict(list)
        all_times = set()
        all_times.add(self.instance_data.opening_time)

        for ch_idx, channel in enumerate(self.instance_data.channels):
            progs = sorted(channel.programs, key=lambda p: p.start)
            self.ch_progs.append(progs)
            self.ch_starts.append([p.start for p in progs])

            for prog in progs:
                all_times.add(prog.start)
                all_times.add(prog.end)
                self.prog_by_id[prog.unique_id] = (prog, ch_idx)
                self.starts_at[prog.start].append((prog, ch_idx))

        self.times = sorted([t for t in all_times
                            if self.instance_data.opening_time <= t <= self.instance_data.closing_time])

        for block in self.instance_data.priority_blocks:
            if block.start not in self.times:
                self.times.append(block.start)
            if block.end not in self.times:
                self.times.append(block.end)
        self.times = sorted(set(self.times))

        self.priority_at: Dict[int, Set[int]] = {}
        for block in self.instance_data.priority_blocks:
            allowed = set(block.allowed_channels)
            for t in range(block.start, block.end):
                if t not in self.priority_at:
                    self.priority_at[t] = allowed.copy()
                else:
                    self.priority_at[t] &= allowed

        self.forbidden_prefix = []
        self.has_priority_blocks = bool(self.instance_data.priority_blocks)
        if self.has_priority_blocks:
            max_t = self.instance_data.closing_time + 100
            for ch_idx, channel in enumerate(self.instance_data.channels):
                ch_id = channel.channel_id
                is_forbidden = [0] * max_t
                for t, allowed in self.priority_at.items():
                    if t < max_t and ch_id not in allowed:
                        is_forbidden[t] = 1

                prefix = [0] * (max_t + 1)
                curr = 0
                for t in range(max_t):
                    curr += is_forbidden[t]
                    prefix[t + 1] = curr
                self.forbidden_prefix.append(prefix)

        self.prefs = self.instance_data.time_preferences
        self.pheromone: Dict[str, float] = {prog_id: 1.0 for prog_id in self.prog_by_id}

        densities = []
        for ch in self.instance_data.channels:
            for p in ch.programs:
                dur = p.end - p.start
                if dur > 0:
                    densities.append(p.score / dur)

        densities.sort(reverse=True)
        if densities:
            top_n = max(1, int(len(densities) * 0.25))
            self.avg_score_per_min = sum(densities[:top_n]) / top_n
        else:
            self.avg_score_per_min = 1.0

        if self.verbose:
            print(f"ACO scheduler: average score density (top 25%): {self.avg_score_per_min:.4f} pts/min")

    def _channel_allowed(self, ch_idx: int, start: int, end: int) -> bool:
        if not self.has_priority_blocks:
            return True
        prefix = self.forbidden_prefix[ch_idx]
        max_t = len(prefix) - 1
        s = min(start, max_t)
        e = min(end, max_t)
        if s >= e:
            return True
        return prefix[e] - prefix[s] == 0

    def _calc_score(self, prog: Program, ch_idx: int,
                    seg_start: int, seg_end: int,
                    prev_ch_id: Optional[int]) -> int:
        duration = seg_end - seg_start
        if duration < self.min_d:
            return -999999

        score = prog.score
        for pref in self.prefs:
            if prog.genre == pref.preferred_genre:
                ov_start = max(seg_start, pref.start)
                ov_end = min(seg_end, pref.end)
                if ov_end - ov_start >= self.min_d:
                    score += pref.bonus
                    break

        if prev_ch_id is not None and prev_ch_id != self.instance_data.channels[ch_idx].channel_id:
            score -= self.instance_data.switch_penalty

        if seg_start > prog.start:
            score -= self.instance_data.termination_penalty
        if seg_end < prog.end:
            score -= self.instance_data.termination_penalty

        return score

    def _heuristic_value(self, score: int, duration: int) -> float:
        if score <= 0:
            return 1.0
        return max(1.0, score / duration)

    def _get_prog(self, ch_idx: int, time: int) -> Optional[Program]:
        idx = bisect.bisect_right(self.ch_starts[ch_idx], time) - 1
        if 0 <= idx < len(self.ch_progs[ch_idx]):
            p = self.ch_progs[ch_idx][idx]
            if p.start <= time < p.end:
                return p
        return None

    def _get_candidates(self, time: int, prev_ch_id: Optional[int],
                        prev_genre: str, genre_streak: int,
                        used_progs: Set[str]) -> List[Tuple[int, int, int, Program, int, int]]:
        candidates = []
        closing = self.instance_data.closing_time

        for ch_idx in range(self.n_channels):
            prog = self._get_prog(ch_idx, time)
            if not prog:
                continue
            if prog.unique_id in used_progs:
                continue

            new_streak = 1 if prog.genre != prev_genre else genre_streak + 1
            if new_streak > self.instance_data.max_consecutive_genre:
                continue

            seg_start = time
            end_options = set()
            nat_end = min(prog.end, closing)
            if nat_end - seg_start >= self.min_d:
                end_options.add(nat_end)

            start_idx = bisect.bisect_right(self.times, seg_start + self.min_d)
            end_idx = bisect.bisect_left(self.times, nat_end)
            for i in range(start_idx, end_idx + 1):
                if i >= len(self.times):
                    break
                t = self.times[i]
                if t > nat_end:
                    break
                end_options.add(t)

            min_end = seg_start + self.min_d
            if min_end <= nat_end:
                end_options.add(min_end)

            for seg_end in sorted(end_options):
                if seg_end > closing:
                    continue
                if not self._channel_allowed(ch_idx, seg_start, seg_end):
                    continue
                score = self._calc_score(prog, ch_idx, seg_start, seg_end, prev_ch_id)
                if score > -999999:
                    candidates.append((score, ch_idx, self.instance_data.channels[ch_idx].channel_id,
                                       prog, seg_start, seg_end))

        if not candidates:
            start_idx = bisect.bisect_right(self.times, time)
            lookahead_count = 0
            for i in range(start_idx, len(self.times)):
                future_time = self.times[i]
                if future_time >= closing:
                    break
                if future_time > time + self.min_d * 4:
                    break
                lookahead_count += 1
                if lookahead_count > 4:
                    break

                for prog, ch_idx in self.starts_at.get(future_time, []):
                    if prog.unique_id in used_progs:
                        continue
                    new_streak = 1 if prog.genre != prev_genre else genre_streak + 1
                    if new_streak > self.instance_data.max_consecutive_genre:
                        continue
                    nat_end = min(prog.end, closing)
                    if nat_end - future_time < self.min_d:
                        continue
                    if not self._channel_allowed(ch_idx, future_time, nat_end):
                        continue
                    score = self._calc_score(prog, ch_idx, future_time, nat_end, prev_ch_id)
                    if score > -999999:
                        candidates.append((score, ch_idx, self.instance_data.channels[ch_idx].channel_id,
                                           prog, future_time, nat_end))

        return candidates

    def _select_candidate(self, candidates: List[Tuple[int, int, int, Program, int, int]]) -> Tuple[int, int, int, Program, int, int]:
        values = []
        total = 0.0
        best = None
        best_score = float('-inf')

        for score, ch_idx, ch_id, prog, seg_start, seg_end in candidates:
            duration = seg_end - seg_start
            pheromone = self.pheromone.get(prog.unique_id, 1.0)
            heuristic = self._heuristic_value(score, duration)
            value = (pheromone ** self.alpha) * (heuristic ** self.beta)
            values.append(value)
            total += value
            if value > best_score:
                best_score = value
                best = (score, ch_idx, ch_id, prog, seg_start, seg_end)

        if not candidates:
            raise ValueError("No candidate available for selection")

        if self.rng.random() < self.q0:
            return best if best is not None else candidates[0]

        if total <= 0:
            return self.rng.choice(candidates)

        threshold = self.rng.random() * total
        cumulative = 0.0
        for value, candidate in zip(values, candidates):
            cumulative += value
            if cumulative >= threshold:
                return candidate

        return candidates[-1]

    def _build_solution(self) -> Solution:
        scheduled = []
        used = set()
        time = self.instance_data.opening_time
        prev_ch_id = None
        prev_genre = ""
        genre_streak = 0
        total_score = 0

        while time < self.instance_data.closing_time:
            candidates = self._get_candidates(time, prev_ch_id, prev_genre, genre_streak, used)
            if not candidates:
                idx = bisect.bisect_right(self.times, time)
                if idx < len(self.times):
                    time = self.times[idx]
                    continue
                break

            score, ch_idx, ch_id, prog, seg_start, seg_end = self._select_candidate(candidates)
            scheduled.append(Schedule(
                program_id=prog.program_id,
                channel_id=ch_id,
                start=seg_start,
                end=seg_end,
                fitness=score,
                unique_program_id=prog.unique_id
            ))
            total_score += score
            used.add(prog.unique_id)

            if prog.genre == prev_genre:
                genre_streak += 1
            else:
                genre_streak = 1
                prev_genre = prog.genre

            prev_ch_id = ch_id
            time = seg_end

        return Solution(scheduled, total_score)

    def _update_pheromone(self, solution: Solution):
        for prog_id in self.pheromone:
            self.pheromone[prog_id] *= (1.0 - self.evaporation)
            if self.pheromone[prog_id] < 1e-6:
                self.pheromone[prog_id] = 1e-6

        if solution.total_score <= 0:
            return

        deposit = solution.total_score / max(1, len(solution.scheduled_programs))
        for sched in solution.scheduled_programs:
            self.pheromone[sched.unique_program_id] += deposit

    def generate_solution(self) -> Solution:
        best_solution: Optional[Solution] = None
        for it in range(1, self.n_iterations + 1):
            iteration_best: Optional[Solution] = None
            for _ in range(self.n_ants):
                sol = self._build_solution()
                if iteration_best is None or sol.total_score > iteration_best.total_score:
                    iteration_best = sol
            if iteration_best is not None:
                self._update_pheromone(iteration_best)
                if best_solution is None or iteration_best.total_score > best_solution.total_score:
                    best_solution = iteration_best

            if self.verbose:
                score_text = iteration_best.total_score if iteration_best is not None else 0
                print(f"ACO iteration {it}/{self.n_iterations}: best score={score_text}")

        return best_solution if best_solution is not None else Solution([], 0)
