"""

MAPF Simulator

author: Justin Li (@justin871030)

"""

import sys
sys.path.insert(0, './')
from math import fabs
from environment import Agent_Task, Agent_Charge
from copy import deepcopy
import random

class Order:
    def __init__(self, shelf_location, station_name): #shelf which is asked by the station
        self.shelf_location = shelf_location
        self.station_name = station_name
    def set_shelf_location(location):
        self.shelf_location = shelf_location

class Return:
    def __init__(self, shelf_location, station_name): #shelf which is asked by the station
        self.shelf_location = shelf_location
        self.station_name = station_name
    def set_shelf_location(location):
        self.shelf_location = shelf_location
        
class Station:
    def __init__(self, locations):
        self.idle_locations = locations
        self.busy_locations = []
    
    def get_idle_location(self):
        if not self.idle_locations:
            return False
        location = self.idle_locations.pop(-1)
        self.busy_locations.append(location)
        return location
    
    def free_busy_location(self, location):
        for busy_location_index in range(len(self.busy_locations)):
            if(location == self.busy_locations[busy_location_index]):
                self.idle_locations.append(self.busy_locations.pop(busy_location_index))
                break
                
    def __str__(self):
        return "idle_locations:" + str(len(self.idle_locations)) + " busy_locations:" + str(len(self.busy_locations))

class Parking_Place:
    def __init__(self, locations):
        self.idle_locations = locations
        self.busy_locations = []
    
    def get_nearest_idle_location(self, start_location):
        if not self.idle_locations:
            return False
        
        temp_distance = float('inf')
        temp_index = -1

        for index in range(len(self.idle_locations)):
            distance = self.location_distance(self.idle_locations[index], start_location)
            if(distance < temp_distance):
                temp_distance = distance
                temp_index = index
        location = self.idle_locations.pop(temp_index)
        self.busy_locations.append(location)
        
        return location
    
    def __str__(self):
        return "idle_locations:" + str(len(self.idle_locations)) + " busy_locations:" + str(len(self.busy_locations))
    
    def get_nearest_idle_location_or_current_location(self, start_location):
        
        temp_distance = float("inf")
        temp_index = -1

        for index in range(len(self.idle_locations)):
            distance = self.location_distance(self.idle_locations[index], start_location)
            if(distance < temp_distance):
                temp_distance = distance
                temp_index = index
        
        if(temp_index == -1):
            return False
        else:
            location = self.idle_locations.pop(temp_index)
            self.busy_locations.append(location)
            return location
    
    
    def get_idle_location(self):
        if not self.idle_locations:
            return False
        
        location = self.idle_locations.pop(-1)
        self.busy_locations.append(location)
        return location
    
    def free_busy_location(self, location):
        for busy_location_index in range(len(self.busy_locations)):
            if(location == self.busy_locations[busy_location_index]):
                self.idle_locations.append(self.busy_locations.pop(busy_location_index))
                break
                    
    def location_distance(self, location1, location2):
        return fabs(location1.x - location2.x) + fabs(location1.y - location2.y)

class Shelf_Place:
    def __init__(self, locations, backups):
        self.idle_locations = locations
        self.busy_locations = []
        self.backup_location = backups
    
    def get_location(self, target):
        for index in range(len(self.idle_locations)):
            if(self.idle_locations[index] == target):
                location = self.idle_locations.pop(index)
                self.busy_locations.append(location)
                return location
        return False
    
    def change_location(self, origin_location):
        for index in range(len(self.idle_locations)):
            if(self.busy_locations[index] == origin_location and self.backup_location):
                new_location = self.backup_location.pop(random.randint(0,len(self.backup_location)-1))
                location = self.busy_locations.pop(index)
                self.busy_locations.append(new_location)
                self.backup_location.append(location)
                return new_location
        return origin_location
    
    def free_busy_location(self, location):
        for busy_location_index in range(len(self.busy_locations)):
            if(location == self.busy_locations[busy_location_index]):
                self.idle_locations.append(self.busy_locations.pop(busy_location_index))
                break
                
    def __str__(self):
        return "idle_locations:" + str(len(self.idle_locations)) + " busy_locations:" + str(len(self.busy_locations))

    
