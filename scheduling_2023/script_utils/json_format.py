import json
from typing import Dict
from discrete_optimization.rcpsp.specialized_rcpsp.rcpsp_specialized_constraints import SpecialConstraintsDescription, \
    RCPSPModelPreemptive, RCPSPModelSpecialConstraints, \
    RCPSPModelSpecialConstraintsPreemptive
from discrete_optimization.rcpsp.rcpsp_model import RCPSPModel
from discrete_optimization.rcpsp_multiskill.rcpsp_multiskill import Employee, SkillDetail, MS_RCPSPModel
import numpy as np


def discrete_to_full_numpy(discretized_ressource_array, full_horizon):
    ressource_availability = np.zeros(full_horizon, dtype=np.int)
    for p in discretized_ressource_array:
        ressource_availability[p[1]:p[1]+p[2]] = p[0]
    return ressource_availability


class RCPSPEncoder(json.JSONEncoder):
    def default(self, z):
        if isinstance(z, np.int64):
            return int(z)
        if isinstance(z, Dict):
            some_key = list(z.keys())[0]
            if isinstance(z[some_key], Employee):
                return {"type": z[some_key].__class__.__name__,
                        "content": {k: z[k].to_json(with_calendar=False) for k in z}}
            return super().default(z)
        if isinstance(z, Employee):
            return {"type": z.__class__.__name__,
                    "content": z.to_json(with_calendar=False)}
        if isinstance(z, SpecialConstraintsDescription):
            return {"type": z.__class__.__name__,
                    "content": {attr: getattr(z, attr) for attr in ["task_mode",
                                                                    "start_times",
                                                                    "end_times",
                                                                    "start_times_window",
                                                                    "end_times_window",
                                                                    "partial_permutation",
                                                                    "list_partial_order",
                                                                    "start_together",
                                                                    "start_at_end",
                                                                    "start_at_end_plus_offset",
                                                                    "start_after_nunit",
                                                                    "disjunctive_tasks"]}}
        elif isinstance(z, set):
            return list(z)
        else:
            return super().default(z)


def decode_rcpsp_json(dct):
    if "type" in dct:
        if dct["type"] == "Employee":
            content = dct["content"]
            return Employee(dict_skill={s: SkillDetail(**content["dict_skill"][s])
                                        for s in content["dict_skill"]},
                            calendar_employee=content["calendar_employee"])
        if dct["type"] == "SpecialConstraintsDescription":
            content = dct["content"]
            for key in ["task_mode", "start_times", "end_times", "start_times_window", "end_times_window"]:
                if content[key] is not None:
                    content[key] = {int(k): content[key][k] for k in content[key]}
            return SpecialConstraintsDescription(**content)
    return dct


def load_instance_rcpsp(json_path=None, dict_instance=None):
    if dict_instance is None:
        dict_instance = json.load(open(json_path, "r"), object_hook=decode_rcpsp_json)
    dict_instance["mode_details"] = {
        int(t): {
            int(m): dict_instance["mode_details"][t][m]
            for m in dict_instance["mode_details"][t]
        }
        for t in dict_instance["mode_details"]
    }
    dict_instance["successors"] = {
        int(t): dict_instance["successors"][t] for t in dict_instance["successors"]
    }
    if "resources_availability_discretized" in dict_instance:
        dict_instance["resources"] = {}
        for k in dict_instance["resources_availability_discretized"]:
            if len(dict_instance["resources_availability_discretized"][k]) > 1 or True:
                dict_instance["resources"][k] = \
                    discrete_to_full_numpy(discretized_ressource_array=dict_instance
                                           ["resources_availability_discretized"][k],
                                           full_horizon=dict_instance["horizon"])
    if "preemptive_indicator" in dict_instance:
        dict_instance["preemptive_indicator"] = {int(x): dict_instance["preemptive_indicator"][x]
                                                 for x in dict_instance["preemptive_indicator"]}
    # dict_instance["name_task"] = {
    #     int(t): dict_instance["name_task"][t] for t in dict_instance["name_task"]
    # }
    model = None
    if dict_instance["class"] in {"RCPSPModel",
                                  "MultiModeRCPSPModel",
                                  "RCPSPModelCalendar",
                                  "SingleModeRCPSPModel"}:
        model = RCPSPModel(**dict_instance)
    if dict_instance["class"] == "RCPSPModelSpecialConstraints":
        model = RCPSPModelSpecialConstraints(**dict_instance)
    if dict_instance["class"] == "RCPSPModelPreemptive":
        model = RCPSPModelPreemptive(**dict_instance)
    if dict_instance["class"] == "RCPSPModelSpecialConstraintsPreemptive":
        model = RCPSPModelSpecialConstraintsPreemptive(**dict_instance)
    if "additional_data" in dict_instance:
        model.additional_data = dict_instance["additional_data"]
    return model


