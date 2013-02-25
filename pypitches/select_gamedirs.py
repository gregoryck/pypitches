# The downloaded data tends to be problematic for several reasons
# Some directories are empty
# Some directories have a game.xml but nothing else, due to rain postponement
# Some games have an inning_all.xml but were still postponed
# Some games could be broken across 2 dates because they were suspended

# This script examines all directories. 
# It writes that list to the db


import os
from os.path import abspath
import sys
from BeautifulSoup import BeautifulStoneSoup
from collections import defaultdict
import pdb
from model import GameDir, Session
import datetime

def classify_dir(callback, gamedir, files):
    """Determine if a game was postponed by looking in its boxscore.xml and, if necessary, in its inning_all.xml

    Intended for use through os.path.walk, so first arg is a callback function. 

    Handling of suspended games is complicated. 
    The game may be restarted from the first inning even if an inning or two was played, 
    but I don't want to throw out that data.
    """
    if 'boxscore.xml' not in files:
        return #don't care about other dirs
    status_ind = BeautifulStoneSoup(open(os.path.join(gamedir, 'boxscore.xml'))).findAll('boxscore')[0]['status_ind']
    game_pk = BeautifulStoneSoup(open(os.path.join(gamedir, 'game.xml'))).findAll('game')[0]['game_pk'] 
    innings = len(BeautifulStoneSoup(open(os.path.join(gamedir, 'inning', 'inning_all.xml'))).findAll('inning'))
    date_str = BeautifulStoneSoup(open(os.path.join(gamedir, 'boxscore.xml'))).findAll('boxscore')[0]['date']
    date = datetime.datetime.strptime(date_str, "%B %d, %Y").date()
    
    if status_ind == 'F':
        callback(gamedir, status='final', pk=game_pk, innings=innings, date=date)
    elif status_ind == 'P' or status_ind == 'PR':
        callback(gamedir, status='postponed', pk=game_pk, innings=innings, date=date)
    else:
        # Can't stop here.  Check that at least one at-bat was actually played
        atbats = len(BeautifulStoneSoup(open(os.path.join(gamedir, 'inning/inning_all.xml'))).findAll('atbat'))
        if atbats == 0:
            #raise MissingAtbatsError(gamedir, "status_ind=%s but no plate appearances took place" % (status_ind,))
            callback(gamedir, status='error', status_long="status_ind=%s but no plate appearances took place" % (status_ind,), 
                     pk=game_pk, innings=innings, atbats=atbats, date=date)
        else:
            callback(gamedir, status='maybe_partial', status_long='status_ind={0}'.format(status_ind), 
                     pk=game_pk, innings=innings, atbats=atbats, date=date)

class GameDirError(RuntimeError):
    def __init__(self, gamedirs, descr):
        self.gamedirs = gamedirs
        self.value  = descr
    def __str__(self):
        return self.value + str(self.gamedirs)
   
class DuplicateGamesError(GameDirError):
    pass
class MissingAtbatsError(GameDirError):
    pass

