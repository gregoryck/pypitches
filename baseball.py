from sqlalchemy import *

from sqlalchemy.orm import *
import yaml
import os
import pdb
import sqlite3


def start_sqlite(sqlite_file, tables_file):
   if not os.path.exists(sqlite_file):
      # Create sqlite file and create tables 
      conn = sqlite3.connect(sqlite_file)
      c = conn.cursor()
      c.executescript(''.join(list(open(tables_file))))
      conn.close()
   engine = create_engine("sqlite:///%s" % (sqlite_file), echo=False)
   metadata = MetaData(engine)
   Session = sessionmaker(bind=engine)
   return Session, metadata

settings = None #To be set by init()
session = None
mappers_mapped = False
def init(settingsfilename='baseball.yaml'):
   """Fire up the database and initialize some
   global settings (yeah...)
   Returns a dictionary of settings and an SQLAlchemy Session()
   """

   global settings # Hmm...
   global session  # What's the nicest way to set something module-wide?
   global mappers_mapped
   settings = yaml.load(file(settingsfilename))
   if settings['engine'] == 'postgres':
      user = settings['user']
      password = settings['password']
      db = settings['postgres_db']
      engine = create_engine("postgres://%s:%s@localhost/%s" % (user, password, db), echo=False)
      metadata = MetaData(engine)
      Session = sessionmaker(bind=engine)
   elif settings['engine'] == 'sqlite':
      Session, metadata =start_sqlite(settings['sqlite_file'], settings['tables_file'])
   else:
      raise ValueError, "What is settings['engine']:", settings['engine']

   if not mappers_mapped: #don't re-run this part
      mappers_mapped = True
      playeringame_table = Table('playeringame', metadata, autoload=True)
      atbat_table = Table('atbat', metadata, autoload=True)
      game_table = Table('game', metadata, autoload=True)
      pitch_table = Table('pitch', metadata, autoload=True)
      player_table = Table('player', metadata, autoload=True)
      #umpire_table = Table('umpire', metadata, autoload=True)
      runner_table = Table('runner', metadata, autoload=True)
      team_table = Table('team', metadata, autoload=True)
      stadium_table = Table('stadium', metadata, autoload=True)
      mapper(Player, player_table)
      #mapper(Umpire, umpire_table)
      mapper(Game, game_table)
      mapper(Team, team_table)
      mapper(Stadium, stadium_table)
      mapper(PlayerInGame, playeringame_table, 
            properties={'player': relation(Player, backref="ingames"),
                        'game'  : relation(Game, backref="players"),})
      mapper(AtBat, atbat_table,
            properties={'game':    relation(Game, backref='atbats'),
                        'pitchedby': relation(Player, backref='atbats_pitching',
                                            primaryjoin=(atbat_table.c.pitcher==player_table.c.id)),
                        'wasbatter' : relation(Player, backref='atbats_hitting',
                                            primaryjoin=(atbat_table.c.batter==player_table.c.id)),
                        })
      mapper(Runner, runner_table,
            properties={'game': relation(Game),
                        'player': relation(Player, backref='baserunning'),
                        'atbat': relation(AtBat, backref='runners', 
                           primaryjoin=and_(atbat_table.c.num == runner_table.c.atbatnum ,
                              atbat_table.c.game_pk == runner_table.c.game_pk),
                              )})

      mapper(Pitch, pitch_table,
            properties={'pitchedby': relation(Player, backref='pitches',
                                            primaryjoin=(pitch_table.c.pitcher==player_table.c.id)),
                        'game'   : relation(Game,   uselist=False, backref='pitches', primaryjoin=(pitch_table.c.game_pk == game_table.c.game_pk), foreign_keys=[game_table.c.game_pk]),
                        'atbat'  : relation(AtBat,  backref='pitches',
                           primaryjoin=and_(atbat_table.c.num == pitch_table.c.atbatnum ,
                                        atbat_table.c.game_pk == pitch_table.c.game_pk),
                           ),})
   session = Session()
   return settings, session 

class Pitch(object):
   def __init__(self):
      pass
class Game(object):
   def __init__(self):
      pass
class Team(object):
   def __init__(self):
      pass
class Stadium(object):
   def __init__(self):
      pass
class Player(object):
   def __init__(self):
      pass
class Umpire(object):
   def __init__(self):
      pass
class PlayerInGame(object):
   def __init__(self):
      pass
class AtBat(object):
   def __init__(self):
      pass
class Runner(object):
   def __init__(self):
      pass

