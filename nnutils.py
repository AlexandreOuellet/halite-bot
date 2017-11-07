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
    return planetsModel, shipsModel

def discretizePlanets(map):
    planetsRadius = [None] * tileWidth * tileHeight
    planetsNumDockingSpots = [None] * tileWidth * tileHeight
    planetsCurrentProduction = [None] * tileWidth * tileHeight
    planetsRemainingResources = [None] * tileWidth * tileHeight
    planetsOwner = [None] * tileWidth * tileHeight
    planetsHealth = [None] * tileWidth * tileHeight

    planets = map.all_planets()
    for planet in planets:
        tileIndex = mapToArrayIndex(planet.x, planet.y)
        
        planetsRadius[tileIndex] = planet.radius
        planetsNumDockingSpots[tileIndex] = planet.num_docking_spots
        planetsCurrentProduction[tileIndex] = planet.current_production
        planetsRemainingResources[tileIndex] = planet.remaining_resources
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

def mapToArrayIndex(x, y):
    return (int)(x + y * tileHeight)