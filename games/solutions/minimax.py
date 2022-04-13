from typing import Callable

def minimax(node : Tree.Node,
            tree: Tree,
            depth : int,
            maximizing_player : bool,
            evaluate : Callable[[Tree.Node], float]):
    if depth == 0 or tree.is_terminal(node):
        return evaluate(node)
    if maximizing_player:
        value = -float('inf')
        for child in tree.get_children(node):
            tentative = minimax(child[0], tree, depth - 1, False, evaluate)
            if tentative >= value:
                node._best_child = child
                value = tentative
        return value
    else:
        value = float('inf')
        for child in tree.get_children(node):
            tentative = minimax(child[0], tree, depth - 1, True, evaluate)
            if tentative <= value:
                node._best_child = child
                value = tentative
        return value