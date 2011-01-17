class GameLoop:

    def __init__(self, world):
        self.world = world

    def setup(self):
        pass

    def update(self, time):
        self.world.get_dot().update(time)

    def teardown(self):
        pass
