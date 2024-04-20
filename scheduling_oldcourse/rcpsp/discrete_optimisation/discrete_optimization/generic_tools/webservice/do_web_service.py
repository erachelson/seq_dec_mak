from discrete_optimization.generic_tools.result_storage.result_storage import ResultStorage
from fastapi import FastAPI, File, UploadFile
from starlette.responses import StreamingResponse
from uvicorn.loops import asyncio
from discrete_optimization.generic_tools.do_solver import SolverDO
from discrete_optimization.generic_tools.do_problem import Problem
import time
import os
import cv2
import io
from typing import Dict, Any
from enum import Enum
FILEDIR = os.path.dirname(os.path.abspath(__file__))
output_image_directory = os.path.join(FILEDIR, "output/")
if not os.path.exists(output_image_directory):
    os.makedirs(output_image_directory)
app = FastAPI()


class SolverNameException(Exception):
    def __init__(self, string_message):
        self.string_message = string_message

    def __str__(self):
        return str(self.string_message)


class ProblemType(Enum):
    COLORING = "COLORING"
    FACILITY_LOCATION = "FACILITY_LOCATION"
    FLEET_ALLOCATION = "FLEET_ALLOCATION"
    FLEET_ROTATION = "FLEET_ROTATION"
    KNAPSACK = "KNAPSACK"
    PICKUP_VRP = "PICKUP_VRP"
    RCPSP = "RCPSP"
    MS_RCPSP = "MS_RCPSP"
    TSP = "TSP"
    TTP = "TTP"
    VRP = "VRP"


class StaticSolverService:
    def __init__(self, tag: str, problem_type: ProblemType):
        self.tag = tag
        self.problem_type = problem_type
        self.do_domain: Problem = None
        self.do_solver: SolverDO = None
        self.params_solver: Dict[Any, Any] = None
        self.results: ResultStorage = None
        x = find_right_module_solvers(self.problem_type)
        if x is not None:
            self.solvers_map = x[1]
            self.solvers_list = [k.__name__ for k in self.solvers_map]
        else:
            self.solvers_map = None
            self.solvers_list = None

    def __str__(self):
        s = "Solver service id="+str(self.tag)
        s += "Type of problem="+str(self.problem_type)
        s += "Domain :"+str(self.do_domain)

        if self.do_solver is not None:
            s += "Solver ="+str(self.do_solver.__class__.__name__)
        if self.results is not None:
            s += "Results = "+str(self.results)
        return s

    def concise_str(self):
        s = "Solver service id="+str(self.tag)
        s += "Type of problem="+str(self.problem_type)
        if self.do_solver is not None:
            s += "Solver ="+str(self.do_solver.__class__.__name__)
        return s

    def get_available_solvers(self):
        return self.solvers_list

    def init_solver(self, solver_string, **args):
        right_solvers = [k for k in self.solvers_map if k.__name__ == solver_string]
        if len(right_solvers) == 0:
            raise SolverNameException("Error, please choose among this : "+str(self.solvers_list))
        else:
            solver_class = right_solvers[0]
        if len(args) == 0 or args is None:
            args = self.solvers_map[solver_class][1]
        solver = solver_class(self.do_domain, **args)
        self.do_solver = solver
        self.params_solver = args
        return solver

    def get_params(self, solver_string):
        right_solvers = [k for k in self.solvers_map if k.__name__ == solver_string]
        if len(right_solvers) == 0:
            raise SolverNameException("Error, please choose among this : " + str(self.solvers_list))
        else:
            solver_class = right_solvers[0]
        return self.solvers_map[solver_class][1]

    def solve_domain(self, **args):
        for k in args:
            self.params_solver[k] = args[k]
        result = self.do_solver.solve(**self.params_solver)
        return result


def find_right_module_solvers(problem_type: ProblemType):
    if problem_type.value == problem_type.COLORING.value:
        import discrete_optimization.coloring.coloring_solvers as coloring_solvers
        from discrete_optimization.coloring.coloring_parser import parse, parse_file
        module = coloring_solvers
        return module, module.solvers_map,\
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.FACILITY_LOCATION.value:
        import discrete_optimization.facility.facility_solvers as facility_solvers
        module = facility_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.FLEET_ALLOCATION.value:
        return None # TODO
    if problem_type.value == problem_type.FLEET_ROTATION.value:
        import discrete_optimization.fleet_rotation.solver.fleet_rotation_solvers as fleet_rotation_solvers
        module = fleet_rotation_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.KNAPSACK.value:
        import discrete_optimization.knapsack.knapsack_solvers as knapsack_solvers
        module = knapsack_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.PICKUP_VRP.value:
        return None  # TODO
    if problem_type.value == problem_type.RCPSP.value:
        import discrete_optimization.rcpsp.rcpsp_solvers as rcpsp_solvers
        module = rcpsp_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.MS_RCPSP.value:
        import discrete_optimization.rcpsp_multiskill.rcpsp_multiskill_solvers as rcpsp_multiskill_solvers
        module = rcpsp_multiskill_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.TSP.value:
        import discrete_optimization.tsp.tsp_solvers as tsp_solvers
        module = tsp_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver
    if problem_type.value == problem_type.TTP.value:
        return None  # TODO
    if problem_type.value == problem_type.VRP.value:
        import discrete_optimization.vrp.vrp_solvers as vrp_solvers
        module = vrp_solvers
        return module, module.solvers_map, \
               module.solvers_compatibility, module.look_for_solver


