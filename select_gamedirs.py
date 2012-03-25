# The downloaded data tends to be problematic for several reasons
# Some directories are empty
# Some directories have a game.xml but nothing else, due to rain postponement
# Some games have an inning_all.xml but were still postponed
# Some games could be broken across 2 dates because they were suspended

# This script generates a list of "good" directories. 
# load.py will depend on that list

# usage 
# (to create gamedirs.yaml)
# python select_gamedirs.py gamedirs.yaml

import os
import sys
from BeautifulSoup import BeautifulStoneSoup
from collections import defaultdict
import pdb
import json

def postponed(gamedir):
   """Determine if a game was postponed by looking in its boxscore.xml and, if necessary, in its inning_all.xml
   
   Handling of suspended games is complicated. 
   The game may be restarted from the first inning even if an inning or two was played, 
   but I don't want to throw out that data.
   """
   status_ind = BeautifulStoneSoup(open(os.path.join(gamedir, 'boxscore.xml'))).findAll('boxscore')[0]['status_ind']
   if status_ind == 'F':
      return False
   elif status_ind == 'P' or status_ind == 'PR':
      return True
   else:
      # Can't stop here.  Check that at least one at-bat was actually played
      atbats = BeautifulStoneSoup(open(os.path.join(gamedir, 'inning/inning_all.xml'))).findAll('atbat')
      if len(atbats) == 0:
         print >>sys.stderr, "Warning: status_ind=%s but no plate appearances took place for game %s" % (status_ind, gamedir)
         return True

class DuplicateGamesError(RuntimeError):
   def __init__(self, gamedirs, descr):
      self.gamedirs = gamedirs
      self.value  = descr
   def __str__(self):
      return self.value + str(self.gamedirs)
   


def loseinnings(gamedirs):
   """Look at a set of gamedirs from different dates.
   Decide if innings from the first should be kept as part of that game,
   or considered "lost innings".
   
   Dropping lost innings for now...
   Yields only the gamedirs that did count for the final box score.
   """
   def is_final(gamedir):
      final_codes = set(['F', 'FR'])
      return BeautifulStoneSoup(open(os.path.join(gamedir, 'boxscore.xml'))).findAll('boxscore')[0]['status_ind'] in final_codes
   def innings_of(gamedir):
         return set([int(inningdata['num']) for inningdata in 
                     BeautifulStoneSoup(open(os.path.join(gamedir, 'inning/inning_all.xml'))).findAll('inning')])

   finalgame = [g for g in gamedirs if is_final(g)]

   if len(finalgame) == 1 and len(gamedirs) == 1:
      yield finalgame[0]
      return

   # check for nastiness here...
   elif len(finalgame) > 1:
      raise DuplicateGamesError(gamedirs, "Only one of these should have status_ind='F'")
   elif len(finalgame) == 0:
      if len(gamedirs) > 1:
         raise DuplicateGamesError(gamedirs, "Multiple dates for one game, none is status_ind='F'")
      else:
         only_gamedir = gamedirs.pop()
         if len(innings_of(only_gamedir)) != 0:
            # only one dir, it's not final but has innings
            print >>sys.stderr, "including game even though final score wasn't found: %s" % (only_gamedir,)
            yield only_gamedir
            return
         else:
            # only one dir, no innings, drop it
            return # don't yield anything -- empty generator

   #put suspended games back together, if necessary
   yield finalgame[0]
   innings_represented = innings_of(finalgame[0])
   while min(innings_represented) != 1:
      for gamedir in (g for g in gamedirs if not is_final(g)):
         these_innings = innings_of(gamedir)
         if max(these_innings) == min(innings_represented) - 1:
            innings_represented = innings_represented.union(these_innings)
            yield gamedir

def good_dirs():
   """Yield directories that contain useful game info. Print warnings about the rest."""
   def candidate_dirs():
      dir_of_game_pk = defaultdict(set)
      #first pass
      for year in os.listdir('downloads'):
         year_dir = os.path.join('downloads', year)
         for month in os.listdir(year_dir):
            month_dir = os.path.join(year_dir, month)
            for day in os.listdir(month_dir):
               day_dir = os.path.join(month_dir, day)
               for game in os.listdir(day_dir):
                  game_dir = os.path.join(day_dir, game)
                  if not os.path.exists(os.path.join(game_dir, 'game.xml')):
                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'game.xml')
                  elif not os.path.exists(os.path.join(game_dir, 'boxscore.xml')):
                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'boxscore.xml')
                  elif not os.path.exists(os.path.join(game_dir, 'inning/inning_all.xml')):
                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'inning/inning_all.xml')
                  elif postponed(game_dir): 
                     print >>sys.stderr, "game was postponed: " + game_dir
                  else:
                     game_pk = BeautifulStoneSoup(open(os.path.join(game_dir, 'game.xml'))).findAll('game')[0]['game_pk'] 
                     if game_pk in dir_of_game_pk.keys():
                        print >>sys.stderr, "duplicate game_pk: " + game_dir
                        print >>sys.stderr, "\talso seen in ", dir_of_game_pk[game_pk]
                        dir_of_game_pk[game_pk].add(game_dir)
                     else:
                        dir_of_game_pk[game_pk].add(game_dir)
      return dir_of_game_pk

   dir_of_game_pk = candidate_dirs()
   #second pass: drop some last ones
   for game_pk, dirs in dir_of_game_pk.iteritems():
      dirs = set(loseinnings(dirs))
      yield game_pk, list(dirs)


def game_pk_map():
   dirs = list(good_dirs())
   dirs.sort()
   for game_pk, directories in dirs:
      yield game_pk, directories


if __name__ == "__main__":
   outfilename = sys.argv[1]
   json.dump(dict(game_pk_map()), open(outfilename, "w"))





