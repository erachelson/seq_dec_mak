from correction.nb2_jobshopsolver import SolverJobShop

solver = SolverJobShop(jobshop_problem=example_jobshop)
solution = solver.solve()
check_solution(solution, example_jobshop)
plot_solution(solution, example_jobshop)