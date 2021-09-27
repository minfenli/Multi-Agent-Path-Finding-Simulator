"""

MAPF Simulator

author: Justin Li (@justin871030)

"""

import sys
import time
sys.path.insert(0, './')
from pbs import PBS
from copy import deepcopy
import matplotlib
from matplotlib.patches import Circle, Rectangle
import matplotlib.pyplot as plt
from matplotlib import animation

from random import randint

from environment import Environment
from controller import Shelf_Place, Parking_Place, Station, Controller

def time_use(time_list):
    count = 0 
    for i in time_list:
        count += i
    print("used time: " + str(count) + "s")
    return


def save_map_information_at_the_time(env, shelfs, stations, parkings, constraints, shelf_now_locations):
    shelf_locations = deepcopy(shelfs)
    station_locations = []
    for station_name, station in stations.items():
        station_locations += deepcopy(station.idle_locations)
        station_locations += deepcopy(station.busy_locations)
    parking_locations = deepcopy(parkings)
    agent_locations = []
    agent_shelf_locations = []
    agent_station_locations = []
    agent_parking_locations = []
    agent_target_locations = []
    constraints_locations = []
    agent_batterys = []
    
    shelf_now_locations = deepcopy(shelf_now_locations)
    
    for agent_name, agent in env.agent_dict.items():
        agent_locations.append(agent.location)
        agent_target_locations.append(agent.target)
        agent_batterys.append(agent.battery_power/agent.battery_limit)
                    
        agent_shelf_locations.append(agent.task.shelf_location)
        agent_station_locations.append(agent.task.station_location)
        
    for vc in constraints:
        constraints_locations.append((vc.location, vc.agent))
        #print(constraints_locations)
    return [shelf_locations, station_locations, parking_locations, agent_locations, shelf_now_locations,
            agent_shelf_locations, agent_station_locations, agent_target_locations, constraints_locations, agent_batterys]
    

def run(env, map_obstacle_list, station_dict, shelf_list, parking_list, agent_list, order_list, shelf_rate = 0.66, priority_by_order_time = True, not_allow_return = False, check_troubles = True, trouble_may_happen = False):
    
    map_time_location_data = []
    map_time_count_data = []
    map_finish_count_data = []
    
    env.read_map_by_2d_list(map_obstacle_list)
    env.set_agents(deepcopy(agent_list))
    
    stations = {}
    for station_name, station_list in station_dict.items():
        stations.update({station_name : Station(deepcopy(station_list))})
        
    start_point = int(len(shelf_list)*shelf_rate)
        
    controller = Controller(env.agent_dict, Parking_Place(deepcopy(parking_list)), Shelf_Place(deepcopy(shelf_list[:start_point]),deepcopy(shelf_list[start_point:])), stations)
    
    controller.add_orders(order_list)
    
    pbs = PBS(env, priority_by_order_time, not_allow_return) 

    time_count = 0
    
    map_time_location_data.append(save_map_information_at_the_time(env, shelf_list, stations, parking_list, pbs.constraints.vertex_constraints, deepcopy(controller.get_shelf_locations())))
    
    order_queue_finished = False
    
    env.init_shelf_obstacles(deepcopy(controller.shelf_place.idle_locations))

    while time_count < env.total_run_time:
        charges, charge_priority_list = controller.deal_with_charges()
        env.assign_charges(charges)
        tasks, order_priority_list = controller.deal_with_orders()
        env.assign_tasks(tasks)
        moves = controller.get_idle_agent_away()
        env.assign_moves(moves)
        
        time_start = time.time() #Timecount start

        solution = pbs.search(moves, charge_priority_list, order_priority_list)

        if not solution:
            print("solution not found")
            input()

        # Time count
        time_end = time.time()

        time_c= time_end - time_start 

        map_time_count_data.append(time_c)
        print("time step " + str(time_count) + ": " + str(time_c))

        for i in range(env.time_step_per_planning):
            if check_troubles:
                trouble_logs = env.update_one_timestep(trouble_may_happen)
                if(trouble_logs):
                    #input()
                    print(trouble_logs, "Trouble happened!")
                    pbs.solve_trouble_constraints(trouble_logs)
            else:
                env.update_one_timestep()
                
            map_time_location_data.append(save_map_information_at_the_time(env, shelf_list, stations, parking_list, pbs.constraints.vertex_constraints, deepcopy(controller.get_shelf_locations(env.get_finish_tasks()))))

        tasks = env.return_finish_tasks()
        
        controller.deal_with_finished_tasks(tasks)
        
        charges = env.return_finish_charges()
        controller.deal_with_finished_charges(charges)
        
        time_count += env.time_step_per_planning
        map_finish_count_data.append(controller.finish_count)
        
        if not controller.order_queue and not order_queue_finished:
            time_count = env.total_run_time - 10 * env.time_step_per_planning # 10 more rounds after assigning all tasks
            order_queue_finished = True
    
    return map_time_location_data, map_time_count_data, map_finish_count_data, env.get_time_cost_logs()

