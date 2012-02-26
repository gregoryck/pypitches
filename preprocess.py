# to preprocess sql files
# a toy

# USAGE
#  python preprocess.py FLAG1 FLAG2 .. FLAGN filename
# lines that don't end with --:<something> are printed always
# lines that end with --:<something> are printed if and only if that flag 
# was given as an argument

import re
import sys


def process(filename, flags):
    with open(filename) as handle:
        for line in handle:
            line = line.rstrip()
            match = re.search("--:(\S+)$", line)
            if match is None:
                print line
            elif match.groups()[0] in flags:
                print line

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "usage: python preprocess.py FLAG1 FLAG2 .. FLAGN filename"
    else:
        filename = sys.argv[-1]
        flags = sys.argv[1:-1]
        process(filename, flags)


