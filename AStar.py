#!/usr/bin/python3
from queue import PriorityQueue
import itertools
import random
import time
import threading
from typing import Optional, Set, Tuple

# States


class State(object):
    """
    Base state class. Contains placeholder functions and creates attributes common to all states.
        How to use:
            You should overload some of the methods of this state for use with your own solvers.
            get_dist(self) - Should return the distance heuristic for what you are solving.
            create_children(self) - Should append children states to the "self.children" attribute of your object.
        Init parameters:
            value - The value of this state.
            parent - This states parent.
            start - The start value for this state.
            goal - The goal value for this state.
    """

    def __init__(self, value, parent, start=0, goal=0):
        self.children = []
        self.parent = parent
        self.value = value
        self.dist = 0
        if parent:
            # If this state has a parent, take some parameters from the parent
            self.path = parent.path[:]
            self.path.append(value)
            self.start = parent.start
            self.goal = parent.goal
        else:
            self.path = [value]
            self.start = start
            self.goal = goal

    def get_dist(self):
        """
        Placeholder function for getting distance
        """

        pass

    def create_children(self, forbidden_states=set()):
        """
        Placeholder function for creating children of this state\n
        Can optionally be passed a forbidden_states set to prevent these states from being generated.
        """

        pass


class StateString(State):
    """
    State class used by the StringSolver class.
        Init parameters:
            value - The value of this state.
            parent - This states parent.
            start - The start value for this state.
            goal - The goal value for this state.
    """

    def __init__(self, value: str, parent: Optional[State], start: str = "", goal: str = ""):

        super(StateString, self).__init__(value, parent, start, goal)
        self.dist = self.get_dist()

    def get_dist(self) -> int:
        """
        Calculate the distance heuristic for this object.
        """

        dist = 0

        # If the value of this is the same as the goal, then the distance is zero.
        if self.value == self.goal:
            return dist

        # Calculate how far we are away from the goal (defined by how far each letter is out from it's goal possition)
        for i in range(len(self.goal)):
            letter = self.goal[i]

            if self.value.count(letter) == 1:
                # Distance can be worked out like this where there are no repeating characters
                dist += abs(i - self.value.index(letter))
            else:
                # Using this slightly more complex code makes the algorithm slower on strings with only one occurance of each character
                # But massively improves the performance for strings with many of the same character contained within
                val_store = list(self.value)
                goal_store = list(self.goal)
                while val_store.count(letter) > 0:
                    val_letter_pos = val_store.index(letter)
                    goal_letter_pos = goal_store.index(letter)
                    dist += abs(goal_letter_pos - val_letter_pos)
                    val_store.pop(val_letter_pos)
                    goal_store.pop(goal_letter_pos)
        return dist

    def create_children(self, forbidden_states: Optional[set] = set()):
        """
        Create the children of this state\n
        Can optionally be passed a forbidden_states set to prevent these states from being generated.
        """

        if not self.children:
            # Generate all permutations of the string (with one swap)
            permutations = set()
            for i in range(len(self.goal)):
                for x in range(len(self.goal)):
                    val = list(self.value)
                    val[i], val[x] = val[x], val[i]

                    # Convert permutation to a string
                    val = "".join(val)

                    if self.__valid_perm(val, permutations):
                        # If the permutation is valid, add it to the permutations list
                        permutations.add(val)
            for item in permutations:

                if not(item in forbidden_states):
                    child = StateString(item, self)
                    self.children.append(child)

    def __valid_perm(self, val: str, permutations: Set[str]):
        "Check whether permutation is a valid one."
        if val == self.value:
            return False
        elif val in permutations:
            return False
        return True


