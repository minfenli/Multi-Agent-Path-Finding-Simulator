"""

MAPF Simulator

author: Justin Li (@justin871030)

"""

import sys
sys.path.insert(0, './')
import random
from copy import deepcopy


class Location:
    def __init__(self, x=-1, y=-1):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __str__(self):
        return str((self.x, self.y))

class State:
    def __init__(self, time, location):
        self.time = time
        self.location = location
    def __eq__(self, other):
        return self.time == other.time and self.location == other.location
    def __hash__(self):
        return hash(str(self.time)+str(self.location.x) + str(self.location.y))
    def is_equal_except_time(self, state):
        return self.location == state.location
    def __str__(self):
        return str((self.time, self.location.x, self.location.y))
    
class Agent:
    def __init__(self, name, location, target):
        self.name = name
        self.location = location
        self.target = target
        self.path_list = []
        self.finished_path_list = []
        self.state = Agent_State(self)
        self.task = Agent_Task()
        self.finished_task = []
        self.charge = Agent_Charge()
        self.finished_charge = []
        
        self.charge_limit = 1000
        self.battery_limit = 2000
        self.battery_power = 2000
        
        self.time_cost = 0
        self.time_cost_log = []
        
        pop_buffer = []

    def set_location(self, location):
        self.location = location
    
    def set_target(self, target):
        self.target = target
    
    def update_path(self, path_list):
        self.path_list += path_list
        
    def assign_task(self, task):
        self.task = task
        self.time_cost = 0
        if self.task.return_task:
            self.target = self.task.station_location
        else:    
            self.target = self.task.shelf_location
        self.state.state = 1
        
    def assign_charge(self, charge):
        self.charge = charge
        self.target = self.charge.location
        self.state.state = 5
        
    def assign_move(self, target):
        self.target = target
        self.state.state = 7
    
    def update_state(self): 
        self.time_cost += 1
        if self.state.next(): # true if finish a task
            self.finished_task.append(self.task)
            self.task = Agent_Task()
            self.time_cost_log.append(self.time_cost)
            return self.time_cost

    def is_idle(self):
        return self.state.state == 0
    
    def is_getting_away(self):
        return self.state.state == 7
    
    def __str__(self):
        return "Name: " + self.name  + \
            "Location: (" + str(self.location.x) + ", " + str(self.location.y) + ") " + \
            "Target: (" + str(self.target.x) + ", " + str(self.target.y) + ") " + \
            "State: (" + str(self.state) + ") "

class Agent_Task:
    def __init__(self, shelf_location = Location(), station_location = Location(), return_task = False):
        self.shelf_location = shelf_location
        self.station_location = station_location
        self.return_task = return_task

class Agent_Charge:
    def __init__(self, charge_location = Location()):
        self.location = charge_location
        
    
