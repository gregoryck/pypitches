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
from model import GameDir, SessionManager
import datetime

@SessionManager.withsession
def classify_dir(session, callback, gamedir, files):
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

@SessionManager.withsession
def update_or_add_gamedir(session, path, status, innings=None, pk=None, status_long=None, atbats=None, date=None):
    maybe_gamedir = session.query(GameDir).filter(GameDir.path==path).all()
    if len(maybe_gamedir) == 1:
        gamedir = maybe_gamedir[0]
    elif len(maybe_gamedir) == 0:
        gamedir = GameDir()
        session.add(gamedir)
    else:
        raise ValueError, "Duplicate gamedir.path in database: {0}".format(path)
    gamedir.path = path
    gamedir.status = status
    gamedir.status_long = status_long
    gamedir.local_copy = True
    gamedir.game_pk = pk
    gamedir.innings = innings
    gamedir.atbats = atbats
    gamedir.date = date


@SessionManager.withsession
def classify_local_dirs_by_filesystem(session, rootdir):
    os.path.walk(abspath(rootdir), classify_dir, update_or_add_gamedir)
    session.flush()

@SessionManager.withsession
def classify_local_dirs_by_database(session):
    for path, in session.query(GameDir.path).filter(GameDir.local_copy == True).filter(GameDir.path != None):
        classify_dir(update_or_add_gamedir, path, os.listdir(path))
    session.flush()


if __name__ == "__main__":
    db, user, password, start_dir = sys.argv[1:5]
    #classify_local_dirs_by_filesystem(start_dir)
    classify_local_dirs_by_database()






