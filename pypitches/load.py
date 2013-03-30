# Load the XML data into a database
# expects to find a gamedirs.yaml file,
# which was created by select_gamedirs.py

from BeautifulSoup import BeautifulStoneSoup
import os.path
import os
import sys
import pdb
import yaml #use this for hand-written configs
import json #use this for generated files
from sqlalchemy.exc import IntegrityError
from dateutil import parser
import model
from model import GameDir, Player, Game, Pitch, Team, AtBat, Runner


verbose = False

errorlog = open("err", "w")
nonamelog = open("unsaved_attrs.err", "w")

def xml2obj(attrs, baseballclass):
   """Takes a list of attributes (as returned by BeautifulStoneSoup)
   and a class from py

   Apply those attributes to a new instance of that class."""
   obj = baseballclass()
   for name, val in dict(attrs).iteritems():
      if val == '':
         val = None
      if name in dir(baseballclass):
         try:
            obj.__setattr__(name, val)
         except TypeError:
            pdb.set_trace()
         except AttributeError:
            pdb.set_trace()
         except UnicodeEncodeError:
            obj.__setattr__(name, None)
            #print >>errorlog, "Funny character in:\n" , str(attrs)
      else:
         try:
            print >>nonamelog, name, val, str(baseballclass)
         except ValueError:
            print >>nonamelog, name
   return obj

def get_start_date(gamedirs):
   """Look at files in all these dirs and return the earliest date."""
   def date_of(gamedir):
      datestring = BeautifulStoneSoup(open(os.path.join(gamedir, "boxscore.xml"))).findAll('boxscore')[0]['date']
      return dateutils.parse(datestring)

@model.SessionManager.withsession
def loadbox(session, gamedirs):
   """Load game and box score data from game.xml, boxscore.xml
   Team names,  etc.
   Takes a list of directories, not just one, in case of suspensions."""

   #most info will be grabbed from the first
   gamefile = os.path.join(gamedirs[0], "game.xml")
   boxscorefile = os.path.join(gamedirs[0], "boxscore.xml")
   gamedata = BeautifulStoneSoup(open(gamefile))
   boxscoredata = BeautifulStoneSoup(open(boxscorefile))
   for teamdata in gamedata.findAll('team'):
      teamobj = xml2obj(teamdata.attrs, Team)
      if not session.query(Team).filter(Team.code == teamobj.code).all():
         session.add(teamobj)
         session.flush()
   gameobj = xml2obj(boxscoredata.findAll('boxscore')[0].attrs + gamedata.findAll('game')[0].attrs, Game)
   gameobj.game_pk = int(gameobj.game_pk)
   gameobj.start_date = get_start_date(gamedirs)
   session.add(gameobj)
   session.flush()
   return gameobj

players = {}
@model.SessionManager.withsession
def loadplayers(session, playersfile, gameobj):
   """Load players.xml"""
   ids = {}
   playersdata  = BeautifulStoneSoup(open(playersfile))
   for team in playersdata.findAll('team'):
      for playerdata in team.findAll('player'):
         if playerdata['id'] in ids:
            print >>errorlog, "ignoring duplicate playerdata: %s from file %s" % (str(playerdata.attrs), playersfile)
            continue
         ids[playerdata['id']] = playerdata
         if playerdata['id'] not in players:
            playerobj  = xml2obj(playerdata.attrs, Player)
            session.add(playerobj)
            players[playerdata['id']] = playerdata
         else:
            pass

class DuplicatePitchError(RuntimeError):
   pass
class InningStructureError(RuntimeError):
   def __init__(self, offending_xml_file, inningdata, description):
      self.offending_xml_file = offending_xml_file
      self.inningdata =  inningdata
      self.description = description
class MissingFileError(RuntimeError):
   def __init__(self, directory, missing_file):
      self.directory = directory
      self.missing_file = missing_file
      self.value = "Looking for %s in %s" % (missing_file, directory)
   def __str__(self):
      return self.value

def check_innings(innings, pitchesfilename):
   """Takes a bunch of inning xml datasets.
   Sanity check. Does each inning have a top?
   Does each inning except possibly the last have a bottom?
   Does each atbat have some pitches?
   Return a list of atbats for the whole game.
   """
   for inningdata in innings:
      if len(inningdata.findAll('top')) != 1: 
         raise InningStructureError(pitchesfilename, inningdata, "missing top of inning")
   for inningdata in innings[:-1]:
      if len(inningdata.findAll('bottom')) != 1: 
         raise InningStructureError(pitchesfilename, inningdata, "missing bottom of inning")
   for inningdata in innings:
      for half in 'top', 'bottom':
         halfdata = inningdata.findAll(half)
         if halfdata:
            for atbatdata in halfdata[0].findAll('atbat'):
               if not atbatdata.findAll('pitch'):
                  #FIXME: an atbat will be skipped if a runner is picked off to end the inning before the first pitch.
                  # Is that desired behavior?
                  # Other cases where this could happen?
                  print >>errorlog, "skipping atbat %s because no pitches (dir %s)" % (atbatdata['num'], pitchesfilename)
               else:
                  atbatdata.attrs.append(('inning',  inningdata['num'])) # I like to refer to inning # in the same structure
                  yield atbatdata


