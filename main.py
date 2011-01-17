#!/usr/bin/env python

import pygame
from pygame.locals import *

import os, sys
import tokens

from game import GameLoop
from interface import InterfaceLoop

# Objectives and Goals {{{1
# ====================
# 1. Have dots move along their given path.  Initially this could be done in a
#    jerky manner, but eventually I want the dots to appear to move smoothly
#    between tiles
# 
# 2. Implement a messenger system.  I think it would be wise to do this before
#    I write much more of the game, because it really is supposed to be a
#    central part of the architecture.  The longer I put it off, the more code
#    I'll have to rewrite.
#
# 3. Create a sandbox game.  More specifically, this will involve allowing
#    dots to move, fight, and reproduce.  From a user interface perspective,
#    the dots will also have to be individually selectable and controllable.
# }}}1

# Choose a map from the command line, if possible
try: map = sys.argv[1]
except IndexError:
    map = "maps/hole.hex"

# Create some important game managers.
world = tokens.World()

clock = pygame.time.Clock()
loops = GameLoop(world), InterfaceLoop(world)

# Load the game world.
world.load(map)

# Setup the  loops.
for loop in loops:
    loop.setup()

# Play the game!
while True:
    time = clock.tick(40)
    for loop in loops:
        loop.update(time)

# Close all the loops down.
for loop in loops:
    loop.teardown()
