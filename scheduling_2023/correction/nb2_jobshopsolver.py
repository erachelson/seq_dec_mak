from typing import List
from ortools.sat.python import cp_model
from typing import Tuple


class SolutionJobshop:
    def __init__(self, schedule: List[List[Tuple[int, int]]]):
        # For each job and subjob, start and end time given as tuple of int.
        self.schedule = schedule


class Subjob:
    machine_id: int
    processing_time: int

    def __init__(self, machine_id, processing_time):
        self.machine_id = machine_id
        self.processing_time = processing_time


class JobShopProblem:
    n_jobs: int
    n_machines: int
    list_jobs: List[List[Subjob]]

    def __init__(self, list_jobs: List[List[Subjob]], n_jobs: int = None, n_machines: int = None):
        self.n_jobs = n_jobs
        self.n_machines = n_machines
        self.list_jobs = list_jobs
        if self.n_jobs is None:
            self.n_jobs = len(list_jobs)
        if self.n_machines is None:
            self.n_machines = len(set([y.machine_id for x in self.list_jobs
                                       for y in x]))
        # Store for each machine the list of subjob given as (index_job, index_subjob)
        self.job_per_machines = {i: [] for i in range(self.n_machines)}
        for k in range(self.n_jobs):
            for sub_k in range(len(list_jobs[k])):
                self.job_per_machines[list_jobs[k][sub_k].machine_id] += [(k, sub_k)]


class SolverJobShop:
    def __init__(self, jobshop_problem: JobShopProblem):
        self.jobshop_problem = jobshop_problem
        self.model = cp_model.CpModel()
        self.variables = {}
    
    def init_model(self, max_time: int = 300):
        # Write variables, constraints
        starts = [[self.model.NewIntVar(0, max_time, f"starts_{j,k}")
                   for k in range(len(self.jobshop_problem.list_jobs[j]))]
                  for j in range(self.jobshop_problem.n_jobs)]
        ends = [[self.model.NewIntVar(0, max_time, f"ends_{j, k}")
                 for k in range(len(self.jobshop_problem.list_jobs[j]))]
                for j in range(self.jobshop_problem.n_jobs)]
        intervals = [[self.model.NewIntervalVar(start=starts[j][k],
                                                size=self.jobshop_problem.list_jobs[j][k].processing_time,
                                                end=ends[j][k],
                                                name=f"task_{j, k}")
                     for k in range(len(self.jobshop_problem.list_jobs[j]))]
                     for j in range(self.jobshop_problem.n_jobs)]
        for j in range(self.jobshop_problem.n_jobs):
            for k in range(1, len(self.jobshop_problem.list_jobs[j])):
                self.model.Add(starts[j][k] >= ends[j][k-1])
        for machine in self.jobshop_problem.job_per_machines:
            self.model.AddNoOverlap([intervals[x[0]][x[1]]
                                     for x in self.jobshop_problem.job_per_machines[machine]])
        makespan = self.model.NewIntVar(0, max_time, name="makespan")
        self.model.AddMaxEquality(makespan, [ends[i][j] for i in range(len(ends))
                                             for j in range(len(ends[i]))])
        self.model.Minimize(makespan)
        self.variables["starts"] = starts
        self.variables["ends"] = ends
        
    def solve(self, **kwargs) -> SolutionJobshop:
        self.init_model(**kwargs)
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 10
        status = solver.Solve(self.model)
        status_human = solver.StatusName(status)
        print("Solver finished ", status_human)
        print("Objective value : ", solver.ObjectiveValue())
        schedule = []
        for job in range(self.jobshop_problem.n_jobs):
            sch = []
            for subjob in range(len(self.variables["starts"][job])):
                sch += [(solver.Value(self.variables["starts"][job][subjob]),
                         solver.Value(self.variables["ends"][job][subjob]))]
            schedule += [sch]
        return SolutionJobshop(schedule)