class Agent_State:
    def __init__(self, agent, state = 0, hold_time_cost = 3, wait_time_cost = 3, put_time_cost = 3):
        
        self.state_dict = {0: "Idle", 1: "Move", 2:"Hold", 3:"Carry", 4:"Wait", 5: "Return", 6: "Put", 7: "Back"}
        self.state = state
        self.agent = agent
        self.hold_time_cost = hold_time_cost
        self.hold_time_count = 0
        self.wait_time_cost = wait_time_cost
        self.wait_time_count = 0
        self.put_time_cost = put_time_cost
        self.put_time_count = 0
    
    def __str__(self):
        return self.state_dict[self.state]
    
    def check_repeat_constraints(self, location, path_list):
        for i in path_list:
            if(location == i):
                return True
        return False
            
    
    def next(self): #True if finish a task
        if (self.state == 0):
            self.agent.battery_power -= 1
            return False
        if (self.state == 1):
            self.agent.battery_power -= 5
            if self.agent.location == self.agent.target:
                    self.state = 2
                    return False
            if len(self.agent.path_list):
                if not self.check_repeat_constraints(self.agent.location,self.agent.path_list):
                    self.agent.finished_path_list.append(self.agent.location)
                self.agent.location = self.agent.path_list.pop(0)
                if self.agent.location == self.agent.target:
                    self.state = 2
                return False
            return False
        if (self.state == 2):
            self.agent.battery_power -= 5
            if(self.hold_time_count < self.hold_time_cost):
                self.hold_time_count += 1
                return False
            if self.agent.task.return_task:
                self.agent.target = self.agent.task.shelf_location
            else:
                self.agent.target = self.agent.task.station_location
            self.hold_time_count = 0
            self.state = 3
        if (self.state == 3):
            self.agent.battery_power -= 5
            if self.agent.location == self.agent.target:
                    self.state = 4
                    return False
            if len(self.agent.path_list):
                if not self.check_repeat_constraints(self.agent.location,self.agent.path_list):
                    self.agent.finished_path_list.append(self.agent.location)
                self.agent.location = self.agent.path_list.pop(0)
                    
                if self.agent.location == self.agent.target:
                    self.state = 4
                return False
            return False
        if (self.state == 4):
            self.agent.battery_power -= 5
            if(self.wait_time_count < self.wait_time_cost):
                self.wait_time_count += 1
                return False
            self.wait_time_count = 0
            self.state = 0
            return True
        
        #charge
        if (self.state == 5):
            self.agent.battery_power -= 5
            if self.agent.location == self.agent.target:
                    self.state = 6
                    return False
            if len(self.agent.path_list):
                if not self.check_repeat_constraints(self.agent.location,self.agent.path_list):
                    self.agent.finished_path_list.append(self.agent.location)
                self.agent.location = self.agent.path_list.pop(0)
                    
                if self.agent.location == self.agent.target:
                    self.state = 6
                return False
            return False
        if (self.state == 6):
            self.agent.battery_power +=20
            if self.agent.battery_power >= self.agent.battery_limit:
                self.agent.battery_power = self.agent.battery_limit
                self.state = 0
                self.agent.finished_charge.append(self.agent.charge)
                self.agent.charge = Agent_Charge()
            return False
        
        #move
        
        if (self.state == 7):
            self.agent.battery_power -= 5
            if self.agent.location == self.agent.target:
                    self.state = 0
                    return False
            if len(self.agent.path_list):
                if not self.check_repeat_constraints(self.agent.location,self.agent.path_list):
                    self.agent.finished_path_list.append(self.agent.location)
                self.agent.location = self.agent.path_list.pop(0)
                    
                if self.agent.location == self.agent.target:
                    self.state = 0
                return False
            return False
    


