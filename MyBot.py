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
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 

MEMORY_FILENAME = str(time.time() * 1000)

# REWARD_FILENAME = MEMORY_FILENAME+'_totalRewards'
# totalRewards = load(REWARD_FILENAME)

nbTurn = 0
try:
    import hlt
    import logging

    name = "Guylaine"
    if len(sys.argv) != 1:
        name = sys.argv[1]

    game = hlt.Game(name)
    
    import nnutils
    import game as g
    import numpy as np

    import nn.CattleV2 as Cattle
    from nn import starterBot

    game_map = game.map
    

    cattle = Cattle.Cattle((nnutils.input_size,), nnutils.output_size, name)
    cattle.load()

    command_queue = []

    while True:
        command_queue.clear()
        game_map = game.update_map()

        nbTurn += 1

        if len(sys.argv) == 1: # nullbot
            game.send_command_queue(command_queue)
            continue

        # Get State
        for ship in game_map.get_me().all_ships():
            observations = nnutils.observe(game_map, ship)
            ship_state = nnutils.createStateFromObservations(nbTurn,
                ship,
                observations)

            logging.debug(observations)
            # cattle.remember(ship, ship_state, reward, next_state)

            actions = cattle.predict(ship_state, ship, game_map)
            command = nnutils.getCommand(game_map, ship, actions, observations)
            if (command != None):
                command_queue.append(command)
            
        game.send_command_queue(command_queue)

except Exception as e:
    try:
        logging.exception(str(e))

        if len(sys.argv) != 1:
            cattle.saveMemory(MEMORY_FILENAME)
            # save(totalRewards, REWARD_FILENAME)

    except Exception as f:
        logging.exception(str(f))