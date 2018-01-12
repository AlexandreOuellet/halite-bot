del *.log /Q
del *.hlt /Q

FOR /L %%A IN (1,1,2000000) DO (
  halite.exe -d "240 160" -s 2168 "python MyBot.py G1" "python MyBot.py"
  ping localhost -n 10
  python train.py
)