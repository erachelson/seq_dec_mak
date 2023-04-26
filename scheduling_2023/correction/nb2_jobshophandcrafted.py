handcrafted_solution = SolutionJobshop([[[0, 3], [4, 6], [6, 8]], [[3, 5], [5, 6], [7, 11]],
                                        [[0, 4], [8, 11]]])
check_solution(solution=handcrafted_solution, problem=example_jobshop)
plot_solution(handcrafted_solution, example_jobshop)