class Controller:
    def __init__(self, agent_dict, parking_place, shelf_place, station_dict):
        self.agent_dict = agent_dict
        self.parking_place = parking_place
        self.shelf_place = shelf_place
        self.station_dict = station_dict
        self.order_queue = []
        self.return_queue = []
        
        self.move_location_list = []
        
        self.finish_count = 0
        
    def get_shelf_locations(self, finished_tasks = []):
        locations = deepcopy(self.shelf_place.idle_locations)
        for location in self.shelf_place.busy_locations:
            shelf = deepcopy(location)
            for return_task in self.return_queue:
                if(return_task.shelf_location == shelf):
                    shelf = return_task.station_location
                    break
                    
            for agent_name, agent in self.agent_dict.items():
                if not agent.is_idle() and agent.task.shelf_location == location:
                    if agent.task.return_task and agent.state.state == 1:
                        shelf = agent.task.station_location
                    elif not agent.state.state ==1:
                        shelf = deepcopy(agent.location)
                    
            
            for task in finished_tasks:
                if(not task.return_task):
                    if(task.shelf_location == shelf):
                        shelf = task.station_location
                        
            
            locations.append(shelf)
        return locations
        
    def init_parking_places_with_agents(self):
        for agent_name, agent in self.agent_dict.items():
            for index in range(len(self.parking_place.idle_locations)):
                if(agent.location == self.parking_place.idle_locations[index]):
                    self.parking_place.busy_locations.append(self.parking_place.idle_locations.pop(index))
                    break
    
    def add_orders(self, orders):
        self.order_queue = self.order_queue + orders
        
    def deal_with_orders(self):
        priority_list = []
        
        if not self.order_queue:
            return {}
        
        except_list = []
        
        index = 0 
        
        task_dict, except_list_return = self.deal_with_returns()
        
        except_list += except_list_return
        
        while(index < len(self.order_queue)):
            task = self.deal_with_one_order(self.order_queue[index], except_list)
            if task:
                task_dict.update(task)
                self.order_queue.pop(index)
                for agent_name in task.keys():
                    priority_list.append(agent_name)
            else:
                index += 1

        return task_dict, priority_list
                
        
    def deal_with_one_order(self, order, except_list):
        
        shelf_location = self.shelf_place.get_location(order.shelf_location)

        if(shelf_location):
            agent_name = self.get_nearest_agent(order.shelf_location, except_list)
            if(agent_name):
                for station_name, station in self.station_dict.items():
                    if(station_name == order.station_name):
                        station_location = station.get_idle_location()
                        if(station_location):
                            self.move_location_list.append(shelf_location)
                            self.move_location_list.append(station_location)
                            except_list.append(agent_name)
                            return {agent_name: Agent_Task(shelf_location, station_location)}
            #if fail, free
            self.shelf_place.free_busy_location(shelf_location)
                
        return False
    
    def deal_with_charges(self):
        
        priority_list = []
        charge_dict = {}
        
        for agent_name, agent in self.agent_dict.items():
            
            if agent.battery_power < agent.charge_limit and agent.is_idle():
                
                parking_location = \
                self.parking_place.get_nearest_idle_location_or_current_location(self.agent_dict[agent_name].location)
                
                if(parking_location):
                    self.move_location_list.append(parking_location)
                    charge_dict.update({agent_name: Agent_Charge(parking_location)})
                    priority_list.append(agent_name)
                
        return charge_dict, priority_list
        
    
    def deal_with_returns(self):
        
        if not self.return_queue:
            return {}, []
        
        task_dict = {}
        
        index = 0 
        
        except_list = []
        
        while(index < len(self.return_queue)):
            # 10% to start a return task
            if(random.randint(0,9)!=9):
                index += 1
                continue
            agent_name = self.get_nearest_agent(self.return_queue[index].station_location, except_list)
            if(agent_name):
                self.move_location_list.append(self.return_queue[index].shelf_location)
                self.move_location_list.append(self.return_queue[index].station_location)
                
                task_dict.update({agent_name: self.return_queue[index]})
                self.return_queue.pop(index)
                except_list.append(agent_name)
            else:
                index += 1
                
        return task_dict, except_list
    
    def deal_with_finished_tasks(self, tasks):
        for task in tasks:
            self.finish_count += 1
            if not task.return_task:
                # 10% to change to a different shelf location
                if(random.randint(0,9)%9 == 1):
                    task.shelf_location = self.shelf_place.change_location(task.shelf_location)
                self.return_queue.append(Agent_Task(deepcopy(task.shelf_location), task.station_location, True)) #return task
                continue
            self.shelf_place.free_busy_location(task.shelf_location)
            for station_name, station in self.station_dict.items(): 
                station.free_busy_location(task.station_location)

    def deal_with_finished_charges(self, charges):
        for charge in charges:
            self.parking_place.free_busy_location(charge.location)
        
    def location_distance(self, location1, location2):
        return fabs(location1.x - location2.x) + fabs(location1.y - location2.y)
    
    def get_nearest_agent(self, target, except_list):
        temp_distance = float('inf')
        temp_name = ""
        
        for agent_name, agent in self.agent_dict.items():
            if agent_name in except_list:
                continue
            if((agent.is_idle() or agent.is_getting_away()) and agent.battery_power > agent.charge_limit):
                distance = self.location_distance(agent.location, target)
                if(distance < temp_distance):
                    temp_distance = self.location_distance(agent.location, target)
                    temp_name = agent_name
        if(temp_name == ""):
            return False
        return temp_name
    
    # deal with the idle agent stand on the location using by a task
    def get_idle_agent_away(self):
        move_list = []
        
        for target in self.move_location_list:
            for agent_name, agent in self.agent_dict.items():
                if (agent.is_idle() and agent.location == target) or (agent.is_getting_away() and agent.target == target):
                    move_list.append(agent_name)
        self.move_location_list = []
        
        return move_list

    def __str__(self):
        string = ""
        for i in self.order_queue:
            string += str(i.shelf_location) + "\n"
        return string