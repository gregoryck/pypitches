from classes import *
from helpers import *
import session


Session = None
def start_postgres(db, user, password=None):
    global Session
    Session = session.start_postgres(db, user, password)


