import random

tic_tac_toe = TicTacToe(TIC_TAC_TOE)
tic_tac_toe_tree = TicTacToeTree(tic_tac_toe)

def call_alphabeta_pruning(tic_tac_toe_tree: TicTacToeTree,
                           node: Tree.Node) -> None:
    alphabeta(node=node,
              tree = tic_tac_toe_tree,
              depth=1000,
              alpha=-float("inf"),
              beta=float("inf"),
              maximizing_player=True,
              evaluate = lambda n : n.terminal_value)
    
def call_random_player(tic_tac_toe_tree: TicTacToeTree,
                       node: Tree.Node) -> None:
    node._best_child = random.sample(tic_tac_toe_tree.get_children(node), 1)[0]

node = tic_tac_toe_tree.get_node(data=tic_tac_toe.reset())
tic_tac_toe.render(node.data)

while not node.terminal:
    if node.max_player:
        call_alphabeta_pruning(tic_tac_toe_tree, node)
    else:
        call_random_player(tic_tac_toe_tree, node)
        
    node = node.best_child[0]
    tic_tac_toe.render(node.data)