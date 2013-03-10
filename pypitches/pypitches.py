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
'classify',
]

def main():
    try:
        cmd = sys.argv[1]
        assert(cmd in cmds)
    except:
        invocations = ["python pypitches.py {0}".format(cmd) for cmd in cmds]
        print "usage:  " + "\n        ".join(invocations)
        sys.exit()
    if cmd == 'initdb':
        setup_postgres.initdb(postgres_db, postgres_user, postgres_password)
        sys.exit()
    else:
        import model
        model.SessionManager.create(postgres_db, postgres_user, postgres_password)
        import load
        from web.app import app
        import select_gamedirs

    if cmd == 'web':
        app.run()
    elif cmd == 'webtest':
        app.run('pypitchestest', 'pypitches', 'slider')
    elif cmd == 'ipython':
        embed()
    elif cmd == 'file':
        # will generate output by a config file
        # a la plot_pitch_locations.py
        raise NotImplementedError
    elif cmd == 'download':
        # hit the MLBAM server and get it all
        pass
    elif cmd == 'classify':
        with model.SessionManager.get().begin_nested():
            static_dir = sys.argv[2]
            select_gamedirs.classify_local_dirs_by_filesystem(static_dir)
        model.SessionManager.commit()
    elif cmd == 'load':
        statuses=set(sys.argv[2:]) or set(['final'])
        with model.SessionManager.get().begin_nested():
            load.load(statuses)
        model.SessionManager.commit()


        

if __name__ == "__main__":
    main()
