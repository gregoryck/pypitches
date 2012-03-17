# assuming there's a pypitches user with createdb permission

from subprocess import call, Popen, PIPE
import sys
import preprocess

db_name = sys.argv[1]
sql_file = "baseball.sql"

call(['dropdb', '-U', 'pypitches', db_name])
call(['createdb', '-U', 'pypitches', db_name])
with open(sql_file, "w") as outhandle:
    preprocess.process(sql_file + '.pre', ['POSTGRES'],outhandle)
with open(sql_file) as inhandle:
    call(['psql', '-U', 'pypitches', '-d', db_name], stdin=inhandle)
