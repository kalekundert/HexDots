#!/usr/bin/env python

import tokens, pygame
from pygame.locals import *

from math import *
from vector import *

# Known Bugs {{{1
# ==========
# None!
#
# Areas to Improve {{{1
# ================
# 1. The point_to_tile() method in the geometry class isn't super-accurate.
# This is a consequence of the algorithm that's being used, which assumes a
# rectangular map, not a hexagonal one.
# }}}1

# Interface Loop {{{1
class InterfaceLoop:

    def __init__(self, world):
        self.world = world
        self.screen = None

        map = self.world.get_map()
        dot = self.world.get_dot()

        self.geometry = Geometry(map, 30)
        self.controls = Controls(dot)
        self.style = Style(self.geometry)

        self.artists = [ 
                MapArtist(self, map),
                DotArtist(self, dot),
                TargetArtist(self) ]

        self.actors = {
                QUIT : QuitActor(self),
                MOUSEBUTTONUP : TargetActor(self, self.controls) }

    def get_geometry(self):
        return self.geometry
    def get_controls(self):
        return self.controls
    def get_style(self):
        return self.style

    def setup(self):
        pygame.init()

        self.geometry.load()
        self.controls.load()
        self.style.load()

        for actor in self.actors.values():
            actor.load()

        for artist in self.artists:
            artist.load()

        size = self.geometry.for_window()
        self.screen = pygame.display.set_mode(size)

    def update(self):

        background = self.style.for_background()
        self.screen.fill(background)

        # Handle incoming events.
        for event in pygame.event.get():
            try:
                actor = self.actors[event.type]
                actor.handle(event)
            except KeyError:
                pass

        # Draw the next frame.
        for artist in self.artists:
            artist.draw(self.screen)

        # Update the display and sleep.
        pygame.display.flip()

    def teardown(self):
        pass
# }}}1

# Geometry {{{1
class Geometry:

    def __init__(self, map, side):
        self.map = map
        self.side = side

    def load(self):
        s = side = self.side
        self.offsets = self.map.get_offsets()

        self.a = a = side * cos(pi / 3)
        self.b = b = side * sin(pi / 3)

        self.width = w = 2 * b
        self.height = h = 2 * a + s

        self.grid_width = 2 * b
        self.grid_height = a + s

        self.corners =                                  \
                Vector(0, h / 2), Vector(b, s / 2),     \
                Vector(b, -s / 2), Vector(0, -h / 2),   \
                Vector(-b, -s / 2), Vector(-b, s / 2)

    def get_side(self):
        return self.side
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    def get_dimensions(self):
        return self.width, self.height

    def for_tile(self, tile):
        center = self.tile_to_point(tile)
        return [(corner + center).get_int_tuple()
                for corner in self.corners]

    def for_window(self):
        columns, rows = self.map.get_dimensions()

        width = columns * self.grid_width
        height = rows * self.grid_height + self.a

        return int(width), int(height)

    def dot_to_point(self, dot):
        tile = dot.get_position()
        return self.tile_to_point(tile)

    def point_to_dot(self, x, y):
        tile = self.point_to_tile(x, y)
        # Return the dot on this tile, if there is one.
        raise NotImplementedError

    def tile_to_point(self, tile):
        row, column = tile.get_position()

        x = self.grid_width * (column + 0.5)
        y = self.side * row + self.a * (row + 1) + self.side / 2

        if self.offsets[row]:
            x += self.grid_width * 0.5

        return Vector(x, y)

    def point_to_tile(self, x, y):
        row = int(y / self.grid_height)

        if self.offsets[row]:
            x -= self.grid_width * 0.5

        column = int(x / self.grid_width)

        return self.map.get_tile(row, column)

# Controls {{{1
class Controls:
    
    def __init__(self, selection):
        self.target = None
        self.selection = selection

    def load(self):
        pass

    def get_target(self):
        return self.target
    def get_selection(self):
        if not self.selection:
            raise EmptySelection()
        return self.selection

    def set_target(self, target):
        self.target = target
    def set_selection(self, selection):
        self.selection = selection

    def clear_target(self):
        self.target = None

