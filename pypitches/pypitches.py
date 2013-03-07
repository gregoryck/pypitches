import sys
from IPython import embed
import setup_postgres
import settings
from settings import postgres_password, postgres_user, postgres_db
from os import path

cmds = [
'web',
'ipython',
'file',
'webtest',
'initdb',
'load',
]

def main():
    try:
        cmd = sys.argv[1]
        assert(cmd in cmds)
    except:
        print "usage: python pypitches.py web\nor\n       python pypitches.py ipython"
        sys.exit()
    if cmd == 'initdb':
        setup_postgres.initdb(postgres_db, postgres_user, postgres_password)
        sys.exit()
    else:
        import model
        model.SessionManager.create(postgres_db, postgres_user, postgres_password)
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
        pass
    elif cmd == 'load':
        import select_gamedirs
        static_dir = sys.argv[2]
        select_gamedirs.classify_local_dirs_by_filesystem(static_dir)
        load.load()
        self.assertEqual(self.session.query(Game).count(), 3)


        

if __name__ == "__main__":
    main()