class Environment:
    def __init__(self, dimension = [0,0], agents = [], obstacles = [], window_size = 10, buffer_size = 10,\
                 time_step_per_planning = 10, total_run_time = 100):
        
        self.dimension = dimension
        
        self.obstacles = obstacles
        
        self.window_size = window_size
        
        self.buffer_size = buffer_size
        
        self.time_step_per_planning = time_step_per_planning
        
        self.total_run_time = total_run_time
        
        self.agent_dict = {}

        self.make_agent_dict(agents)
        
    def read_map_by_2d_list(self, map_list = []):
        if not len(map_list):
            self.dimension = [0,0]
            self.obstacles = []
            return
        self.dimension = [len(map_list[0]), len(map_list)]
        self.obstacles = []
        for y in range(len(map_list)):
            for x in range(len(map_list[0])):
                if (map_list[y][x] == 1):
                    self.obstacles.append((x,y))
                    
    def update_one_timestep(self, trouble_may_happen = False): #return conflict logs if conflict
        troubles = {}
        only_one = True
        for agent_name, agent in self.agent_dict.items():
            if(trouble_may_happen and random.randint(0,99)%99 == 0 and agent.state.state == 1 and only_one):
                if(self.get_trouble(agent)):
                    print(agent_name, agent.location, "One agent is out of its paths.")
                    only_one = False
                    input()
                    self.agent_dict[agent_name].finished_path_list += self.agent_dict[agent_name].path_list
                    self.agent_dict[agent_name].path_list = []
                    troubles.update({agent_name: agent.location})  
            else:
                agent.update_state()
                
            if(not agent.task.return_task):
                if(agent.state.state == 2):
                    self.release_shelf_obstacle(deepcopy(agent.task.shelf_location))
            elif(agent.state.state == 2):
                    self.add_shelf_obstacle(deepcopy(agent.task.shelf_location))

        for agent_name, agent in self.agent_dict.items():
            for agent_name_check, agent_check in self.agent_dict.items():
                if(agent_name == agent_name_check):
                    continue
                #if need to check to path which has been done, add checking finished_path_list here.
                for location in agent_check.path_list:
                    if (location == agent.location):
                        print(agent_name_check ,agent_name, location, "Conflict may happened, enter everything to skip.")
                        input()
                        self.agent_dict[agent_name_check].finished_path_list += self.agent_dict[agent_name_check].path_list
                        self.agent_dict[agent_name_check].path_list = []
                        troubles.update({agent_name_check: agent_check.location})  
                        break
        return troubles
    
    def get_trouble(self, agent):
        if  agent.location.x+1 < self.dimension[0] and (agent.location.x+1, agent.location.y) not in self.obstacles and Location(agent.location.x+1, agent.location.y) not in agent.path_list:
            agent.finished_path_list.append(Location(agent.location.x, agent.location.y))
            agent.location = Location(agent.location.x+1, agent.location.y)
            return True
        if agent.location.y+1 < self.dimension[1] and (agent.location.x, agent.location.y+1) not in self.obstacles and Location(agent.location.x, agent.location.y+1) not in agent.path_list:
            agent.finished_path_list.append(Location(agent.location.x, agent.location.y))
            agent.location = Location(agent.location.x, agent.location.y+1)
            return True
        if agent.location.x-1 >= 0 and (agent.location.x-1, agent.location.y) not in self.obstacles and Location(agent.location.x-1, agent.location.y) not in agent.path_list:
            agent.finished_path_list.append(Location(agent.location.x, agent.location.y))
            agent.location = Location(agent.location.x-1, agent.location.y)
            return True
        if agent.location.y-1 >= 0 and (agent.location.x, agent.location.y-1) not in self.obstacles and Location(agent.location.x, agent.location.y-1) not in agent.path_list:
            agent.finished_path_list.append(Location(agent.location.x, agent.location.y))
            agent.location = Location(agent.location.x, agent.location.y-1)
            return True
        return False
        
    def set_agents(self, agents):
        self.make_agent_dict(agents)
        
    def assign_tasks(self, tasks):
        for agent_name, task in tasks.items():
            self.agent_dict[agent_name].assign_task(task)
    
    def assign_charges(self, charges):
        for agent_name, charge_location in charges.items():
            self.agent_dict[agent_name].assign_charge(charge_location)
            
    def assign_moves(self, names):
        for agent_name in names:
            self.agent_dict[agent_name].assign_move(self.get_random_location(self.agent_dict[agent_name].location))

    def get_finish_tasks(self):#just read
        finish_task_list = []
        for agent_name, agent in self.agent_dict.items():
            finish_task_list += agent.finished_task
        return finish_task_list 
    
    def get_time_cost_logs(self):
        logs = {}
        for agent_name, agent in self.agent_dict.items():
            logs.update({agent_name: agent.time_cost_log})
        return logs
            
    def return_finish_tasks(self): #clean
        finish_task_list = []
        for agent_name, agent in self.agent_dict.items():
            finish_task_list += agent.finished_task
            agent.finished_task = []
        return finish_task_list
    
    def return_finish_charges(self):
        finish_charge_list = []
        for agent_name, agent in self.agent_dict.items():
            finish_charge_list += agent.finished_charge
            agent.finished_charge = []
        return finish_charge_list
    
    def set_agent_target(self, agent_name, target):
        self.agent_dict[agent_name].target = target

    def make_agent_dict(self, agents):
        for agent in agents:
            self.agent_dict.update({agent.name : agent})
            
    def get_random_location(self, start):
        x, y = random.randint(0,self.dimension[0]-1), random.randint(0,self.dimension[1]-1)
        while((x,y) in self.obstacles or Location(x,y) == start):
            x, y = random.randint(0,self.dimension[0]-1), random.randint(0,self.dimension[1]-1)
        return Location(x,y)
    
    def init_shelf_obstacles(self, locations):
        for location in locations:
            self.obstacles.append((location.x, location.y))
    
    def release_shelf_obstacle(self, location):
        for index in range(len(self.obstacles)):
            if(self.obstacles[index] == (location.x, location.y)):
                self.obstacles.pop(index)
                break
    
    def add_shelf_obstacle(self, location):
        if (location.x, location.y) not in self.obstacles:
            self.obstacles.append((location.x, location.y))