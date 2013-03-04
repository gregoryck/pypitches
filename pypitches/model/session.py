from sqlalchemy import create_engine 
from sqlalchemy.orm import scoped_session, sessionmaker
from settings import postgres_db, postgres_user, postgres_password
from contextlib import contextmanager
import sys

class ExistingSession(object):
    pass

class NewSession(object):
    pass

class SessionManager(object):
    _engine = None
    _sessionmaker = None
    _managed_sessions = []

    @classmethod
    def create(cls, db=None, user=None, password=None):
        if not cls._engine:
            cls._engine, cls._sessionmaker = cls.create_engine(db, user, password)

        if cls._managed_sessions:
            cls._managed_sessions[-1].begin_nested()
            cls._managed_sessions += cls._managed_sessions[-1:] # add same session to the list again
                                                                # it expects another .commit() now
        else:
            new_session = scoped_session(cls._sessionmaker)
            cls._managed_sessions += [new_session]
        return cls._managed_sessions[-1]

    @classmethod
    def get(cls):
        if cls._managed_sessions:
            return cls._managed_sessions[-1]
        else:
            return cls.create()

    @classmethod
    def create_engine(cls, db, user, password):
        if None in (db, user, password):
            raise ValueError, "SessionManager.create_engine got no database connection parameters. Call create(db, user, password) first."
        engine = create_engine("postgres://%s:%s@localhost/%s" 
                                        % (user, password, db),
                                    echo=False)
        return engine, sessionmaker(engine)

    ## This many be unnecessary when SA gives us begin_nested() as a context manager
    # @classmethod
    # @contextmanager
    # def context(cls):
    #     session = cls.create(db, user, password)
    #     try:
    #         yield session
    #         session.commit()
    #         session.close()
    #         cls._managed_sessions.pop()
    #     except:
    #         session.rollback()
    #         session.close()
    #         cls._managed_sessions.pop()
    #         raise

    @classmethod
    def withsession(cls, fn, opt=ExistingSession):
        """Decorator.
           Given a function that requires a session as its first arg,
           returns a function that takes a session as an optional kwarg.
           If ExistingSession is given, use the most recent session.
           If NewSession is given, create a new one and add it to the list.
        """
        if opt == NewSession:
            def new_fn(*args, **kwargs):
                with cls.context() as new_session:
                    return fn(new_session, *args, **kwargs)
        elif opt == ExistingSession:
            def new_fn(*args, **kwargs):
                session = cls.get()
                return fn(session, *args, **kwargs)
        new_fn.__realname__ = fn.__name__
        return new_fn


