from typing import Optional, Set

class GameRTDP:
    
    def __init__(
        self,
        graph: ProbabilisticGameGraph,
        heuristic: Optional[
            Callable[[ProbabilisticGameGraph.StateNode], float]
        ] = None,
        max_steps: int = 1000,
        trials_number: int = 100,
        verbose: bool = False,
        render: bool = False,
    ) -> None:

        self._graph = graph
        self._heuristic = (
            (lambda _: 0.0) if heuristic is None else heuristic
        )
        self._max_steps = max_steps
        self._trials_number = trials_number
        self._verbose = verbose
        self._render = render
        self._values = {}

    def solve_from(self, tree_node: Tree.Node) -> None:
        
        def extender(node, explored):
            actions = []
            for action in self._graph.get_successors(node):
                for next_state, _ in action._successors:
                    if next_state not in explored:
                        if self._verbose:
                            print('New node {}'.format(str(next_state)))
                        next_state._best_value = self._heuristic(next_state)
                        explored.add(next_state)
                actions.append(action)
            return actions
        
        root_node = self._graph.get_node(tree_node)
        trial_id = 0
        explored = set()
        explored.add(root_node)
        root_node._best_value = self._heuristic(root_node)
        
        while trial_id < self._trials_number:
            self.trial(root_node, extender, explored)
            trial_id += 1
        
        tree_node._best_child = root_node._best_action.data
    
    def trial(self,
              root_node: ProbabilisticGameGraph.StateNode,
              extender : Callable[[ProbabilisticGameGraph.StateNode,
                                   Set[ProbabilisticGameGraph.StateNode]],
                                  List[ProbabilisticGameGraph.ActionNode]],
              explored: Set[ProbabilisticGameGraph.StateNode]) -> None:
        
        state_node = root_node
        steps = 0
        
        while not self._graph.is_goal(state_node) and steps < self._max_steps:
            action_node, best_value = self.greedy_action(state_node, extender, explored)
            self.update(state_node, action_node, best_value)
            state_node = self.pick_next_state(action_node)
            steps += 1
    
    def greedy_action(self,
                      node: ProbabilisticGameGraph.StateNode,
                      extender : Callable[[ProbabilisticGameGraph.StateNode,
                                           Set[ProbabilisticGameGraph.StateNode]],
                                          List[ProbabilisticGameGraph.ActionNode]],
                      explored: Set[ProbabilisticGameGraph.StateNode]) -> Tuple[ProbabilisticGameGraph.ActionNode, float]:
        best_value = -float('inf')
        best_action = None
        for action_node in extender(node, explored):
            action_value = 0
            for next_state, probability in action_node._successors:
                action_value += probability * next_state._best_value
            if action_value > best_value:
                best_value = action_value
                best_action = action_node
        assert best_action is not None
        return best_action, best_value
    
    def update(self,
               state_node: ProbabilisticGameGraph.StateNode,
               action_node: ProbabilisticGameGraph.ActionNode,
               value: float) -> None:
        state_node._best_value = value
        state_node._best_action = action_node
    
    def pick_next_state(self, action_node: ProbabilisticGameGraph.ActionNode) -> ProbabilisticGameGraph.StateNode:
        population = []
        weights = []
        for ns, prob in action_node._successors:
            population.append(ns)
            weights.append(prob)
        return random.choices(population, weights=weights, k=1)[0]