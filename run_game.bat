del *.log /Q
del *.hlt /Q

REM FOR /L %%A IN (1,1,100) DO (
REM   halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
REM   REM ping localhost -n 1
REM   REM python train.py
REM )

REM python train.py

FOR /L %%A IN (1,1,20) DO (
  halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
  REM ping localhost -n 1
  python train.py
)

FOR /L %%A IN (1,1,20000) DO (
  halite.exe -d "240 160" "python MyBot.py G2" "python MyBot.py G2"
  REM ping localhost -n 1
  python train.py True
)