#def loseinnings(gamedirs):
#   """Look at a set of gamedirs from different dates.
#   Decide if innings from the first should be kept as part of that game,
#   or considered "lost innings".
#   
#   Dropping lost innings for now...
#   Yields only the gamedirs that did count for the final box score.
#   """
#   def is_final(gamedir):
#      final_codes = set(['F', 'FR'])
#      return BeautifulStoneSoup(open(os.path.join(gamedir, 'boxscore.xml'))).findAll('boxscore')[0]['status_ind'] in final_codes
#   def innings_of(gamedir):
#         return set([int(inningdata['num']) for inningdata in 
#                     BeautifulStoneSoup(open(os.path.join(gamedir, 'inning/inning_all.xml'))).findAll('inning')])
#
#   finalgame = [g for g in gamedirs if is_final(g)]
#
#   if len(finalgame) == 1 and len(gamedirs) == 1:
#      yield finalgame[0]
#      return
#
#   # check for nastiness here...
#   elif len(finalgame) > 1:
#      raise DuplicateGamesError(gamedirs, "Only one of these should have status_ind='F'")
#   elif len(finalgame) == 0:
#      if len(gamedirs) > 1:
#         raise DuplicateGamesError(gamedirs, "Multiple dates for one game, none is status_ind='F'")
#      else:
#         only_gamedir = gamedirs.pop()
#         if len(innings_of(only_gamedir)) != 0:
#            # only one dir, it's not final but has innings
#            print >>sys.stderr, "including game even though final score wasn't found: %s" % (only_gamedir,)
#            yield only_gamedir
#            return
#         else:
#            # only one dir, no innings, drop it
#            return # don't yield anything -- empty generator
#
#   #put suspended games back together, if necessary
#   yield finalgame[0]
#   innings_represented = innings_of(finalgame[0])
#   while min(innings_represented) != 1:
#      for gamedir in (g for g in gamedirs if not is_final(g)):
#         these_innings = innings_of(gamedir)
#         if max(these_innings) == min(innings_represented) - 1:
#            innings_represented = innings_represented.union(these_innings)
#            yield gamedir
#
#def good_dirs():
#   """Yield directories that contain useful game info. Print warnings about the rest."""
#   def candidate_dirs():
#      dir_of_game_pk = defaultdict(set)
#      #first pass
#      for year in os.listdir('downloads'):
#         year_dir = os.path.join('downloads', year)
#         for month in os.listdir(year_dir):
#            month_dir = os.path.join(year_dir, month)
#            for day in os.listdir(month_dir):
#               day_dir = os.path.join(month_dir, day)
#               for game in os.listdir(day_dir):
#                  game_dir = os.path.join(day_dir, game)
#                  if not os.path.exists(os.path.join(game_dir, 'game.xml')):
#                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'game.xml')
#                  elif not os.path.exists(os.path.join(game_dir, 'boxscore.xml')):
#                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'boxscore.xml')
#                  elif not os.path.exists(os.path.join(game_dir, 'inning/inning_all.xml')):
#                     print >>sys.stderr, "no " +  os.path.join(game_dir, 'inning/inning_all.xml')
#                  elif postponed(game_dir): 
#                     print >>sys.stderr, "game was postponed: " + game_dir
#                  else:
#                     game_pk = BeautifulStoneSoup(open(os.path.join(game_dir, 'game.xml'))).findAll('game')[0]['game_pk'] 
#                     if game_pk in dir_of_game_pk.keys():
#                        print >>sys.stderr, "duplicate game_pk: " + game_dir
#                        print >>sys.stderr, "\talso seen in ", dir_of_game_pk[game_pk]
#                        dir_of_game_pk[game_pk].add(game_dir)
#                     else:
#                        dir_of_game_pk[game_pk].add(game_dir)
#      return dir_of_game_pk
#
#   dir_of_game_pk = candidate_dirs()
#   #second pass: drop some last ones
#   for game_pk, dirs in dir_of_game_pk.iteritems():
#      dirs = set(loseinnings(dirs))
#      yield game_pk, list(dirs)
#
#
#def game_pk_map():
#   dirs = list(good_dirs())
#   dirs.sort()
#   for game_pk, directories in dirs:
#      yield game_pk, directories
#

def update_or_add_gamedir(path, status, innings=None, pk=None, status_long=None, atbats=None):
    maybe_gamedir = Session.query(GameDir).filter(GameDir.path==path).all()
    if len(maybe_gamedir) == 1:
        gamedir = maybe_gamedir[0]
    elif len(maybe_gamedir) == 0:
        gamedir = GameDir()
        Session.add(gamedir)
    else:
        raise ValueError, "Duplicate gamedir.path in database: {0}".format(path)
    gamedir.path = path
    gamedir.status = status
    gamedir.status_long = status_long
    gamedir.local_copy = True
    gamedir.game_pk = pk
    gamedir.innings = innings
    gamedir.atbats = atbats

def classify_local_dirs_by_filesystem(rootdir):
    os.path.walk(abspath(rootdir), classify_dir, update_or_add_gamedir)
    Session.commit()

def classify_local_dirs_by_database():
    for path, in Session.query(GameDir.path).filter(GameDir.local_copy == True).filter(GameDir.path != None):
        classify_dir(update_or_add_gamedir, path, os.listdir(path))
    Session.commit()


if __name__ == "__main__":
    db, user, password, start_dir = sys.argv[1:5]
    #classify_local_dirs_by_filesystem(start_dir)
    classify_local_dirs_by_database()






