import hlt
import logging
import numpy as np

from enum import Enum

class Action(Enum):
    NOTHING = 0
    DOCK = 1
    UNDOCK = 2
    NORTH = 3
    SOUTH = 4
    EAST = 5
    WEST = 6
    # def getActions(self):
    #     return [DOCK, UNDOCK, NORTH, SOUTH, EAST, WEST]

def doAction(map, ship, actions):
    actionToDo = np.argmax(actions)
    # actionToDo = Action.NOTHING
    # for i in range(0, len(Action)):
    #     if actions[i] == 1:
    #         actionToDo = i
    #         break

    if actionToDo == Action.DOCK: #dock
        closestPlanet = _getClosestPlanet(map, ship)
        return ship.dock(closestPlanet)
    if actionToDo == Action.UNDOCK:
        return ship.undock()
    if actionToDo == Action.NORTH:
        return ship.thrust(0, 7)
    if actionToDo == Action.EAST:
        return ship.thrust(90, 7)
    if actionToDo == Action.SOUTH:
        return ship.thrust(180, 7)
    if actionToDo == Action.WEST:
        return ship.thrust(270, 7)

def _getClosestPlanet(map, ship):
    closestPlanet = None
    shortestDistance = 9999999
    for planet in map.all_planets():
        distance = ship.calculate_distance_between(planet)
        if distance < shortestDistance:
            closestPlanet = planet
    return closestPlanet