def visualize(env, location_data, interval = 200):
    
    dimension = env.dimension

    aspect = dimension[0] / dimension[1]

    fig = plt.figure(frameon=False, figsize=(4 * aspect, 4))
    ax = fig.add_subplot(111, aspect='equal')
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1, wspace=None, hspace=None)

    xmin = -0.5
    ymin = -0.5
    xmax = dimension[0] - 0.5
    ymax = dimension[1] - 0.5

    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)

    def animate(i):
        
        colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'brown']
        
        ax.patches = []
        ax.texts = []

        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='white', edgecolor='black'))

        text = ax.text(xmax - 0.5, ymax - 0.5, str(i))
        text.set_horizontalalignment('center')
        text.set_verticalalignment('center')

        time_data = location_data[i]

        for location in time_data[0]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='blue', alpha = 1))

        for location in time_data[1]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='red', alpha = 1))

        for location in time_data[2]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='green', alpha = 1))
            
        for index in range(len(time_data[8])):
            x, y = time_data[8][index][0].x, time_data[8][index][0].y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor= colors[time_data[8][index][1]%len(colors)], edgecolor='none', alpha = 0.2))

        for location in time_data[4]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='blue', edgecolor='black', alpha = 0.5))
            
        for index in range(len(time_data[5])):
            x, y = time_data[5][index].x, time_data[5][index].y
            ax.add_patch(Circle((x, y), 0.3, facecolor= 'white', edgecolor='black', alpha = 0.1))
            text = ax.text(x, y, str(index))
            text.set_horizontalalignment('center')
            text.set_verticalalignment('center')
        for index in range(len(time_data[6])):
            x, y = time_data[6][index].x, time_data[6][index].y
            ax.add_patch(Circle((x, y), 0.3, facecolor= 'white', edgecolor='black', alpha = 0.1))
            text = ax.text(x, y, str(index))
            text.set_horizontalalignment('center')
            text.set_verticalalignment('center')
        for index in range(len(time_data[7])):
            x, y = time_data[7][index].x, time_data[7][index].y
            ax.add_patch(Circle((x, y), 0.4, facecolor= 'none', edgecolor='red', alpha = 1, linewidth = 2))
            text = ax.text(x, y, str(index))
            text.set_horizontalalignment('center')
            text.set_verticalalignment('center')
            
        for index in range(len(time_data[3])):
            x, y = time_data[3][index].x, time_data[3][index].y
            ax.add_patch(Circle((x, y), 0.3, facecolor= 'orange', edgecolor='black', alpha = time_data[9][index]))
            text = ax.text(x, y, str(index))
            text.set_horizontalalignment('center')
            text.set_verticalalignment('center')
            
        


    def init():
        ax.patches = []
        ax.texts = []
        
        ax.add_patch(Rectangle((xmin, ymin), xmax - xmin, ymax - ymin, facecolor='white', edgecolor='black'))

        time_data = location_data[0]

        for location in time_data[0]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='blue', alpha = 1))

        for location in time_data[1]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='red', alpha = 1))

        for location in time_data[2]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='none', edgecolor='green', alpha = 1))

        for location in time_data[3]:
            x, y = location.x, location.y
            ax.add_patch(Circle((x, y), 0.3, facecolor= 'orange', edgecolor='black'))

        for location in time_data[4]:
            x, y = location.x, location.y
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), 1, 1, facecolor='blue', edgecolor='black', alpha = 0.5))


    return animation.FuncAnimation(fig=fig, func=animate, frames=len(location_data), init_func=init,
                                  interval=interval, blit=False)