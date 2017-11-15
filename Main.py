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
    # Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
    import hlt
    import logging

    # GAME START
    # Here we define the bot's name as Guylaine and initialize the game, including communication with the Halite engine.
    game = hlt.Game("Guylaine")

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
    from nn.dqn import DQN

    # https://github.com/FitMachineLearning/FitML/blob/master/LunarLander_QL.py

    # stateOfGame = pickle.load( open( "save.pickle", "rb" ) )
    # planetStates = stateOfGame[0]
    # shipStates = stateOfGame[1]

    planetStates, shipStates = nnutils.Observe(game.map)

    # pickle.dump( game, open( "game.pickle", "wb" ) )
    

    brain = Guylaine.Guylaine(planetStates, shipStates, len(g.Action))
    brain.load()
    brain.setInitState(planetStates, shipStates)

    while True:
        # TURN START
        # Update the map for the new turn and get the latest version
        game_map = game.update_map()

        command_queue = []

        oldPlanetStates = planetStates
        oldShipStates = shipStates
        planetStates, shipStates = nnutils.Observe(game_map)

        actionIndex = brain.getAction(planetStates, shipStates)
        actionIndex = 3
        actions = np.zeros(len(g.Action))
        actions[actionIndex] = 1

        for ship in game.map.get_me().all_ships():
            command = g.doAction(game_map, ship, actions)
            logging.debug(command)
            command_queue.append(command)
        

        reward = nnutils.GetReward(game_map)
        
        brain.setPerception(oldPlanetStates, oldShipStates, actions, reward, planetStates, shipStates, False)

        game.send_command_queue(command_queue)
        
        # logging.info("Reward:" + str(reward))

        # # Here we define the set of commands to be sent to the Halite engine at the end of the turn
        # command_queue = []

        # # For every ship that I control
        # for ship in game_map.get_me().all_ships():
            
        #     # If the ship is docked
        #     if ship.docking_status != ship.DockingStatus.UNDOCKED:
        #         # Skip this ship
        #         continue

        #     # For each planet in the game (only non-destroyed planets are included)
        #     for planet in game_map.all_planets():
        #         # If the planet is owned
        #         if planet.is_owned():
        #             # Skip this planet
        #             continue

        #         # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
        #         if ship.can_dock(planet):
        #             # We add the command by appending it to the command_queue
        #             command_queue.append(ship.dock(planet))
        #         else:
        #             # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
        #             # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
        #             # We run this navigate command each turn until we arrive to get the latest move.
        #             # Here we move at half our maximum speed to better control the ships
        #             # In order to execute faster we also choose to ignore ship collision calculations during navigation.
        #             # This will mean that you have a higher probability of crashing into ships, but it also means you will
        #             # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
        #             # wish to turn that option off.
        #             navigate_command = ship.navigate(
        #                 ship.closest_point_to(planet),
        #                 game_map,
        #                 speed=int(hlt.constants.MAX_SPEED/2),
        #                 ignore_ships=True)
        #             # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
        #             # or we are trapped (or we reached our destination!), navigate_command will return null;
        #             # don't fret though, we can run the command again the next turn)
        #             if navigate_command:
        #                 command_queue.append(navigate_command)
        #         break

        # # Send our set of commands to the Halite engine for this turn
        # game.send_command_queue(command_queue)
        # TURN END
    # GAME END
except Exception as e:
    brain.save()
    # traceback.print_exc()
    logging.exception(str(e))