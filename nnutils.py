from hlt import entity as ntt
import hlt
import logging
import numpy as np
import string
import math
import random
from enum import Enum
from operator import itemgetter
import pandas as pd

class ObservationIndexes(Enum):
    closestFriendlyPlanets = 0
    closestEmptyPlanets = 1
    closestEnemyPlanets = 2

    closestFriendlyShips = 3
    closestEnemyShips = 4

# [nbTurn, myState, closestFriendlyPlanetx5, closestEmptyPlanetx5, closestEnemyPlanetsx5, closestFriendlyShip x 5, closestEnemyShipx5]


null_ship_state = [0, 0, 0, 0, 0, 0, 0]
null_planet_state = [0, 0, 0, 0, 0, 0, 0]
input_size = 1 + len(null_ship_state) + len(null_planet_state) * 5 * 3 + len(null_ship_state) * 5 * 2 + 6 + 1
output_size = 15 # dock/undock/nothing

def getReward(map1, map2):
    r2 = _getReward(map2)
    r1 = _getReward(map1)
    logging.debug("r1 %s",  r1)
    logging.debug("r2 %s",  r2)
    # finalReward = r1
    finalReward = r2 - r1

    logging.debug("finalReward %s",  finalReward)

    return finalReward

def getFriendlyObservation(map):
    myId = map.get_me().id

    productionSpeed = 0
    for planet in map.all_planets():
        if planet.owner == None or planet.owner.id != myId:
            continue
        for dockedShip in planet.all_docked_ships():

            productionSpeed += 1

    nbShips = len(map.get_me().all_ships())
    health = 0
    for ship in map.get_me().all_ships():
        health += (ship.health/255)

    return productionSpeed, nbShips, health 


def getEnemyObservation(map):
    myId = map.get_me().id

    productionSpeed = 0
    for planet in map.all_planets():
        if planet.owner == None or planet.owner.id == myId:
            continue
        for dockedShip in planet.all_docked_ships():

            productionSpeed += 1

    nbShips = len(map.get_me().all_ships())
    health = 0

    for player in map.all_players():
        if player.id == myId:
            continue
        for ship in map.get_me().all_ships():
            health += (ship.health/255)
            nbShips += 1

    return productionSpeed, nbShips, health

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
    # totalShipReward = (totalShips[myId] - (nbShips - totalShips[myId])) / nbShips
    totalShipReward = totalShips[myId] - (nbShips - totalShips[myId])
    # totalShipReward = totalShips[myId]

    nbShipHealth = np.sum(totalShipsHealth)
    shipHealthReward = totalShipsHealth[myId]/255 - ((nbShipHealth - totalShipsHealth[myId])/255)
    # shipHealthReward = totalShipsHealth[myId] / (255)

    productionSpeedReward = np.sum(productionSpeedPerPlayer)
    if productionSpeedReward != 0:
        productionSpeedReward = productionSpeedPerPlayer[myId] - (productionSpeedReward - productionSpeedPerPlayer[myId])
        # productionSpeedReward = productionSpeedPerPlayer[myId]

    logging.debug("totalShipReward %s",  totalShipReward)
    logging.debug("shipHealthReward %s",  shipHealthReward)
    logging.debug("productionSpeedReward %s",  productionSpeedReward)

    totalReward = totalShipReward + shipHealthReward + productionSpeedReward

    return totalReward

def observe(map, ship):
    myId = map.get_me().id
    allEntity = map.nearby_entities_by_distance(ship)
    keysByDistance = sorted(allEntity.keys(), reverse=False)

    planets = []
    for k in keysByDistance:
        for entity in [entity for entity in allEntity[k] if type(entity) is ntt.Planet]:
            planets.append(entity)

    neutralPlanets = []
    friendlyPlanets = []
    enemyPlanets = []
    for entity in planets:
        if entity.owner == None:
            neutralPlanets.append(entity)
        elif entity.owner.id == myId:
            friendlyPlanets.append(entity)
        else:
            enemyPlanets.append(entity)

    ships = []
    for k in keysByDistance:
        for entity in [entity for entity in allEntity[k] if type(entity) is ntt.Ship]:
            ships.append(entity)

    ships = np.array(ships)
    ships = ships.flatten()

    friendlyShips = [entity for entity in ships if entity.owner.id == myId]
    enemyShips = [entity for entity in ships if entity.owner.id != myId]

    return [friendlyPlanets, neutralPlanets, enemyPlanets, friendlyShips, enemyShips]

