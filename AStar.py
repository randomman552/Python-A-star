#!/usr/bib/python3
from queue import PriorityQueue
import itertools
import random
import time
import threading

#States
class State(object):
    "Base state class. Contains placeholder functions and creates atributes common to all states."
    def __init__(self, value, parent, start = 0, goal = 0):
        self.children = []
        self.parent = parent
        self.value = value
        self.dist = 0
        if parent:
            #If this state has a parent, take some parameters from the parent
            self.path = parent.path[:]
            self.path.append(value)
            self.start = parent.start
            self.goal = parent.goal
        else:
            self.path = [value]
            self.start = start
            self.goal = goal

    def GetDist(self):
        "Placeholder function for getting distance"
        pass

    def CreateChildren(self):
        "Placeholder function for creating children of this state"
        pass
class State_String(State):
    "State class used with the String_Solver class"
    def __init__(self, value, parent, start = 0, goal = 0):
        super(State_String, self).__init__(value, parent, start, goal)
        self.dist = self.GetDist()
    
    def GetDist(self):
        if self.value == self.goal:
            return 0
        dist = 0
        for i in range(len(self.goal)):
            #Calculate how far we are away from the goal (defined by how far each letter is out from it's goal possition)
            letter = self.goal[i]
            if self.value.count(letter) == 1:
                #Distance can be worked out like this where there are no repeating characters
                dist += abs(i - self.value.index(letter))
            else:
                #Using this slightly more complex code makes the algorithm slower on strings with only one occurance of each character
                #But massively improves the performance for strings with many of the same character contained within
                val_store = list(self.value)
                goal_store = list(self.goal)
                while val_store.count(letter) > 0:
                    val_letter_pos = val_store.index(letter)
                    goal_letter_pos = goal_store.index(letter)
                    dist += abs(goal_letter_pos - val_letter_pos)
                    val_store.pop(val_letter_pos)
                    goal_store.pop(goal_letter_pos)
        return dist

    def CreateChildren(self):
        if not self.children:
            #Generate all permutations of the string (with one swap)
            permutations = []
            for i in range(len(self.goal)):
                for x in range(len(self.goal)):
                    val = list(self.value)
                    val[i],val[x] = val[x],val[i]
                    if self.__validPerm(val, permutations):
                        #If the permutation is valud, add it to the permutations list
                        permutations.append(val)
            for item in permutations:
                #Convert each permutation to a string and create objects
                child = State_String(self.__toStr(item), self)
                self.children.append(child)
    
    def __toStr(self, Input):
        "Convert a list of characters into a string"
        output = ""
        for char in Input:
            output += char
        return output

    def __validPerm(self, val, permutations):
        "Check whether permutation is a valid one."
        if val == list(self.value):
            return False
        elif val in permutations:
            return False
        return True
class State_2D_Movement(State):
    "State class used with the Movement_2D_Solver"
    def __init__(self, value, parent, diagonal_enabled=False, start = 0, goal = 0):
        super(State_2D_Movement, self).__init__(value, parent, start, goal)
        self.diagonal_enabled = diagonal_enabled
        self.dist = self.GetDist()

    def GetDist(self):
        if self.value == self.goal:
            return 0
        dist = 0
        if self.parent:
            self.g = self.parent.g + 1
            self.h = 0
            for i in range(len(self.value) - 1):
                self.h += abs(self.value[i] - self.goal[i])
            dist = self.g + self.h
        else:
            self.g = 0
            self.h = 0
        return dist

    def CreateChildren(self):
        if not self.children:
            allowed_moves = [[1,0],[0,1],[-1,0],[0,-1]]
            if self.diagonal_enabled:
                allowed_moves += [[1,1],[1,-1],[-1,1],[-1,-1]]
            for i in allowed_moves:
                val = [self.value[0] + i[0], self.value[1] + i[1]]
                child = State_2D_Movement(val, self, self.diagonal_enabled)
                self.children.append(child)

