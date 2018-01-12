import hlt
import logging

def load():
    return 0

def predict(game_state, ship_state, ship, game_map):
    return predictStarterBot(ship, game_map)

def remember(oldState, old_ship_state, action_taken, reward, game_state, next_ship_state, isTerminal):
    return 0

def saveMemory():
    return 0

def predictStarterBot(ship, game_map):

    if ship.docking_status != ship.DockingStatus.UNDOCKED:
        # Skip this ship
        return None

    # For each planet in the game (only non-destroyed planets are included)
    for planet in game_map.all_planets():
        # If the planet is owned
        if planet.is_owned():
            # Skip this planet
            continue

        # If we can dock, let's (try to) dock. If two ships try to dock at once, neither will be able to.
        if ship.can_dock(planet):
            # We add the command by appending it to the command_queue
            return ship.dock(planet)
        else:
            # If we can't dock, we move towards the closest empty point near this planet (by using closest_point_to)
            # with constant speed. Don't worry about pathfinding for now, as the command will do it for you.
            # We run this navigate command each turn until we arrive to get the latest move.
            # Here we move at half our maximum speed to better control the ships
            # In order to execute faster we also choose to ignore ship collision calculations during navigation.
            # This will mean that you have a higher probability of crashing into ships, but it also means you will
            # make move decisions much quicker. As your skill progresses and your moves turn more optimal you may
            # wish to turn that option off.
            navigate_command = ship.navigate(
                ship.closest_point_to(planet),
                game_map,
                speed=int(hlt.constants.MAX_SPEED/2),
                ignore_ships=True)
            # If the move is possible, add it to the command_queue (if there are too many obstacles on the way
            # or we are trapped (or we reached our destination!), navigate_command will return null;
            # don't fret though, we can run the command again the next turn)
            if navigate_command:
                return navigate_command
        break
    return None