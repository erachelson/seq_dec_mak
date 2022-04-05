from discrete_optimization.rcpsp.rcpsp_model_preemptive import RCPSPModelPreemptive
from discrete_optimization.rcpsp.specialized_rcpsp.rcpsp_specialized_constraints import \
    RCPSPModelSpecialConstraintsPreemptive, RCPSPModelSpecialConstraints
from discrete_optimization.rcpsp_multiskill.rcpsp_multiskill import MS_RCPSPModel, \
    SpecialConstraintsDescription, MS_RCPSPModel_Variant, MS_RCPSPSolution
from discrete_optimization.rcpsp.rcpsp_model import RCPSPModel
from typing import Union
import math
from copy import deepcopy

# WARNING works for singlemode versions !


def transform_preemptive_to_classical(rcpsp_model: Union[RCPSPModelPreemptive, MS_RCPSPModel],
                                      delta_time: int,
                                      preempt_partial_preemptive: bool = False):
    if preempt_partial_preemptive:
        preemptive_tasks = [t for t in rcpsp_model.tasks_list
                            if rcpsp_model.preemptive_indicator[t]]
    else:
        preemptive_tasks = [t for t in rcpsp_model.tasks_list
                            if rcpsp_model.preemptive_indicator[t]
                            and all(rcpsp_model.partial_preemption_data[t][1][r]
                                    for r in rcpsp_model.partial_preemption_data[t][1])]
    special_constraints: SpecialConstraintsDescription = rcpsp_model.special_constraints
    resource_blocking_data = []
    new_added_task = {}
    for task in preemptive_tasks:
        duration = rcpsp_model.mode_details[task][1]["duration"]
        if duration > delta_time:
            new_added_task[task] = []
            int_part = int(math.ceil(duration/delta_time))
            done_duration = 0
            for j in range(int_part):
                delta = min(delta_time, duration-done_duration)
                new_added_task[task] += [(str(task)+"-"+str(j), delta)]
                done_duration += delta
            #   print(done_duration, duration)
    resource_blocking_data = []

    new_tasks_list = list(rcpsp_model.tasks_list)
    for t in new_added_task:
        new_tasks_list.remove(t)
        for new_task in new_added_task[t]:
            new_tasks_list.append(new_task[0])
        rs = set([r for r in rcpsp_model.partial_preemption_data[t][1]
                  if not rcpsp_model.partial_preemption_data[t][1][r]])
        if len(rs) > 0:
            resource_blocking_data += [([p[0] for p in new_added_task[t]], rs)]
    # new_successors = deepcopy(rcpsp_model.successors)
    new_successors = {}
    for p in rcpsp_model.successors:
        if p not in new_added_task:
            new_successors[p] = []
            for s in rcpsp_model.successors[p]:
                if s in new_added_task:
                    new_successors[p] += [new_added_task[s][0][0]]
                else:
                    new_successors[p] += [s]
        else:
            for new_task_name in new_added_task[p]:
                new_successors[new_task_name[0]] = []
            for j in range(len(new_added_task[p])-1):
                new_successors[new_added_task[p][j][0]] += [new_added_task[p][j+1][0]]

            for s in rcpsp_model.successors[p]:
                if s in new_added_task:
                    new_successors[new_added_task[p][-1][0]] += [new_added_task[s][0][0]]
                else:
                    new_successors[new_added_task[p][-1][0]] += [s]
    new_mode_details = {}
    for s in rcpsp_model.mode_details:
        if s not in new_added_task:
            new_mode_details[s] = deepcopy(rcpsp_model.mode_details[s])
        else:
            for k in new_added_task[s]:
                new_mode_details[k[0]] = deepcopy(rcpsp_model.mode_details[s])
                new_mode_details[k[0]][1]["duration"] = k[1]

    new_special_constraints = SpecialConstraintsDescription(task_mode=special_constraints.task_mode,
                                                            start_times=special_constraints.start_times,
                                                            end_times=special_constraints.end_times,
                                                            start_times_window={},
                                                            end_times_window={},
                                                            partial_permutation=special_constraints.partial_permutation,
                                                            list_partial_order=special_constraints.list_partial_order,
                                                            start_together=[],
                                                            start_at_end=[],
                                                            start_at_end_plus_offset=[],
                                                            start_after_nunit=[],
                                                            disjunctive_tasks=[])
    for t in special_constraints.start_times_window:
        if t in new_added_task:
            new_special_constraints.start_times_window[new_added_task[t][0][0]] = special_constraints.start_times_window[t]
        else:
            new_special_constraints.start_times_window[t] = special_constraints.start_times_window[t]
    for t in special_constraints.end_times_window:
        if t in new_added_task:
            new_special_constraints.end_times_window[new_added_task[t][-1][0]] = special_constraints.end_times_window[t]
        else:
            new_special_constraints.end_times_window[t] = special_constraints.end_times_window[t]
    for s1, s2 in special_constraints.start_together:
        s1_1 = s1 if s1 not in new_added_task else new_added_task[s1][0][0]
        s2_1 = s2 if s2 not in new_added_task else new_added_task[s2][0][0]
        new_special_constraints.start_together += [(s1_1, s2_1)]
    for s1, s2, delta in special_constraints.start_after_nunit:
        s1_1 = s1 if s1 not in new_added_task else new_added_task[s1][0][0]
        s2_1 = s2 if s2 not in new_added_task else new_added_task[s2][0][0]
        new_special_constraints.start_after_nunit += [(s1_1, s2_1, delta)]
    for s1, s2 in special_constraints.start_at_end:
        s1_1 = s1 if s1 not in new_added_task else new_added_task[s1][-1][0]
        s2_1 = s2 if s2 not in new_added_task else new_added_task[s2][0][0]
        new_special_constraints.start_at_end += [(s1_1, s2_1)]
    for s1, s2, delta in special_constraints.start_at_end_plus_offset:
        s1_1 = s1 if s1 not in new_added_task else new_added_task[s1][-1][0]
        s2_1 = s2 if s2 not in new_added_task else new_added_task[s2][0][0]
        new_special_constraints.start_at_end_plus_offset += [(s1_1, s2_1, delta)]
    new_special_constraints = SpecialConstraintsDescription(task_mode=new_special_constraints.task_mode,
                                                            start_times=new_special_constraints.start_times,
                                                            end_times=new_special_constraints.end_times,
                                                            start_times_window=new_special_constraints.start_times_window,
                                                            end_times_window=new_special_constraints.end_times_window,
                                                            partial_permutation=new_special_constraints.partial_permutation,
                                                            list_partial_order=new_special_constraints.list_partial_order,
                                                            start_together=new_special_constraints.start_together,
                                                            start_at_end=new_special_constraints.start_at_end,
                                                            start_at_end_plus_offset=new_special_constraints.start_at_end_plus_offset,
                                                            start_after_nunit=new_special_constraints.start_after_nunit,
                                                            disjunctive_tasks=new_special_constraints.disjunctive_tasks)

    if isinstance(rcpsp_model, RCPSPModelSpecialConstraintsPreemptive):
        return RCPSPModelSpecialConstraints(resources=rcpsp_model.resources,
                                            non_renewable_resources=rcpsp_model.non_renewable_resources,
                                            mode_details=new_mode_details,
                                            successors=new_successors,
                                            horizon=rcpsp_model.horizon,
                                            special_constraints=new_special_constraints,
                                            relax_the_start_at_end=rcpsp_model.relax_the_start_at_end,
                                            tasks_list=new_tasks_list,
                                            source_task=rcpsp_model.source_task,
                                            sink_task=rcpsp_model.sink_task, name_task=rcpsp_model.name_task)

    if isinstance(rcpsp_model, MS_RCPSPModel):
        partial_preemption_data = {}
        for t in rcpsp_model.partial_preemption_data:
            if t not in new_added_task:
                partial_preemption_data[t] = rcpsp_model.partial_preemption_data[t]
            else:
                for j in range(len(new_added_task[t])):
                    partial_preemption_data[new_added_task[t][j][0]] = rcpsp_model.partial_preemption_data[t]
        return MS_RCPSPModel_Variant(skills_set=rcpsp_model.skills_set,
                                     resources_set=rcpsp_model.resources_set,
                                     non_renewable_resources=rcpsp_model.non_renewable_resources,
                                     resources_availability=rcpsp_model.resources_availability,
                                     employees=rcpsp_model.employees,
                                     mode_details=new_mode_details,
                                     successors=new_successors,horizon=rcpsp_model.horizon,
                                     employees_availability=rcpsp_model.employees_availability,
                                     tasks_list=new_tasks_list,
                                     employees_list=rcpsp_model.employees_list,
                                     horizon_multiplier=rcpsp_model.horizon_multiplier,
                                     sink_task=rcpsp_model.sink_task,
                                     source_task=rcpsp_model.source_task,
                                     one_unit_per_task_max=rcpsp_model.one_unit_per_task_max,
                                     preemptive=False, preemptive_indicator={t: False for t in new_tasks_list},
                                     special_constraints=new_special_constraints,
                                     partial_preemption_data=partial_preemption_data,
                                     always_releasable_resources=rcpsp_model.always_releasable_resources,
                                     never_releasable_resources=rcpsp_model.never_releasable_resources,
                                     resource_blocking_data=resource_blocking_data)


