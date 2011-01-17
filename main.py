#!/usr/bin/env python

import pygame
from pygame.locals import *

import os, sys
import tokens

from game import GameLoop
from interface import InterfaceLoop

# Run in a background process
#if os.fork():
    #raise SystemExit

# Choose a map from the command line, if possible
try: map = sys.argv[1]
except IndexError:
    map = "maps/hole.hex"

# Create some important game managers.
world = tokens.World()
loops = GameLoop(world), InterfaceLoop(world)

# Load the game world.
world.load(map)

# Setup the  loops.
for loop in loops:
    loop.setup()

# Play the game!
while True:
    loop.update()
    pygame.time.wait(50)

# Close all the loops down.
for loop in loops:
    loop.teardown()

