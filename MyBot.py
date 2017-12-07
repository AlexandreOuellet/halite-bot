"""
Welcome to your first Halite-II bot!

This bot's name is Guylaine. It's purpose is simple (don't expect it to win complex games :) ):
1. Initialize game
2. If a ship is not docked and there are unowned planets
2.a. Try to Dock in the planet if close enough
2.b If not, go towards the planet

Note: Please do not place print statements here as they are used to communicate with the Halite engine. If you need
to log anything use the logging module.
"""

nbTurn = 0
try:
    import sys
    stdout = sys.stdout
    sys.stdout = open('./null.txt', 'w')

    # Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
    import hlt
    import logging

    # GAME START
    # Here we define the bot's name as Guylaine and initialize the game, including communication with the Halite engine.
    game = hlt.Game("Guylaine")

    import tensorflow as tf


    import os
    #disable warning of tensorflow
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99'

    tf.logging.set_verbosity(tf.logging.ERROR)

    import pickle
    # Then let's import the logging module so we can print out information
    
    import nnutils
    import game as g
    import numpy as np

    # import nn.GuylaineV2 as GuylaineV2
    import nn.Cattle as Cattle
    sys.stdout = stdout

    game_state = nnutils.Observe(game.map)

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
        game_map = game.update_map()
        nbTurn += 1
        game_state = nnutils.Observe(game_map)

        reward = nnutils.GetReward(game_map)
        logging.debug("Reward: %s", reward)


        if ship_action_dictionary != None:
            for key in ship_action_dictionary.keys():
                ship_state, action_taken = ship_action_dictionary[key]
                ship = game.map.get_me().get_ship(key)


                if ship != None:
                    next_ship_state = nnutils.getShipState(ship) 
                
                    cattle.remember(oldState, ship_state, action_taken, reward, game_state, next_ship_state, ship != None)
        
        command_queue = []


        for ship in game.map.get_me().all_ships():
            ship_state = nnutils.getShipState(ship)
            ship_action = cattle.predict(game_state, ship_state, ship, game_map)
            logging.debug("ship_action: %s", ship_action)

            action_index = np.argmax(ship_action)
            
            logging.debug("action_index: %s", action_index)


            ship_action_dictionary[ship.id] = (ship_state, action_index)
            # cattle.remember(game_state, ship_state, ship_action, reward, ship_state, False)

            command = nnutils.doActionIndex(game_map, ship, action_index)
            logging.debug(command)

            if (command != None):
                command_queue.append(command)

        game.send_command_queue(command_queue)

except Exception as e:
    try:
        logging.exception(str(e))
        # if nbTurn != 0 and sys.argv[1] == 'G1':
        #     # guylaine.save()
        #     # cattle.replay(nbTurn)
        #     cattle.saveMemory()

            # guylaine.replay(nbTurn)
    except Exception as f:
        logging.exception(str(f))
    # traceback.print_exc()
