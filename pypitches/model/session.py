from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session, sessionmaker
Session = None

def start_postgres(db, user, password=None):
    global Session
    if Session is None:
        if password:
            engine = create_engine("postgres://%s:%s@localhost/%s" % 
                                   (user, password, db), echo=False)
        else:
            engine = create_engine("postgres://%s@localhost/%s" % 
                                   (user, db), echo=False)
        Session = scoped_session(sessionmaker(bind=engine))
        return Session
    else:
        raise ValueError, "Session was not None, called model.start_postgres twice?\n{0}".format(Session)

