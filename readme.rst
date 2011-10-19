=========
PyPitches
=========

Introduction
------------
This is a set of scripts to download PITCHf/x XML data from mlb.com,
to load that data into a database (SQLite or Postgres),
and to generate figures from that data.

Requires
--------
- SQLite3 or PostgreSQL
- PyYAML (included in recent Python )
- BeautifulSoup
- SQLAlchemy
- NumPy
- matplotlib

Usage
-----
- see run.sh
- It will download 2011 data from MLB (about 90 MB per month)
  and load into an SQlite file,
  then make some example plots
- Alternatively, download http://web.mit.ed/gkettler/www/pitches.sql.gz
  and put that in an sqlite database

Contents
--------
download.py 
   script to download the necessary files from gdx.mlb.com 
select_gamedirs.py
   script to inspect downloaded files. 
   Purpose is to reject games that were not actually played (due to rain, etc.). 
   Writes the list of valid game directories to a YAML file.
load.py
   Puts that information into an SQL database. Using SQLite by default. 
   Depends on the YAML output from select_gamedirs.py.
queries.py
   Quick utility functions to consruct SQLAlchemy queries for certain pitches,
   and to marshall the output as a NumPy array.
plot_pitch_locations.py and plot_pitch_types.py 
   Examples of Matplotlib plots built on queries.py
test_load.py
   The beginnings of a test suite. Only a few checks right now, but useful 
   for making sure that last schema change didn't blow everything up
   without waiting to load the whole dataset. 
   Depends on the sample data in testdummy/


ToDo
----
- More tests
- load.py is very slow -- where's the holdup?
- Bring Postgres support back up to the level of SQLite
- More interesting plots... How does the previous pitch affect the selection of the next? How does it affect the *outcome* of the next?
- Quantify the effect of fried chicken and beer on Red Sox pitching in September?


examples
--------

.. figure:: buchholz_all.png
   :scale: 50%

   Clay Buchholz has a lot of pitches, each moving in a particular direction.
   Note it's often hard to tell some 4-seam and 2-seam fastballs apart. And his 
   slider and cutter may be one pitch (sometimes referred to by the unfortunate 
   portmanteau, "slutter").

.. figure:: wakefield_all.png
   :scale: 50%

   Tim Wakefield, on the other hand, relies mostly on one pitch. But that knuckleball goes every which way.

.. figure:: lester_ch_r.png

   We can also plot the pitch's final location. 
   Here we easily see that Jon Lester, a lefty, throws a lot of changeups to right-handed
   batters and keeps them away from the batter...

.. figure:: lester_ch_l.png

   ...while throwing very few changeups to lefties.

.. figure:: speed_break_outcome.png
   :scale: 70%
   
   Looking at curveballs thrown by Josh Beckett, it's not easy to predict which pitches will be
   missed and which will be hit hard. In general, slower balls move more (which is no surprise),





The open question is whether you can predict the outcome. 
Take speed, break, release point, and final location and plot them in n dimensions,
then train an algorithm to separate different outcomes.

MLB is already doing something like this, and they give every pitch a "nasty factor" based
on its location, speed and movement.

What if you add even more information, such as its difference or similarity to the previous pitch?
