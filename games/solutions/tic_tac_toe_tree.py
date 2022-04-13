class TicTacToeTree(Tree):
    def __init__(self, tic_tac_toe):
        super().__init__()
        self._tic_tac_toe = tic_tac_toe
    
    def generate_children(self, node: Tree.Node) -> List[Tuple[Tree.Node, str]]:
        state = node.data
        avail_posx, avail_posy = np.asarray(state.array == 0).nonzero()
        for i in range(len(avail_posx)):
            next_state, value, terminal = self._tic_tac_toe.get_next_state(
                state,
                (Player.CrossPlayer if node.max_player else Player.CirclePlayer,
                 Action(x=avail_posx[i], y=avail_posy[i]))
            )
            yield (
                Tree.Node(data=next_state,
                          max_player = not node.max_player,
                          terminal = terminal,
                          terminal_value = value),
                '{} at ({}, {})'.format(
                    'cross' if node.max_player else 'circle',
                    str(avail_posx[i]),
                    str(avail_posy[i])
                )
            )
    
    def render(self, node: Tree.Node) -> None:
        self._tic_tac_toe.render(node.data)