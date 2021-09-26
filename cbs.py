"""

MAPF Simulator

author: Justin Li (@justin871030)

"""

import sys
sys.path.insert(0, './')
from a_star import AStar
from environment import State, Location
from math import fabs
from itertools import combinations
from copy import deepcopy
from random import shuffle

class HighLevelNode:
    def __init__(self): #depth is number of tree node
        self.solution = {}
        self.constraint_dict = {}
        self.priority_list = []
        self.cost = 0

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.solution == other.solution and self.cost == other.cost

    def __hash__(self):
        return hash(self.cost)
    
    def __lt__(self, other):
        return self.cost < other.cost

class Conflict:
    VERTEX = 1
    EDGE = 2
    def __init__(self):
        self.time = -1
        self.type = -1

        self.agent_1 = ''
        self.agent_2 = ''

        self.location_1 = Location()
        self.location_2 = Location()

    def __str__(self):
        return '(' + str(self.time) + ', ' + self.agent_1 + ', ' + self.agent_2 + \
             ', '+ str(self.location_1) + ', ' + str(self.location_2) + ')'

class VertexConstraint:
    def __init__(self, location, agent = 0):
        self.location = location
        self.agent = agent

    def __eq__(self, other):
        return self.location == other.location
    def __hash__(self):
        return hash(str(self.location))
    def __str__(self):
        return '(' + str(self.location) + ')'

class EdgeConstraint:
    def __init__(self, time, location_1, location_2):
        self.time = time
        self.location_1 = location_1
        self.location_2 = location_2
    def __eq__(self, other):
        return self.time == other.time and self.location_1 == other.location_1 \
            and self.location_2 == other.location_2
    def __hash__(self):
        return hash(str(self.time) + str(self.location_1) + str(self.location_2))
    def __str__(self):
        return '(' + str(self.time) + ', '+ str(self.location_1) +', '+ str(self.location_2) + ')'

class Constraints:
    def __init__(self):
        self.vertex_constraints = set()

    def add_constraint(self, other):
        self.vertex_constraints |= other.vertex_constraints
        
    def remove_constraint(self, other):
        self.vertex_constraints -= other.vertex_constraints

    def __str__(self):
        return "VC: " + str([str(vc) for vc in self.vertex_constraints]) 
    
