del *.log /Q
del *.hlt /Q

halite.exe -d "240 160" "python MyBot.py 1 True" "python MyBot.py 2 True"

REM REM FOR /L %%A IN (1,1,100) DO (
REM REM   halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
REM REM   REM ping localhost -n 1
REM REM   REM python train.py
REM REM )

REM REM python train.py

REM FOR /L %%A IN (1,1,20) DO (
REM   halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
REM   REM ping localhost -n 1
REM   python train.py
REM )

REM FOR /L %%A IN (1,1,20000) DO (
REM   halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
REM   REM ping localhost -n 1
REM   python train.py True
REM )