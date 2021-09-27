"""

MAPF Simulator

author: Justin Li (@justin871030)

"""

from controller import Order
from environment import Location, Agent
from copy import deepcopy
from random import randint

def make_order_list(shelfs, station_names, num): #random choose a shelf that a order need
    list = []
    for i in range(num):
        list.append(Order(shelfs[randint(0,len(shelfs)-1)], station_names[randint(0,len(station_names)-1)]))
    return list

def get_default_test_data_kiva(order_num = 50, agent_num = 4, pile_num = 2, map_type = "square"):
    # 0s are the positions that the robot can reach, 1s are the forbidden positions
    # the stations, parking places (the location which may cause troubles) should all be obstacles
    
    if(agent_num > 16 or agent_num < 0):
        agent_num = 16
    if(pile_num > 8 or pile_num < 0):
        agent_num = 8
    
    map_obstacle_dict = {
        "square":[
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0] ],
    #    0         5         10        15  
        "rectangle":[
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0] ],
    #    0         5         10        15  
        "line":[
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],   
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1] ],
    #    0         5         10        15  
        "doubleline":[
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0] ],
    #    0         5         10        15  
    
    
    
    
    }
    
    map_obstacle_list = map_obstacle_dict[map_type]

    #station_list is a list of stations that each station have a series of positions to place shelfs
    station_dict_dict = {
        "square":{
        "station1":[
        Location(15,3), Location(15,4), Location(15,5), Location(15,6), Location(16,3), Location(17,3),
        Location(18,3), Location(16,6), Location(17,6), Location(18,6)
        ] },
        "rectangle":{
        "station1":[
        Location(16,2), Location(16,3), Location(16,4), Location(16,5), Location(16,6), Location(16,7), 
        Location(17,7), Location(18,7), Location(17,2), Location(18,2)
        ] },
        "line":{
        "station1":[
        Location(18,0), Location(18,1), Location(18,2), Location(18,3), Location(18,4), Location(18,5), 
        Location(18,6), Location(18,7), Location(18,8), Location(18,9)
        ] },
        "doubleline":{
        "station1":[
        Location(18,2), Location(18,3), Location(18,4), Location(18,5), Location(18,6), Location(18,7), 
        Location(16,3), Location(16,4), Location(16,5), Location(16,6)
        ] },
    }
    
    station_dict = station_dict_dict[map_type]

    #station_list is a list of shelfs' positions where the shelfs are set
    shelf_list = [
        Location(0,1), Location(0,2), Location(0,3), Location(0,4), Location(0,5), Location(0,6),
        Location(0,7), Location(0,8), 
        Location(1,0), Location(2,0), Location(3,0), Location(4,0), Location(5,0), Location(6,0),
        Location(7,0), Location(8,0), Location(9,0), Location(10,0), Location(11,0), Location(12,0),
        Location(1,9), Location(2,9), Location(3,9), Location(4,9), Location(5,9), Location(6,9),
        Location(7,9), Location(8,9), Location(9,9), Location(10,9), Location(11,9), Location(12,9), 
        Location(2,2), Location(3,2), Location(5,2), Location(6,2), Location(8,2),
        Location(9,2), Location(11,2), Location(12,2),
        Location(2,3), Location(3,3), Location(5,3), Location(6,3), Location(8,3),
        Location(9,3), Location(11,3), Location(12,3),
        Location(2,4), Location(3,4), Location(5,4), Location(6,4), Location(8,4),
        Location(9,4), Location(11,4), Location(12,4),
        Location(2,6), Location(2,7), Location(3,6), Location(3,7), Location(4,6), Location(4,7),
        Location(5,6), Location(5,7), Location(6,6), Location(6,7),
        Location(8,6), Location(8,7), Location(9,6), Location(9,7), Location(10,6), Location(10,7),
        Location(11,6), Location(11,7), Location(12,6), Location(12,7),Location(13,6), Location(13,7),
    ]

    #parking_list is a list of parking places where the robots charge.
    parking_list = [
        Location(13,9), Location(14,9), Location(15,9), Location(16,9),Location(13,0), Location(14,0), Location(15,0), Location(16,0),
    ]
    
    parking_list = parking_list[:pile_num]
    
    start_list = [
        Location(13,9), Location(14,9), Location(15,9), Location(16,9), Location(13,0), Location(14,0), Location(15,0), Location(16,0), Location(17,0), Location(18,0), Location(17,9), Location(18,9), Location(1,1), Location(7,1), Location(1,8), Location(7,8)
    ]

    #agent_list is a list of robots which should be placed at the parking places at start that be set as the default position.
    agent_list = [
        Agent("agent0", start_list[0], start_list[0]),
         Agent("agent1", start_list[1], start_list[1]),
         Agent("agent2", start_list[2], start_list[2]),
         Agent("agent3", start_list[3], start_list[3]),
          Agent("agent4", start_list[4], start_list[4]),
          Agent("agent5", start_list[5], start_list[5]),
          Agent("agent6", start_list[6], start_list[6]),
          Agent("agent7", start_list[7], start_list[7]),
          Agent("agent8", start_list[8], start_list[8]),
          Agent("agent9", start_list[9], start_list[9]),
          Agent("agent10", start_list[10], start_list[10]),
          Agent("agent11", start_list[11], start_list[11]),
          Agent("agent12", start_list[12], start_list[12]),
          Agent("agent13", start_list[13], start_list[13]),
          Agent("agent14", start_list[14], start_list[14]),
          Agent("agent15", start_list[15], start_list[15])
    ]
    
    agent_list = agent_list[:agent_num]


    #agent_list is a list of orders including target shelves
    order_list = make_order_list(shelf_list, list(station_dict.keys()), order_num)
    
    return map_obstacle_list, station_dict, shelf_list, parking_list, agent_list, order_list

