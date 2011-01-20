#!/usr/bin/env python

from __future__ import division

import pygame
from pygame.locals import *

import tokens
import messages

from math import *
from vector import *

# Interface Loop {{{1
class InterfaceLoop:

    def __init__(self, world, messenger):
        self.world = world
        self.messenger = messenger

        self.screen = None

        map = self.world.get_map()
        dots = self.world.get_dots()

        self.geometry = Geometry(map, 30)
        self.controls = Controls(dots)
        self.style = Style()
        self.layers = Layers()

        self.artists = [ 
                MapArtist(self, map),
                DotArtist(self, dots),
                SelectionArtist(self),
                PracticeArtist(self) ]

        self.actors = {
                QUIT : QuitActor(self),
                MOUSEBUTTONUP : TargetActor(self) }

    def get_world(self):
        return self.world
    def get_messenger(self):
        return self.messenger

    def get_dimensions(self):
        return self.screen.get_size()

    def get_geometry(self):
        return self.geometry
    def get_controls(self):
        return self.controls
    def get_style(self):
        return self.style
    def get_layers(self):
        return self.layers

    def get_helpers(self):
        return self.geometry, self.controls, self.style, self.layers

    def setup(self):
        pygame.init()
        pygame.display.set_caption("Dots!")

        for helper in self.get_helpers():
            helper.load()

        size = self.geometry.for_window()
        self.screen = pygame.display.set_mode(size)


        for actor in self.actors.values():
            actor.load()

        for artist in self.artists:
            artist.load()

    def update(self, time):

        background = self.style.for_background()
        self.screen.fill(background)

        # Handle incoming events.
        for event in pygame.event.get():
            try:
                actor = self.actors[event.type]
                actor.handle(event, time)
            except KeyError:
                pass

        # Draw the next frame.
        for layer in self.layers:
            for artist in self.artists:
                artist.draw(self.screen, layer, time)

        # Flip the display buffers.
        pygame.display.flip()

    def teardown(self):
        pass
# }}}1

# Geometry {{{1
class Geometry:

    def __init__(self, map, side):
        self.map = map
        self.side = side

    def get_side(self):
        return self.side
    def get_width(self):
        return self.width
    def get_height(self):
        return self.height
    def get_dimensions(self):
        return self.width, self.height

    def for_tiles(self):
        return self.tiles

    def for_window(self):
        columns, rows = self.map.get_dimensions()

        width = columns * self.grid_width
        height = rows * self.grid_height + self.a

        return int(width), int(height)

    # Load Method {{{2
    def load(self):
        s = side = self.side
        self.offsets = self.map.get_offsets()

        self.a = a = side * cos(pi / 3)
        self.b = b = side * sin(pi / 3)

        self.width = w = 2 * b
        self.height = h = 2 * a + s
        self.radius = r = h / 2

        self.grid_width = 2 * b
        self.grid_height = a + s

        self.corners = [
                Vector.from_degrees(angle)
                for angle in range(30, 360, 60) ]

    # }}}2

    # Dot and Tile Conversions {{{2
    def dot_to_point(self, dot):
        tile = dot.get_position()
        return self.tile_to_point(tile)

    def dot_to_circle(self, dot, scale=1):
        tile = dot.get_position()
        return self.tile_to_circle(tile, scale)

    def dot_to_outline(self, dot, stroke, pad=0):
        tile = dot.get_position()
        return self.tile_to_outline(tile, stroke, pad)

    def tile_to_circle(self, tile, scale=1):
        center = self.tile_to_point(tile)
        radius = self.width * scale
        return center, radius

    def tile_to_hexagon(self, tile, pad=0):
        center = self.tile_to_point(tile)

        factor = 2 * sin(pi / 3)
        radius = self.radius  - (pad / factor)

        return [center + corner * radius
                for corner in self.corners]

    def tile_to_outline(self, tile, stroke, pad=0):
        result = []
        center = self.tile_to_point(tile)

        factor = 2 * sin(pi / 3)

        radius = self.radius  - (pad / factor)
        points = [center + corner * radius for corner in self.corners]

        result.extend(points)
        result.append(points[0])

        radius -= stroke
        points = [center + corner * radius for corner in self.corners]

        result.append(points[0])
        result.extend(reversed(points))

        return result

    def tile_to_point(self, tile):
        row, column = tile.get_position()

        x = self.grid_width * (column + 0.5)
        y = self.side * row + self.a * (row + 1) + self.side / 2

        if self.offsets[row]:
            x += self.grid_width * 0.5

        return Vector(x, y)

    # Coordinate Conversions {{{2
    def point_to_dot(self, x, y):
        tile = self.point_to_tile(x, y)
        # Return the dot on this tile, if there is one.
        raise NotImplementedError

    def point_to_tile(self, x, y):
        row = int(y / self.grid_height)

        if self.offsets[row]:
            x -= self.grid_width * 0.5

        column = int(x / self.grid_width)

        return self.map.get_tile(row, column)
    # }}}2

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

    def load(self):
        self.tile_stroke = 3
        self.tile_outline = Color(0, 0, 0)
        self.tile_fill = [
                Color(255, 255, 255),
                Color(245, 245, 245),
                Color(225, 225, 225) ]

        self.background_color = Color(0, 0, 0)

        self.dot_fill = Color(255, 0, 0)
        self.dot_outline = Color(0, 0, 0)
        self.dot_scale = 30 / 100
        self.dot_stroke = 3

        self.selected_outline = Color(255, 0, 0)
        self.selected_stroke = 5

        self.target_color = Color(0, 255, 0)
        self.target_stroke = 5

        self.waypoint_color = Color(255, 0, 255)
        self.waypoint_scale = 10 / 100

    def for_tile(self, tile):
        column = tile.get_column()
        offset = tile.get_offset()
        
        position = column if not offset else column - 1
        fill = self.tile_fill[position % 3]

        return fill, self.tile_outline, self.tile_stroke

    def for_background(self):
        return self.background_color

    def for_dot(self):
        return (self.dot_fill, self.dot_scale,
                self.dot_outline, self.dot_stroke)

    def for_selected(self):
        return self.selected_outline, self.selected_stroke
        
    def for_target(self):
        return self.target_color, self.target_stroke

    def for_waypoint(self):
        return self.waypoint_color

