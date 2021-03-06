import graph

# World {{{1
class World:

    def __init__(self):
        self.map = Map()
        self.dots = [Dot(self.map)]

    def load(self, path):
        self.map.load(path)

        home = self.map.get_home_tile()
        self.dots[0].load(home)

    def get_map(self):
        return self.map

    def get_dots(self):
        return self.dots

# Dot {{{1
class Dot:

    def __init__(self, map):
        self.position = None

        self.speed = 500
        self.progress = 0

        self.route = []
        self.target = None

    def load(self, position):
        self.position = position

    def update(self, time):
        if not self.route:
            return

        self.progress += time
        if self.progress > self.speed:
            self.position = self.route.pop()
            self.progress = 0

        if not self.route:
            self.target = None

    def get_position(self):
        return self.position
    def get_route(self):
        return self.route
    def get_target(self):
        return self.target

    def set_route(self, loop, route):
        self.route = route
    def set_target(self, loop, target):
        self.target = target
# }}}1

# Tile {{{1
class Tile(graph.Node):

    def __init__(self, row, column, offset):
        graph.Node.__init__(self, 1)

        self.row = row
        self.column = column
        self.offset = offset

    def get_row(self):
        return self.row
    def get_column(self):
        return self.column
    def get_offset(self):
        return self.offset

    def get_position(self):
        return (self.row, self.column)

class ClearTile(Tile):
    def __init__(self, row, column, offset):
        Tile.__init__(self, row, column, offset)
        self.activate()

class ImpassableTile(Tile):
    def __init__(self, row, column, offset):
        Tile.__init__(self, row, column, offset)
        self.deactivate()

# Map {{{1
class Map(graph.SparseGraph):

    # Constructor {{{2
    def __init__(self):
        graph.SparseGraph.__init__(self)

        self.map = {}
        self.offsets = []

        self.rows = 0
        self.columns = 0

        self.home_tile = None

    # Attributes {{{2
    def get_map(self):
        return self.map
    def get_rows(self):
        return self.map.values()
    def get_offsets(self):
        return self.offsets
    def get_tile(self, row, column):
        try:
            tile = self.map[row][column]

            if tile.is_active(): return tile
            else: raise InactiveTile(tile)

        except IndexError:
            raise NoSuchTile()

    def get_home_tile(self):
        return self.home_tile

    def get_width(self):
        return self.columns
    def get_height(self):
        return self.rows
    def get_dimensions(self):
        return (self.columns, self.rows)
    # }}}2

    def heuristic(self, end, target):
        return 0

    # Load From File {{{2

    # For Each Line...
    # ----------------
    # 1. Find the offset of the line.  This requires finding the first
    #    non-space character, since spaces represent impassable tiles.
    #
    # 2. Remove the extraneous spaces.  This requires knowing the offset
    #    for each line, because some spaces are significant.
    #
    # 3. Create a grid of tiles.  Each tile needs to know its position in
    #    the grid and the offset of its row.
    # 
    # 4. Create edges to connect the nodes.  This also requires the offset
    #    data, because it will affect the inter-row connectivity.
        
    def load(self, path):
        """ Builds this map object from the provided file.  The file format
        should be as follows:
        
        The only allowed characters are ' ' and 'F'.  'F' represents a clear
        tile and ' ' represents an impassable one.  Because the map is made of
        hexagonal tiles, every other row should be indented by one space and
        there should be a space between each tile character.  These
        restrictions will make the text look like a hexagonal grid. 

        If these restrictions are not followed, the code will probably break
        in unpredictable ways.  There is almost no error-checking. """

        self.map = {}
        self.rows = self.columns = 0

        # Extracting tile data from the file:
        tiles, offsets = self.read_file(path)

        # Storing new nodes in the graph:
        self.make_nodes(tiles, offsets)
        self.make_edges(offsets)

    def read_file(self, path):
        """ Reads data from the given map file into memory.  This is a private
        method and should not be called outside of this class. """

        tiles = []
        offsets = []

        with open(path) as file:
            for line in file:

                # Ignore empty lines and comments.
                line = line.rstrip().upper()
                if not line or line[0] == '#':
                    continue

                # Determine whether or not this line is offset.
                leading_tile = line.index('F')
                offset = (leading_tile % 2 == 1)

                # Prune irrelevant characters from the line.
                relevant_tiles = ""
                for index, character in enumerate(line):
                    if (index % 2) == (leading_tile % 2):
                        relevant_tiles += character

                # Save information about the map.
                tiles.append(relevant_tiles)
                offsets.append(offset)

                self.rows += 1
                self.columns = max(self.columns, len(relevant_tiles))

        self.offsets = offsets
        return tiles, offsets

    def make_nodes(self, tiles, offsets):
        """ Creates graph nodes based on the information read out of the map
        file.  This is a private method and should not be called outside this
        class. """

        row = 0
        map = self.map

        for line, offset in zip(tiles, offsets):
            column = 0
            map[row] = {}

            for character in line:
                if character == ' ':
                    tile = ImpassableTile(row, column, offset)
                else:
                    tile = ClearTile(row, column, offset)
                    if character == 'H': self.home_tile = tile

                self.add_node(tile)
                map[row][column] = tile

                column += 1
            row += 1

    def make_edges(self, offsets):
        """ Creates graph edges based on the data read out of the map file.
        Two-way edges are mimicked using two one-way edges in each case.  This
        is a private method and should not be called from outside of this
        class. """

        behind = [(-1, -1), (0, -1), (-1, 0),  (1, 0), (-1, 1),  (0, 1)]
        in_front = [(0, -1), (1, -1), (-1, 0),  (1, 0), (0, 1),  (1, 1)]

        map = self.map
        add_edge = self.add_edge

        for tile in self.get_nodes():
            y, x = tile.get_position()

            offset = offsets[y]
            neighbors = in_front if offset else behind

            for data in neighbors:
                try:
                    dx, dy = data
                    neighbor = map[y + dy][x + dx]

                    add_edge(graph.Edge(tile, neighbor))
                    add_edge(graph.Edge(neighbor, tile))

                except KeyError:
                    pass
# }}}1

# Tile Exception {{{1
class TileException(Exception):
    pass

# No Such Tile {{{1
class NoSuchTile(TileException):
    pass

# Inactive Tile {{{1
class InactiveTile(TileException):

    def __init__(self, tile):
        TileException.__init__(self)
        self.tile = tile

    def get_title(self):
        return self.tile
# }}}1
