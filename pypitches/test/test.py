import nose
import sys
from os.path import split, join, abspath, curdir, dirname
from subprocess import call
from .. import preprocess
from ..model import GameDir, start_postgres, Team
import pdb

pypitches_root = split(split(dirname(abspath(__file__)))[0])[0]
sql_dir = join(pypitches_root, "sql")
template_file = join(sql_dir, "baseball.template.sql")
sql_file = join(sql_dir, "baseball.test.sql")
db_name = "pypitchestest"
user = "pypitches"
static_dir = join(dirname(abspath(__file__)), 'static', 'testdummy')

Session =  None

# TODO Launch test web server

def setup():
    # Destroy/Create test database
    call(['dropdb', '-U', user, db_name])
    call(['createdb', '-U', user, db_name])
    with open(sql_file, "w") as outhandle:
        preprocess.process(template_file, ['postgres', 'ranges'],outhandle)
    with open(sql_file) as inhandle:
        call(['psql', '-U', user, '-d', db_name], stdin=inhandle)
    global Session
    Session = start_postgres(db_name, user, 'slider')

def teardown():
    pass

def test_basics():
    team = Team()
    team.id = 1
    team.code = 'MAR'
    team.name = "Martian War Machines"
    team.name_full = "Martian War Machines"
    team.name_brief = "Mars"
    Session.add(team)
    
    team2 = Team()
    team2.id = 2
    team2.code = 'VEN'
    team2.name = "Venusian Pressure Cookers"
    team2.name_full = "Venusian Pressure Cookers"
    team2.name_brief = "Venus"
    Session.add(team2)

    Session.commit()

def test_classify():
    from pypitches import select_gamedirs
    select_gamedirs.Session = Session
    select_gamedirs.classify_local_dirs(static_dir)
    assert Session.query(GameDir).count() == 4
    assert Session.query(GameDir).filter(GameDir.status=='postponed').count() == 1
    




if __name__ == "__main__":
    nose.main()
