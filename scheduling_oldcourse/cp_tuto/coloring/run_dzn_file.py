from dataclasses import InitVar
from datetime import timedelta
from minizinc import Model, Instance, Solver, Result
from enum import Enum
from typing import List, Any
import pymzn
import argparse
import json


class ColoringCPSolution:
    objective: int
    __output_item: InitVar[str] = None

    def __init__(self, objective, _output_item, **kwargs):
        self.objective = objective
        self.dict = kwargs
        print("New solution ", self.objective)
        print("Output ", _output_item)

    def check(self) -> bool:
        return True


class CPSolverName(Enum):
    """
    Enum choice of underlying CP/LP solver used by Minizinc typically
    """
    CHUFFED = 0
    GECODE = 1
    CPLEX = 2
    CPOPT = 3
    GUROBI = 4
    ORTOOLS = 5


map_cp_solver_name = {CPSolverName.CHUFFED: "chuffed",
                      CPSolverName.GECODE: "gecode",
                      CPSolverName.CPLEX: "cplex",
                      CPSolverName.CPOPT: "cpo",
                      # need to install https://github.com/IBMDecisionOptimization/cpofzn
                      CPSolverName.GUROBI: "gurobi",
                      CPSolverName.ORTOOLS: "ortools"}


class ParametersCP:
    """
    Parameters that can be used by any cp - solver
    """
    TimeLimit: int
    TimeLimit_iter0: int
    PoolSolutions: int
    intermediate_solution: bool
    all_solutions: bool
    nr_solutions: int
    free_search: bool
    multiprocess: bool
    nb_process: int

    def __init__(self,
                 time_limit,
                 pool_solutions,
                 intermediate_solution: bool,
                 all_solutions: bool,
                 nr_solutions: int,
                 free_search: bool = False,
                 multiprocess: bool = False,
                 nb_process: int = 1):
        """

        :param time_limit: in seconds, the time limit of solving the cp model
        :param pool_solutions: TODO remove it it's not used
        :param intermediate_solution: retrieve intermediate solutions
        :param all_solutions: returns all solutions found by the cp solver
        :param nr_solutions: max number of solution returned
        """
        self.TimeLimit = time_limit
        self.TimeLimit_iter0 = time_limit
        self.PoolSolutions = pool_solutions
        self.intermediate_solution = intermediate_solution
        self.all_solutions = all_solutions
        self.nr_solutions = nr_solutions
        self.free_search = free_search
        self.multiprocess = multiprocess
        self.nb_process = nb_process

    @staticmethod
    def default():
        return ParametersCP(time_limit=100,
                            pool_solutions=10000,
                            intermediate_solution=True,
                            all_solutions=False,
                            nr_solutions=1000,
                            free_search=False)

    @staticmethod
    def default_fast_lns():
        return ParametersCP(time_limit=10,
                            pool_solutions=10000,
                            intermediate_solution=True,
                            all_solutions=False,
                            nr_solutions=1000,
                            free_search=False)

    @staticmethod
    def default_free():
        return ParametersCP(time_limit=100,
                            pool_solutions=10000,
                            intermediate_solution=True,
                            all_solutions=False,
                            nr_solutions=1000,
                            free_search=True)

    def copy(self):
        return ParametersCP(time_limit=self.TimeLimit,
                            pool_solutions=self.PoolSolutions,
                            intermediate_solution=self.intermediate_solution,
                            all_solutions=self.all_solutions,
                            nr_solutions=self.nr_solutions,
                            free_search=self.free_search)


def retrieve_solutions(result: Result) -> List[Any]:
    colors = []
    objectives = []
    solutions_fit = []
    for i in range(len(result)):
        colors += [result[i].dict["color_graph"]]
        objectives += [result[i].objective]
    for k in range(len(colors)):
        sol = [colors[k][i] - 1
               for i in range(len(colors[k]))]
        color_sol = sol
        fit = len(set(sol))
        solutions_fit += [(color_sol, fit)]
    return solutions_fit


def check(solution, dict_instance):
    problems = []
    for i in range(len(dict_instance["list_edges"])):
        i1 = dict_instance["list_edges"][i][0]
        i2 = dict_instance["list_edges"][i][1]
        if not solution[i1-1] != solution[i2-1]:
            problems += [{"n1": i1, "n2": i2, "color_n1": solution[i1-1], "color_n2": solution[i2-1]}]
    feasible = len(problems) == 0
    return feasible, problems


def run_model_on_data(model_path: str,
                      data_path: str,
                      time_limit: int=100,
                      output_str: str = None):
    path = model_path
    some_dzn = data_path
    model = Model(path)
    model.output_type = ColoringCPSolution
    model.add_file(some_dzn)
    # model.add_file("/Users/poveda_g/Documents/git_repos/discrete-optimisation/"
    #                "discrete_optimization/coloring/minizinc/coloring.mzc.mzn")
    solver = Solver.lookup("chuffed")
    instance = Instance(solver, model)
    dict_instance = pymzn.dzn2dict(dzn=some_dzn)
    instance["include_seq_chain_constraint"] = False
    params = ParametersCP.default()
    params.multiprocess = False
    params.nb_process = 4
    params.TimeLimit = time_limit
    result: Result = instance.solve(timeout=timedelta(seconds=time_limit),
                                    intermediate_solutions=True,
                                    processes=params.nb_process
                                    if params.multiprocess else None,
                                    free_search=params.free_search,
                                    verbose=True)
    print(result.status)
    sols = retrieve_solutions(result)
    checks = []
    for sol, fit in sols:
        checks += [check(sol, dict_instance)]
    if output_str is not None:
        json.dump({"model": model_path,
                   "data": data_path,
                   "results": sols, "checks": checks},
                  open(output_str, "w"),
                  indent=4)
    return sols


def example():
    run_model_on_data(model_path=
                      "/discrete_optimization/coloring/minizinc/coloring.mzn",
                      data_path="/tests/coloring/solvers/dumped_dzn_coloring/gc_20_1.dzn",
                      output_str="results.json")


if __name__ == "__main__":
    # example()
    parser = argparse.ArgumentParser(
        description="Solve coloring problem with a given minizinc file"
    )
    parser.add_argument("--m", type=str,
                        default="coloring_to_fill.mzn",
                        required=True, help="path to the minizinc model (.mzn)")
    parser.add_argument("--d", type=str,
                        default="dumped_dzn_coloring/gc_4_1.dzn",
                        required=True, help="path to the minizinc data (.dzn)")
    parser.add_argument("--lim", type=int,
                        default=100,
                        required=False, help="in seconds, time limit for the solver")
    parser.add_argument(
        "--o", type=str, required=False,
        default=None,
        help="store the solution in a json file."
    )
    args = parser.parse_args()
    run_model_on_data(model_path=args.m, data_path=args.d,
                      time_limit=args.lim, output_str=args.o)



