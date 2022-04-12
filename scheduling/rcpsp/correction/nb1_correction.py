import numpy as np
from typing import List, Hashable
def sgs_algorithm(rcpsp_model: RCPSPModel, 
                  permutation_of_task: List[Hashable], predecessors=None):
    # Compute predecessors for each task. 
    if predecessors is None:
        predecessors = {k: set() for k in rcpsp_model.tasks_list}
        for k in rcpsp_model.successors:
            succ = rcpsp_model.successors[k]
            for s in succ:
                predecessors[s].add(k)
    schedule = {k: {"start_time": None,
                    "end_time": None}
                for k in rcpsp_model.tasks_list}
    duration_task = {k: rcpsp_model.mode_details[k][1]["duration"] for k in rcpsp_model.mode_details}
    resources_availability = {r: rcpsp_model.get_resource_availability_array(r) 
                              for r in rcpsp_model.resources_list}
    
    done = set()
    minimum_time = {t: 0 for t in rcpsp_model.tasks_list}
    while True:
        # Select task to be scheduled at this round...
        # etc
        next_task = next(x for x in permutation_of_task 
                         if all(p in done for p in predecessors[x]) 
                         and x not in done)
        
        if duration_task[next_task] == 0:
            time_to_schedule_task = minimum_time[next_task]
        else:
            time_to_schedule_task = next(t for t in range(minimum_time[next_task], rcpsp_model.horizon)
                                         if 
                                         all(min(resources_availability[r][t:t+duration_task[next_task]])>=
                                             rcpsp_model.mode_details[next_task][1][r]
                                             for r in resources_availability))
        schedule[next_task]["start_time"] = time_to_schedule_task
        schedule[next_task]["end_time"] = time_to_schedule_task+duration_task[next_task]
        for r in resources_availability:
            need = rcpsp_model.mode_details[next_task][1][r]
            if r in rcpsp_model.non_renewable_resources:
                resources_availability[r][schedule[next_task]["start_time"]:]-=need
            else:
                resources_availability[r][schedule[next_task]["start_time"]:schedule[next_task]["end_time"]]-=need
        for s in rcpsp_model.successors[next_task]:
            minimum_time[s] = max(minimum_time[s], schedule[next_task]["end_time"])
        done.add(next_task) 
        if all(x in done for x in schedule):
            break
    return schedule  

