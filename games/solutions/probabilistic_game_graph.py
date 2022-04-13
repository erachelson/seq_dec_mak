from __future__ import annotations
from typing import Dict

class ProbabilisticGameGraph:
    class StateNode:
        def __init__(self, data: Tree.Node):
            self._data = data
            self._best_action = None
            self._best_value = None
            self._successors: List[ProbabilisticGameGraph.ActionNode] = []
            
        @property
        def data(self):
            return self._data
        
        @property
        def best_action(self):
            return self._best_action
        
        @property
        def best_value(self):
            return self._best_value
            
        def __eq__(self, other: ProbabilisticGameGraph.StateNode):
            return self._data.__eq__(other._data)
        
        def __hash__(self):
            return hash(self._data)
        
        def __str__(self):
            return str(self._data)
        
        def __repr__(self):
            return 'Node(data: {}, best action: {}, best value: {})'.format(
                repr(self._data),
                repr(self._best_action) if self._best_action is not None else None,
                repr(self._best_value) if self._best_value is not None else None)
    
    class ActionNode:
        def __init__(self, data: Any):
            self._data = data
            self._successors: List[Tuple[ProbabilisticGameGraph.StateNode, float]] = []
            
        @property
        def data(self):
            return self._data
            
        def __eq__(self, other: ProbabilisticGameGraph.ActionNode):
            return self._data.__eq__(other._data)
        
        def __hash__(self):
            return hash(self._data)
        
        def __str__(self):
            return str(self._data)
        
        def __repr__(self):
            return 'ActionNode(data: {})'.format(
                repr(self._data))
    
    def __init__(self,
                 game_tree: Tree,
                 opponent_policy: Callable[[Tree.Node],
                                           List[Tuple[float, Tree.Node]]]):
        self._nodes: Dict[Any, ProbabilisticGameGraph.StateNode] = {}
        self._game_tree = game_tree
        self._opponent_policy = opponent_policy
    
    def get_node(self, data: Any):
        if data not in self._nodes:
            self._nodes[data] = ProbabilisticGameGraph.StateNode(data)
        return self._nodes[data]
        
    def get_successors(self, node: StateNode) -> List[ActionNode]:
        if node.data not in self._nodes or len(node._successors) == 0:
            node._successors = list(self.generate_successors(node))
            self._nodes[node.data] = node
        return self._nodes[node.data]._successors
    
    def generate_successors(self, node: StateNode) -> List[ActionNode]:
        for tree_node, action_str in self._game_tree.get_children(node.data):
            action_node = ProbabilisticGameGraph.ActionNode(data=(tree_node, action_str))
            if self._game_tree.is_terminal(tree_node):
                action_node._successors.append(tuple([self.get_node(tree_node),
                                                      1.0]))
            else:
                for probability, next_tree_node in self._opponent_policy(tree_node):
                    action_node._successors.append(tuple([self.get_node(next_tree_node),
                                                        probability]))
            yield action_node
    
    def is_goal(self, node: StateNode) -> bool:
        return self._game_tree.is_terminal(node.data)
    
    def render(self, node: StateNode) -> None:
        self._game_tree.render(node.data)