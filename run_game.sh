#!/bin/sh
rm *.log
rm *.hlt
./halite -d "240 160" "python3 Main.py G1" "python3 Main.py G2"