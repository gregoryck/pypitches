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
        initdb(postgres_test_db, postgres_user, postgres_password)
        self.session = model.SessionManager.create(postgres_test_db, postgres_user, postgres_password) 
        self.game_pk = createGame(self.session, )
        self.batter_id = createPlayer(self.session, )
        self.pitcher_id = createPlayer(self.session, )
        self.someguy_id = createPlayer(self.session, )
        self.atbat_num = createAtBat(self.session, self.game_pk, self.pitcher_id, self.batter_id)
        self.pitch_id = createPitch(self.session, self.game_pk, self.atbat_num, self.batter_id, self.pitcher_id)

    # def tearDown(self):
    #     self.session.rollback()
    #     self.session.close()

    def test_simple_query(self):
        pitches = self.session.query(Pitch).filter(Pitch.batter == self.batter_id).all()
        self.assertEqual(len(pitches), 1)
        self.assertEqual(pitches[0].id, self.pitch_id)

    # def test_other_guy(self):
        # self.other_atbat = createAtBat(self.game, self.pitcher, self.someguy_id)
        # atbats = self.session.query(AtBat).filter(AtBat.batter == self.)




game_pk = 1

def createGame(session):
    global game_pk
    # conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    sql = """
          INSERT INTO game
          (game_pk, away_fname, home_fname, away_sname, home_sname, date)
          VALUES
          (%s, 'Boston Red Sox', 'Chicago White Sox', '', '', '2013-04-01')
          """
    session.connection().execute(sql, [game_pk] )
    game_pk += 1
    return game_pk - 1

playerid = 1
def createPlayer(session):
    global playerid
    sql = """
          INSERT INTO player
          (id, first, last)
          VALUES
          (%s, 'Testy', 'Testerson')
          """
    # conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    session.connection().execute(sql, [playerid])
    playerid  += 1
    return playerid - 1

atbatnum = 1
def createAtBat(session, game, pitcher, batter):
    global atbatnum
    sql = """
          INSERT INTO atbat
          (inning, num, b, s, batter, stand, p_throws, pitcher, des, event, brief_event, game_pk, date)
          VALUES
          (1, %s, 1, 1, %s, 'R', 'R', %s, 'batted ball hits a dove', 'single', 'single', %s, '2013-04-01')
          """
    # conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    session.connection().execute(sql, [atbatnum, batter, pitcher, game])
    atbatnum += 1
    return atbatnum - 1

pitchid = 1
def createPitch(session, game_pk, atbat_num, batter_id, pitcher_id):
    global pitchid
    sql = """
          INSERT INTO pitch
          (id, game_pk, atbatnum, batter, pitcher)
          VALUES
          (%s, %s, %s, %s, %s)
          """
    # conn, cursor = get_cursor(postgres_test_db, postgres_user, postgres_password)
    session.connection().execute(sql, [pitchid, game_pk, atbat_num, batter_id, pitcher_id])
    pitchid += 1
    return pitchid - 1

