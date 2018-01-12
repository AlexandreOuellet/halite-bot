#!/bin/sh
rm *.log
rm *.hlt
./halite -d "240 160" -r -t "python3 MyBot.py G1" "python3 MyBot.py"