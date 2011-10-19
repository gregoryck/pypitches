import baseball
from baseball_query import pitches, normalized_pitch_height
import matplotlib.pyplot as plt
import numpy
import sys
import yaml


import pdb


if len(sys.argv) != 2:
   print "python plot_pitch_locations.py lester_break.yaml"
else:
   with open(sys.argv[1]) as handle:
      plot_settings = yaml.load(handle)

db_settings, session = baseball.init()

name = plot_settings['name']

results = {}
results['sw_strike'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
                    des="Swinging Strike")
results['foul'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
                    des="Foul")
results['groundout']= pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Groundout", payoff=True)
results['flyout']= pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Flyout", payoff=True)
results['lineout']= pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Lineout", payoff=True)
results['single'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Single", payoff=True)
results['double'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Double", payoff=True)
#results['triple'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
#      event="Triple", payoff=True)
results['homerun'] = pitches(session, name=name, pitch_type = plot_settings['pitch_type'],
      event="Home Run", payoff=True)
legend_lines = []
keys = []
for key, pitchset in results.iteritems():
   #plt.scatter(norm_pz, indices)
   legend_lines.append( plt.scatter(pitchset['break_length'], pitchset['start_speed'], marker=plot_settings['outcomes'][key]['marker'], color=plot_settings['outcomes'][key]['color']))
   keys.append( key)

plt.legend(legend_lines, keys, 'lower left')
plt.xlabel('break length')
plt.ylabel('pitch starting speed')

plt.savefig(plot_settings['filename'], format='png')

