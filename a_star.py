"""

AStar search

author: Ashwin Bose (@atb033)

"""
    
class AStar():
    def __init__(self, cbs):
        self.cbs = cbs
        self.env = cbs.env

    def reconstruct_path(self, came_from, current):
        total_path = [current]
        while current in came_from.keys():
            current = came_from[current]
            total_path.append(current)
        return total_path[::-1]

    def search(self, agent_name):
        """
        low level search 
        """
        initial_state = self.cbs.get_location_state(agent_name)

        step_cost = 1
        
        closed_set = set()
        open_set = {initial_state} 

        came_from = {}

        g_score = {} 
        g_score[initial_state] = 0

        f_score = {} 

        f_score[initial_state] = self.cbs.admissible_heuristic(initial_state, agent_name)
        
        while open_set: #open_set start from only self.agent_dict[agent_name]["start"]
            
            temp_dict = {open_item:f_score.setdefault(open_item, float("inf")) for open_item in open_set}
            current = min(temp_dict, key=temp_dict.get)
            
            if self.cbs.is_at_goal(current, agent_name):
#                 if(g_score.setdefault(current, float("inf")) < self.env.window_size):
#                     for i in range(self.env.window_size - g_score.setdefault(current, float(0))):
#                         came_from[self.cbs.state_wait(current)] = current
#                         current = self.cbs.state_wait(current)
                return self.reconstruct_path(came_from, current)

            if g_score.setdefault(current, float("inf")) == self.env.window_size: #window-size can make here
                return self.reconstruct_path(came_from, current)

            open_set -= {current} #path that can take
            closed_set |= {current}  #path that have taken

            neighbor_list = self.cbs.get_neighbors(current, agent_name) # actions you can choose

            for neighbor in neighbor_list:
                if neighbor in closed_set: 
                    continue
                    
                tentative_g_score = g_score.setdefault(current, float("inf")) + step_cost

                if neighbor not in open_set:
                    open_set |= {neighbor}
                elif tentative_g_score >= g_score.setdefault(neighbor, float("inf")):
                    continue

                came_from[neighbor] = current

                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + self.cbs.admissible_heuristic(neighbor, agent_name)
        return []

