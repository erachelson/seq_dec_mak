import os
import json

this_directory = os.path.abspath(os.path.dirname(__file__))


class JSPLIBInstance:
    def __init__(self, instance):
        self.name = instance["name"]
        self.n_jobs = instance["jobs"]
        self.n_machines = instance["machines"]
        self.optimum = instance["optimum"]
        if self.optimum is None and instance['bounds'] is not None:
            self.lower_bound = instance['bounds']['lower']
            self.upper_bound = instance['bounds']['upper']
        else:
            self.lower_bound = None
            self.upper_bound = None
        self.path = instance['path']

    def jsplib_to_jobshop(self):
        file = open(os.path.join(this_directory, "data/jobshop/%s" % self.path), 'r')
        split_lines = []
        lines = file.readlines()
        processed_line = 0
        problem = []
        for line in lines:
            if not (line.startswith("#")):
                split_line = line.split()
                job = []
                if processed_line == 0:
                    if not (int(split_line[0]) == self.n_jobs
                            and int(split_line[1]) == self.n_machines):
                        exit(1)
                else:
                    for num, n in enumerate(split_line):
                        if num % 2 == 0:
                            machine = int(n)
                        else:
                            job.append({"machine_id": machine, "processing_time": int(n)})
                    problem.append(job)
                processed_line += 1
        return problem


def instance_names():
    file = open(os.path.join(this_directory, "data/jobshop/instances.json"), "r")
    data = json.load(file)
    instance = [inst["name"] for inst in data]
    return instance


def instance_opti():
    file = open(os.path.join(this_directory, "data/jobshop/instances.json"), "r")
    data = json.load(file)
    optimum = {inst["name"]: inst["optimum"] for inst in data}
    return optimum


def create_jsplib_instance(instance_name) -> JSPLIBInstance:
    """

    :param instance_name: name of a JSPlib instance of jobshop problem
    :return: an instance of type JSPLIBInstance that can be translated in a JobshopProblem
    """
    file = open(os.path.join(this_directory, "data/jobshop/instances.json"), "r")
    data = json.load(file)
    instance = [inst for inst in data if inst['name'] == instance_name]
    if len(instance) == 0:
        raise Exception("There is no instance named %s" % instance_name)
    instance = instance[0]
    file.close()
    return JSPLIBInstance(instance)
