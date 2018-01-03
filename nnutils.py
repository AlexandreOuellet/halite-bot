import hlt
import logging
import numpy as np
import string
import math

# the world seems to always be a ratio of 24x16
tileWidth = 320
tileHeight = 240

angleStep = 15 # increments of 15 for angle
nbAngleStep = int(360/angleStep) # How many angle steps we have
speedStep = 2 # increments of 2 for speed
nbSpeedStep = int(8/speedStep) # 1, 3, 5, 7

def GetReward(map1, map2):
    r2 = _getReward(map2)
    r1 = _getReward(map1)
    logging.debug("r1 %s",  r1)
    logging.debug("r2 %s",  r2)
    finalReward = r2 - r1
    logging.debug("finalReward %s",  finalReward)

    return finalReward

def _getReward(map):
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

    nbShips = np.sum(totalShips)
    totalShipReward = (totalShips[myId] - (nbShips - totalShips[myId])) / nbShips

    nbShipHealth = np.sum(totalShipsHealth)
    shipHealthReward = (totalShipsHealth[myId] - (nbShipHealth - totalShipsHealth[myId])) / nbShipHealth

    productionSpeedReward = np.sum(productionSpeedPerPlayer)
    if productionSpeedReward != 0:
        productionSpeedReward = (productionSpeedPerPlayer[myId] - (productionSpeedReward - productionSpeedPerPlayer[myId]) ) / productionSpeedReward


    logging.debug("totalShipReward %s",  totalShipReward)
    logging.debug("shipHealthReward %s",  shipHealthReward)
    logging.debug("productionSpeedReward %s",  productionSpeedReward)

    totalReward = (totalShipReward + shipHealthReward + productionSpeedReward) / 3.0

    return totalReward

    # average = np.average((totalShipReward, shipHealthReward, productionSpeedReward))
    # return average

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
    planetsNumDockingSpots = np.ndarray(shape=(tileWidth, tileHeight))
    planetsCurrentProduction = np.ndarray(shape=(tileWidth, tileHeight))
    planetsRemainingResources = np.ndarray(shape=(tileWidth, tileHeight))
    planetsOwner = np.ndarray(shape=(tileWidth, tileHeight))
    planetsHealth = np.ndarray(shape=(tileWidth, tileHeight))

    planetsNumDockingSpots.fill(0)
    planetsCurrentProduction.fill(0)
    planetsRemainingResources.fill(0)
    planetsOwner.fill(0)
    planetsHealth.fill(0)

    planets = map.all_planets()
    for planet in planets:
        # tileIndex = mapToArrayIndex(planet.x, planet.y)
        planetsNumDockingSpots = drawPlanet([planet.x, planet.y], planet.radius, planetsNumDockingSpots, planet.num_docking_spots)
        planetsCurrentProduction = drawPlanet([planet.x, planet.y], planet.radius, planetsCurrentProduction, planet.current_production)
        planetsRemainingResources = drawPlanet([planet.x, planet.y], planet.radius, planetsRemainingResources, planet.remaining_resources)
        if planet.owner != None:
            planetsOwner = drawPlanet([planet.x, planet.y], planet.radius, planetsOwner, planet.owner.id)
        # planetsHealth[int(planet.x)][int(planet.y)] = planet.health
        planetsHealth = drawPlanet([planet.x, planet.y], planet.radius, planetsHealth, planet.health)

    return planetsNumDockingSpots, planetsCurrentProduction, planetsRemainingResources, planetsOwner, planetsHealth

def drawPlanet(planetCenter, radius, toModify, value):
    # draw the circle
    for angle in range(0, 360, 5):
        x = radius * math.sin(math.radians(angle)) + planetCenter[0]
        y = radius * math.cos(math.radians(angle)) + planetCenter[1]
        toModify[int(round(x))][int(round(y))] = value
    return toModify

def discretizedShips(map):
    # shipsPlayer1Present = [None] * tileWidth * tileHeight
    shipsPlayerHealth = np.ndarray(shape=(4, tileWidth, tileHeight))
    shipsPlayerDockingStatus = np.ndarray(shape=(4, tileWidth, tileHeight))

    shipsPlayerHealth.fill(0)
    shipsPlayerDockingStatus.fill(0)

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

def getShipState(ship):
    return np.array([ship.x, ship.y, ship.health, int(ship.docking_status.value)])

def parseCommandToActionIndex(command):
    if command == None:
        return None
    commands = command.split(" ")
    if commands[0] == 'd':
        return 0
    if commands[0] == 'u':
        return 1
    if commands[0] == 't':
        speed = int(commands[2])
        angle = int(commands[3])

        speedIndex = int(speed/speedStep)
        angleIndex = int(angle/angleStep)
        
        return int((angleIndex * nbSpeedStep) + speedIndex + 2)

def doActionIndex(map, ship, actionIndex):
    if actionIndex == None:
        return None
    if actionIndex == 0:
        for planet in map.all_planets():
            if ship.can_dock(planet):
                logging.debug("Docking: %s, %s", ship, planet)
                return ship.dock(planet)

        logging.debug("Docking but nothing found: %s", ship)
        return None

    if actionIndex == 1:
        logging.debug("Undocking: %s", ship)
        return ship.undock()
    if actionIndex == 2: # Do Nothing
        logging.debug("Nothing to do: %s", ship)
        return None
    else:
        index = actionIndex - 2
        angle = int(index/nbSpeedStep) * angleStep
        speed = int(index % nbSpeedStep) + 1

        logging.debug("Thrusting: ship:%s, speed:%d, angle:%d", ship, speed, angle)
        return ship.thrust(speed, angle)