class PBS:
    def __init__(self, environment, priority_by_order_time = True):
        self.env = environment
        self.a_star = AStar(self)
        self.constraints = Constraints()
        self.constraint_dict = {}
        self.retry_time_if_fail = 5
        self.priority_list = []
        self.priority_by_order_time = priority_by_order_time
        
    def search(self, move_priority_list = [], charge_priority_list = [], order_priority_list = []):
        
        if not self.priority_list:
            for agent_name in self.env.agent_dict.keys():
                self.priority_list.append(agent_name)
                
        for agent_name in charge_priority_list:
            for index in range(len(self.priority_list)):
                if(self.priority_list[index] == agent_name):
                    self.priority_list = [self.priority_list[index]] + self.priority_list[:index] + self.priority_list[index+1:]
        
        for agent_name in move_priority_list:
            for index in range(len(self.priority_list)):
                if(self.priority_list[index] == agent_name):
                    self.priority_list = [self.priority_list[index]] + self.priority_list[:index] + self.priority_list[index+1:]

        for agent_name in order_priority_list:
            for index in range(len(self.priority_list)):
                if(self.priority_list[index] == agent_name):
                    if(self.priority_by_order_time):
                        self.priority_list = self.priority_list[:index] + self.priority_list[index+1:] + [self.priority_list[index]]
                        check_start_point = len(self.priority_list) -1
                    else:
                        check_start_point = index
                    break
            for index in range(check_start_point - 1):
                if(self.env.agent_dict[self.priority_list[index]].target == self.env.agent_dict[agent_name].location):
                    self.priority_list = self.priority_list[:index] + [self.priority_list[check_start_point]] + self.priority_list[index:check_start_point] + self.priority_list[check_start_point+1:]
                    break
 
        
        start = HighLevelNode()
        
        start.priority_list = self.priority_list
        
        start.solution = self.compute_solution(start.priority_list)
        
        if start.solution:
            
            print("solution found")
            
            return self.generate_plan(start.solution)
        
        count = 0
        
        while count < self.retry_time_if_fail:
            
            shuffle(start.priority_list)
            
            start.solution = self.compute_solution(start.priority_list)
        
            if start.solution:
            
                print("solution found")
                
                return self.generate_plan(start.solution)
            
            count += 1
        

        return {}
    
    def get_neighbors(self, state, agent_name):
        neighbors = []
        
        
        # Right action
        n = State(state.time + 1, Location(state.location.x+1, state.location.y))
        if self.state_valid(n, agent_name):
            neighbors.append(n)
            
        # Left action
        n = State(state.time + 1, Location(state.location.x-1, state.location.y))
        if self.state_valid(n, agent_name):
            neighbors.append(n)
            
        # Up action
        n = State(state.time + 1, Location(state.location.x, state.location.y+1))
        if self.state_valid(n, agent_name):
            neighbors.append(n)
        # Down action
        n = State(state.time + 1, Location(state.location.x, state.location.y-1))
        if self.state_valid(n, agent_name):
            neighbors.append(n)   
            
        # Wait action
        n = State(state.time + 1, state.location)
        if self.state_valid(n, agent_name):
            neighbors.append(n)
            
        return neighbors
    
    def state_wait(self, state):
        return State(state.time + 1, state.location)

    def create_constraints_from_path(self, solution, agent_num = 0): # agent_num for who made constraints
        if(not len(solution)):
            return
        for i in range(0,len(solution)):
            self.constraints.vertex_constraints |= {VertexConstraint(solution[i], agent_num)}

    
    def get_state(self, agent_name, solution, t):
        if t < len(solution[agent_name]):
            return solution[agent_name][t]
        else:
            return solution[agent_name][-1]

    def state_valid(self, state, agent_name, allow_repeat_path = True):
        if State(0, self.env.agent_dict[agent_name].location).is_equal_except_time(state):
            return True
        elif VertexConstraint(state.location) not in self.constraints.vertex_constraints:
            if State(0, self.env.agent_dict[agent_name].task.shelf_location).is_equal_except_time(state):
                return True
            if State(0, self.env.agent_dict[agent_name].task.station_location).is_equal_except_time(state):
                return True
            if State(0, self.env.agent_dict[agent_name].charge.location).is_equal_except_time(state):
                return True
        
        # if allow repeat paths 
        if (allow_repeat_path):
            for location in self.env.agent_dict[agent_name].path_list:
                if(location == state.location):
                    return True
            
        return state.location.x >= 0 and state.location.x < self.env.dimension[0] \
            and state.location.y >= 0 and state.location.y < self.env.dimension[1] \
            and VertexConstraint(state.location) not in self.constraints.vertex_constraints \
            and (state.location.x, state.location.y) not in self.env.obstacles

    def admissible_heuristic(self, state, agent_name):
        goal = self.env.agent_dict[agent_name].target
        return fabs(state.location.x - goal.x) + fabs(state.location.y - goal.y)

    def get_location_state(self, agent_name):
        if(self.env.agent_dict[agent_name].path_list):
            return State(0, self.env.agent_dict[agent_name].path_list[-1])
        return State(0, self.env.agent_dict[agent_name].location)
    
    def is_at_goal(self, state, agent_name):
        goal_state = State(0, self.env.agent_dict[agent_name].target)
        return state.is_equal_except_time(goal_state)
    
    def compute_solution(self, priority_list):
        solution = {}
        self.release_constraints()
        for agent in priority_list:
            local_solution = self.a_star.search(agent)
            
            # this function for checking whether an agent has no choice, even the current location
            if not local_solution:
                return False

            solution.update({agent:local_solution})
            self.update_path_list(agent, local_solution)
        
        return solution
    

    def compute_solution_cost(self, solution):
        return sum([len(path) for path in solution.values()])
    
    def update_states(self, solution, time):
        for agent, path in solution.items():
            for state in path:
                if(state['t'] == time):
                    self.env.agent_dict[agent].location = Location(state['x'], state['y'])
    
    def generate_plan(self, solution):
        plan = {}
        for agent, path in solution.items():
            path_dict_list = [{'t':state.time, 'x':state.location.x, 'y':state.location.y} for state in path]
            plan[agent] = path_dict_list
        return plan
    
    def update_path_list(self, agent, path):
        if not path:
            return
        
        path_list = [state.location for state in path]
        start = path_list.pop(0)
        
        #deal with buffer of waits
        while(len(self.env.agent_dict[agent].path_list)>=2 and self.env.agent_dict[agent].path_list[-1] == self.env.agent_dict[agent].path_list[-2]):
            self.env.agent_dict[agent].path_list.pop(-2)
            
        #deal with waiting out of the target
        while(path_list and fabs(path_list[-1].x - self.env.agent_dict[agent].target.x) + fabs(path_list[-1].y - self.env.agent_dict[agent].target.y) == 1):
            path_list.pop(-1)
            
        
        append_num = self.env.buffer_size - len(self.env.agent_dict[agent].path_list)
        self.env.agent_dict[agent].update_path(path_list[:append_num])
        self.create_constraints_from_path([start]+path_list[:append_num], int(agent.split("agent")[1]))
        
    
    def release_constraints(self):
        #print("re")
        constraints = Constraints()
        for agent_name, agent in self.env.agent_dict.items():
            for location in agent.finished_path_list:
                constraints.vertex_constraints |= {VertexConstraint(location)}
            agent.finished_path_list = []
                
        self.constraints.remove_constraint(constraints)
       
    
    def solve_trouble_constraints(self, agents_locations):
        #delete all the path constraint
        constraints = Constraints()
        for agent_name, location in agents_locations.items():
            for location in self.env.agent_dict[agent_name].finished_path_list:
                constraints.vertex_constraints |= {VertexConstraint(location)}
            self.env.agent_dict[agent_name].finished_path_list = []
        self.constraints.remove_constraint(constraints)
        #contraints on the re-start point
        for agent_name, location in agents_locations.items():
            self.constraints.vertex_constraints |= {VertexConstraint(location, int(agent_name.split("agent")[1]))}
            self.env.agent_dict[agent_name].path_list.append(location)
    
    def print_solution(self, solution):
        for agent, path in solution.items():
            path_dict_list = [{'t':state.time, 'x':state.location.x, 'y':state.location.y} for state in path]
            print(agent)
            print(path_dict_list)