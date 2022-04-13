tic_tac_toe = TicTacToe(TIC_TAC_TOE)
tic_tac_toe_tree = TicTacToeTree(tic_tac_toe)

def opponent_policy(tree_node: Tree.Node,
                    opponent_game_graph: ProbabilisticGameGraph) -> List[Tuple[float, Tree.Node]]:
    if (opponent_game_graph is not None and
        tree_node in opponent_game_graph._nodes and
        opponent_game_graph.get_node(tree_node)._best_action is not None):
        return [(1., opponent_game_graph.get_node(tree_node)._best_action.data[0])]
    else:
        num_samples = len(tic_tac_toe_tree.get_children(tree_node))
        return [(1. / float(num_samples), n) for n, _ in tic_tac_toe_tree.get_children(tree_node)]

def call_game_rtdp(game_tree: Tree,
                   node: Tree.Node,
                   opponent_game_graph: ProbabilisticGameGraph,
                   max_value: float,
                   max_or_min_player: bool) -> None:
    game_graph = ProbabilisticGameGraph(
        game_tree=game_tree,
        opponent_policy=lambda tree_node : opponent_policy(tree_node, opponent_game_graph)
    )
    rtdp = GameRTDP(
        graph=game_graph,
        heuristic = lambda n : ((2 * int(max_or_min_player) - 1) * n.data.terminal_value
                                if n.data.terminal else
                                (2 * int(max_or_min_player) - 1) * max_value),
        max_steps=1000,
        trials_number=100,
        verbose=False,
        render=False)
    rtdp.solve_from(node)
    return game_graph

node = tic_tac_toe_tree.get_node(data=tic_tac_toe.reset())
tic_tac_toe.render(node.data)
current_game_graph = None

while not node.terminal:
    print('Player {}\'s turn'.format(
        'Cross' if node.max_player else 'Circle'
    ))
    current_game_graph = call_game_rtdp(
        tic_tac_toe_tree,
        node,
        current_game_graph,
        1,
        node.max_player
    )
    
    node = node.best_child[0]
    tic_tac_toe.render(node.data)