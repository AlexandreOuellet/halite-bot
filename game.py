import hlt
import logging
import numpy as np
import nnutils

from enum import Enum

def doAction(map, ship, actionIndex):

    if actionIndex == None:
        return None
    if actionIndex == 0:
        closestPlanet = _getClosestPlanet(map, ship)
        return ship.dock(closestPlanet)
    if actionIndex == 1:
        return ship.undock()
    else:
        index = actionIndex - 2
        angle = int(index / nnutils.angleStep)
        speed = int(index % nnutils.nbSpeedStep)
        return ship.thrust(speed, angle)

def _getClosestPlanet(map, ship):
    closestPlanet = None
    shortestDistance = 9999999
    for planet in map.all_planets():
        distance = ship.calculate_distance_between(planet)
        if distance < shortestDistance:
            closestPlanet = planet
    return closestPlanet