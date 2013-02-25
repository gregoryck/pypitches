from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session, sessionmaker
from settings import postgres_db, postgres_user, postgres_password
from contextlib import contextmanager

class SessionMaker(object):
    _engine = None
    _sessionmaker = None

    @classmethod
    def create(cls, db=None, user=None, password=None):
        if not cls._engine:
            cls._engine, cls._sessionmaker = cls.create_engine(db, user, password)
        return scoped_session(cls._sessionmaker)

    @classmethod
    def create_engine(cls, db, user, password):
        engine = create_engine("postgres://%s:%s@localhost/%s" 
                                        % (user, password, db),
                                    echo=False)
        return engine, sessionmaker(engine)

    @classmethod
    @contextmanager
    def context(cls):
        session = cls.create(db, user, password)
        try:
            yield session
            session.commit()
            session.close()
        except:
            session.rollback()
            session.close()
            raise

Session = SessionMaker.create(postgres_db, postgres_user, postgres_password)