import os
import sys
import yaml
import unittest

from load import load_games
import pypitches as baseball
import baseball_query
from baseball_query import pitches

settings_file = 'baseball_test.yaml'

class testLoad(unittest.TestCase):
   def setUp(self):
      """Blows up the sqlite database and recreates it for each test"""
      if len(sys.argv) > 1:
         print "test_load.py doesn't recognize arguments -- gets options from baseball_test.yaml"
      else:
         sqlitefilename = yaml.load(open(settings_file))['sqlite_file']
         if os.path.exists(sqlitefilename): os.remove(sqlitefilename) 
         settings, self.session = baseball.init(settings_file)
         gamedirs_file = settings['gamedirs_file']
         load_games(self.session, gamedirs_file)

   # Test queries using SQLAlchemy directly
   def test_pitches_per_atbat(self):
      """Does the first atbat have the right # of pitches?"""
      atbat = self.session.query(baseball.AtBat).filter(baseball.AtBat.num == 1).one()
      assert(len(atbat.pitches)) == 7

   def test_count_atbats(self):
      """Should be 8 atbats I think."""
      atbats = self.session.query(baseball.AtBat).all()
      assert(len(atbats)) == 8

   # Now test queries constructed by baseball_query.py
   def testPlots(self):
      found_pitches = pitches(self.session, des="Swinging Strike")
      assert(len(found_pitches)) == 2
      found_pitches = pitches(self.session, des="Swinging Strike (Blocked)")
      assert(len(found_pitches)) == 1

   def testCount(self):
      found_pitches = pitches(self.session, balls=0, strikes=0) #every atbat has a 0-0 pitch, right?
      assert(len(found_pitches)) == 8
      found_pitches = pitches(self.session, balls=0, strikes=1) #Not exactly all first-pitch strikes
      assert(len(found_pitches)) == 3
      found_pitches = pitches(self.session, balls=0, strikes=0, payoff=True) #One-pitch at-bats. Add to previous result for all first-pitch strikes
      assert(len(found_pitches)) == 2

   def testStand(self):
      found_pitches = pitches(self.session, stand='L', payoff=True) #Lefty batters
      assert(len(found_pitches)) == 6

      found_pitches = pitches(self.session, stand='R', payoff=True)
      assert(len(found_pitches)) == 2




      



if __name__ == "__main__":
   unittest.main()
   
      