def createStateFromObservations(nbTurn, myShip, observations,
                currentProduction, nbShips, health,
                enemyProduction, nbEnemyShips, enemyHealth):
    # [nbTurn, myState, closestFriendlyPlanetx5, closestEmptyPlanetx5, closestEnemyPlanetsx5, closestFriendlyShip x 5, closestEnemyShipx5]
    
    turnState = [].append(nbTurn)
    myState = _getShipState(myShip, myShip)

    friendlyPlanetStates = _fetchClosestPlanetStates(myShip, observations[ObservationIndexes.closestFriendlyPlanets.value], 5)
    neutralPlanetStates = _fetchClosestPlanetStates(myShip, observations[ObservationIndexes.closestEmptyPlanets.value], 5)
    enemyPlanetStates = _fetchClosestPlanetStates(myShip, observations[ObservationIndexes.closestEnemyPlanets.value], 5)

    friendlyShipStates = _fetchClosestShipStates(myShip, observations[ObservationIndexes.closestFriendlyShips.value], 5)
    enemyShipStates = _fetchClosestShipStates(myShip, observations[ObservationIndexes.closestEnemyShips.value], 5)

    allStates = []
    allStates.append(nbTurn)
    for feature in myState:
        allStates.append(feature)
    for planet in friendlyPlanetStates:
        for feature in planet:
            allStates.append(feature)
    for planet in neutralPlanetStates:
        for feature in planet:
            allStates.append(feature)
    for planet in enemyPlanetStates:
        for feature in planet:
            allStates.append(feature)
    for ship in friendlyShipStates:
        for feature in ship:
            allStates.append(feature)
    for ship in enemyShipStates:
        for feature in ship:
            allStates.append(feature)


    allStates.append(currentProduction)
    allStates.append(nbShips)
    allStates.append(health)
    allStates.append(enemyProduction)
    allStates.append(nbEnemyShips)
    allStates.append(enemyHealth)

    allStates.append(random.uniform(0, 1))

    npAllStates = np.array(allStates)
    
    return npAllStates

def _fetchClosestPlanetStates(myShip, planets, nb_planet_to_fetch):
    planet_states = []
    for planet in planets[:min([len(planets), nb_planet_to_fetch])]:
        planetState = _getPlanetState(myShip,planet)
        planet_states.append(planetState)

    while len(planet_states) < nb_planet_to_fetch:
        planet_states.append(null_planet_state)

    return planet_states

def _fetchClosestShipStates(myShip, ships, nb_ship_to_fetch):
    ship_states = []
    for ship in ships[:min([len(ships), 5])]:
        ship_state = _getShipState(myShip, ship)
        ship_states.append(ship_state)

    while len(ship_states) < 5:
        ship_states.append(null_ship_state)

    return ship_states

def _getPlanetState(myShip, planet):
    myId = myShip.owner
    state = np.array([])
    state = np.append(state, myShip.calculate_distance_between(planet))

    state = np.append(state, planet.health)
    state = np.append(state, planet.num_docking_spots)
    state = np.append(state, planet.current_production)

    # isEmpty
    # isEnemy
    # isFriendly
    if planet.owner == None:
        state = np.append(state, 1)
        state = np.append(state, 0)
        state = np.append(state, 0)
    else:
        
        state = np.append(state, 0)

        if planet.owner.id != myId:
            state = np.append(state, 1)
        else:
            state = np.append(state, 0)

        if planet.owner.id == myId:
            state = np.append(state, 1)
        else:
            state = np.append(state, 0)

    assert len(state) == len(null_planet_state)

    return state

def _getShipState(myShip, ship):
    state = np.array([])

    if myShip == ship:
        state = np.append(state, 0)
    else:
        state = np.append(state, myShip.calculate_distance_between(ship))

    state = np.append(state, ship.health)

    if ship.docking_status == None:
        state = np.append(state, 1)
    else:
        state = np.append(state, 0)

    if ship.docking_status == ntt.Ship.DockingStatus.UNDOCKED:
        state = np.append(state, 1)
    else:
        state = np.append(state, 0)

    if ship.docking_status == ntt.Ship.DockingStatus.DOCKING:
        state = np.append(state, 1)
    else:
        state = np.append(state, 0)

    if ship.docking_status == ntt.Ship.DockingStatus.DOCKED:
        state = np.append(state, 1)
    else:
        state = np.append(state, 0)

    if ship.docking_status == ntt.Ship.DockingStatus.UNDOCKING:
        state = np.append(state, 1)
    else:
        state = np.append(state, 0)

    assert len(state) == len(null_ship_state)
    return state

