from typing import Callable

def alphabeta(node : Tree.Node,
              tree: Tree,
              depth : int,
              alpha : float,
              beta : float,
              maximizing_player : bool,
              evaluate : Callable[[Tree.Node], float]):
    if depth == 0 or tree.is_terminal(node):
        return evaluate(node)
    if maximizing_player:
        value = -float('inf')
        for child in tree.get_children(node):
            tentative = alphabeta(child[0], tree, depth - 1, alpha, beta, False, evaluate)
            if tentative >= value:
                node._best_child = child
                value = tentative
            if value >= beta:
                break
            alpha = max(alpha, value)
        return value
    else:
        value = float('inf')
        for child in tree.get_children(node):
            tentative = alphabeta(child[0], tree, depth - 1, alpha, beta, True, evaluate)
            if tentative <= value:
                node._best_child = child
                value = tentative
            if value <= alpha:
                break
            beta = min(beta, value)
        return value