# to preprocess sql files
# a toy

# USAGE
#  python preprocess.py FLAG1 FLAG2 .. FLAGN filename
# lines that don't end with --:<something> are printed always
# lines that end with --:<something> are printed if and only if that flag 
# was given as an argument

import re
import sys
from jinja2 import Template


def process(filename, flags,outhandle=sys.stdout):
    flags_as_dict = dict([(flag, True) for flag in flags])
    with open(filename) as inhandle:
        template = Template(inhandle.read())
        outhandle.write(template.render(flags_as_dict))
    

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage: python preprocess.py FLAG1 FLAG2 .. FLAGN filename"
    else:
        filename = sys.argv[-1]
        flags = sys.argv[1:-1]
        process(filename, flags)