def load_instance_msrcpsp(json_path=None, dict_instance=None):
    if dict_instance is None:
        dict_instance = json.load(open(json_path, "r"), object_hook=decode_rcpsp_json)
    dict_instance["mode_details"] = {
        int(t): {
            int(m): dict_instance["mode_details"][t][m]
            for m in dict_instance["mode_details"][t]
        }
        for t in dict_instance["mode_details"]
    }
    dict_instance["successors"] = {
        int(t): dict_instance["successors"][t] for t in dict_instance["successors"]
    }
    change_employee_key_to_int = False
    if set(dict_instance["employees"]) != set(dict_instance["employees_list"]):
        # it is the case when the employees name are int and not string for example..
        dict_instance["employees"] = {int(k): dict_instance["employees"][k] for k in dict_instance["employees"]}
        change_employee_key_to_int = True
    dict_instance.pop("class")
    dict_instance["resources_availability"] = {r: None for r in dict_instance["resources_set"]}
    if "resources_availability_discretized" in dict_instance:
        for k in dict_instance["resources_availability_discretized"]:
            if len(dict_instance["resources_availability_discretized"][k]) > 1 or True:
                dict_instance["resources_availability"][k] = \
                    discrete_to_full_numpy(discretized_ressource_array=dict_instance
                                           ["resources_availability_discretized"][k],
                                           full_horizon=dict_instance["horizon"])

    if "unit_availability_discretized" in dict_instance:
        for k in dict_instance["unit_availability_discretized"]:
            if len(dict_instance["unit_availability_discretized"][k]) > 1 or True:
                calendar = \
                    discrete_to_full_numpy(discretized_ressource_array=dict_instance
                                           ["unit_availability_discretized"][k],
                                           full_horizon=dict_instance["horizon"])
                if change_employee_key_to_int:
                    dict_instance["employees"][int(k)].calendar_employee = calendar
                else:
                    dict_instance["employees"][k].calendar_employee = calendar
    dict_instance.pop("resources_availability_discretized")
    dict_instance.pop("unit_availability_discretized")
    if "special_constraints" in dict_instance:
        if dict_instance["special_constraints"] == {}:
            dict_instance.pop("special_constraints")
    if "preemptive_indicator" in dict_instance:
        dict_instance["preemptive_indicator"] = {int(x): dict_instance["preemptive_indicator"][x]
                                                 for x in dict_instance["preemptive_indicator"]}
    model = MS_RCPSPModel(**{k: dict_instance[k] for k in dict_instance if k != "additional_data"})
    if "additional_data" in dict_instance:
        model.additional_data = dict_instance["additional_data"]
    return model


def load_any_json(json_path):
    dict_instance = json.load(open(json_path, "r"), object_hook=decode_rcpsp_json)
    if dict_instance["class"] in {"RCPSPModel",
                                  "RCPSPModelSpecialConstraints",
                                  "RCPSPModelPreemptive",
                                  "RCPSPModelSpecialConstraintsPreemptive",
                                  "SingleModeRCPSPModel",
                                  "MultiModeRCPSPModel"}:
        return load_instance_rcpsp(dict_instance=dict_instance)
    return load_instance_msrcpsp(dict_instance=dict_instance)


def load_any_dict(dict_instance):
    if dict_instance["class"] in {"RCPSPModel",
                                  "RCPSPModelSpecialConstraints",
                                  "RCPSPModelPreemptive",
                                  "RCPSPModelSpecialConstraintsPreemptive",
                                  "SingleModeRCPSPModel",
                                  "RCPSPModelCalendar",
                                  "MultiModeRCPSPModel"}:
        return load_instance_rcpsp(dict_instance=dict_instance)
    return load_instance_msrcpsp(dict_instance=dict_instance)


def load_calendar_instance_example():
    model = load_instance_msrcpsp("json_format_ms/100_10_26_15..json")
    for k in model.employees:
        print(model.employees[k].calendar_employee[:21])