#Solvers
class AStar_Solver:
    """Base A* solver class, all other solvers are to be based on this class.
    Look at the string_solver for an example of implementation."""
    def __init__(self, start, goal, allowed_states = None):
        self.path = []
        self.visitedQueue = []
        self.PriorityQueue = PriorityQueue()
        #Start and goal must be copies to prevent the solver from interacting with other components
        self.start = start[:]
        self.goal = goal[:]
        self.allowed_states = allowed_states
        self.start_state = None
        self.time_taken = 0
        self.nodes_considered = 0
    
    def Solve(self):
        """Creates a solution on how to get from the start, to the goal.\n
        This method returns the path created, but it can also be gained by using the .path atribute.\n
        The .paths_considered and .time_taken atributes can be looked at if you want to gauge the performance of this algorithm.\n
        If no solution is found, this method will raise an exception, which can then be caught with a try except."""
        start_time = time.time()
        startState = self.start_state
        #Check if startState is set.
        if startState != None:
            count = 0
            self.PriorityQueue.put((0, count, startState))
            while (not self.path) and (self.PriorityQueue.qsize()):
                closestChild = self.PriorityQueue.get()[2]
                if closestChild.dist == 0:
                    self.path = closestChild.path
                    break
                closestChild.CreateChildren()
                self.visitedQueue.append(closestChild.value)
                for child in closestChild.children:
                    if (child.value not in self.visitedQueue) and (self.allowed_states == None or child.value in self.allowed_states):
                        count += 1
                        if not child.dist:
                            self.path = child.path
                            break
                        self.PriorityQueue.put((child.dist, count, child))
            if not self.path:
                raise Exception("No path")
            end_time = time.time()
            self.time_taken = int(round((end_time - start_time) * 1000, 0))
            self.nodes_considered = count
            return self.path
        else:
            #If the startState is not set, raise an exception
            raise Exception("startState is not set. Are you instansiating the wrong class?")

    def __get_start_state(self):
        return None

    def __validate(self):
        return True
class String_Solver(AStar_Solver):
    """A* solver for string reorganisation.
    start = The start state of the string, e.g. 'bcda'.
    goal = The desired end state of the string, e.g. 'abcd'.
    allowed_states is an optional argument, when set it will prevent any children being created outside of these set states."""
    def __init__(self, start, goal, allowed_states = None):
        super(String_Solver, self).__init__(start, goal, allowed_states)
        if not self.__validate():
            raise Exception("Invalid inputs")
        else:
            self.start_state = self.__get_start_state()

    def __get_start_state(self):
        "Returns the state of the first node."
        return State_String(self.start, 0, self.start, self.goal)

    def __validate(self):
        "Validate the data put into the solver."
        for goal_char in self.goal:
            if self.goal.count(goal_char) != self.start.count(goal_char):
                return False
        for start_char in self.start:
            if self.start.count(start_char) != self.goal.count(start_char):
                return False
        return True
class Movement_2D_Solver(AStar_Solver):
    def __init__(self, start, goal, allowed_states = None, diagonal_enabled = False):
        super(Movement_2D_Solver, self).__init__(start, goal, allowed_states)
        self.diagonal_enabled = diagonal_enabled
        self.start_state = self.__get_start_state()
    
    def __get_start_state(self):
        return State_2D_Movement(self.start, 0, self.diagonal_enabled, self.start, self.goal)

def String_Solver_Example():
    goal = """Did you ever hear the tragedy of Darth Plagueis "the wise"?"""
    temp = list(goal)
    random.shuffle(temp)
    start = ""
    for char in temp:
        start += char
    a = String_Solver(start, goal)
    a.Solve()
    for num,step in enumerate(a.path):
        print(str(num) + ": " + str(step))
    print("Time Taken: " + str(a.time_taken))
    print("Nodes Considered: " + str(a.nodes_considered))

def Movement_2D_Solver_Example():
    goal = [11,11]
    start = [1,1]
    allowed_states = None
    a = Movement_2D_Solver(start, goal, allowed_states, diagonal_enabled = True)
    a.Solve()
    for num,step in enumerate(a.path):
        print(str(num) + ": " + str(step))
    print("Time Taken: " + str(a.time_taken))
    print("Nodes Considered: " + str(a.nodes_considered))

if __name__ == "__main__":
    Movement_2D_Solver_Example()
    #String_Solver_Example()