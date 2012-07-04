import nose
import sys
from os.path import split, join, abspath, curdir, dirname
#sys.path.append(split(dirname(abspath(__file__)))[0])
from subprocess import call
from .. import preprocess
from .. import model
from ..model import GameDir

pypitches_root = split(split(dirname(abspath(__file__)))[0])[0]
sql_dir = join(pypitches_root, "sql")
template_file = join(sql_dir, "baseball.template.sql")
sql_file = join(sql_dir, "baseball.test.sql")
db_name = "pypitchestest"
static_dir = join(dirname(abspath(__file__)), 'static', 'testdummy')

# Launch test web server


#ServerThread(

# Destroy/Create test database
def setup():
    call(['dropdb', '-U', 'pypitches', db_name])
    call(['createdb', '-U', 'pypitches', db_name])
    with open(sql_file, "w") as outhandle:
        preprocess.process(template_file, ['postgres', 'ranges'],outhandle)
    with open(sql_file) as inhandle:
        call(['psql', '-U', 'pypitches', '-d', db_name], stdin=inhandle)
    model.start_postgres(db_name,'pypitches', 'slider')
    print model.Session
    assert model.Session is not None
        

def teardown():
    pass

def test_basics():
    team = model.Team()
    team.id = 1
    team.code = 'MAR'
    team.name = "Martian War Machines"
    team.name_full = "Martian War Machines"
    team.name_brief = "Mars"
    model.Session.add(team)
    
    team2 = model.Team()
    team2.id = 2
    team2.code = 'VEN'
    team2.name = "Venusian Pressure Cookers"
    team2.name_full = "Venusian Pressure Cookers"
    team2.name_brief = "Venus"
    model.Session.add(team2)

    model.Session.commit()

#    game = model.Game()
#    game.game_pk = 1
#    game.away_team_code = 'MAR'
#    game.home_team_code = 'VEN'
#    game.stadium = 1
#    game.game_pk = 1
#    game.game_pk = 1
#    game.game_pk = 1
#    game.game_pk = 1


def test_classify():
    from pypitches import select_gamedirs
    select_gamedirs.classify_local_dirs(static_dir)
    assert model.Session.query(GameDir).count() == 4
    assert model.Session.query(GameDir).filter(GameDir.status=='postponed').count() == 1
    




if __name__ == "__main__":
    nose.main()
