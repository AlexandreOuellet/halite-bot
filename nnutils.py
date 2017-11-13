import hlt
import logging
import numpy as np

# the world seems to always be a ratio of 24x16
tileWidth = 24
tileHeight = 16

def GetReward(map):
    myId = map.get_me().id
    totalShips = np.zeros(4)
    totalShipsHealth = np.zeros(4)
    productionSpeedPerPlayer = np.zeros(4)


    for planet in map.all_planets():
        # if planet.owner != None:
        #     productionSpeedPerPlayer[planet.owner] += planet.
        
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
    planetsModel = discretizePlanets(map)
    shipsModel = discretizedShips(map)
    return planetsModel, shipsModel

def discretizePlanets(map):
    planetsRadius = np.zeros(tileWidth * tileHeight)
    planetsNumDockingSpots = np.zeros(tileWidth * tileHeight)
    planetsCurrentProduction = np.zeros(tileWidth * tileHeight)
    planetsRemainingResources = np.zeros(tileWidth * tileHeight)
    planetsOwner = np.zeros(tileWidth * tileHeight)
    planetsHealth = np.zeros(tileWidth * tileHeight)

    planets = map.all_planets()
    for planet in planets:
        tileIndex = mapToArrayIndex(planet.x, planet.y)

        planetsRadius[tileIndex] = planet.radius
        planetsNumDockingSpots[tileIndex] = planet.num_docking_spots
        planetsCurrentProduction[tileIndex] = planet.current_production
        planetsRemainingResources[tileIndex] = planet.remaining_resources
        if planet.owner != None:
            planetsOwner[tileIndex] = planet.owner
        planetsHealth[tileIndex] = planet.health

        # planetsDockedShipPlayer1[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer2[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer3[tileIndex] = [None] * tileWidth * tileHeight
        # planetsDockedShipPlayer4[tileIndex] = [None] * tileWidth * tileHeight


    return planetsRadius, planetsNumDockingSpots, planetsCurrentProduction,planetsRemainingResources,planetsOwner,planetsHealth

def discretizedShips(map):
    # shipsPlayer1Present = [None] * tileWidth * tileHeight
    shipsPlayerHealth = [None] * tileWidth * tileHeight
    shipsPlayerDockingStatus = [None] * tileWidth * tileHeight

    for x in range(0, 3):
        shipsPlayerHealth[x] = np.zeros(tileWidth * tileHeight)
        shipsPlayerDockingStatus[x] = np.zeros(tileWidth * tileHeight)
    
    for player in map.all_players():
        for ship in player.all_ships():
            index = mapToArrayIndex(ship.x, ship.y)
            # shipsPlayer1Present[index] = 1
            shipsPlayerHealth[player.id][index] = ship.health

            # logging.info(ship.DockingStatus.value)
            # shipsPlayerDockingStatus[player.id][index] = ship.DockingStatus.value

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