class State2DMovement(State):
    """
    State class used by the Movement2DSolver.
        Init paramters:
            value (tuple) - The position of this state.
            parent (State) - The parent of this state.
            start (tuple) - The start coordinate.
            goal (tuple) - The goal coordinate
            diagonal_enabled (bool) - Whether diagonal moving is enabled.
    """

    def __init__(self, value: Tuple[int, int], parent: State, start: Optional[Tuple[int, int]] = None, goal: Optional[Tuple[int, int]] = None, diagonal_enabled: Optional[bool] = False):

        super(State2DMovement, self).__init__(
            tuple(value), parent, start, goal)
        self.diagonal_enabled = diagonal_enabled
        self.dist = self.get_dist()

    def get_dist(self):
        """Calculate the distance heuristic for this object."""

        dist = 0

        # If we have reached the goal, the distance is 0
        if self.value == self.goal:
            return dist

        # If this objects parent is set, then calculat the heuristic.
        if self.parent:
            # Calculate the distance vector between this state and its parent state (g).
            vector = [self.parent.value[0] - self.value[0],
                      self.parent.value[1] - self.value[1]]

            self.g = abs(vector[0]) + abs(vector[1])

            # Calculate the distance between this state and the goal state (h).
            self.h = 0
            for i in range(len(self.value)):
                self.h += abs(self.value[i] - self.goal[i])

            # Distance is the combination of g and h
            dist = self.g + self.h
        else:
            self.g = 0
            self.h = 0

        return dist

    def create_children(self, forbidden_states: Optional[set] = set()):
        """
        Create the children of this state\n
        Can optionally be passed a forbidden_states set to prevent these states from being generated.
        """

        # If children have not already been generated
        if not self.children:
            # Create transformation vectors. If diagonal movement is enabled, create the diagonal move vectors.
            allowed_moves = [[1, 0], [0, 1], [-1, 0], [0, -1]]
            if self.diagonal_enabled:
                allowed_moves += [[1, 1], [1, -1], [-1, 1], [-1, -1]]

            # Create new state objects with the vectors
            for i in allowed_moves:
                val = (self.value[0] + i[0], self.value[1] + i[1])
                if not(val in forbidden_states):
                    child = State2DMovement(
                        val, self, diagonal_enabled=self.diagonal_enabled)
                    self.children.append(child)

# Solvers


class AStarSolver:
    """
    Base A* solver class, all other solvers are to be based on this class.
        How to use:
            In order to create a functional solver based on this, you must overload the following methods:
            __get_state_state(self) - Should return the starting state for the solver you are implementing.
            __validate(self) - A function that validates the variables passed to the object when creating it.
        Init parameters:
            start - The start value.
            goal - The goal the algorithm aims for.
            allowed_states (set) - Any states in this set will be permitted. If it is empty, then all states will be permitted.
            forbidden_states (set) - Any states in this set will not be permitted. Ff it is empty and the allowed_states is also empty, no states will be forbidden.
            visited_queue (set) - A state to initalise the visited queue to, anything in this set will be ignored.

    """

    def __init__(self, start, goal, allowed_states: Optional[set] = set(), forbidden_states: Optional[set] = set(), visited_queue: Optional[set] = set()):

        if not(visited_queue):
            visited_queue = forbidden_states.difference(allowed_states)

        self.allowed_states = allowed_states
        self.forbidden_states = forbidden_states
        self.visited_queue = visited_queue

        self.path = []
        self.priority_queue = PriorityQueue()

        # Start and goal must be copies to prevent the solver from interacting with other components
        self.start = start[:]
        self.goal = goal[:]
        self.start_state = None
        self.time_taken = 0
        self.nodes_considered = 0

    def Solve(self):
        """
        Creates a solution on how to get from the start, to the goal.\n
        This method returns the path created, but it can also be gained by using the .path atribute.\n
        The .paths_considered and .time_taken atributes can be looked at if you want to gauge the performance of this algorithm.\n
        If no solution is found, this method will raise an exception, which can then be caught with a try except.
        """

        start_time = time.time()
        startState = self.start_state

        # Check if startState is set.
        if startState != None:
            count = 0

            # Put the starting object into the priority queue
            self.priority_queue.put((0, count, startState))

            # Loop until the path is complete, or until the queue is emptied
            while (not self.path) and (self.priority_queue.qsize()):
                closestChild = self.priority_queue.get()[2]
                closestChild.create_children(self.visited_queue)

                # If the goal and start value are the same, then nothing needs to be done
                if closestChild.value == self.goal:
                    self.path = closestChild.path
                    break

                # Place the children of the child that is currently being evaluated into the queue
                for child in closestChild.children:
                    if not(closestChild.value in self.visited_queue):
                        count += 1
                        if not child.dist:
                            self.path = child.path
                            break
                        self.priority_queue.put((child.dist, count, child))

                # Place the evalutaed child into the visited queue
                self.visited_queue.add(closestChild.value)

            # If the loop completes without setting the path, raise an exception
            if not self.path:
                raise Exception("No path")

            end_time = time.time()
            self.time_taken = int(round((end_time - start_time) * 1000, 0))
            self.nodes_considered = count
            return self.path
        else:
            # If the startState is not set, raise an exception
            raise Exception(
                "startState is not set. Are you instansiating the wrong class?")

    def __get_start_state(self) -> State:
        """Placeholder method for generating the starting state object."""

        return None

    def __validate(self) -> bool:
        """Placehodler method for validating the starting information given to the solver."""

        return True


