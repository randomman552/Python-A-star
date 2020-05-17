import multiprocessing
import AStar
from typing import Optional, Dict, Tuple


class Movement2DSolver(AStar.Movement2DSolver):
    """
    Sub-class of the normal Movement2DSolver with an update method for updating shared memory.
        Init parameters:
            start (tuple) - The starting string.
            goal (tuple) - The goal string.
            diagonal_enabled (bool) - Defines whether diagonal movement is permitted.
            shared_memory (dict) - The shared memory object to update.
            allowed_states (set) - Any states in this set will be permitted.
            if it is empty, then all states will be permitted.
            forbidden_states (set) - Any states in this set will not be permitted.
            if it is empty and the allowed_states is also empty, no states will be forbidden.
            visited_queue (set) - A state to initalise the visited queue to, anything in this set will be ignored.
    """

    def __init__(self, shared_memory: dict, start: Tuple[int, int], goal: Tuple[int, int],  allowed_states: Optional[set] = set(), forbidden_states: Optional[set] = set(), diagonal_enabled: Optional[bool] = False):
        super().__init__(
            start,
            goal,
            diagonal_enabled,
            allowed_states,
            forbidden_states
        )
        self.shared_memory = shared_memory

    def update(self):
        """Method to update the shared memory object with the current visited_queue."""

        self.shared_memory["visited"] = self.visited_queue


class BaseSolverProcess(multiprocessing.Process):
    """
    Base class for running an AStar solver on another process (to allow for updating of the pygame display to happen in parallel)
        How to use:
            If you want this to use a different solver, then you can create a subclass of it, 
            in the __init_ method call super().__init__() with the solver you want to use, a shared memory dict, and then its kwargs.
            You can see an example of this with Movement2DProcess in the AStar_multiprocessing.py file.
        Init parameters:
            start (Tuple[int, int]) - The coordinates to start at.
            goal (Tuple[int, int]) - The coordinates to end at.
            shared_memory (dict) - The shared memory object created by the MapCreationWindow object.
            allowed_set (set) - The set of allowed locations for the solver.
            forbidden_set (set) - The set of forbidden locations for the solver.
            diagonal_enabled (bool) - Whether diagonal movement is allowed.
    """

    def __init__(self, solver: AStar.AStarSolver, shared_memory: dict, **kwargs):

        super(BaseSolverProcess, self).__init__()
        # Save the shared memory, kwargs, and solver class for later
        self.shared_memory = shared_memory
        self.kwargs = kwargs
        self.solver = solver

    def run(self):
        """
        Override of the normal process run method, creates and runs the solver.
        If there is no path, it will cancel and set the "path" in shared memory to -1.
        """

        # Instantiate sovler
        solver = self.solver(shared_memory=self.shared_memory, **self.kwargs)

        try:
            solver.solve()
            self.shared_memory["path"] = solver.path
        except Exception as e:
            self.shared_memory["path"] = -1
            print(e)

        self.shared_memory["time taken"] = solver.time_taken
        self.shared_memory["nodes considered"] = solver.nodes_considered


class Movement2DProcess(BaseSolverProcess):
    """
    Class for running a movement solver on another process.
        Init parameters:
            start (Tuple[int, int]) - The coordinates to start at.
            goal (Tuple[int, int]) - The coordinates to end at.
            shared_memory (dict) - The shared memory object created by the MapCreationWindow object.
            allowed_set (set) - The set of allowed locations for the solver.
            forbidden_set (set) - The set of forbidden locations for the solver.
            diagonal_enabled (bool) - Whether diagonal movement is allowed.
    """

    def __init__(self, start: Tuple[int, int], goal: Tuple[int, int], shared_memory: dict, allowed_states: Optional[set] = set(), forbidden_states: Optional[set] = set(), diagonal_enabled: Optional[bool] = False):
        super(Movement2DProcess, self).__init__(
            Movement2DSolver,
            shared_memory,
            start=start,
            goal=goal,
            allowed_states=allowed_states,
            forbidden_states=forbidden_states,
            diagonal_enabled=diagonal_enabled
        )
