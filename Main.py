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

    import nn.Guylaine as Guylaine
    import nn.GuylaineV2 as GuylaineV2
    from nn.dqn import DQN

    states = nnutils.Observe(game.map)

    guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth * nnutils.tileHeight, len(states), 100, 'GuylaineV2')
    # guylaine.setInitState(states, len(g.Action))
    act_value = guylaine.act(states)

    # brain = Guylaine.Guylaine(planetStates, shipStates, len(g.Action), sys.argv[1])
    # brain.load()
    # brain.setInitState(planetStates, shipStates)

    while True:
        # TURN START
        # Update the map for the new turn and get the latest version
        game_map = game.update_map()

        command_queue = []

        oldPlanetStates = np.copy(planetStates)
        oldShipStates = np.copy(shipStates)
        planetStates, shipStates = nnutils.Observe(game_map)

        actionIndex = brain.getAction(planetStates, shipStates)
        actions = np.zeros(len(g.Action))
        actions[actionIndex] = 1

        for ship in game.map.get_me().all_ships():
            command = g.doAction(game_map, ship, actions)
            logging.debug(command)
            if (command != None):
                command_queue.append(command)
        

        reward = nnutils.GetReward(game_map)
        
        brain.setPerception(oldPlanetStates, oldShipStates, actions, reward, planetStates, shipStates, False)

        game.send_command_queue(command_queue)

except Exception as e:
    try:
        logging.exception(str(e))
        brain.save()
        brain.replay(25)
    except Exception as f:
        logging.exception(str(f))
    # traceback.print_exc()
    