def getCommand(game_map, myShip, action_prediction, observations):
    # observation is what is returned from the observe() method:
    #  [nbTurn, myState, closestFriendlyPlanetx5, closestEmptyPlanetx5, closestEnemyPlanetsx5, closestFriendlyShip x 5, closestEnemyShipx5]

    # actions are :
    # colonize 1st closest friendly planet
    # colonize 2nd closest friendly planet
    # colonize ...5th closest friendly planet
    # colonize 1st closest neutral planet
    # colonize 2nd closest neutral planet
    # colonize ...5th closest neutral planet
    # move towards 1st closest enemy ship
    # move towards 2nd closest enemy ship
    # move towards ...5th closest enemy ship

    action = np.argmax(action_prediction)
    # if action == 0:
    #     logging.debug("Colonizing 1st closest friendly planet")
    # if action == 1:
    #     logging.debug("Colonizing 2nd closest friendly planet")
    # if action == 2:
    #     logging.debug("Colonizing 3rd closest friendly planet")
    # if action == 3:
    #     logging.debug("Colonizing 4th closest friendly planet")
    # if action == 4:
    #     logging.debug("Colonizing 5th closest friendly planet")
    # if action == 5:
    #     logging.debug("Colonizing 1st closest empty planet")
    # if action == 6:
    #     logging.debug("Colonizing 2nd closest empty planet")
    # if action == 7:
    #     logging.debug("Colonizing 3rd closest empty planet")
    # if action == 8:
    #     logging.debug("Colonizing 4th closest empty planet")
    # if action == 9:
    #     logging.debug("Colonizing 5th closest empty planet")
    # if action == 10:
    #     logging.debug("Attacking 1st closest enemy ship")
    # if action == 11:
    #     logging.debug("Attacking 2nd closest enemy ship")
    # if action == 12:
    #     logging.debug("Attacking 3rd closest enemy ship")
    # if action == 13:
    #     logging.debug("Attacking 4th closest enemy ship")
    # if action == 14:
    #     logging.debug("Attacking 5th closest enemy ship")

    if action < 10: # colonize 1st closest friendly planet

        if action < 5:
            planets = observations[ObservationIndexes.closestFriendlyPlanets.value]
        if action >= 5:
            planets = observations[ObservationIndexes.closestEmptyPlanets.value]

        # logging.debug("Planets to colonize : %s", planets)

        planetIndex = action % 5
        if len(planets) <= planetIndex:
            return None

        planet = planets[planetIndex]

        if planet != None:
            if myShip.can_dock(planet):
                return myShip.dock(planet)
            
            return myShip.navigate(
                myShip.closest_point_to(planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)
    else:
        otherShips = observations[ObservationIndexes.closestEnemyShips.value]
        # logging.debug("enemyShips : %s", otherShips)
        shipIndex = action - 10
        if len(otherShips) <= shipIndex:
            return None

        otherShip = otherShips[action - 10]
        if otherShip == None:
            return None

        return myShip.navigate(
                otherShip,
                game_map,
                speed=int(hlt.constants.MAX_SPEED/2),
                ignore_ships=True)
    return None

def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def _getCentroid(game_map, friendly: bool):
    myId = game_map.get_me().id

    total_x = 0
    total_y = 0
    nb_ships = 0
    ships = game_map.get_me().all_ships()

    if not friendly:
        for player in game_map.all_players():
            if player.id != myId:
                ships = player.all_ships()

    for ship in ships:
        nb_ships += 1
        total_x += ship.x
        total_y += ship.y
    return ntt.Position(total_x / nb_ships, total_y / nb_ships)

def CreateCommonDataFrame(game_map):
    logging.debug("createCommonDataFrame")

    pdSerie = pd.Series(planetState)

    myId = game_map.get_me().id

    friendly_centroid = _getCentroid(game_map, True)
    enemy_centroid = _getCentroid(game_map, False)

    all_planets = game_map.all_planets()
    for planet in all_planets:

        id = planet.id
        health = planet.health / (planet.radius * 255)
        radius = planet.radius
        num_docking_spots = planet.num_docking_spots
        friendly_ships_docked = 0
        enemy_ships_docked = 0
        distance_to_friendly_centroid = planet.calculate_distance_between(friendly_centroid)
        distance_to_enemy_centroid = planet.calculate_distance_between(enemy_centroid)

        if planet.owner != None:
            if planet.owner.id == myId:
                friendly_ships_docked = ntity.num_docking_spots - (len(planet.all_docked_ships()) / planet.num_docking_spots)
            else:
                enemy_ships_docked = planet.num_docking_spots - (len(planet.all_docked_ships()) / planet.num_docking_spots)

        planetState = []
        planetState.append(id)

        planetState.append(health)
        planetState.append(health ** 2)

        planetState.append(radius)
        planetState.append(radius ** 2)

        planetState.append(num_docking_spots)
        planetState.append(num_docking_spots ** 2)
        
        planetState.append(friendly_ships_docked)
        planetState.append(friendly_ships_docked ** 2)

        planetState.append(enemy_ships_docked)
        planetState.append(enemy_ships_docked ** 2)

        planetState.append(distance_to_friendly_centroid)
        planetState.append(distance_to_friendly_centroid ** 2)

        planetState.append(distance_to_enemy_centroid)
        planetState.append(distance_to_enemy_centroid ** 2)

        pdSerie.append(planetState,)
    
    return pdSerie