def get_default_test_data_big(order_num = 50, agent_num = 8, pile_num = 4):
    # 0s are the positions that the robot can reach, 1s are the forbidden positions
    # the stations, parking places (the location which may cause troubles) should all be obstacles
    map_obstacle_list = [
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0], 
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],  
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],  
        [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],   
        [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1] 
    ]
    #    0         5         10        15  

    #station_list is a list of stations that each station have a series of positions to place shelfs
    station_dict = {
        "station1":[
        Location(17,2), Location(17,3), Location(17,4)
        ],
        "station2":[
        Location(17,6), Location(17,7), Location(17,8)
        ],
        "station3":[
        Location(17,10), Location(17,11), Location(17,12)
        ],
        "station4":[
        Location(17,14), Location(17,15), Location(17,16)
        ],
        "station5":[
        Location(15,2), Location(15,3), Location(15,4)
        ],
        "station6":[
        Location(15,6), Location(15,7), Location(15,8)
        ],
        "station7":[
        Location(15,10), Location(15,11), Location(15,12)
        ],
        "station8":[
        Location(15,14), Location(15,15), Location(15,16)
        ]
    }

    #station_list is a list of shelfs' positions where the shelfs are set
    shelf_list = [
        Location(2,2), Location(3,2), Location(5,2), Location(6,2), Location(8,2), Location(9,2), Location(11,2), Location(12,2),
        Location(2,3), Location(3,3), Location(5,3), Location(6,3), Location(8,3), Location(9,3), Location(11,3), Location(12,3),
        Location(2,4), Location(3,4), Location(5,4), Location(6,4), Location(8,4), Location(9,4), Location(11,4), Location(12,4),
        Location(2,6), Location(3,6), Location(5,6), Location(6,6), Location(8,6), Location(9,6), Location(11,6), Location(12,6),
        Location(2,7), Location(3,7), Location(5,7), Location(6,7), Location(8,7), Location(9,7), Location(11,7), Location(12,7),
        Location(2,8), Location(3,8), Location(5,8), Location(6,8), Location(8,8), Location(9,8), Location(11,8), Location(12,8),
        Location(2,10), Location(3,10), Location(5,10), Location(6,10), Location(8,10), Location(9,10), Location(11,10), Location(12,10),
        Location(2,11), Location(3,11), Location(5,11), Location(6,11), Location(8,11), Location(9,11), Location(11,11), Location(12,11),
        Location(2,12), Location(3,12), Location(5,12), Location(6,12), Location(8,12), Location(9,12), Location(11,12), Location(12,12),
        Location(2,14), Location(3,14), Location(5,14), Location(6,14), Location(8,14), Location(9,14), Location(11,14), Location(12,14),
        Location(2,15), Location(3,15), Location(5,15), Location(6,15), Location(8,15), Location(9,15), Location(11,15), Location(12,15),
        Location(2,16), Location(3,16), Location(5,16), Location(6,16), Location(8,16), Location(9,16), Location(11,16), Location(12,16),
    ]
    
    parking_list = [
        Location(0,1), Location(0,2), Location(0,3), Location(0,4), Location(0,5), Location(0,6), Location(0,7), 
        Location(0,8),Location(0,9), Location(0,10), Location(0,11), Location(0,12), Location(0,13), Location(0,14), 
        Location(0,15), Location(0,16), Location(0,17)
    ]
    
    parking_list = parking_list[:pile_num]
    
    start_list = [
        Location(0,1), Location(0,2), Location(0,3), Location(0,4), Location(0,5), Location(0,6), Location(0,7), 
        Location(0,8),Location(0,9), Location(0,10), Location(0,11), Location(0,12), Location(0,13), Location(0,14), 
        Location(0,15), Location(0,16), Location(0,17),
        Location(1,0), Location(2,0), Location(3,0), Location(4,0), Location(5,0), Location(6,0), Location(7,0), Location(8,0)
    ]

    #agent_list is a list of robots which should be placed at the parking places at start that be set as the default position.
    agent_list = [
        Agent("agent0", start_list[0], start_list[0]),
        Agent("agent1", start_list[1], start_list[1]),
        Agent("agent2", start_list[2], start_list[2]),
        Agent("agent3", start_list[3], start_list[3]),
        Agent("agent4", start_list[4], start_list[4]),
        Agent("agent5", start_list[5], start_list[5]),
        Agent("agent6", start_list[6], start_list[6]),
        Agent("agent7", start_list[7], start_list[7]),
        Agent("agent8", start_list[8], start_list[8]),
        Agent("agent9", start_list[9], start_list[9]),
        Agent("agent10", start_list[10], start_list[10]),
        Agent("agent11", start_list[11], start_list[11]),
        Agent("agent12", start_list[12], start_list[12]),
        Agent("agent13", start_list[13], start_list[13]),
        Agent("agent14", start_list[14], start_list[14]),
        Agent("agent15", start_list[15], start_list[15]),
        Agent("agent16", start_list[16], start_list[16]),
        Agent("agent17", start_list[17], start_list[17]),
        Agent("agent18", start_list[18], start_list[18]),
        Agent("agent19", start_list[19], start_list[19]),
        Agent("agent20", start_list[20], start_list[20]),
        Agent("agent21", start_list[21], start_list[21]),
        Agent("agent22", start_list[22], start_list[22]),
        Agent("agent23", start_list[23], start_list[23])
    ]
    
    agent_list = agent_list[:agent_num]


    #agent_list is a list of orders including target shelves
    order_list = make_order_list(shelf_list, list(station_dict.keys()), order_num)
    
    return map_obstacle_list, station_dict, shelf_list, parking_list, agent_list, order_list
