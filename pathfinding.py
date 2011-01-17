import time
import trees
import graph

# Base Search Algorithm {{{1
class SearchAlgorithm:

    # Operators {{{2
    def __init__(self):
        self.route = []
        self.routes = {}
        self.visited = {}

        self.found = False
        self.searching = False

        self.start_time = 0
        self.search_time = 0

    def __str__(self):
        return "[%s] Search Time: %f" % (self.get_name(), self.get_search_time())

    # Attributes {{{2
    def is_searching(self):
        return self.searching
    def was_target_found(self):
        return self.found
    def get_search_time(self):
        return self.search_time

    def get_route(self):
        return self.route
    def get_routes(self):
        return self.routes
    # }}}2

    # Search Methods {{{2
    def search(self, source, target):
        self.searching = True
        self.start_time = time.time()

    def target_found(self, routes, source, target):
        tile = target
        route = [tile]

        while tile != source:
            tile = routes[tile]
            route.append(tile)

        self.route = route
        self.routes = routes

        self.found = True
        self.searching = False
        self.search_time = time.time() - self.start_time

    def target_not_found(self, routes):
        self.route = []
        self.routes = routes

        self.found = False
        self.searching = False
        self.search_time = time.time() - self.start_time

# }}}1

# Depth First Search {{{1
class DepthFirstSearch(SearchAlgorithm):
    def search(self, map):
        SearchAlgorithm.search(self, map)

        source = map.get_source()
        target = map.get_target()

        routes = dict()
        visited = set()

        dummy = graph.Edge(source, source)
        edges = [dummy]
        
        while edges:
            edge = edges.pop()
            start = edge.get_start()
            end = edge.get_end()

            routes[end] = start
            visited.add(end)

            if end == target:
                self.target_found(routes, source, target)
                break

            edges_from = map.expand_node(end)
            if not edges_from:
                edges_from = map.get_edges_from(end)

            # Use comprehensions for performance gains.
            new_edges = [ edge for edge in edges_from
                          if edge.is_active()
                          if edge.get_end() not in visited ]
            edges += new_edges

        else:
            self.target_not_found(routes)

# Breadth First Search {{{1
class BreadthFirstSearch(SearchAlgorithm):
    def search(self, map):
        SearchAlgorithm.search(self, map)

        source = map.get_source()
        target = map.get_target()

        routes = {}
        visited = set([source])

        dummy = graph.Edge(source, source)
        stack = [dummy]

        while stack:
            edge = stack.pop(0)
            start = edge.get_start()
            end = edge.get_end()

            routes[end] = start

            if end == target:
                self.target_found(routes, source, target)
                break

            edges_from = map.expand_node(end)
            if not edges_from:
                edges_from = map.get_edges_from(end)

            for edge in edges_from:
                if not edge.is_active(): continue
                if edge.get_end() in visited: continue

                stack.append(edge)
                visited.add(edge.get_end())
        else:
            self.target_not_found(routes)
# }}}1

# The Mighty A* {{{1
class A_Star(SearchAlgorithm):

    def __init__(self, graph):
        SearchAlgorithm.__init__(self)
        self.graph = graph

    def search(self, source, target):
        SearchAlgorithm.search(self, source, target)

        routes = {}
        starting_nodes = { source : source }

        real_costs = { source : 0 }
        estimated_costs = { source : 0 }

        frontier_nodes = trees.IndexedPQ(estimated_costs)
        frontier_nodes.push(source)

        heuristic = self.graph.heuristic

        # Loop through the graph.
        while not frontier_nodes.empty():

            closest_node = frontier_nodes.pop()
            routes[closest_node] = starting_nodes[closest_node]

            # Check to see if the target was found.
            if closest_node == target:
                self.target_found(routes, source, target)
                break

            # Add more edges to consider.
            edges_from = self.graph.expand_node(closest_node)
            if not edges_from:
                edges_from = self.graph.get_edges_from(closest_node)

            for edge in edges_from:
                if not edge.is_active(): continue
                if edge.get_end() in routes: continue

                start = edge.get_start()
                end = edge.get_end()

                real_cost = real_costs[start] + edge.get_cost()
                heuristic_cost = heuristic(end, target)

                if end in frontier_nodes:
                    # Already considering this node; choose the shortest path.
                    if real_cost < real_costs[end]:
                        real_costs[end] = real_cost
                        estimated_costs[end] = real_cost + heuristic_cost

                        starting_nodes[end] = start
                        frontier_nodes.update(end)
                else:
                    # Haven't been here before; store the edge.
                    real_costs[end] = real_cost
                    estimated_costs[end] = real_cost + heuristic_cost

                    starting_nodes[end] = start
                    frontier_nodes.push(end)
        else:
            self.target_not_found(routes)

# Dijkstra's Algorithm {{{1
class Dijkstra(A_Star):
    def __init__(self):
        A_Star.__init__(self, self.__heuristic)

    def __heuristic(self, start, end):
        return 0
# }}}1
