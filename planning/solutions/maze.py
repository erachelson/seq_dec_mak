from copy import deepcopy
from enum import Enum
from typing import Any, NamedTuple, Tuple, List

# %matplotlib inline
import matplotlib.pyplot as plt
from IPython.display import display, clear_output


DEFAULT_MAZE = """
+-+-+-+-+o+-+-+-+-+-+
|   |             | |
+ + + +-+-+-+ +-+ + +
| | |   |   | | |   |
+ +-+-+ +-+ + + + +-+
| |   |   | |   |   |
+ + + + + + + +-+ +-+
|   |   |   | |     |
+-+-+-+-+-+-+-+ +-+ +
|             |   | |
+ +-+-+-+-+ + +-+-+ +
|   |       |       |
+ + + +-+ +-+ +-+-+-+
| | |   |     |     |
+ +-+-+ + +-+ + +-+ +
| |     | | | |   | |
+-+ +-+ + + + +-+ + +
|   |   |   |   | | |
+ +-+ +-+-+-+-+ + + +
|   |       |     | |
+-+-+-+-+-+x+-+-+-+-+
"""


class State(NamedTuple):
    x: int
    y: int


class Action(Enum):
    up = 0
    down = 1
    left = 2
    right = 3


class Maze:
    def __init__(self, maze_str: str = DEFAULT_MAZE):
        maze = []
        for y, line in enumerate(maze_str.strip().split("\n")):
            line = line.rstrip()
            row = []
            for x, c in enumerate(line):
                if c in {" ", "o", "x"}:
                    row.append(1)  # spaces are 1s
                    if c == "o":
                        self._start = State(x, y)
                    if c == "x":
                        self._goal = State(x, y)
                else:
                    row.append(0)  # walls are 0s
            maze.append(row)
        # self._render_maze = deepcopy(self._maze)
        self._maze = maze
        self._num_cols = len(maze[0])
        self._num_rows = len(maze)
        self._ax = None
        self._fig = None
        self._image = None

    def get_transition_state_and_cost(self, state: State, action: Action) -> Tuple[State, float]:

        if action == Action.left:
            next_state = State(state.x - 1, state.y)
        if action == Action.right:
            next_state = State(state.x + 1, state.y)
        if action == Action.up:
            next_state = State(state.x, state.y - 1)
        if action == Action.down:
            next_state = State(state.x, state.y + 1)

        # If candidate next state is valid
        if (
            0 <= next_state.x < self._num_cols
            and 0 <= next_state.y < self._num_rows
            and self._maze[next_state.y][next_state.x] == 1
        ):
            return (
                next_state,
                abs(next_state.x - state.x) + abs(next_state.y - state.y)  # every move costs 1
            )
        else:
            return (
                state,
                2  # big penalty when hitting a wall
            )
    
    def get_initial_state(self) -> State:
        return self._start
    
    def is_goal(self, state: State) -> bool:
        return state == self._goal

    def render(self, state: State, path: List[State] = None) -> Any:
        if self._ax is None:
            fig, ax = plt.subplots(1)
            fig.canvas.set_window_title("Maze")
            ax.set_aspect("equal")  # set the x and y axes to the same scale
            plt.xticks([])  # remove the tick marks by setting to an empty list
            plt.yticks([])  # remove the tick marks by setting to an empty list
            ax.invert_yaxis()  # invert the y-axis so the first row of data is at the top
            self._ax = ax
            self._fig = fig
            plt.ion()
        maze = deepcopy(self._maze)
        maze[self._goal.y][self._goal.x] = 0.7
        maze[state.y][state.x] = 0.3
        if path is not None:
            for s in path:
                maze[s.y][s.x] = 0.5
        if self._image is None:
            self._image = self._ax.imshow(maze)
        else:
            self._image.set_data(maze)
        display(self._fig)
        clear_output(wait = True)
        plt.pause(0.001)
        
maze = Maze()
maze.render(maze.get_initial_state())