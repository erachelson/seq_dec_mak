astar = Astar(
    flight_graph,
    lambda n : FlightGraph.compute_great_circle_distance(n.data, flight_graph.arrival),
    verbose=False,
    render=False  # set to true if you want visual rendering of the search
)
solution = astar.solve_from(FlightGraph.Node(flight_graph.departure))
path = [n[0].data for n in solution[1]]
flight_graph.render(path[-1], path)