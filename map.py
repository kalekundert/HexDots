import math
import time

from graph import *
from math import *

from pprint import *

FREE = "free"
CHEAP = "cheap"
EXPENSIVE = "expensive"
IMPASSABLE = "impassable"

# Tile {{{1
class Tile(Node):

    WEIGHTS = { FREE:1, CHEAP:1.5, EXPENSIVE:2 }

    def __init__(self, type, row, column):
        Node.__init__(self, 0)

        self.__row = row
        self.__column = column

        self.set_type(type)

    def get_type(self):
        return self.__type
    def set_type(self, type):
        self.__type = type

        if type == IMPASSABLE:
            self.deactivate()
        else:
            weight = Tile.WEIGHTS[type]
            self.set_weight(weight)

            self.activate()

    def get_row(self):
        return self.__row
    def get_column(self):
        return self.__column
    def get_position(self):
        return (self.__row, self.__column)
# Clearing {{{1
class Clearing(Tile):
    def __init__(self, map, row, column, spacing):
        Tile.__init__(self, map, row, column, spacing)
        self.activate()

# Barrier {{{1
class Barrier(Tile):
    def __init__(self, map, row, column, spacing):
        Tile.__init__(self, map, row, column, spacing)
        self.deactivate()
# }}}1

# Heuristics {{{1
def euclidean_heuristic(start, end):
    x1, y1 = start.get_position()
    x2, y2 = end.get_position()

    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def manhattan_heuristic(start, end):
    x1, y1 = start.get_position()
    x2, y2 = end.get_position()

    return abs(x2 - x1) + abs(y2 - y1)
# }}}1

# Map {{{1
class Map(SparseGraph):

    LOAD_FORMAT = { 'F':FREE, 'C':CHEAP, 'E':EXPENSIVE, 'I':IMPASSABLE }
    SAVE_FORMAT = { FREE:'F', CHEAP:'C', EXPENSIVE:'E', IMPASSABLE:'I' }

    # Initialization {{{2
    def __init__(self, path):
        SparseGraph.__init__(self)
        self.load(path)

    # Attributes {{{2
    def get_map(self):
        return self.__map
    def get_rows(self):
        return self.__map.values()
    def get_tile(self, row, column):
        return self.__map[row][column]

    def get_source(self):
        return self.__source
    def get_target(self):
        return self.__target
    def get_waypoints(self):
        return self.__waypoints

    def get_rows(self):
        return self.__rows
    def get_columns(self):
        return self.__columns
    def get_dimensions(self):
        return (self.__rows, self.__columns)

    def get_load_time(self):
        return self.__load_time

    def set_source(self, tile):
        if tile.get_type() != IMPASSABLE:
            self.__source = tile
    def set_target(self, tile):
        if tile.get_type() != IMPASSABLE:
            self.__target = tile
    def set_waypoints(self, *tiles):
        if tile.get_type() != IMPASSABLE:
            self.__waypoints = tiles

    def insert_waypoint(self, index, tile):
        self.__waypoints.insert(index, tile)
    def remove_waypoint(self, tile):
        self.__waypoints.remove(tile)
    # }}}2

    # Load From File {{{2

    # File format for load():
    #  Only the characters 'X' and 'O' are allowed, although any line
    #  beginning with a '#' will be ignored.  The 'O' character will create
    #  a clearing tile while the 'X' character will create a barrier one. 
    #  Any uncommented character besides those two will cause an exception.  

    def load(self, path):
        start_time = time.time()

        # Extracting tile data from the file:
        tiles, waypoints = self.read_file(path)

        # Saving dimension information:
        self.__map = {}
        self.__rows = len(tiles)
        self.__columns = len(tiles[0])

        # Storing new nodes in the graph:
        self.make_nodes(tiles)
        self.make_edges()
        self.make_waypoints(waypoints)

        # Gather profiling information:
        self.__load_time = time.time() - start_time

    def read_file(self, path):
        with open(path) as file:

            tiles = []
            waypoints = []

            for line in file:
                line = line.strip().upper()

                if not line or line[0] == '#':
                    continue
                elif line[0] in Map.LOAD_FORMAT.keys():
                    tiles.append(line)
                elif line[0].isdigit():
                    values = tuple(line.split())
                    waypoints.append(values)
                else:
                    raise ValueError("Unrecognized leading character '%s' in '%s'" % (line[0], path))

        return tiles, waypoints

    def make_nodes(self, tiles):
        row = 0
        map = self.__map

        for line in tiles:
            column = 0
            map[row] = {}

            for character in line:
                type = Map.LOAD_FORMAT[character]
                tile = Tile(type, row, column)

                self.add_node(tile)
                map[row][column] = tile

                column += 1
            row += 1

            assert column == self.get_columns()
        assert row == self.get_rows()

    def make_edges(self):
        square = 1
        diagonal = sqrt(2) * square

        neighbors = [(-1, -1, diagonal), (0, -1, square), (1, -1, diagonal),
                     (-1, 0, square),                     (1, 0, square),
                     (-1, 1, diagonal),  (0, 1, square),  (1, 1, diagonal)]

        map = self.__map
        add_edge = self.add_edge

        for tile in self.get_nodes():
            y, x = tile.get_position()
            
            for data in neighbors:
                try:
                    dx, dy, distance = data
                    neighbor = map[y + dy][x + dx]

                    add_edge(Edge(tile, neighbor, distance))
                    add_edge(Edge(neighbor, tile, distance))

                except KeyError:
                    pass

    def make_waypoints(self, waypoints):

        def get_waypoint(position):
            row, column = position
            node = self.get_tile(int(row), int(column))
            if node.is_active(): return node
            else:
                raise ValueError("The waypoint at R:%d C:%d is not over an active node." % position)

        source = waypoints.pop(0)
        self.__source = get_waypoint(source)

        target = waypoints.pop()
        self.__target = get_waypoint(target)

        for position in waypoints:
            node = self.get_waypoint(position)
            self.__waypoints.append(node)

    # }}}2
    # Write To File {{{2
    def save(self, path):
        with open(path, 'w') as file:
            file.write("# Waypoints:\n")
            file.write("%d %d\n" % self.get_source().get_position())
            file.write("%d %d\n" % self.get_target().get_position())

            file.write("\n# Tiles:\n")

            string = ""
            rows, columns = self.get_dimensions()

            for row in range(rows):
                for column in range(columns):
                    tile = self.get_tile(row, column)
                    string += Map.SAVE_FORMAT[tile.get_type()]

                file.write("%s\n" % string)
                string = ""

    # }}}2
# }}}1
