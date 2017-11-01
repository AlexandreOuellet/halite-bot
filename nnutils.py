import hlt
import logging

# the world seems to always be a ratio of 24x16
tileWidth = 24
tileHeight = 16

def discretizeTheWorld(map):
    
    planetRadiuses = [None] * tileWidth * tileHeight
    # discretizedPlanets = [None] * 24 * 16
    # discretizedShipPlayer1 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer2 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer3 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer4 = [0] * tileWidth * tileHeight

    planets = map.all_planets()
    for planet in planets:
        planetIndex = mapToArrayIndex([planet.x, planet.y])
         planetRadiuses[planetIndex] = planet.radius
         


        self.id = planet_id
        self.x = x
        self.y = y
        self.radius = radius
        self.num_docking_spots = docking_spots
        self.current_production = current
        self.remaining_resources = remaining
        self.health = hp
        self.owner = owner if bool(int(owned)) else None
        self._docked_ship_ids = docked_ships
        self._docked_ships = {}

        logging.info(planet)
        logging.info(planet.x)
        logging.info(planet.y)
        logging.info(planet.radius)

    return 0

def discretizePlanets(map):
    planetsRadius = [None] * tileWidth * tileHeight
    planetsNumDockingSpots = [None] * tileWidth * tileHeight
    planetsCurrentProduction = [None] * tileWidth * tileHeight
    planetsRemainingResources = [None] * tileWidth * tileHeight
    planetsOwner = [None] * tileWidth * tileHeight
    planetsHealth = [None] * tileWidth * tileHeight
    planetsDockedShipPlayer1 = [None] * tileWidth * tileHeight
    planetsDockedShipPlayer2 = [None] * tileWidth * tileHeight
    planetsDockedShipPlayer3 = [None] * tileWidth * tileHeight
    planetsDockedShipPlayer4 = [None] * tileWidth * tileHeight
    # discretizedPlanets = [None] * 24 * 16
    # discretizedShipPlayer1 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer2 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer3 = [0] * tileWidth * tileHeight
    # discretizedShipPlayer4 = [0] * tileWidth * tileHeight

    planets = map.all_planets()
    for planet in planets:
        tileIndex = mapToArrayIndex([planet.x, planet.y])
        
        planetsRadius[tileIndex] = planet.radius
        planetsNumDockingSpots[tileIndex] = planet.num_docking_spots
        planetsCurrentProduction[tileIndex] = planet.current_production
        planetsRemainingResources[tileIndex] = planet.remaining_resources
        planetsOwner[tileIndex] = planet.owner.id
        planetsHealth[tileIndex] = planet.health
        planetsDockedShipPlayer1[tileIndex] = [None] * tileWidth * tileHeight
        planetsDockedShipPlayer2[tileIndex] = [None] * tileWidth * tileHeight
        planetsDockedShipPlayer3[tileIndex] = [None] * tileWidth * tileHeight
        planetsDockedShipPlayer4[tileIndex] = [None] * tileWidth * tileHeight
         


        self.id = planet_id
        # self.x = x
        # self.y = y
        self.radius = radius
        self.num_docking_spots = docking_spots
        self.current_production = current
        self.remaining_resources = remaining
        self.health = hp
        self.owner = owner if bool(int(owned)) else None
        self._docked_ship_ids = docked_ships
        self._docked_ships = {}

        logging.info(planet)
        logging.info(planet.x)
        logging.info(planet.y)
        logging.info(planet.radius)



def mapToArrayIndex(coordinate):
    return coordinate[0] * 24 + coordinate[1] * 16

if __name__ == '__main__':
    index = mapToArrayIndex([2000, 300])