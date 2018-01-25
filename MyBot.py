"""
Main function for halite.  Essentially creates a memory files, attempt to dump anything/everything to it,
and play the game
"""
import time
import sys
import copy
import os
import numpy
from hlt import entity as ntt

try:
    import hlt
    import logging
    
    name = "Guylaine"
    if len(sys.argv) >= 2:
        name = sys.argv[1]
    version = name
    game = hlt.Game(name)
    
    import nnutils
    import nn.GuylaineV3 as Guylaine
    import game as g
    import numpy as np

    from nn import starterBot

    game_map = game.map

    MAX_COMMAND = 25
    

    guylaine = Guylaine.Guylaine(version)
    guylaine.load()

    command_queue = []

    while True:
        command_queue.clear()
        # advance the simulation 1 step
        game_map = game.update_map()


        
        if len(sys.argv) == 2 and sys.argv[1] == "starterbot":
            for ship in game_map.get_me().all_ships():
                command = starterBot.predictStarterBot(ship, game_map)
                if command != None:
                    command_queue.append(command)

            game.send_command_queue(command_queue)
            continue
        # if len(sys.argv) == 1: # nullbot
        #     game.send_command_queue(command_queue)
        #     continue

        nbCommand = 0
        for ship in game_map.get_me().all_ships():
            command = None
            if nbCommand >= MAX_COMMAND:
                # logging.debug("maxCommand, skipping the rests")
                break

            target = guylaine.predict(ship, game_map)


            if target != None:
                # logging.debug("target is planet, distance : %s", distance_remaining)
                if ship.can_dock(target) and len(target.all_docked_ships()) < target.num_docking_spots and (target.owner == None or target.owner.id == game_map.get_me().id):
                    # logging.debug("target is planet, docking")
                    command = ship.dock(target)
                else:
                    if target.owner != None:
                        target = target.all_docked_ships()[0]
                    command = ship.navigate(
                        ship.closest_point_to(target),
                        game_map,
                        speed=int(hlt.constants.MAX_SPEED),
                        ignore_ships=False,
                        max_corrections=110)
                    # logging.debug("navigating closer, command: %s", command)

            # logging.debug("Command: %s", command)
            if (command != None):
                nbCommand += 1
                command_queue.append(command)
            
        game.send_command_queue(command_queue)
        

except Exception as e:
    try:
        logging.exception(str(e))

    except Exception as f:
        logging.exception(str(f))