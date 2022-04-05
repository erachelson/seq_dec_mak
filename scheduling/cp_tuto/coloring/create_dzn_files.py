# Class to dump dzn files for coloring problems
import os

from discrete_optimization.coloring.coloring_parser import files_available, parse_file
from discrete_optimization.coloring.solvers.coloring_cp_solvers import ColoringCP, ColoringCPModel


def script_to_create_dzn_files():
    this_folder = os.path.dirname(os.path.abspath(__file__))
    folder_to_dump = os.path.join(this_folder, "dumped_dzn_coloring/")
    if not os.path.exists(folder_to_dump):
        os.makedirs(folder_to_dump)
    for file in files_available:
        coloring_model = parse_file(file_path=file)
        solver = ColoringCP(coloring_problem=coloring_model)
        solver.init_model(greedy_start=False,
                          object_output=True,
                          include_seq_chain_constraint=True,
                          cp_model=ColoringCPModel.DEFAULT)
        solver.export_dzn(os.path.join(folder_to_dump, os.path.basename(file)+".dzn"),
                          keys=[k for k in solver.dict_datas if k != "include_seq_chain_constraint"])





if __name__ == "__main__":
    script_to_create_dzn_files()

