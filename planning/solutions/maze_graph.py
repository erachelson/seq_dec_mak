class MazeGraph(Graph):
    def __init__(self, maze: Maze):
        super().__init__()
        self._maze = maze
    
    def generate_successors(self, node: Graph.Node) -> List[Tuple[Graph.Node, float, str]]:
        for action in Action:
            successor, cost = self._maze.get_transition_state_and_cost(node.data, action)
            yield (
                Graph.Node(successor, parent=node),
                cost,
                str(action)
            )
    
    def is_goal(self, node: Graph.Node) -> bool:
        return self._maze.is_goal(node.data)
    
    def render(self, node: Graph.Node) -> None:
        self._maze.render(node.data)