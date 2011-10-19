# 'Quick' script to plot a pitcher's movement for each pitch type
# driven by a yaml settings file

import baseball
from baseball_query import pitches, normalized_pitch_height, callcolors
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from collections import defaultdict
import numpy
import sys
import yaml


if len(sys.argv) != 2:
   print "python plot_pitch_locations.py wakefield_loc.yaml"
else:
   with open(sys.argv[1]) as handle:
      plot_settings = yaml.load(handle)

db_settings, session = baseball.init()

name = plot_settings['name']
plots = plot_settings['plots']

# first pass: plot one image for each pitch type
for plot in plots:
   plot = defaultdict(lambda:None, plot) #if it's not mentioned in the yaml file, forget it
   pitchset = pitches(session, name=name, pitch_type = plot['pitch_type'], stand=plot['stand'],
                      payoff=plot['payoff'], des=plot['des'], event=plot['event'])

   fig = plt.figure()
   ax = fig.add_subplot(111)

   for call in ('X', 'S', 'B'):
      subset = pitchset[pitchset['type'] == call]
      norm_pz = normalized_pitch_height(subset)
      plt.plot(subset['px'],
                norm_pz, c=plot_settings['colors'][call], marker=plot_settings['marker'], linestyle='None')

   #draw strike zone
   codes = [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
   vertices = [(-1,1.6), (1,1.6), (1, 3.65), (-1, 3.65), (0,0)]
   vertices = numpy.array(vertices, float)
   path = Path(vertices, codes)
   pathpatch = PathPatch(path, facecolor='None', edgecolor='black')
   ax.add_patch(pathpatch)

   plt.xlim([-3,3])
   plt.ylim([0,6])
   plt.savefig(plot['filename'], format='png')

