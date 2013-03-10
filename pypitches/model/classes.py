from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy import Float, Boolean, Text, CHAR, Date, func
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class Pitch(Base):
    __tablename__ = "pitch"

    des = Column(String) 
    type = Column(CHAR(1))
    id = Column(Integer, primary_key=True) #INTEGER,
    x = Column(Float) #FLOAT,
    y = Column(Float) #FLOAT,
    sv_id = Column(String) #VARCHAR(128),
    start_speed = Column(Float)
    end_speed  = Column(Float)
    sz_top = Column(Float) 
    sz_bot = Column(Float)
    pfx_x = Column(Float)
    pfx_z = Column(Float)
    px = Column(Float)
    pz = Column(Float)
    x0 = Column(Float)
    y0 = Column(Float)
    z0 = Column(Float)
    vx0 = Column(Float)
    vy0 = Column(Float)
    vz0 = Column(Float)
    ax = Column(Float)
    ay = Column(Float)
    az = Column(Float)
    break_y = Column(Float)
    break_angle = Column(Float)
    break_length = Column(Float)
    pitch_type = Column(String)
    type_confidence = Column(Float)
    spin_dir = Column(Float)
    spin_rate = Column(Float)
    nasty = Column(Integer)
    on_1b = Column(Integer, ForeignKey('player.id'))
    on_2b = Column(Integer, ForeignKey('player.id'))
    on_3b = Column(Integer, ForeignKey('player.id'))
    payoff = Column(Boolean)
    balls = Column(Integer)
    strikes = Column(Integer)
 
    game_pk          = Column(Integer, ForeignKey('game.game_pk'), primary_key=True )
    pitcher          = Column(Integer, ForeignKey('player.id'))
    batter           = Column(Integer, ForeignKey('player.id'))
    atbatnum         = Column(Integer, ForeignKey('atbat.num'))
    pitchedby        = relationship("Player", primaryjoin="Pitch.pitcher==Player.id")
    seenby        = relationship("Player", primaryjoin="Pitch.batter==Player.id")
 

class Game(Base):
    __tablename__ = "game"
    game_pk        = Column(Integer, primary_key=True)
    away_team_code = Column(CHAR(3), ForeignKey('team.code'))
    home_team_code = Column(CHAR(3), ForeignKey('team.code'))
    away_fname     = Column(Text)
    home_fname     = Column(Text)
    away_sname     = Column(Text)
    home_sname     = Column(Text)
    stadium        = Column(Integer, ForeignKey('stadium.id'))
    date           = Column(Date)


class Team(Base):
    __tablename__     = "team"
    id                = Column(Integer)
    code              = Column(CHAR(3), primary_key=True)
    name              = Column(Text)
    name_full         = Column(Text)
    name_brief        = Column(Text)
class Stadium(Base):
    __tablename__     = "stadium"

    id                = Column(Integer, primary_key=True)
    name                = Column(Text)
    location                = Column(Text)
class Player(Base):
    __tablename__    = "player"
    id               = Column(Integer, primary_key=True)
    first               = Column(Text)
    last               = Column(Text)
    boxname               = Column(Text)
    rl                = Column(CHAR(1))
class PlayerInGame(Base):
    __tablename__    = "playeringame"
    id               = Column(Integer, ForeignKey('player.id'), primary_key=True)
    game_pk          = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)
    num               = Column(Integer)
    position          = Column(CHAR(2)) #starting position?
    bat_order        = Column(Integer)
    game_position    = Column(CHAR(2)) #wtf?
    avg              = Column(Float)
    era              = Column(Float)
    hr               = Column(Integer)
    rbi              = Column(Integer)
    wins             = Column(Integer)
    wins             = Column(Integer)
    wins             = Column(Integer)
    losses             = Column(Integer)
    
class AtBat(Base):
    __tablename__    = "atbat"


    inning           = Column(Integer)
    num              = Column(Integer, primary_key=True)
 
    game_pk              = Column(Integer, ForeignKey('game.game_pk'), primary_key=True)
    b           = Column(Integer)
    s           = Column(Integer)
    stand       = Column(CHAR(1))
    p_throws       = Column(CHAR(1))
    inning           = Column(Integer)
    batter           = Column(Integer, ForeignKey('player.id'))
    pitcher           = Column(Integer, ForeignKey('player.id'))
    b_height         = Column(Text)
    des         = Column(Text)
    event         = Column(Text)
    brief_event         = Column(Text)
    date              = Column(Date)
 
    game = relationship("Game", backref=backref("atbat", order_by=num))
    pitchedby = relationship("Player", primaryjoin="AtBat.pitcher==Player.id")
    wasbatter = relationship("Player", primaryjoin="AtBat.batter==Player.id")
   

class Runner(Base):
    __tablename__     = "runner"
    runner_pk         = Column(Integer, primary_key=True)
    atbatnum          = Column(Integer, ForeignKey('atbat.num'))
    game_pk           = Column(Integer, ForeignKey('game.game_pk'))
    id                = Column(Integer, ForeignKey('player.id'))
    start             = Column(Text)
    end               = Column(Text)
    score             = Column(CHAR(1))
    rbi               = Column(CHAR(1))
    earned            = Column(CHAR(1))
    event             = Column(Text)
class GameDir(Base):
    __tablename__     = "gamedir"
    
    id                 = Column(Integer, primary_key=True)
    local_copy         = Column(Boolean)
    url                = Column(Text)
    path               = Column(Text)
    status             = Column(Text)
    status_long        = Column(Text)
    loaded             = Column(Boolean, default=False)
    game_pk            = Column(Integer)
    atbats             = Column(Integer)
    innings            = Column(Integer)
    downloaded_time    = Column(DateTime)
    loaded_time        = Column(DateTime)
    date_scheduled     = Column(Date)
    classified_time    = Column(DateTime, server_default=func.now())

    def __init_(self, url=None, path=None, status='not examined', local_copy=True):
        self.url = url
        self.path =path 
        self.status= status
        self.local_copy = local_copy


