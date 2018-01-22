"""
Main function for halite.  Essentially creates a memory files, attempt to dump anything/everything to it,
and play the game
"""
import time
import sys
import copy
import pickle
import os
import numpy
from hlt import entity as ntt

try:
    import hlt
    import logging

    name = "Guylaine"
    if len(sys.argv) != 1:
        name = sys.argv[1]

    MEMORY_FILENAME = str(time.time() * 1000)

    game = hlt.Game(name)
    
    import nnutils
    import nn.GuylaineV3 as Guylaine
    import game as g
    import numpy as np

    from nn import starterBot

    game_map = game.map
    

    guylaine = Guylaine.Guylaine("guylaine")
    guylaine.load()

    command_queue = []

    while True:
        command_queue.clear()

        # advance the simulation 1 step
        game_map = game.update_map()

        if len(sys.argv) == 1: # nullbot
            game.send_command_queue(command_queue)
            continue

        # Get State
        for ship in game_map.get_me().all_ships():
            command = None

            target = guylaine.predict(ship, game_map)
            if type(target) is ntt.Planet:
                ship.can_dock(target)
                command = ship.dock(target)
            else:
                command = ship.navigate(
                    ship.closest_point_to(target),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)

            if (command != None):
                command_queue.append(command)
            
        game.send_command_queue(command_queue)
        

except Exception as e:
    try:
        logging.exception(str(e))

    except Exception as f:
        logging.exception(str(f))