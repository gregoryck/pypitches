import sys
from web.app import run
from IPython import embed
import yaml
import setup_postgres

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
        setup_postgres.initdb()
        sys.exit()
    else:
        import model
        import load

    if cmd == 'web':
        run()
    elif cmd == 'webtest':
        run('pypitchestest', 'pypitches', 'slider')
    elif cmd == 'ipython':
        embed()
    elif cmd == 'initdb':
        initdb()
    elif cmd == 'file':
        # will generate output by a config file
        # a la plot_pitch_locations.py
        raise NotImplementedError
        
if len(sys.argv) > 2:
    settings_file = sys.argv[2]
else:
    thisdir = path.dirname(__file__)
    settings_file = path.join(thisdir, "settings.yaml")
with open(settings_file) as handle:
    settings = yaml.load(handle)



if __name__ == "__main__":
    main()