def build_multimode_rcpsp_calendar_representative(rcpsp_model: MS_RCPSPModel):
    # put skills as ressource.
    if len(rcpsp_model.resources_list) == 0:
        skills_availability = {s: [0] * int(rcpsp_model.horizon)
                               for s in rcpsp_model.skills_set}
    else:
        skills_availability = {s: [0]*len(rcpsp_model.resources_availability[rcpsp_model.resources_list[0]])
                               for s in rcpsp_model.skills_set}
    for emp in rcpsp_model.employees:
        for j in range(len(rcpsp_model.employees[emp].calendar_employee)):
            if rcpsp_model.employees[emp].calendar_employee[min(j,
                                                            len(rcpsp_model.employees[emp].calendar_employee)-1)]:
                for s in rcpsp_model.employees[emp].dict_skill:
                    skills_availability[s][min(j,
                                               len(skills_availability[s])-1)] += rcpsp_model.employees[emp].dict_skill[s].skill_value
    res_availability = deepcopy(rcpsp_model.resources_availability)
    for s in skills_availability:
        res_availability[s] = [int(x) for x in skills_availability[s]]
    mode_details = deepcopy(rcpsp_model.mode_details)
    for task in mode_details:
        for mode in mode_details[task]:
            for r in rcpsp_model.resources_set:
                if r not in mode_details[task][mode]:
                    mode_details[task][mode][r] = int(0)
            for s in rcpsp_model.skills_set:
                if s not in mode_details[task][mode]:
                    mode_details[task][mode][s] = int(0)
    if rcpsp_model.do_special_constraints:
        return RCPSPModelSpecialConstraints(resources=res_availability,
                                            non_renewable_resources=list(rcpsp_model.non_renewable_resources),
                                            mode_details=mode_details,
                                            tasks_list=rcpsp_model.tasks_list,
                                            source_task=rcpsp_model.source_task,
                                            sink_task=rcpsp_model.sink_task,
                                            successors=rcpsp_model.successors,
                                            special_constraints=rcpsp_model.special_constraints,
                                            horizon=rcpsp_model.horizon,
                                            horizon_multiplier=rcpsp_model.horizon_multiplier,
                                            name_task={i: str(i) for i in rcpsp_model.tasks})
    else:
        return RCPSPModel(resources=res_availability,
                          non_renewable_resources=list(rcpsp_model.non_renewable_resources),
                          mode_details=mode_details,
                          tasks_list=rcpsp_model.tasks_list,
                          source_task=rcpsp_model.source_task,
                          sink_task=rcpsp_model.sink_task,
                          successors=rcpsp_model.successors,
                          horizon=rcpsp_model.horizon,
                          horizon_multiplier=rcpsp_model.horizon_multiplier,
                          name_task={i: str(i) for i in rcpsp_model.tasks})



