del *.log /Q
del *.hlt /Q

FOR /L %%A IN (1,1,200) DO (
  halite.exe -d "240 160" "python MyBot.py G1" "python MyBot.py G2"
  ping localhost -n 20
  python train.py
)