# Style {{{1
class Style:

    def __init__(self, geometry):
        self.geometry = geometry

    def load(self):
        tile_width = self.geometry.get_width()

        self.tile_stroke = 3
        self.tile_outline = Color(0, 0, 0)
        self.tile_fill = [
                Color(255, 255, 255),
                Color(245, 245, 245),
                Color(225, 225, 225) ]

        self.background_color = Color(0, 0, 0)

        self.dot_fill = Color(255, 0, 0)
        self.dot_outline = Color(0, 0, 0)
        self.dot_radius = int(tile_width / 3)
        self.dot_stroke = 3

        self.target_color = Color(0, 255, 0)
        self.target_radius = int(tile_width / 5)

        self.waypoint_color = Color(255, 0, 255)
        self.waypoint_radius = int(tile_width / 5)

    def for_tile(self, tile):
        column = tile.get_column()
        offset = tile.get_offset()
        
        position = column if not offset else column - 1
        fill = self.tile_fill[position % 3]

        return fill, self.tile_outline, self.tile_stroke
    
    def for_background(self):
        return self.background_color

    def for_dot(self):
        return (self.dot_fill, self.dot_radius,
                self.dot_outline, self.dot_stroke)
        
    def for_target(self):
        return self.target_color, self.target_radius

    def for_waypoint(self):
        return self.waypoint_color, self.waypoint_radius
# }}}1

# Map Artist {{{1
class MapArtist:

    def __init__(self, gui, map):
        self.gui = gui; self.map = map
        self.tiles = []

    def load(self):
        self.tiles = []

        style = self.gui.get_style()
        geometry = self.gui.get_geometry()

        for tile in self.map:
            if not tile.is_active():
                continue

            points = geometry.for_tile(tile)
            fill, outline, stroke = style.for_tile(tile)

            self.tiles.append((points, fill, outline, stroke))

    def draw(self, screen):
        for points, fill, outline, stroke in self.tiles:
            pygame.draw.polygon(screen, fill, points)
            pygame.draw.polygon(screen, outline, points, stroke)

# Dot Artist {{{1
class DotArtist:

    def __init__(self, gui, dot):
        self.gui = gui
        self.dot = dot

    def load(self):
        pass

    def draw(self, screen):
        style = self.gui.get_style()
        geometry = self.gui.get_geometry()

        center = geometry.dot_to_point(self.dot).get_int_tuple()
        fill, radius, outline, stroke = style.for_dot()

        pygame.draw.circle(screen, outline, center, radius)
        pygame.draw.circle(screen, fill, center, radius - stroke)

        for tile in self.dot.get_waypoints():
            center = geometry.tile_to_point(tile).get_int_tuple()
            color, radius = style.for_waypoint()

            pygame.draw.circle(screen, color, center, radius)

# Target Artist {{{1
class TargetArtist:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        pass

    def draw(self, screen):
        style = self.gui.get_style()
        geometry = self.gui.get_geometry()
        controls = self.gui.get_controls()

        target = controls.get_target()
        if not target:
            return

        center = geometry.tile_to_point(target).get_int_tuple()
        color, radius = style.for_target()

        pygame.draw.circle(screen, color, center, radius)
# }}}1

# Quit Actor {{{1
class QuitActor:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        pass

    def handle(self, event):
        raise SystemExit

# Target Actor {{{1
class TargetActor:

    def __init__(self, gui, controls):
        self.gui = gui
        self.controls = controls

    def load(self):
        pass

    def handle(self, event):
        controls = self.controls
        geometry = self.gui.get_geometry()

        try: 
            dot = controls.get_selection()
            pathfinder = dot.get_pathfinder()

            source = dot.get_position()
            target = geometry.point_to_tile(*event.pos)

            pathfinder.search(source, target)

        except EmptySelection:
            return

        except tokens.TileException:
            return

        controls.set_target(target)
# }}}1

# Empty Selection {{{1
class EmptySelection(Exception):
    pass
# }}}1