# Layers {{{1
class Layers:

    def __iter__(self):
        yield self.map_layer
        yield self.outline_layer
        yield self.dots_layer

    def load(self):
        self.map_layer = 0
        self.outline_layer = 1
        self.dots_layer = 2

    def drawing_map(self, layer):
        return (layer == self.map_layer)

    def finishing_map(self, layer):
        return (layer == self.outline_layer)

    def drawing_dots(self, layer):
        return (layer == self.dots_layer)
# }}}1

# Map Artist {{{1
class MapArtist:

    def __init__(self, gui, map):
        self.gui = gui; self.map = map
        self.tiles = []

    def load(self):
        style = self.gui.get_style()
        geometry = self.gui.get_geometry()

        for tile in self.map:
            if not tile.is_active():
                continue

            fill, outline, stroke = style.for_tile(tile)
            points = [point.get_int_tuple()
                    for point in geometry.tile_to_hexagon(tile) ]

            self.tiles.append((points, fill, outline, stroke))

    def draw(self, screen, layer, time):
        layers = self.gui.get_layers()

        for points, fill, outline, stroke in self.tiles:
            if layers.drawing_map(layer):
                pygame.draw.polygon(screen, fill, points)
            if layers.finishing_map(layer):
                pygame.draw.polygon(screen, outline, points, stroke)

# Dot Artist {{{1
class DotArtist:

    def __init__(self, gui, dots):
        self.gui = gui
        self.dots = dots

    def load(self):
        pass

    def draw(self, screen, layer, time):

        style = self.gui.get_style()
        geometry = self.gui.get_geometry()
        layers = self.gui.get_layers()

        if layers.drawing_dots(layer):

            for dot in self.dots:
                fill, scale, outline, stroke = style.for_dot()
                center, radius = geometry.dot_to_circle(dot, scale)

                center = center.get_int_tuple()
                radius = int(radius)

                pygame.draw.circle(screen, outline, center, radius)
                pygame.draw.circle(screen, fill, center, radius - stroke)

# Selection Artist {{{1
class SelectionArtist:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        pass

    def draw(self, screen, layer, time):
        helpers = self.gui.get_helpers()
        geometry, controls, style, layers = helpers

        if not layers.drawing_map(layer):
            return

        tile_to_outline = geometry.tile_to_outline

        for dot in controls.get_selection():
            target = dot.get_target()
            position = dot.get_position()

            # Highlight the selected dot.
            color, stroke = style.for_selected()
            points = [point.get_int_tuple()
                    for point in tile_to_outline(position, stroke) ]

            pygame.draw.polygon(screen, color, points)

            # Draw where the dot is going to.
            if target:
                color, stroke = style.for_target()
                points = [point.get_int_tuple()
                        for point in tile_to_outline(target, stroke) ]

                pygame.draw.polygon(screen, color, points)

# Practice Artist {{{1
class PracticeArtist:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        width, height = self.gui.get_dimensions()

        pad = 0; stroke = 25
        radius = 100

        center = Vector(width, height) / 2

        factor = 2 * sin(pi / 3)

        outer_radius = self.gui.geometry.radius  - (pad / factor)
        inner_radius = radius - stroke

        inner_points = [center + corner * inner_radius
                for corner in self.gui.geometry.corners]
        outer_points = [center + corner * outer_radius
                for corner in self.gui.geometry.corners]

        points = []

        points.extend(outer_points)
        points.append(outer_points[0])
        points.append(inner_points[0])
        points.extend(reversed(inner_points))

        self.points = [point.get_int_tuple() for point in points]

    def draw(self, screen, layer, time):
        pass

# }}}1

# Quit Actor {{{1
class QuitActor:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        pass

    def handle(self, event, time):
        raise SystemExit

# Target Actor {{{1
class TargetActor:

    def __init__(self, gui):
        self.gui = gui

    def load(self):
        pass

    def handle(self, event, time):
        controls = self.gui.get_controls()
        geometry = self.gui.get_geometry()
        messenger = self.gui.get_messenger()

        try: 
            dots = controls.get_selection()
            target = geometry.point_to_tile(*event.pos)

            controls.set_target(target)

            message = messages.MoveDot(dots, target)
            messenger.send(message.type, message)

        except EmptySelection: return
        except tokens.TileException: return
# }}}1

# Empty Selection {{{1
class EmptySelection(Exception):
    pass
# }}}1
