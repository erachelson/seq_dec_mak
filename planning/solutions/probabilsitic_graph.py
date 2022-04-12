from __future__ import annotations
from typing import Dict

class ProbabilisticGraph:
    class StateNode:
        def __init__(self, data: Any):
            self._data = data
            self._best_action = None
            self._best_value = None
            self._successors: List[ProbabilisticGraph.ActionNode] = []
            
        @property
        def data(self):
            return self._data
        
        @property
        def best_action(self):
            return self._best_action
        
        @property
        def best_value(self):
            return self._best_value
            
        def __eq__(self, other: ProbabilisticGraph.StateNode):
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
            self._successors: List[Tuple[ProbabilisticGraph.StateNode, float, float]] = []
            
        @property
        def data(self):
            return self._data
            
        def __eq__(self, other: ProbabilisticGraph.ActionNode):
            return self._data.__eq__(other._data)
        
        def __hash__(self):
            return hash(self._data)
        
        def __str__(self):
            return str(self._data)
        
        def __repr__(self):
            return 'Node(data: {}, parent: {})'.format(
                repr(self._data))
    
    def __init__(self):
        self._nodes: Dict[Any, ProbabilisticGraph.StateNode] = {}
    
    def get_node(self, data: Any):
        if data not in self._nodes:
            self._nodes[data] = ProbabilisticGraph.StateNode(data)
        return self._nodes[data]
        
    def get_successors(self, node: StateNode) -> List[ActionNode]:
        if node.data not in self._nodes or len(node._successors) == 0:
            node._successors = list(self.generate_successors(node))
            self._nodes[node.data] = node
        return self._nodes[node.data]._successors
    
    def generate_successors(self, node: Node) -> List[ActionNode]:
        raise NotImplementedError
    
    def is_goal(self, node: StateNode) -> bool:
        raise NotImplementedError
    
    def render(self, node: StateNode) -> None:
        pass
