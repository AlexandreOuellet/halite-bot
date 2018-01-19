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
# os.environ['CUDA_VISIBLE_DEVICES'] = '-1' 

def load(dirAndFile):
    # if os.path.exists(dirAndFile) == False:
    #     os.makedirs(dirAndFile)
    if os.path.isfile(dirAndFile):
        return pickle.load(open(dirAndFile, 'rb'))
    return []

def save(dataToSave, dirAndFile):
    # if os.path.exists(dirAndFile) == False:
    #     os.makedirs(dirAndFile)
    pickle.dump(dataToSave, open(dirAndFile, 'wb'))

nbTurn = 0

NO_ACTION_PENALTY = -5
try:
    import hlt
    import logging

    name = "Guylaine"
    if len(sys.argv) != 1:
        name = sys.argv[1]

    MEMORY_FILENAME = str(time.time() * 1000)

    REWARD_FILENAME = "./{}/{}_totalRewards".format(name, MEMORY_FILENAME)
    totalRewards = load(REWARD_FILENAME)

    game = hlt.Game(name)
    
    import nnutils
    import game as g
    import numpy as np

    import nn.CattleV2 as Cattle
    from nn import starterBot

    game_map = game.map
    

    cattle = Cattle.Cattle((nnutils.input_size,), nnutils.output_size, name)
    forceZeroEpsilon = True
    if len(sys.argv) == 3:
        forceZeroEpsilon = False
    cattle.load(forceZeroEpsilon)

    command_queue = []
    shipStateAction = []

    while True:
        command_queue.clear()
        old_map = copy.deepcopy(game_map)

        # advance the simulation 1 step
        game_map = game.update_map()
        nbTurn += 1

        overallReward = nnutils.getReward(old_map, game_map)
        totalRewards.append(overallReward)

        currentProduction, nbShips, health = nnutils.getFriendlyObservation(game_map)
        enemyProduction, nbEnemyShips, enemyHealth = nnutils.getEnemyObservation(game_map)

        if len(sys.argv) == 1: # nullbot
            game.send_command_queue(command_queue)
            continue

        # Get State
        for ship in game_map.get_me().all_ships():
            observations = nnutils.observe(game_map, ship)
            ship_state = nnutils.createStateFromObservations(nbTurn,
                ship,
                observations,
                currentProduction, nbShips, health,
                enemyProduction, nbEnemyShips, enemyHealth)

            # logging.debug("observations")
            # logging.debug("closestEmptyPlanets: %s", observations[nnutils.ObservationIndexes.closestEmptyPlanets.value])
            # logging.debug("closestEnemyPlanets: %s", observations[nnutils.ObservationIndexes.closestEnemyPlanets.value])
            # logging.debug("closestEnemyShips: %s", observations[nnutils.ObservationIndexes.closestEnemyShips.value])
            # logging.debug("closestFriendlyShips: %s", observations[nnutils.ObservationIndexes.closestFriendlyShips.value])
            # logging.debug("closestFriendlyPlanets: %s", observations[nnutils.ObservationIndexes.closestFriendlyPlanets.value])
            # logging.debug("ship_state: %s", ship_state)

            actions = cattle.predict(ship_state, ship, game_map)
            action_taken = np.argmax(actions)

            reward = overallReward

            command = nnutils.getCommand(game_map, ship, actions, observations)
            if command == None:
                reward -= NO_ACTION_PENALTY

            cattle.rememberNextState(ship.id, ship_state, action_taken, reward)

            # logging.debug("Command: %s", command)

            if (command != None):
                command_queue.append(command)
            
        game.send_command_queue(command_queue)
        
        # if len(sys.argv) != 1:
        #     cattle.saveMemory(MEMORY_FILENAME)

except Exception as e:
    try:
        logging.exception(str(e))

        if len(sys.argv) != 1:
            cattle.saveMemory(MEMORY_FILENAME)
            save(totalRewards, REWARD_FILENAME)

    except Exception as f:
        logging.exception(str(f))