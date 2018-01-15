del *.log /Q
del *.hlt /Q

FOR /L %%A IN (1,1,250) DO (
  halite.exe -d "240 160" "python MyBot.py G1" "python MyBot.py"
  REM ping localhost -n 1
  REM python train.py
)