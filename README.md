# Using your starter kit

All starter kits should contain a `run_game.sh` and `run_game.bash`, you can use these scripts to quickly run a game of halite. By default, this script runs the basic __Settler__ bot against itself.

## Bot submission guidelines

Before submitting a bot, make sure you adhere to our guidelines, or the upload or compilation of your bot will fail.

1. You should have a `MyBot.{extension for language}` in the root folder of your zip. For Rust, this should be a `cargo.toml`
2. If you are building on top of starter kit provided by us, make sure to include the hlt folder.

## Uploading your bot

* Website: You can use the [play page](https://halite.io/play-programming-challenge) in the Halite website to submit your bot.
* Halite Client: If you a command line experience, you can use the [Halite Client tool](https://halite.io/learn-programming-challenge/halite-cli-and-tools/halite-client-tools) to upload your bot.

## TODO :
1. 2 things that can be done in parallel :
    1.1 Define and program actions for each ship (Dock(planet), Move(target), Attack(target), Undock)
    1.2 Define the input layer of the neural network and the evaluation function of the state
2. Create the LSTM Neural Network
3. Create a game loop that interact with the LSTM Neural Network
4. Figure out learning without supervision
5. Automate the learning process
6. Conquer the world!