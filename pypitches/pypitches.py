import model
import load
import sys
import yaml
import json
from web.app import run
from IPython import embed

cmds = [
'web',
'ipython',
'file',
'webtest',
]
def main():
    try:
        cmd = sys.argv[1]
        assert(cmd in cmds)
    except:
        print "usage: python pypitches.py web\nor\n       python pypitches.py ipython"
        sys.exit()
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



if __name__ == "__main__":
    main()
