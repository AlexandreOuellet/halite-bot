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
    
    name = sys.argv[1]
    
    applyRandomizedWeight = False

    if len(sys.argv) >= 3:
        applyRandomizedWeight = sys.argv[2] == "True"

    game = hlt.Game(name)
    
    import nnutils
    import nn.GuylaineV3 as Guylaine
    import game as g
    import numpy as np

    from nn import starterBot

    game_map = game.map
    

    guylaine = Guylaine.Guylaine(name)
    guylaine.load(applyRandomizedWeight)
    
    guylaine.save(applyRandomizedWeight)

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
            logging.debug("target: %s", target)
            distance_remaining = ship.calculate_distance_between(ship.closest_point_to(target))

            if type(target) is ntt.Planet:
                logging.debug("target is planet, distance : %s", distance_remaining)
                if ship.can_dock(target):
                    logging.debug("target is planet, docking")
                    command = ship.dock(target)
                else:
                    
                    command = ship.navigate(
                        target,
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED/2),
                        ignore_ships=False)
                    logging.debug("navigating closer, command: %s", command)


            else:
                command = ship.navigate(
                    ship.closest_point_to(target),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED/2),
                    ignore_ships=False)

            if (command != None):
                logging.debug("Command: %s", command)
                command_queue.append(command)
            
        game.send_command_queue(command_queue)
        

except Exception as e:
    try:
        logging.exception(str(e))

    except Exception as f:
        logging.exception(str(f))