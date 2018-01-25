import compare_bots
import os
import sys
import pickle
import random

CURRENT_VERSION = 1

LEARNING_RATE = 1

def randomize_weight(version):
    dir = './v/{}/'.format(version)
    if os.path.isfile(dir+'planetWeights'):
        planetWeights = pickle.load(open(dir+'planetWeights', 'rb'))
    # if os.path.isfile(dir+'shipWeights'):
    #     shipWeights = pickle.load(open(dir+'shipWeights', 'rb'))


    for i in range(0, len(planetWeights)):
        rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
        planetWeights[i] += rand
    # for i in range(0, len(shipWeights)):
    #     rand = ((random.random()-0.5)  * 2) * LEARNING_RATE
    #     shipWeights[i] += rand

    version += 1
    dir = './v/{}/'.format(version)
        
    if os.path.exists(dir) == False:
        os.makedirs(dir)
    pickle.dump(planetWeights, open(dir+'planetWeights', 'wb'))
    # pickle.dump(shipWeights, open(dir+'shipWeights', 'wb'))


key0 = "#0,"
key1 = "#1,"
if __name__ == "__main__":
    # version = int(sys.argv[1])
    # randomize_weight(version)
    halite_binary = "./halite.exe"
    best_version = CURRENT_VERSION
    contender = best_version + 1
    while True:
        randomize_weight(best_version)
        run_commands = ["python MyBot.py {}".format(best_version), "python MyBot.py {}".format(contender)]
        # with RedirectStdStreams(stdout=devnull):
        results = compare_bots.play_games(halite_binary,
                                240, 160,
                                run_commands, 10)
        if key1 not in results:
            continue
            
        elif key0 not in results or results["#1,"] > 6:
            best_version = contender
            print("NEW BEST VERSION! : ", best_version)

        contender = best_version + 1
        
