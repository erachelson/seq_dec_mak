from heapq import heappop, heappush
from itertools import count
from typing import Callable, Optional, List

class Astar:
    
    def __init__(
        self,
        graph: Graph,
        heuristic: Optional[
            Callable[[Graph.Node], float]
        ] = None,
        verbose: bool = False,
        render: bool = False,
    ) -> None:

        self._graph = graph
        self._heuristic = (
            (lambda _: 0.0) if heuristic is None else heuristic
        )
        self._verbose = verbose
        self._render = render
        self._values = {}

    def solve_from(self, root_node: Graph.Node) -> List[Graph.Node]:
        
        def extender(node, explored):
            for node, cost, label in self._graph.get_successors(node):
                if node not in explored:
                    if self._verbose:
                        print('New node {}'.format(str(node)))
                    yield (
                        node,
                        cost,
                        label,
                    )

        push = heappush
        pop = heappop

        # The queue is the OPEN list.
        # It stores priority, node, cost to reach and label (i.e. edge, any data type) of transition from parent.
        # Uses Python heapq to keep in priority order.
        # Add a counter to the queue to prevent the underlying heap from
        # attempting to compare the nodes themselves. The hash breaks ties in the
        # priority and is guaranteed unique for all nodes in the graph.
        c = count()

        # TODO: check if necessary (a priori used to keep additional infos)
        initial_label = {root_node: None}
        # Maps enqueued nodes to distance of discovered paths and the
        # computed heuristics to target. We avoid computing the heuristics
        # more than once and inserting the node into the queue too many times.
        enqueued = {
            root_node: (0, self._heuristic(root_node))
        }
        queue = [
            (enqueued[root_node][1], next(c), root_node, 0, initial_label[root_node])
        ]
        # The explored dict is the CLOSED list.
        # It maps explored nodes to a pair of parent closest to the source and label of transition from parent.
        explored = {}
        path = []
        estim_total = 0.0
        while queue:
            # Pop the smallest item from queue, i.e. with smallest f-value
            estim_total, __, curnode, dist, label = pop(queue)
            if self._render:
                self._graph.render(curnode)
            if self._verbose:
                print(
                    curnode,
                    f"- cumulated cost: {dist} - estimated total cost: {estim_total}",
                )
            if self._graph.is_goal(curnode):
                path = [(curnode.parent, label), (curnode, None)]
                node = curnode.parent
                while node is not None:
                    label = explored[node]
                    if node.parent is not None:
                        path.insert(0, (node.parent, label))
                    node = node.parent
                break  # return path, dist, enqueued[curnode][0], len(enqueued)
            if curnode in explored:
                continue
            explored[curnode] = label
            for neighbor, cost, lbl in extender(curnode, explored):
                if neighbor in explored:
                    continue
                ncost = dist + cost
                if neighbor in enqueued:
                    qcost, h = enqueued[neighbor]
                    # if qcost < ncost, a longer path to neighbor remains
                    # enqueued. Removing it would need to filter the whole
                    # queue, it's better just to leave it there and ignore
                    # it when we visit the node a second time.
                    if qcost <= ncost:
                        continue
                else:
                    h = self._heuristic(neighbor)
                enqueued[neighbor] = ncost, h
                push(
                    queue,
                    (
                        ncost + h,
                        next(c),
                        neighbor,
                        ncost,
                        lbl,
                    ),
                )
        return estim_total, path