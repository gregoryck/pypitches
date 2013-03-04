import sys
import preprocess
import psycopg2
from os.path import split, join, dirname, abspath
#from pypitches import pypitches



    # call(['dropdb', '-U', 'pypitches', db_name])
    # call(['createdb', '-U', 'pypitches', db_name])

pypitches_root = split(dirname(abspath(__file__)))[0]
sql_dir = join(pypitches_root, "sql")
sql_file = join(sql_dir, "baseball.sql")
def initdb(db, user, password):
    try:
        conn = psycopg2.connect("dbname='%(postgres_db)s' user='%(postgres_user)s' host='localhost' password='%(postgres_password)s'" 
                                % dict(postgres_db=db, postgres_user=user, postgres_password=password))
    except psycopg2.OperationalError as err:
        if 'password authentication failed' in err.args[0]:
            raise EnvironmentError, err.args[0] + "\n\n is the postgres user %s created?" % (user,)
        if 'does not exist' in err.args[0]:
            raise EnvironmentError, err.args[0] + "\n\n has the database been created?"
        raise

    cursor = conn.cursor()


    with open(sql_file) as inhandle:
        ddl_string = "".join(list(inhandle))
    cursor.execute(ddl_string)
    conn.commit()

if __name__ == "__main__":
    settings = dict(postgres_db='pypitches', postgres_user='pypitches', postgres_password='slider')
    initdb(settings)