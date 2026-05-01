"""
Local Search Scheduler - Optimizimi i një zgjidhje me kërkimin lokal
Merr zgjidhjen më të mirë nga ACO dhe e përmirëson përmes kërkimit lokal.
"""

from typing import List, Dict, Tuple, Optional, Set
from collections import defaultdict
import random
import time

from models.instance_data import InstanceData
from models.solution import Solution
from models.schedule import Schedule
from models.program import Program
from utils.utils import Utils


class LocalSearchScheduler:
    """
    Local Search Optimizer - përmirëson një zgjidhje ekzistuese
    përmes kërkimit lokal (2-opt neighborhood moves)
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
        self.n_channels = len(self.instance_data.channels)
        self.ch_progs: List[List[Program]] = []
        self.prog_by_id: Dict[str, Tuple[Program, int]] = {}
        
        for ch_idx, channel in enumerate(self.instance_data.channels):
            progs = sorted(channel.programs, key=lambda p: p.start)
            self.ch_progs.append(progs)
            for prog in progs:
                self.prog_by_id[prog.unique_id] = (prog, ch_idx)

        # Priority blocks
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
        current_solution = self.initial_solution
        current_score = current_solution.total_score
        
        if self.verbose:
            print(f"\n[Local Search] Zgjidhje fillestare: {current_score}")
        
        no_improvement_count = 0
        
        for iteration in range(self.max_iterations):
            # Gjenero fqinjësi - provojë zhvendosje të programeve
            improved = False
            
            for _ in range(self.neighborhood_size):
                neighbor_solution = self._generate_neighbor(current_solution)
                
                if neighbor_solution is not None:
                    if neighbor_solution.total_score > current_score:
                        current_solution = neighbor_solution
                        current_score = neighbor_solution.total_score
                        improved = True
                        no_improvement_count = 0
                        
                        if self.verbose:
                            print(f"[Local Search] Iteracion {iteration + 1}: {current_score}")
                        break
            
            if not improved:
                no_improvement_count += 1
                
            # Nëse nuk ka përmirësim për shumë iteracione, ndaloj
            if no_improvement_count > 10:
                if self.verbose:
                    print(f"[Local Search] Ndalesa - nuk ka përmirësim")
                break
        
        if self.verbose:
            print(f"[Local Search] Zgjidhje përfundimtare: {current_score}")
        
        return current_solution

    def _generate_neighbor(self, solution: Solution) -> Optional[Solution]:
        """
        Gjenero zgjidhje fqinj përmes zhvendosjes (move neighborhood)
        Zhvendos një program në pozicion tjetër në të njëjtin kanal ose në kanal tjetër
        """
        if not solution.scheduled_programs:
            return None
        
        # Zgjidh rastësisht një program
        program_idx = self.rng.randint(0, len(solution.scheduled_programs) - 1)
        selected = solution.scheduled_programs[program_idx]
        
        new_start = selected.start
        new_channel_id = selected.channel_id
        
        # 50% mundësia për të ndryshuar kohën, 50% për të ndryshuar kanalin
        if self.rng.random() < 0.5:
            # Ndryshim kohe në të njëjtin kanal
            new_start = self._find_alternative_time(selected)
        else:
            # Ndryshim kanali në të njëjtën kohë
            new_channel_id = self._find_alternative_channel(selected)
        
        if new_start is None and new_channel_id is None:
            return None
        
        if new_start is None:
            new_start = selected.start
        if new_channel_id is None:
            new_channel_id = selected.channel_id
        
        # Merr programin për të marrë informacion (duration, gjëra të tjera)
        prog_info = self.prog_by_id.get(selected.unique_program_id)
        if not prog_info:
            return None
        
        program, _ = prog_info
        
        # Krijo zgjidhje të re me zhvendosje
        new_schedule = Schedule(
            program_id=selected.program_id,
            channel_id=new_channel_id,
            start=new_start,
            end=new_start + program.duration,
            fitness=selected.fitness,
            unique_program_id=selected.unique_program_id
        )
        
        # Zëvendëso në listë
        new_scheduled = solution.scheduled_programs.copy()
        new_scheduled[program_idx] = new_schedule
        
        # Njehso pikë të reja
        new_score = self._calculate_score(new_scheduled)
        return Solution(new_scheduled, new_score)

    def _find_alternative_time(self, scheduled: Schedule) -> Optional[int]:
        """Gjendje kohë alternative në të njëjtin kanal"""
        prog = self.prog_by_id.get(scheduled.unique_program_id)
        if not prog:
            return None
        
        program, _ = prog
        current_channel = scheduled.channel_id
        
        # Mundësi për zhvendosje në intervale të tjera kohore
        alternatives = self._get_valid_start_times(program, current_channel)
        
        if alternatives:
            return self.rng.choice(alternatives)
        return None

    def _find_alternative_channel(self, scheduled: Schedule) -> Optional[str]:
        """Gjendje kanali alternative për të njëjtën kohë"""
        prog = self.prog_by_id.get(scheduled.unique_program_id)
        if not prog:
            return None
        
        program, _ = prog
        current_time = scheduled.start
        
        # Kontrollo cilat kanale mund të transmetojnë këtë program
        valid_channels = []
        
        for channel in self.instance_data.channels:
            if self._can_place_on_channel(program, current_time, channel.channel_id):
                valid_channels.append(channel.channel_id)
        
        if valid_channels:
            return self.rng.choice(valid_channels)
        return None

    def _get_valid_start_times(self, program: Program, channel_id: str) -> List[int]:
        """Merr të gjitha kohët fillestare të vlefshme për programin"""
        valid_times = []
        
        for start in range(
            self.instance_data.opening_time,
            self.instance_data.closing_time - program.duration + 1
        ):
            if self._is_valid_placement(program, start, channel_id):
                valid_times.append(start)
        
        return valid_times

    def _can_place_on_channel(self, program: Program, start_time: int, channel_id: str) -> bool:
        """Kontrollo nëse programi mund të vendoset në kanal"""
        # Kontrollo kufizimet e priority blocks
        for t in range(start_time, start_time + program.duration):
            if t in self.priority_at and channel_id not in self.priority_at[t]:
                return False
        return True

    def _is_valid_placement(self, program: Program, start_time: int, channel_id: str) -> bool:
        """Kontrollo nëse vendosja është e vlefshme"""
        # Koha duhet të jetë në hapje-mbyllje
        if start_time + program.duration > self.instance_data.closing_time:
            return False
        
        # Kontrollo priority blocks
        if not self._can_place_on_channel(program, start_time, channel_id):
            return False
        
        return True

    def _calculate_score(self, scheduled_list: List[Schedule]) -> int:
        """Njehso pikën totale të një liste programesh të planifikuar"""
        total_score = 0
        for schedule in scheduled_list:
            # Secila Schedule ka një fitness/score
            if hasattr(schedule, 'fitness') and schedule.fitness is not None:
                total_score += schedule.fitness
            elif hasattr(schedule, 'program') and hasattr(schedule.program, 'score'):
                total_score += schedule.program.score
        return total_score
