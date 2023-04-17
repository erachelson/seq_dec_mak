from ortools.sat.python import cp_model
# Variables
# There is a risk of integer overflow when computing a*b*c*d
# We need small domains...
model = cp_model.CpModel()
start = model.NewIntVar(0, 10, "start")
end = model.NewIntVar(0, 10, "end")
duration = 10
task_var = model.NewIntervalVar(start, duration, end, name="task")
model.Add(task_var.EndExpr() <= 4)


