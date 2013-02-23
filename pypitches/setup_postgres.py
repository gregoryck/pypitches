import sys
import preprocess
import psycopg2
#from pypitches import pypitches



    # call(['dropdb', '-U', 'pypitches', db_name])
    # call(['createdb', '-U', 'pypitches', db_name])

def initdb(settings):
    try:
        psycopg2.connect("dbname='%(postgres_db)s' user='%(postgres_user)s' host='localhost' password='%(postgres_password)s'" % settings)
    except psycopg2.OperationalError as err:
        if 'password authentication failed' in err.args[0]:
            raise EnvironmentError, err.args[0] + "\n\n is the postgres user %s created?" % (settings['postgres_user'])
        if 'does not exist' in err.args[0]:
            raise EnvironmentError, err.args[0] + "\n\n has the database been created?"
        raise


    sql_file = "baseball.sql"

    with open(sql_file, "w") as outhandle:
        preprocess.process(template_file, ['postgres', 'ranges'],outhandle)
    with open(sql_file) as inhandle:
        call(['psql', '-U', 'pypitches', '-d', db_name], stdin=inhandle)


if __name__ == "__main__":
    settings = dict(postgres_db='pypitches', postgres_user='pypitches', postgres_password='slider')
    initdb(settings)