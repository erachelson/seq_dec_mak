def additional_stuff():
    perm_lsd = sorted(model.tasks_list, key=lambda x: solver.map_node[x]._LSD)
    sol_lsd = sgs_algorithm(model, perm_lsd)
    solution_lsd = RCPSPSolution(problem=model, rcpsp_schedule=sol_lsd)
    print("LSD ", model.evaluate(solution_lsd))
    perm_lsd_and_slack = sorted(model.tasks_list, key=lambda x: (solver.map_node[x]._LSD,
                                                                solver.map_node[x]._LSD - solver.map_node[x]._ESD))
    sol_lsd_and_slack = sgs_algorithm(model, perm_lsd_and_slack)
    solution_lsd_and_slack = RCPSPSolution(problem=model, rcpsp_schedule=sol_lsd_and_slack)
    print("LSD AND SLACK", model.evaluate(solution_lsd))