def find_right_parser(problem_type: ProblemType):
    if problem_type.value == problem_type.COLORING.value:
        import discrete_optimization.coloring.coloring_parser as coloring_parser
        module = coloring_parser
        return module.parse, module.parse_file
    if problem_type.value == problem_type.FACILITY_LOCATION.value:
        import discrete_optimization.facility.facility_parser as facility_parser
        module = facility_parser
        return module.parse, module.parse_file
    if problem_type.value == problem_type.FLEET_ALLOCATION.value:
        return None  # TODO
    if problem_type.value == problem_type.FLEET_ROTATION.value:
        import discrete_optimization.fleet_rotation.utils.load_problem as frotation_parser
        return frotation_parser.load_problem, frotation_parser.load_problem
    if problem_type.value == problem_type.KNAPSACK.value:
        import discrete_optimization.knapsack.knapsack_parser as knapsack_parser
        module = knapsack_parser
        return module.parse_input_data, module.parse_file
    if problem_type.value == problem_type.PICKUP_VRP.value:
        return None # TODO
    if problem_type.value == problem_type.RCPSP.value:
        import discrete_optimization.rcpsp.rcpsp_parser as rcpsp_parser
        module = rcpsp_parser
        return module.parse_psplib, module.parse_file
    if problem_type.value == problem_type.MS_RCPSP.value:
        import discrete_optimization.rcpsp_multiskill.rcpsp_multiskill_parser as rcpsp_multiskill_parser
        module = rcpsp_multiskill_parser
        return module.parse_imopse, module.parse_file
    if problem_type.value == problem_type.TSP.value:
        import discrete_optimization.tsp.tsp_parser as tsp_parser
        module = tsp_parser
        return module.parse_input_data, module.parse_file
    if problem_type.value == problem_type.TTP.value:
        import discrete_optimization.ttp.ttp_parser as ttp_parser
        module = ttp_parser
        return module.parse_input_data, module.parse
    if problem_type.value == problem_type.VRP.value:
        import discrete_optimization.vrp.vrp_parser as vrp_parser
        module = vrp_parser
        return module.parse_input, module.parse_file


static_solver_service_dict: Dict[int, StaticSolverService] = {}


@app.post("/init_problem")
def init_problem(file: UploadFile = File(...),
                 problem_type: ProblemType = ProblemType.COLORING,
                 tag: str = None):
    """
    Init a solver service instance with a given problem.
    :param file: file input
    :param problem_type: problem type implemented in DO
    :param tag: name of the solver service instance you want to give.
    :return:
    """
    id_instance = time.time_ns()
    if tag is None:
        tag = id_instance
    tag = str(tag)
    static_solver_service_dict[id_instance] = StaticSolverService(tag=tag, problem_type=problem_type)
    parse_function = find_right_parser(problem_type=problem_type)
    if problem_type.value == problem_type.FLEET_ROTATION.value:
        import pickle
        static_solver_service_dict[id_instance].do_domain = pickle.load(file.file)
    else:
        f = file.file.read()
        static_solver_service_dict[id_instance].do_domain = parse_function[0](f.decode("utf-8"))
    return id_instance, str(static_solver_service_dict[id_instance].do_domain)


@app.post("/get_available_solvers")
def get_available_solvers(id_instance: int = None):
    if id_instance is None:
        id_instance = max(static_solver_service_dict)
    return static_solver_service_dict[id_instance].get_available_solvers()


@app.post("/get_params_solver")
def get_params_solver(solver: str, id_instance: int = None):
    if id_instance is None:
        id_instance = max(static_solver_service_dict)
    return static_solver_service_dict[id_instance].get_params(solver_string=solver)


@app.post("/solve_domain")
def solve_domain(solver_string: str,
                 params: Dict[str, Any] = None,
                 id_instance: int = None):
    """
    :param solver_string: should be an output of get_available_solvers().
    :param id_instance: id of the instance in the static_solver_service_dict
    :param params: params of the solver, if you want to provide custom params, check the ones available
    by calling get_params_solver() service
    :return: evaluation of the best solution found.
    """
    asyncio.asyncio_setup()
    if id_instance is None:
        id_instance = max(static_solver_service_dict)
    try:
        if params is None:
            params = {}
        static_solver_service_dict[id_instance].init_solver(solver_string=solver_string, **params)
    except SolverNameException as e:
        print(e)
        return str(e)
    result = static_solver_service_dict[id_instance].solve_domain(**params)
    static_solver_service_dict[id_instance].results = result
    best_evaluation = static_solver_service_dict[id_instance].do_domain.evaluate(result.get_best_solution())
    return len(result.list_solution_fits),\
           {k: int(best_evaluation[k]) for k in best_evaluation}


@app.post("/get_fitness_evolution", description="plot the fitness evolution inside the algorithm")
def get_fitness_evolution(id_instance: int = None,
                          file_name_png: str = None):
    if id_instance is None:
        id_instance = max(static_solver_service_dict)
    if file_name_png is None:
        file_name_png = str(id_instance)+"temp_fitness_image.png"
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1)
    results = static_solver_service_dict[id_instance].results
    fitness = [x[1] for x in results.list_solution_fits]
    ax.plot(fitness)
    ax.set_title("Fitness evolution")
    ax.set_xlabel("Iteration or #solutions")
    ax.set_ylabel("Fitness ")
    fig.savefig(os.path.join(output_image_directory, file_name_png), dpi=300,
                facecolor=fig.get_facecolor(),
                edgecolor='none')
    img = cv2.imread(os.path.join(output_image_directory, file_name_png))
    res, im_png = cv2.imencode(".png", img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()), media_type="image/png")


@app.get("/get_instanciated_problems")
def get_instanciated_problems():
    return [(k, static_solver_service_dict[k].concise_str())
            for k in static_solver_service_dict]




