"""
Main function for halite.  Essentially creates a memory files, attempt to dump anything/everything to it,
and play the game
"""
import time
import sys
import copy
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 

MEMORY_FILENAME = str(time.time() * 1000)

nbTurn = 0
try:
    # Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
    import hlt
    import logging

    # GAME START
    # Here we define the bot's name as Guylaine and initialize the game, including communication with the Halite engine.
    game = hlt.Game("Guylaine")
    
    import nnutils
    import game as g
    import numpy as np

    # import nn.GuylaineV2 as GuylaineV2
    import nn.Cattle as Cattle

    game_map = game.map
    game_state = nnutils.Observe(game_map)

    ship_input_size = 4
    guylaine_output_size = 100
    cattle_output_size = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
    logging.debug("cattle_output_size: %s", cattle_output_size)
    # guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
    cattle = Cattle.Cattle((14, nnutils.tileWidth, nnutils.tileHeight), (ship_input_size,), cattle_output_size, 'data/Cattle')
    # guylaine_output = guylaine.act(state)

    # guylaine.load()
    cattle.load()

    ship_state = np.array([120, 120, 255, 1])
    # output = cattle.predict(game_state, ship_state)

    ship_action_dictionary = {}

    while True:
        # TURN START
        # Update the map for the new turn and get the latest version
        oldState = np.copy(game_state)
        old_map = copy.deepcopy(game_map)
        game_map = game.update_map()
        nbTurn += 1
        game_state = nnutils.Observe(game_map)

        if (old_map and game_map):
            reward = nnutils.GetReward(old_map, game_map)

        if ship_action_dictionary != None:
            for key in ship_action_dictionary.keys():
                old_ship_state, action_taken = ship_action_dictionary[key]
                ship = game_map.get_me().get_ship(key)


                if ship != None:
                    next_ship_state = nnutils.getShipState(ship) 
                
                    cattle.remember(oldState, old_ship_state, action_taken, reward, game_state, next_ship_state, ship != None)
        
        command_queue = []


        for ship in game_map.get_me().all_ships():
            ship_state = nnutils.getShipState(ship)
            ship_action = cattle.predict(game_state, ship_state, ship, game_map)

            action_index = np.argmax(ship_action)

            ship_action_dictionary[ship.id] = (ship_state, action_index)

            command = nnutils.doActionIndex(game_map, ship, action_index)
            logging.debug(command)

            if (command != None):
                command_queue.append(command)

        game.send_command_queue(command_queue)
        # if (nbTurn % 25) == 0 and sys.argv[1] == 'G1':
        #     cattle.saveMemory(MEMORY_FILENAME)

except Exception as e:
    # cattle.saveMemory(MEMORY_FILENAME)

    # logging.debug(e)
    try:
        logging.exception(str(e))
        cattle.saveMemory(MEMORY_FILENAME)
        # if nbTurn != 0 and sys.argv[1] == 'G1':
        #     # guylaine.save()
        #     # cattle.replay(nbTurn)
        # cattle.saveMemory()

            # guylaine.replay(nbTurn)
    except Exception as f:
        logging.exception(str(f))