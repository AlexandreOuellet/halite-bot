import compare_bots
import os
import sys
import pickle
import random
import numpy as np

LEARNING_RATE_1 = 0.1
LEARNING_RATE_2 = 0.25
word_file = "./words.txt"
WORDS = open(word_file).read().splitlines()

def randomize_weight(version, learning_rate):
    dir = './v/{}/'.format(version)
    if os.path.isfile(dir+'planetWeights'):
        planetWeights = pickle.load(open(dir+'planetWeights', 'rb'))
    else:
        planetWeights = [1, 1, 1, 1, 1, 1, 1, 1, 1]

    for i in range(0, len(planetWeights)):
        rand = ((random.random()-0.5)  * 2) * learning_rate
        planetWeights[i] += rand

    version = random.choice(WORDS)
    dir = './v/{}/'.format(version)

    if os.path.exists(dir) == False:
        os.makedirs(dir)
    pickle.dump(planetWeights, open(dir+'planetWeights', 'wb'))

    return version

def isFirstOrSecond(rewards, index):
    currentReward = rewards[index]
    nbBiggerReward = 0
    for reward in rewards:
        if reward > currentReward:
            nbBiggerReward += 1

    return nbBiggerReward <= 1

if __name__ == "__main__":
    dir = './v/'
    if os.path.isfile(dir+'best_versions'):
        best_versions = pickle.load(open(dir+'best_versions', 'rb'))
    else:
        best_versions = [randomize_weight(random.choice(WORDS), LEARNING_RATE_1), randomize_weight(random.choice(WORDS), LEARNING_RATE_2)]

    key0 = "#0,"
    key1 = "#1,"
    key2 = "#2,"
    key3 = "#3,"

    halite_binary = "./halite.exe"
    while True:
        pickle.dump(best_versions, open(dir+'best_versions', 'wb'))

        
        v2 = randomize_weight(best_versions[0], LEARNING_RATE_1)
        v3 = randomize_weight(best_versions[1], LEARNING_RATE_2)
        best_versions.append(v2) 
        best_versions.append(v3)

        run_commands = ["python MyBot.py {}".format(best_versions[0]), "python MyBot.py {}".format(best_versions[1]), "python MyBot.py {}".format(best_versions[2]), "python MyBot.py {}".format(best_versions[3])]
        print("Comparing bot :  1st {} with 2nd {} and 2 random : {} and {}".format(best_versions[0], best_versions[1], best_versions[2], best_versions[3]))
        results = compare_bots.play_games(halite_binary,
                                320, 240,
                                run_commands, 10)
        

        rewards = [0, 0, 0, 0]
        if key0 in results:
            rewards[0] = results[key0]

        if key1 in results:
            rewards[1] = results[key1]

        if key2 in results:
            rewards[2] = results[key2]

        if key3 in results:
            rewards[3] = results[key3]
        
        first_index = np.argmax(rewards)
        second_index = 0
        for i in range(0, len(rewards)):
            if i == first_index:
                continue
            if isFirstOrSecond(rewards, i):
                second_index = i
        
        if first_index != 0:
            print("OH SNAP!  The best version {} just got replaced by {}".format(best_versions[0], best_versions[first_index]))
        
        if second_index != 1:
            print("OH SNAP!  The second best version {} just got replaced by {}".format(best_versions[1], best_versions[second_index]))

        best_version = best_versions[first_index]
        second_version = best_versions[second_index]

        best_versions = []
        best_versions.append(best_version)
        best_versions.append(second_version)