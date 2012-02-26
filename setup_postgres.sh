dropdb -U pypitches pypitchestest
createdb -U pypitches pypitchestest
python preprocess.py POSTGRES baseball.sql.pre | psql -U pypitches -d pypitchestest 
