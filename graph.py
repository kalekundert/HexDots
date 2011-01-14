# Node {{{1
class Node:

    UNSET_INDEX = -1

    def __init__(self, weight):
        self.index = Node.UNSET_INDEX
        self.weight = weight
        
        self.activate()

    def __repr__(self):
        return "<Node %s>" % self.get_index()

    def get_index(self):
        return self.index
    def get_weight(self):
        assert self.weight
        return self.weight

    def set_index(self, index):
        assert self.get_index() == Node.UNSET_INDEX
        self.index = index
    def set_weight(self, weight):
        self.weight = weight

    def is_active(self):
        return self.active

    def activate(self):
        self.active = True
    def deactivate(self):
        self.active = False

# Edge {{{1
class Edge:

    def __init__(self, start, end, distance=1):
        self.set_nodes(start, end)
        self.set_distance(distance)

    def __repr__(self):
        return "<Edge: %s to %s>" % (self.get_start().get_index(), self.get_end().get_index())

    def is_active(self):
        return self.get_start().is_active() and self.get_end().is_active()

    def get_nodes(self):
        return (self.start, self.end)
    def set_nodes(self, start, end):
        self.start = start
        self.end = end

    def get_start(self):
        return self.start
    def get_end(self):
        return self.end
    def get_distance(self):
        return self.distance

    def get_cost(self):
        weight = self.get_start().get_weight() * self.get_end().get_weight()
        distance = self.get_distance()
        return weight * distance

    def set_start(self, start):
        self.start = start
    def set_end(self, end):
        self.end = end
    def set_distance(self, distance):
        self.distance = distance
# }}}1
# Graph {{{1
class SparseGraph:
    def __init__(self):
        self.nodes = []
        self.edges = {}

    def __iter__(self):
        for node in self.nodes:
            yield node

    def add_node(self, node):
        if node in self.nodes:
            message = "This node is already in the graph at position #%d."
            raise KeyError(message % self.nodes.index(node))

        index = len(self.nodes)
        node.set_index(index)
        self.nodes.append(node)

        return index

    def add_edge(self, edge):
        start = edge.get_start()
        end = edge.get_end()

        if start not in self.edges:
            self.edges[start] = {}
        if end not in self.edges[start]:
            self.edges[start][end] = edge

    def expand_node(self, node):
        pass

    def get_node(self, index):
        return self.nodes[index]
    def get_nodes(self):
        return self.nodes
    def get_num_nodes(self):
        return len(self.nodes)

    def get_index(self, node):
        return self.nodes.index(node)
    def index_exists(self, index):
        return index < len(self.nodes)

    def get_edges(self):
        return self.edges
    def get_edge(self, start, end):
        return self.edges[start][end]
    def get_edges_from(self, node):
        return self.edges[node].values()
    def get_all_edges(self):
        return [edge
                for node in self.get_edges()
                for edge in self.get_edges_from(node)]
    def get_num_edges(self):
        return len(self.get_all_edges())

    def get_neighbors(self, node, cache_ok=True):
        return (edge.get_end() for edge in self.get_edges_from(node))
# }}}1