def build_corresponding_solution(model_with_additional_task: MS_RCPSPModel,
                                 model_without_additional_task: MS_RCPSPModel,
                                 solution_without_additional_task: MS_RCPSPSolution):

    task_additional = model_with_additional_task.tasks_list
    task_initial = model_without_additional_task.tasks_list
    schedule = {}
    employee_usage = {}
    modes = {}
    for t in task_initial:
        if t in task_additional:
            schedule[t] = solution_without_additional_task.schedule[t]
            if t in solution_without_additional_task.employee_usage:
                employee_usage[t] = solution_without_additional_task.employee_usage[t]
            modes[t] = solution_without_additional_task.modes[t]
        else:
            corresponding_tasks = [str(t)+"-"+str(i)
                                   for i in range(model_without_additional_task.mode_details[t][1]["duration"])
                                   if str(t)+"-"+str(i) in model_with_additional_task.tasks_list]
            start = solution_without_additional_task.schedule[t]["start_time"]
            print(corresponding_tasks)
            for j in range(len(corresponding_tasks)):
                schedule[corresponding_tasks[j]] = {"start_time": start,
                                                    "end_time": start +
                                                     model_with_additional_task.mode_details
                                                     [corresponding_tasks[j]][1]["duration"]}
                start += model_with_additional_task.mode_details[corresponding_tasks[j]][1]["duration"]
                modes[corresponding_tasks[j]] = solution_without_additional_task.modes[t]
                employee_usage[corresponding_tasks[j]] = solution_without_additional_task.employee_usage[t]
    return MS_RCPSPSolution(problem=model_with_additional_task,
                            modes=modes,
                            schedule=schedule,
                            employee_usage=employee_usage)












