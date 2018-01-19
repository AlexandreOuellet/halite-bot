del *.log /Q
del *.hlt /Q

REM FOR /L %%A IN (1,1,100) DO (
REM   halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
REM   REM ping localhost -n 1
REM   REM python train.py
REM )

REM python train.py

FOR /L %%A IN (1,1,1000) DO (
  halite.exe -d "240 160" "python MyBot.py G2 False" "python MyBot.py G2"
  REM ping localhost -n 1
  python train.py
)