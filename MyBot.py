"""
Main function for halite.  Essentially creates a memory files, attempt to dump anything/everything to it,
and play the game
"""
import time
import sys

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

    game_state = nnutils.Observe(game.map)

    ship_input_size = 4
    guylaine_output_size = 100
    cattle_output_size = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
    logging.debug("cattle_output_size: %s", cattle_output_size)
    # guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
    cattle = Cattle.Cattle((13, nnutils.tileWidth, nnutils.tileHeight), (ship_input_size,), cattle_output_size, 'data/Cattle')
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
        if (nbTurn % 25) == 0 and sys.argv[1] == 'G1':
            cattle.saveMemory(MEMORY_FILENAME)

except Exception as e:
    cattle.saveMemory(MEMORY_FILENAME)

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