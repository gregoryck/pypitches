from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session, sessionmaker

# This might be called more than once by the same process.
# sqlalchemy says that's inefficient, but should work?
# hard to make sure I init it once without
# 1. hardcoding user/password
# 2. passing Sessions around

def start_postgres(db, user, password=None):
    if password:
        engine = create_engine("postgres://%s:%s@localhost/%s" % 
                               (user, password, db), echo=False)
    else:
        engine = create_engine("postgres://%s@localhost/%s" % 
                               (user, db), echo=False)
    return scoped_session(sessionmaker(bind=engine))

Session = start_postgres('pypitches', 'pypitches')
