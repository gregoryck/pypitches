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
from settings import postgres_password, postgres_user, postgres_test_db
from setup_postgres import initdb, get_cursor

static_dir = join(dirname(abspath(__file__)), 'static', 'testdummy')


class TestBasics(TestCase):
    def setUp(self):
        # Destroy/Create test database
        initdb(postgres_test_db, postgres_user, postgres_password)
        self.session = model.SessionManager.create(postgres_test_db, postgres_user, postgres_password) 

    def tearDown(self):
        self.session.rollback()
        self.session.close()
        model.SessionManager.destroy_all()

    def test_basics(self):
        team = Team()
        team.id = 1
        team.code = 'MAR'
        team.name = "Martian War Machines"
        team.name_full = "Martian War Machines"
        team.name_brief = "Mars"
        self.session.add(team)
        
        team2 = Team()
        team2.id = 2
        team2.code = 'VEN'
        team2.name = "Venusian Pressure Cookers"
        team2.name_full = "Venusian Pressure Cookers"
        team2.name_brief = "Venus"
        self.session.add(team2)
        self.session.flush()

    def test_classify(self):
        from pypitches import select_gamedirs
        select_gamedirs.classify_local_dirs_by_filesystem(static_dir)
        self.assertEqual(self.session.query(GameDir).count(), 4)
        self.assertEqual(self.session.query(GameDir).filter(GameDir.status=='postponed').count(), 1)

    def test_load(self):
        from pypitches import select_gamedirs
        from pypitches import load
        select_gamedirs.classify_local_dirs_by_filesystem(static_dir)
        load.load()
        self.assertEqual(self.session.query(Game).count(), 3)
        self.session.commit()

class TestWeb(TestCase):
    def test_import(self):
        import web
        from web import app

