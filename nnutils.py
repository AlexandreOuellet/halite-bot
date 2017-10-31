import hlt
import logging

# the world seems to always be a ratio of 24x16
tileWidth = 24
tileHeight = 16

def discretizeTheWorld(map):
    
    discretizedPlanets = [0] * tileWidth * tileHeight
    # discretizedPlanets = [None] * 24 * 16
    # discretizedShipPlayer1 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer2 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer3 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer4 = [0] * tileWidth * tileHeight

    planets = map.all_planets()
    for planet in planets:
        planetIndex = mapToArrayIndex([planet.x, planet.y])
        # discretizedPlanets[planetIndex] = planet.radius

        logging.info(planet)
        logging.info(planet.x)
        logging.info(planet.y)
        logging.info(planet.radius)

    return 0

def mapToArrayIndex(coordinate):
    return coordinate.x * 24 + coordinate.y * 16