import os
this_folder = os.path.dirname(os.path.abspath(__file__))
path_data = os.path.join(this_folder, "dumped_dzn_coloring/")
list_dzn_files = [f for f in os.listdir(path_data) if "dzn" in f]

for d in list_dzn_files:
    os.system('python run_dzn_file.py --m '+str(os.path.join(this_folder, "coloring_to_fill.mzn"))+' --d '
              + str(os.path.join(this_folder, d)+" --lim "+str(100)+" --o "+str(os.path.join(this_folder, d+".json"))))
