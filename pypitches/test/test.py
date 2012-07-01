import nose
import sys
from os.path import split, join, abspath, curdir, dirname
sys.path.append(split(dirname(abspath(__file__)))[0])
print sys.path
from subprocess import call
import preprocess

pypitches_root = split(split(dirname(abspath(__file__)))[0])[0]
sql_dir = join(pypitches_root, "sql")
template_file = join(sql_dir, "baseball.template.sql")
sql_file = join(sql_dir, "baseball.test.sql")
db_name = "pypitchestest"

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
        

def teardown():
    pass

def test():
    import pypitches
    from pypitches import model
    pitch = model.Pitch()
    




if __name__ == "__main__":
    nose.main()
