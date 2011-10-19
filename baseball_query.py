# baseball_query.py
# Set of utility functions to grab certain pitches
# by contructing the SQLAlchemy query,
# and return NumPy records for more convenient plotting.

import numpy
import baseball
from baseball import Pitch, AtBat, Player, Game
import matplotlib.pyplot as plt
import pdb

def objs2recarry(objs):
   """Given a list/iterator of Pitch objects, turn it into a NumPy RecArray so
   one field can easily be grabbed

   e.g. objs2recarry(pitches)['start_speed'] gives an easy-to-plot array of pitch speeds"""

   keys = ['start_speed', 'pfx_z', 'pfx_x', 'px', 'pz', 
         'sz_bot', 'sz_top',
         'break_length', 'break_angle', 'type', 'pitch_type']
   types = [float, float, float, float, float, float, float, float, float, '|S1', '|S2'] #|S64 would be strings length <= 64, for example
   retrows = [[pitch.__dict__[key] for key in keys] for pitch in objs]
   retarray = numpy.rec.fromrecords(retrows, dtype=zip(keys, types))
   return retarray

def to_radian(degrees):
   """takes degrees in a system where 0 degrees is straight down, 
   and positive degrees moves clockwise, returns measurement in radians
   on the unit circle"""


   other_degrees = 270 - degrees
   return (other_degrees / 180 * numpy.pi)

def normalized_pitch_height(pitch):
   """Pitch locations are given in inches, but the height of the
   strike zone varies depending on the batter's height and stance.
   Therefore, to plot pitches by one pitcher against many batters,
   the heights must be normalized.

   Take a pitch object and return its height scaled to an average-height
   hitter, in feet.
   1.6 ft represents the bottom of the zone and 3.65 represents the top.
   """

   return ((pitch['pz'] - pitch['sz_bot']) / (pitch['sz_top'] - pitch['sz_bot']) 
            * 2.05 + 1.6)

class NoPitchesError(ValueError):
   def __init__(self, value, query,
         name, event, des, balls, strikes, type_, pitch_type, payoff, date, stand):
      self.value = value
      self.query = query
      self.q_dict = {
            'name' : name,
            'event' : event,
            'des' : des,
            'balls' : balls,
            'strikes' : strikes,
            'type_' : type_,
            'pitch_type' : pitch_type,
            'payoff' : payoff,
            'date' : date,
            'stand' : stand,
            }
   def __str__(self):
      ret_str = self.value
      for key, item in self.q_dict.items():
         if item is not None:
            ret_str += "\n\t%s: %s" % (key, item)
      return ret_str

def pitches(session, name=None, event=None, des=None, date=None, 
      type_=None, pitch_type=None, stand=None, payoff=None,
      balls=None, strikes=None):
   """
   Construct and execute an SQL query to get pitches of interest. Can filter by...
   name: as a tuple (first, last)
      last: Pitcher's last name
      first: first name
   event: "event" field means any pitch from any at-bat with that result (Strikout, Single, Walk, etc)
   des: longer description of the at-bat result as reported by MLB. (Mind your spelling and caps)
   date: a string, in the format of "April 6, 2011"
   type: S, B, or X for strike (called, fouled or swing-and-miss), ball, or in play
   pitch_type (unfortunately similar name): two-letter code to describe the pitch:
               FF: four-seam fastball
               FT: two-seam fastball
               CH: changeup
               CU: curveball
               and more...

   all fields except pitcher's name are optional.
   """
   # This needs to be extended to use more fields. Filter by all the things!
   # The growing series of ifs is a code smell...

   q = session.query(Pitch)
   if name is not None:
      first, last = name
      q = q.join(Pitch.pitchedby, Pitch.atbat).filter(Player.last == last).filter(Player.first==first)
   if event is not None: 
      q = q.filter(AtBat.event == event)
   if des is not None:
      q = q.filter(Pitch.des == des)
   if balls is not None:
      q = q.filter(Pitch.balls == balls)
   if strikes is not None:
      q = q.filter(Pitch.strikes == strikes)
   if type_ is not None:
      q = q.filter(Pitch.type == type_)
   if pitch_type is not None:
      q = q.filter(Pitch.pitch_type == pitch_type)
   if payoff is not None: # If this is that last (deciding) pitch of an at-bat
      q = q.filter(Pitch.payoff == int(payoff))
   if date is not None:
      q = q.join(Pitch.game).filter(Game.date == date)
   if stand is not None:
      q = q.join(Pitch.atbat).filter(AtBat.stand == stand)


   objs = q.all()
   if len(objs) == 0:
      raise NoPitchesError("No pitches were found to match this query.", q, 
            name, event, des, balls, strikes, type_, pitch_type, payoff, date, stand)
   return objs2recarry(objs)

def callcolor(call):
   if call == 'S':
      return '#EE0044'
   elif call == 'B':
      return '#0000EE'
   elif call == 'X':
      return '#00EE00'
   else:
      raise ValueError, call

def callcolors(calls):
   return map(callcolor, calls)