def by_pitchcount(pitchdata1, pitchdata2):
   # Not all pitches have this field. Is id reliable? Or not sorting at all?
   return cmp(pitchdata1['tfs'], pitchdata2['tfs'])

@model.SessionManager.withsession
def loadpitches(session, pitchesfile, gameobj):
   """Load at-bats and individual pitches and runner events
   from inning_all.xml"""

   def makepitchobj(pitchdata, count):
      pitchobj = xml2obj(pitchdata.attrs, Pitch)
      pitchobj.atbatnum = int(atbatdata['num'])
      pitchobj.batter = int(atbatdata['batter'])
      pitchobj.pitcher = int(atbatdata['pitcher'])
      pitchobj.game_pk = gameobj.game_pk
      pitchobj.payoff = False
      call = pitchdata['type']
      pitchobj.balls = count['balls']
      pitchobj.strikes = count['strikes']
      if call == 'B': count['balls'] += 1
      if call == 'S': count['strikes'] += 1
      return pitchobj

   filedata = BeautifulStoneSoup(open(pitchesfile))
   innings = filedata.findAll('inning')
   for atbatdata in check_innings(innings, pitchesfile):
      if verbose: print "\t", atbatdata['des']
      atbatobj = xml2obj(atbatdata.attrs, AtBat)
      atbatobj.game_pk = gameobj.game_pk
      atbatobj.date = parser.parse(atbatdata['start_tfs_zulu']).date().ctime()
      session.add(atbatobj)
      session.flush()
      pitch_datas = atbatdata.findAll('pitch')
      # pitch_datas.sort(by_pitchcount) # Make sure these are in order because...
      count = {'balls': 0, 'strikes': 0}
      for pitchdata in pitch_datas[:-1]:
         pitchobj = makepitchobj(pitchdata, count) # ...balls and strikes are counted as we go and...
         session.add(pitchobj)
         try:
            session.flush()
         except IntegrityError as e:
            print "failed on pitchobj.game_pk = {0} pitchobj.atbatnum = {1} but last atbat added was {2}, {3}".format(pitchobj.game_pk, pitchobj.atbatnum, atbatobj.game_pk, atbatobj.num)
            raise

      pitchdata = pitch_datas[-1] # ... and last one gets special treatment
      pitchobj = makepitchobj(pitchdata, count)
      pitchobj.payoff = True
      session.add(pitchobj)
      # for runnerdata in atbatdata.findAll('runner'):
      #    runnerobj = xml2obj(runnerdata.attrs, Runner)
      #    runnerobj.atbatnum = atbatobj.num
      #    runnerobj.game_pk = gameobj.game_pk
      #    session.add(runnerobj)



@model.SessionManager.withsession
def load_game_data(session, game_pk, gamedirs):
   """Check for files in gamedir and then load game metadata
   (By calling loadbox and loadplayers)
   Then load atbats and pitches.
   """
   gameobj = loadbox(gamedirs)
   print gameobj.date, gameobj.away_team_code, gameobj.home_team_code
   for gamedir in gamedirs:
      loadplayers(os.path.join(gamedir, "players.xml"), gameobj)
   if verbose: print "loaded game metadata: ", gamedir
   load_atbats(gamedirs, gameobj)

def load_atbats(gamedirs, gameobj):
   game_pk = gameobj.game_pk
   for gamedir in gamedirs:
      loadpitches(os.path.join(gamedir, "inning", "inning_all.xml"), gameobj)
   if verbose: print "loaded at-bats and pitches: ", gamedirs
  
def get_keys_and_dirs(gamedirs_file):
   """Takes the name of a json file mapping game primary keys to lists of directories for those games.

   Yields pairs of (key, [list of dirs])
   """
   for key, dirs in json.load(open(gamedirs_file)).iteritems():
      yield key, dirs

@model.SessionManager.withsession
def load(session, statuses=frozenset(['final', 'maybe_partial'])):
   finals = session.query(GameDir).filter(GameDir.status.in_(statuses)).filter(GameDir.loaded == False).all()
   for final in finals:
      print final.path
      load_game_data(final.game_pk, [final.path])
      final.loaded = True

