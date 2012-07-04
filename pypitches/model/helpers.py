from classes import *
import session

def add_gamedir(path, status=None, status_long=None, pk=None, innings=None, atbats=None):
    gamedir = GameDir()
    gamedir.path = path
    gamedir.local_copy = True
    gamedir.status = status
    gamedir.status_long = status_long
    gamedir.game_pk = pk
    gamedir.innings = innings
    gamedir.atbats = atbats
    session.Session.add(gamedir)
    session.Session.commit()


