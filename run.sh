

#python download.py
#python select_gamedirs.py gamedirs.yaml
#python load.py

# Alternatively...
# download pitches.sql from http://web.mit.edu/gkettler/pitches.sql.gz
# uncompress it and load with
sqlite3 baseball.sqlite < pitches.sql
python plot_pitch_types.py wakefield.yaml
python plot_pitch_types.py buchholz.yaml
python scatterplot.py beckett_break.yaml
python plot_pitch_locations.py lester_ch.yaml

rst2html readme.rst > readme.html
