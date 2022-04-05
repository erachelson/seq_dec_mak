include "value_precede_chain.mzn";
int: n_nodes;
int: n_edges;
int: nb_colors;
set of int: NODES = 1..n_nodes;
set of int: EDGES = 1..n_edges;
set of int: COLORS = 1..nb_colors;
array[EDGES, 1..2] of NODES: list_edges;

% specify for each node the chosen color.
array[NODES] of var COLORS: color_graph;
var COLORS: objective;
solve satisfy;
output ["obj=\(objective)"];




