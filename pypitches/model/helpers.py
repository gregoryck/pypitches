from classes import *
import session

def add_gamedir(path, status, status_long=None):
    gamedir = GameDir()
    gamedir.path = path
    gamedir.local_copy = True
    gamedir.status = status
    gamedir.status_long = status_long
    session.Session.add(gamedir)
    session.Session.commit()


