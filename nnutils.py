import hlt
import logging
import numpy as np

# the world seems to always be a ratio of 24x16
tileWidth = 320
tileHeight = 240

def GetReward(map):
    myId = map.get_me().id
    totalShips = np.zeros(4)
    totalShipsHealth = np.zeros(4)
    productionSpeedPerPlayer = np.zeros(4)

    for planet in map.all_planets():
        
        for dockedShip in planet.all_docked_ships():
            productionSpeedPerPlayer[planet.owner.id] += 1

    for player in map.all_players():
        for ship in player.all_ships():
            totalShips[player.id] += 1
            totalShipsHealth[player.id] += ship.health

    totalShipReward = totalShips[myId] / np.sum(totalShips)
    shipHealthReward = totalShipsHealth[myId] / np.sum(totalShipsHealth)

    productionSpeedReward = np.sum(productionSpeedPerPlayer)
    if productionSpeedReward != 0:
        productionSpeedReward = productionSpeedPerPlayer[myId] / productionSpeedReward 

    return np.average([totalShipReward, shipHealthReward, productionSpeedReward])

def _calculateAverage(myId, toCalculate):
    myNb = toCalculate[myId]
    totalNb = 0

    for playerId in range(0, 3):
        if playerId == myId:
            myNb = toCalculate[playerId]

        totalNb += toCalculate[playerId]

def Observe(map):
    
    planetsStates = discretizePlanets(map)
    shipsStates = discretizedShips(map)

    nbStates = len(planetsStates)
    for i in range(0, len(shipsStates)):
        nbStates += len(shipsStates[i])

    states = np.ndarray(shape=(nbStates, tileWidth, tileHeight))
    
    currentState = 0

    for i in range(0, len(planetsStates)):
        states[currentState] = planetsStates[i]
        currentState += 1

    for p in range(0, len(shipsStates)):
        for i in range(0, len(shipsStates[p])):
            states[currentState] = shipsStates[p][i]
            currentState += 1

    return states

def discretizePlanets(map):
    # planetsRadius = np.zeros(tileWidth * tileHeight)
    planetsRadius = np.ndarray(shape=(tileWidth, tileHeight))
    planetsNumDockingSpots = np.ndarray(shape=(tileWidth, tileHeight))
    planetsCurrentProduction = np.ndarray(shape=(tileWidth, tileHeight))
    planetsRemainingResources = np.ndarray(shape=(tileWidth, tileHeight))
    planetsOwner = np.ndarray(shape=(tileWidth, tileHeight))
    planetsHealth = np.ndarray(shape=(tileWidth, tileHeight))

    planets = map.all_planets()
    for planet in planets:
        # tileIndex = mapToArrayIndex(planet.x, planet.y)
        planetsRadius[int(planet.x)][int(planet.y)] = planet.radius
        planetsNumDockingSpots[int(planet.x)][int(planet.y)] = planet.num_docking_spots
        planetsCurrentProduction[int(planet.x)][int(planet.y)] = planet.current_production
        planetsRemainingResources[int(planet.x)][int(planet.y)] = planet.remaining_resources
        if planet.owner != None:
            planetsOwner[int(planet.x)][int(planet.y)] = planet.owner
        planetsHealth[int(planet.x)][int(planet.y)] = planet.health

        # planetsDockedShipPlayer1[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer2[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer3[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer4[tileIndex] = [None] * tileWidth * tileHeight


    return planetsRadius, planetsNumDockingSpots, planetsCurrentProduction,planetsRemainingResources,planetsOwner,planetsHealth

def discretizedShips(map):
    # shipsPlayer1Present = [None] * tileWidth * tileHeight
    shipsPlayerHealth = np.ndarray(shape=(4, tileWidth, tileHeight))
    shipsPlayerDockingStatus = np.ndarray(shape=(4, tileWidth, tileHeight))

    # for i in range(0, 4):
    #     shipsPlayerHealth[i] = np.zeros(shape=(tileWidth, tileHeight))
    #     shipsPlayerDockingStatus[i] = np.zeros(shape=(tileWidth, tileHeight))


    # for x in range(0, 3):
        # shipsPlayerHealth[x] = np.zeros(tileWidth * tileHeight)
        # shipsPlayerDockingStatus[x] = np.zeros(tileWidth * tileHeight)
    
    for player in map.all_players():
        for ship in player.all_ships():
            # index = mapToArrayIndex(ship.x, ship.y)
            # shipsPlayer1Present[index] = 1
            shipsPlayerHealth[player.id][int(ship.x)][int(ship.y)] = ship.health
            shipsPlayerDockingStatus[player.id][int(ship.x)][int(ship.y)] = int(ship.docking_status.value)

    shipsPlayerHealth = _swapArrays(map.get_me().id, 0, shipsPlayerHealth)
    shipsPlayerDockingStatus = _swapArrays(map.get_me().id, 0, shipsPlayerDockingStatus)

    return shipsPlayerHealth, shipsPlayerDockingStatus

def _swapArrays(index1, index2, array):
    tmp = array[index1]
    array[index1] = array[index2]
    array[index2] = tmp

    return array

def mapToArrayIndex(x, y):
    return (int)((x/tileWidth) + tileWidth*(y/tileHeight))