import model
import load
import sys
import yaml
import json
from web.app import app
from IPython import embed

cmds = [
'web',
'ipython',
'file',
]
def main():
    try:
        cmd = sys.argv[1]
        assert(cmd in cmds)
    except:
        print "usage: python pypitches.py web\nor\n       python pypitches.py ipython"
        sys.exit()
    if cmd == 'web':
        app.run()
    elif cmd == 'ipython':
        embed()
    elif cmd == 'file':
        # will generate output by a config file
        # a la plot_pitch_locations.py
        raise NotImplementedError



if __name__ == "__main__":
    main()
