import nose
import sys
from os.path import split, join, abspath, curdir, dirname
from subprocess import call
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

parent_dir = split(dirname(__file__))[0]
pypitches_root = split(split(dirname(abspath(__file__)))[0])[0]
sys.path = [parent_dir] + sys.path 

# this can get imported under different names, 
# which requires a hack
import model
print model.__name__
sys.modules['pypitches.model.session'] = sys.modules[model.__name__]
sys.modules['model.session'] = sys.modules[model.__name__]

from model import GameDir, Team, Game, Pitch
# sys.modules['']
from settings import postgres_password, postgres_user, postgres_test_db
from setup_postgres import initdb, get_cursor

static_dir = join(dirname(abspath(__file__)), 'static', 'testdummy')

class TestPlots(TestCase):
    def setUp(self):
        initdb(postgres_test_db, postgres_user, postgres_password)
        self.session = model.SessionManager.create(postgres_test_db, postgres_user, postgres_password) 

        from pypitches import select_gamedirs
        from pypitches import load
        select_gamedirs.classify_local_dirs_by_filesystem(static_dir)
        try:
            load.load()
        except IntegrityError:
            import pdb
            pdb.set_trace()
        self.assertEqual(self.session.query(Game).count(), 3)

    def tearDown(self):
        self.session.rollback()
        self.session.close() 
        model.SessionManager.destroy_all()

    def test_atbat(self):
        pitch = self.session.query(Pitch).filter().all()[0]
        atbat = pitch.atbat
        self.assertEqual(atbat.game, pitch.game)

class TestDB(TestCase):
    def setUp(self):
        self.game = createGame()
        self.atbat = createAtBat(self.game)
        self.batter = createPlayer()
        self.pitcher = createPlayer()
        self.atbat = createAtBat(self.game, self.pitcher, self.batter)
        self.pitch = createPitch(self.atbat)



game_pk = 1
def createGame():
    global game_pk
    conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    sql = """
          INSERT INTO game
          (game_pk, away_team_code, home_team_code, away_fname, home_fname, away_sname, home_sname, date)
          VALUES
          (%d, 'BOS', 'CHA', 'Boston Red Sox', 'Chicago White Sox', '', '', '2013-04-01')
          """
    cursor.execute(sql, game_pk )
    game_pk += 1
    return game_pk - 1

playerid = 1
def createPlayer():
    global playerid
    sql = """
          INSERT INTO player
          (id, first, last)
          VALUES
          (%d, 'Testy', 'Testerson')
          """
    conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    cursor.execute(sql, playerid)
    playerid  += 1
    return playerid - 1

atbatnum = 1
def createAtBat(game, pitcher, batter):
    global atbatnum
    sql = """
          INSERT INTO atbat
          (inning, num, b, s, batter, stand, p_throws, pitcher, des, event, brief_event, game_pk, date)
          VALUES
          (1, %d, 1, 1, %d, 'R', 'R', %d, 'batted ball hits a dove', 'single', 'single', %d, '2013-04-01')
          """
    conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    cursor.execute(sql, batter.id, pitcher.id, game.game_pk)
    atbatnum += 1
    return atbatnum - 1

