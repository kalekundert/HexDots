class GameLoop:

    def __init__(self, world):
        self.world = world

    def setup(self):
        pass

    def update(self):
        self.world.get_dot().update()

    def teardown(self):
        pass
