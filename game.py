import messages
import pathfinding

class GameLoop:

    def __init__(self, world, messenger):
        self.world = world
        self.messenger = messenger

        self.pathfinder = None

    def setup(self):
        map = self.world.get_map()
        self.pathfinder = pathfinding.A_Star(map)

        type = messages.MoveDot.type
        self.messenger.subscribe(type, self.move_dot)

    def update(self, time):
        for dot in self.world.get_dots():
            dot.update(time)

    def teardown(self):
        pass

    def move_dot(self, message):
        for dot in message.dots:
            source = dot.get_position()
            target = message.target

            pathfinder = self.pathfinder
            pathfinder.search(source, target)

            route = pathfinder.get_route()

            dot.set_route(self, route)
            dot.set_target(self, target)