class StringSolver(AStarSolver):
    """
    A* solver for string reorganisation.
        Init parameters:
            start - The starting string.
            goal - The goal string.
            allowed_states (set) - Any states in this set will be permitted. If it is empty, then all states will be permitted.
            forbidden_states (set) - Any states in this set will not be permitted. If it is empty and the allowed_states is also empty, no states will be forbidden.
            visited_queue (set) - A state to initalise the visited queue to, anything in this set will be ignored.
    """

    def __init__(self, start: str, goal: str, allowed_states: Optional[set] = set(), forbidden_states: Optional[set] = set(), visited_queue: Optional[set] = set()):
        super(StringSolver, self).__init__(start, goal,
                                           allowed_states, forbidden_states, visited_queue)
        if not self.__validate():
            raise Exception("Invalid inputs")
        else:
            self.start_state = self.__get_start_state()

    def __get_start_state(self) -> StateString:
        """Returns the first navigation state."""

        return StateString(self.start, 0, self.start, self.goal)

    def __validate(self) -> bool:
        """Method for validating the starting information given to the solver."""

        for goal_char in self.goal:
            if self.goal.count(goal_char) != self.start.count(goal_char):
                return False
        for start_char in self.start:
            if self.start.count(start_char) != self.goal.count(start_char):
                return False
        return True


class Movement2DSolver(AStarSolver):
    """
    A* solver for movement on a 2D grid.
        Init parameters:
            start (tuple) - The starting string.
            goal (tuple) - The goal string.
            diagonal_enabled (bool) - Defines whether diagonal movement is permitted.
            allowed_states (set) - Any states in this set will be permitted.
            if it is empty, then all states will be permitted.
            forbidden_states (set) - Any states in this set will not be permitted.
            if it is empty and the allowed_states is also empty, no states will be forbidden.
            visited_queue (set) - A state to initalise the visited queue to, anything in this set will be ignored.
    """

    def __init__(self, start, goal, diagonal_enabled: bool, allowed_states: Optional[set] = set(), forbidden_states: Optional[set] = set(), visited_queue: Optional[set] = set()):
        super(Movement2DSolver, self).__init__(tuple(start), tuple(
            goal), allowed_states, forbidden_states, visited_queue)
        self.diagonal_enabled = diagonal_enabled
        self.start_state = self.__get_start_state()

    def __get_start_state(self) -> State2DMovement:
        """Get the starting state object for this solver."""

        return State2DMovement(self.start, 0, self.diagonal_enabled, self.start, self.goal)


def StringSolver_example():
    goal = """Despacito"""
    temp = list(goal)
    random.shuffle(temp)
    start = ""
    for char in temp:
        start += char
    a = StringSolver(start, goal)
    a.Solve()
    for num, step in enumerate(a.path):
        print(str(num) + ": " + str(step))
    print("Time Taken: " + str(a.time_taken))
    print("Nodes Considered: " + str(a.nodes_considered))


def Movement2DSolver_example():
    goal = [100, 100]
    start = [1, 1]
    allowed_states = []
    forbidden_states = []
    a = Movement2DSolver(start, goal, True, allowed_states,
                         forbidden_states)
    a.Solve()
    for num, step in enumerate(a.path):
        print(str(num) + ": " + str(step))
    print("Time Taken: " + str(a.time_taken))
    print("Nodes Considered: " + str(a.nodes_considered))


if __name__ == "__main__":
    # Movement2DSolver_example()
    # string_solve_example
    pass
