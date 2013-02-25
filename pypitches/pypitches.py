import sys
from IPython import embed
import setup_postgres
import settings
from os import path

cmds = [
'web',
'ipython',
'file',
'webtest',
'initdb',
]

def main():
    try:
        cmd = sys.argv[1]
        assert(cmd in cmds)
    except:
        print "usage: python pypitches.py web\nor\n       python pypitches.py ipython"
        sys.exit()
    if cmd == 'initdb':
        setup_postgres.initdb(settings.postgres_db, settings.postgres_user, settings.postgres_password)
        sys.exit()
    else:
        import model
        import load
        from web.app import run

    if cmd == 'web':
        run()
    elif cmd == 'webtest':
        run('pypitchestest', 'pypitches', 'slider')
    elif cmd == 'ipython':
        embed()
    elif cmd == 'file':
        # will generate output by a config file
        # a la plot_pitch_locations.py
        raise NotImplementedError
    elif cmd == 'download':
        # hit the MLBAM server and get it all
        # per
        pass
        

if __name__ == "__main__":
    main()
