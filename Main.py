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
    # Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
    import hlt
    import logging

    # GAME START
    # Here we define the bot's name as Guylaine and initialize the game, including communication with the Halite engine.
    game = hlt.Game("Guylaine" + sys.argv[1])

    import tensorflow as tf
    import os

    import pickle
    # Then let's import the logging module so we can print out information
    
    import nnutils
    import game as g
    import numpy as np
    
    #disable warning of tensorflow
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '99'
    # tf.logging.set_verbosity(tf.logging.ERROR)

    import nn.GuylaineV2 as GuylaineV2
    import nn.Cattle as Cattle

    state = nnutils.Observe(game.map)

    ship_input_size = 4
    guylaine_output_size = 100
    cattle_output_size = 6 # dock/undock/north/south/east/west
    guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
    cattle = Cattle.Cattle(guylaine_output_size, ship_input_size, 6, 'data/Cattle' + sys.argv[1])
    guylaine_output = guylaine.act(state)

    guylaine.load()
    cattle.load()

    ship_input = np.array([120, 120, 255, 1])
    output = cattle.predict(guylaine_output, ship_input)

    while True:
        # TURN START
        # Update the map for the new turn and get the latest version
        oldState = np.copy(state)
        game_map = game.update_map()
        nbTurn += 1
        state = nnutils.Observe(game_map)

        reward = nnutils.GetReward(game_map)
        logging.debug("Reward: %d", reward)

        guylaine.remember(oldState, guylaine_output, reward, state, False)
        command_queue = []

        guylaine_output = guylaine.act(state)

        for ship in game.map.get_me().all_ships():
            ship_state = nnutils.getShipState(ship)
            ship_action = cattle.predict(guylaine_output, ship_state)

            cattle.remember(guylaine_output, ship_state, ship_action, reward, guylaine_output, ship_state, False)

            command = g.doAction(game_map, ship, ship_action)
            logging.debug(command)

            if (command != None):
                command_queue.append(command)

        game.send_command_queue(command_queue)

except Exception as e:
    try:
        logging.exception(str(e))
        if nbTurn != 0:
            cattle.save()
            guylaine.save()

            cattle.replay(nbTurn)
            # guylaine.replay(nbTurn)
    except Exception as f:
        logging.exception(str(f))
    # traceback.print_exc()
