# 'Quick' script to plot a pitcher's movement for each pitch type
# driven by a yaml settings file

import baseball
from baseball_query import pitches, to_radian
import matplotlib.pyplot as plt
import matplotlib.projections
from matplotlib import lines
import sys
import yaml


if len(sys.argv) != 2:
   print "python plot_pitch_types.py wakefield.yaml"
else:
   with open(sys.argv[1]) as handle:
      plot_settings = yaml.load(handle)

db_settings, session = baseball.init()

name = plot_settings['name']
plots = plot_settings['plots']

# first pass: plot one image for each pitch type
for plot in plots:
   pitchset = pitches(session, name=name, pitch_type = plot['pitch_type'])

   fig = plt.figure()
   ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
   ax.plot(map(to_radian, pitchset['break_angle']),
             pitchset['break_length'], c=plot['color'], marker=plot['marker'], linestyle='None')
   ax.set_rmax(18)
   plt.savefig(plot['filename'], format='png')

# second pass: plot one image including all types, color-coded
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], polar=True)
liness= []
namess= []
for plot in plots:
   pitchset = pitches(session, name=name, pitch_type = plot['pitch_type'])
   ax.plot(map(to_radian, pitchset['break_angle']),
             pitchset['break_length'], c=plot['color'], marker=plot['marker'], linestyle='None')
   liness.append(lines.Line2D([], [], color=plot['color'], marker=plot['marker'],lw=0))
   namess.append(plot['filename'].split('.')[0])

plt.figlegend(liness,namess,'upper left')
ax.set_rmax(18)
plt.savefig(plot_settings['all_file'], dpi=200, format='png')
