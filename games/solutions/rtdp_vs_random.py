import random

tic_tac_toe = TicTacToe(TIC_TAC_TOE)
tic_tac_toe_tree = TicTacToeTree(tic_tac_toe)

def call_game_rtdp(game_graph: ProbabilisticGameGraph,
                   node: Tree.Node,
                   max_value: float) -> None:
    rtdp = GameRTDP(
        graph=game_graph,
        heuristic = lambda n : n.data.terminal_value if n.data.terminal else max_value,
        max_steps=1000,
        trials_number=100,
        verbose=False,
        render=False)
    rtdp.solve_from(node)
    
def call_random_player(tic_tac_toe_tree: TicTacToeTree,
                       node: Tree.Node) -> None:
    node._best_child = random.sample(tic_tac_toe_tree.get_children(node), 1)[0]
    
def random_player_policy(node: Tree.Node) -> List[Tuple[float, Tree.Node]]:
    num_samples = len(tic_tac_toe_tree.get_children(node))
    return [(1. / float(num_samples), n) for n, _ in tic_tac_toe_tree.get_children(node)]

node = tic_tac_toe_tree.get_node(data=tic_tac_toe.reset())
tic_tac_toe.render(node.data)

game_graph = ProbabilisticGameGraph(game_tree=tic_tac_toe_tree,
                                    opponent_policy=random_player_policy)

while not node.terminal:
    if node.max_player:
        call_game_rtdp(game_graph, node, 1)
    else:
        call_random_player(tic_tac_toe_tree, node)
        
    node = node.best_child[0]
    tic_tac_toe.render(node.data)