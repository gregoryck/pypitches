import json

with open("gamedirs.2011.json") as handle:
    bigd = json.load(handle)

littled = dict([(key, val[0]) for key, val in bigd.iteritems()
                   if 'bos' in val[0]])

with open("gamedirs.small.json", "w") as handle2:
    json.dump(littled, handle2)
