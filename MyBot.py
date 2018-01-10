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


def save(data, filename):
    pickle.dump(data, open('./data/'+filename, 'wb'))

def load(fileName):
    if os.path.isfile(fileName):
        return pickle.load(open('./data/'+fileName, 'rb'))
    return []

MEMORY_FILENAME = str(time.time() * 1000)

REWARD_FILENAME = MEMORY_FILENAME+'_totalRewards'
totalRewards = load(REWARD_FILENAME)

nbTurn = 0
try:
    # Let's start by importing the Halite Starter Kit so we can interface with the Halite engine
    import hlt
    import logging

    # GAME START
    # Here we define the bot's name as Guylaine and initialize the game, including communication with the Halite engine.
    if sys.argv[1] == 'G1':
        game = hlt.Game("Guylaine")
    else:
        game = hlt.Game("Starterbot")
    
    import nnutils
    import game as g
    import numpy as np

    # import nn.GuylaineV2 as GuylaineV2
    import nn.Cattle as Cattle
    from nn import starterBot

    game_map = game.map
    game_state = nnutils.Observe(game_map)

    ship_input_size = 5
    guylaine_output_size = 320*240
    cattle_output_size = 3 + nnutils.nbAngleStep * nnutils.nbSpeedStep # dock/undock/nothing
    logging.debug("cattle_output_size: %s", cattle_output_size)
    # guylaine = GuylaineV2.GuylaineV2(nnutils.tileWidth, nnutils.tileHeight, len(state), guylaine_output_size, 'data/GuylaineV2' + sys.argv[1])
    

    if sys.argv[1] == 'G1':
        cattle = Cattle.Cattle((14, nnutils.tileWidth, nnutils.tileHeight), (ship_input_size,), cattle_output_size, 'data/Cattle')
    # guylaine_output = guylaine.act(state)

    # guylaine.load()
    if sys.argv[1] == 'G1':
        cattle.load()

    ship_state = np.array([120, 120, 255, 1, 250])
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
            totalRewards.append(reward)

        if sys.argv[1] == 'G1':
            if ship_action_dictionary != None:
                for key in ship_action_dictionary.keys():
                    old_ship_state, action_taken = ship_action_dictionary[key]
                    ship = game_map.get_me().get_ship(key)


                    if ship != None:
                        next_ship_state = nnutils.getShipState(ship) 
                        next_ship_state = numpy.append(next_ship_state, nbTurn)
                    
                        cattle.remember(oldState, old_ship_state, action_taken, reward, game_state, next_ship_state, ship != None)
            
        command_queue = []


        for ship in game_map.get_me().all_ships():
            ship_state = nnutils.getShipState(ship)
            ship_state = numpy.append(ship_state, nbTurn)
            if sys.argv[1] == 'G1':
                ship_action = cattle.predict(game_state, ship_state, ship, game_map)


                action_index = np.argmax(ship_action)

                ship_action_dictionary[ship.id] = (ship_state, action_index)

                command = nnutils.doActionIndex(game_map, ship, action_index)
            else:
                command = starterBot.predictStarterBot(ship, game_map)
                logging.debug("Command: %s", command)
            logging.debug(command)

            if (command != None):
                command_queue.append(command)

        if sys.argv[1] != 'G1':
            command_queue.clear()
            
        game.send_command_queue(command_queue)
        # if (nbTurn % 25) == 0 and sys.argv[1] == 'G1':
        #     cattle.saveMemory(MEMORY_FILENAME)

except Exception as e:
    # cattle.saveMemory(MEMORY_FILENAME)

    # logging.debug(e)
    try:
        logging.exception(str(e))
        if sys.argv[1] == 'G1':
            cattle.saveMemory(MEMORY_FILENAME)
            save(totalRewards, REWARD_FILENAME)
        # if nbTurn != 0 and sys.argv[1] == 'G1':
        #     # guylaine.save()
        #     # cattle.replay(nbTurn)
        # cattle.saveMemory()

            # guylaine.replay(nbTurn)
    except Exception as f:
        logging.exception(str(f))