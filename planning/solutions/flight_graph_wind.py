AIRCRAFT_SPEED = 500
WIND_SPEED = 50

class FlightGraphWithWind(FlightGraph):
    
    def __init__(self, json_dict):
        super().__init__(json_dict)
        
    def generate_successors(self, node: Graph.Node) -> List[Tuple[Graph.Node, float, str]]:
        for nwp, d in self._gotos[node.data].items():
            xdir = EARTH_RADIUS * (nwp.long - node.data.long) * pi / 180.
            ydir = EARTH_RADIUS * (nwp.lat - node.data.lat) * pi / 180.
            xdir_normalized = xdir / sqrt(xdir**2 + ydir**2)
            ydir_normalized = ydir / sqrt(xdir**2 + ydir**2)
            temp = - ydir_normalized * WIND_SPEED
            speed_proj = temp + sqrt(temp**2 - WIND_SPEED**2 + AIRCRAFT_SPEED**2)
            yield (
                Graph.Node(data=nwp, parent=node),
                d / speed_proj,
                str('GOTO {}'.format(node.data))
            )