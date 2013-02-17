# assuming there's a pypitches user with createdb permission

from subprocess import call, Popen, PIPE
import sys
import preprocess


try:
    call(['psql', '--help'])
except:
    raise EnvironmentError, "This script (and PyPitches) requires PostgreSQL"

db_name = "pypitches" 
sql_file = "baseball.sql"
template_file = sys.argv[1] #"baseball.template.sql"

call(['dropdb', '-U', 'pypitches', db_name])
call(['createdb', '-U', 'pypitches', db_name])
with open(sql_file, "w") as outhandle:
    preprocess.process(template_file, ['postgres', 'ranges'],outhandle)
with open(sql_file) as inhandle:
    call(['psql', '-U', 'pypitches', '-d', db_name], stdin=inhandle)
