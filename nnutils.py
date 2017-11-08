import hlt
import logging
import numpy as np

# the world seems to always be a ratio of 24x16
tileWidth = 384
tileHeight = 256

def GetReward(map):
    myId = map.get_me().id
    totalShips = [0] * 4
    totalShipsHealth = [0] * 4
    productionSpeedPerPlayer = [0] * 4


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
    return [planetsModel, shipsModel]

def discretizePlanets(map):
    planetsRadius = [0] * tileWidth * tileHeight
    planetsNumDockingSpots = [0] * tileWidth * tileHeight
    planetsCurrentProduction = [0] * tileWidth * tileHeight
    planetsRemainingResources = [0] * tileWidth * tileHeight
    planetsOwner = [0] * tileWidth * tileHeight
    planetsHealth = [0] * tileWidth * tileHeight

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
    shipsPlayerHealth = [None] * 4
    shipsPlayerDockingStatus = [None] * 4

    for x in range(0, 3):
        shipsPlayerHealth[x] = [None] * tileWidth * tileHeight
        shipsPlayerDockingStatus[x] = [None] * tileWidth * tileHeight
    
    for player in map.all_players():
        for ship in player.all_ships():
            index = mapToArrayIndex(ship.x, ship.y)
            # shipsPlayer1Present[index] = 1
            shipsPlayerHealth[player.id][index] = ship.health
            shipsPlayerDockingStatus[player.id][index] = ship.DockingStatus

    shipsPlayerHealth = _swapArrays(map.get_me().id, 0, shipsPlayerHealth)
    shipsPlayerDockingStatus = _swapArrays(map.get_me().id, 0, shipsPlayerDockingStatus)

    return shipsPlayerHealth, shipsPlayerDockingStatus

def _swapArrays(index1, index2, array):
    tmp = array[index1]
    array[index1] = array[index2]
    array[index2] = tmp

    return array


def mapToArrayIndex(x, y):
    return (int)(x + y * tileHeight)