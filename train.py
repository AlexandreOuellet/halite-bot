import generate_weights as gw
import compare_bots
import sys

CURRENT_VERSION = 59


class RedirectStdStreams(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr

    def __enter__(self):
        self.old_stdout, self.old_stderr = sys.stdout, sys.stderr
        self.old_stdout.flush(); self.old_stderr.flush()
        sys.stdout, sys.stderr = self._stdout, self._stderr

    def __exit__(self, exc_type, exc_value, traceback):
        self._stdout.flush(); self._stderr.flush()
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

# devnull = open(os.devnull, 'w')

# with RedirectStdStreams(stdout=devnull, stderr=devnull):
key0 = "#0,"
key1 = "#1,"
if __name__ == "__main__":
    # version = int(sys.argv[1])
    # randomize_weight(version)
    halite_binary = "./halite.exe"
    best_version = CURRENT_VERSION
    contender = best_version + 1
    while True:
        gw.randomize_weight(best_version)
        run_commands = ["python MyBot.py {}".format(best_version), "python MyBot.py {}".format(contender)]
        # with RedirectStdStreams(stdout=devnull):
        results = compare_bots.play_games(halite_binary,
                                160, 240,
                                run_commands, 7)
        if key1 not in results:
            continue
            
        elif key0 not in results or results["#1,"] > results["#0,"]:
            best_version = contender
            print("NEW BEST VERSION! : ", best_version)

        contender = best_version + 1        
        
