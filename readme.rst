=========
PyPitches
=========

Introduction
------------
This is a set of scripts to download PITCHf/x XML data from mlb.com,
to load that data into a database (SQLite or Postgres),
and to generate figures from that data.

You can find a pdf of this readme (with images, as the code generates them)
at http://web.mit.edu/gkettler/www/pypitches.pdf

Requires
--------
- SQLite3 or PostgreSQL
- PyYAML (included in recent Python releases)
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
- Alternatively, download http://web.mit.edu/gkettler/www/pitches.sql.gz
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


What do the columns mean?
-------------------------

Copied from Alan M. Nathan's summary at http://webusers.npl.illinois.edu/~a-nathan/pob/tracking.htm 

x, y, and z 
    location of pitch as it crosses the front of home plate. The units are in camera pixels and are therefore not very useful. I recommend ignoring these two parameters and instead use p_x and p_z, defined below.
 
start_speed
    speed of ball in mph at the starting position (defined below).
 
end_speed
    speed of ball in mph as it crosses the front of home plate, located 1.417 ft from the point of home plate (i.e., at the coordinate y=1.417). Note the end_speed is less than start_speed due to the effect of air resistance.
 
sz_top, sz_bottom
    a line of constant z (in ft) defining the lower and upper limits, respectively, of the strike zone. That is, these are the height above home plate of the top and bottom of the strike zone. Currently, these parameters are set for each batter by the operator by visually observing the image from the center-field camera.
 
pfx_x,pfx_z
    The deviation (in inches) of the pitch trajectory from a straight-line in the x (horizontal) and z (vertical) directions between y=40 ft and the front edge of home plate, y=1.417 ft. It is important to note two things. First, the initial value is y=40 ft, regardless of the value of the initial value y0 (defined below). If the pitcher's release point had been used (approximately y=55 ft), then the deviation would have been nearly twice as large. Second, the effect of gravity has been removed from pfx_z, so that both parameters are the "break" of the pitch due to the Magnus force on a spinning baseball. Note that the online Gameday reports the quantity pfx, which is presumably the square root of pfx_x2+pfx_z2. Given our sign conventions, a positive value of pfx_x cooresponds a deviation to the catcher's right and a negative value to the catcher's left. Similarly, a postive value of of pfx_z is a pitch the drops less than it would from gravity alone (most pitches fall in this category), whereas a negative value is a pitch that drops more than from gravity alone (e.g., a "12-6" curveball).
 
p_x, p_z
    location of pitch in the x and z coordinates, respectively, as it crosses the front of home plate, in units of ft. When you watch Gameday, this is the location of the dot on the screen that appears for each pitch. It is computed from the tracked trajectory. There is a one-to-one correlation between p_x and x and between p_z and y (see above description of x and y).
 
x0,y0,z0, vx0,vy0,vz0,ax,ay,az
    These parameters are the most important ones in the database, since all others are computed using these. The parameters represent the result of making a least-squares fit to the measured trajectory assuming constant acceleration, for each of the three dimensions. The first three parameters are the initial positions in ft, the next three are initial velocities in ft/s, the next three are the accelerations (assumed constant) in ft/s2. To calculate the full trajectory, use the formula x(t)=x0+vx0*t+0.5*ax*t2, and a similar formula for y(t) and z(t), where t is the time. Note that y0, which is the distance from the point of home plate where the tracking begins, is 50 ft for the file discussed above although earlier files used 55 ft or 40 ft. This point is the location where the start_speed is determined and from which the break parameters (see below) are calculated.. Note that start_speed is just the square root of vx_02+vy_02+vz_02, converted to mph.
 
break_y,break_angle, break_length
    These quantities refer to a different definition of "break" than the quantities pfx_x, pfx_z defined above. They are arrived at as follows. A straight line is drawn from the starting location x0,y0,z0 to the final location defined by p_x, p_z and y=1.417 ft. Such a line determines a straight-line trajectory from starting point to ending point. That trajectory is then compared to the actual trajectory determined by the constant acceleration fit to the data. The quantity break_length is the largest deviation, in inches, of the actual from the straight-line trajectory. The quantity break_y is the y-distance from home plate where the maximum deviation occurs. The quantity break_angle is the direction of the deviation, with the convention that a pitch that breaks away from or toward a RHH has a negative or positive angle, respectively; a break_angle of 0 is a pitch with no horizontal break and is typical of a straight fastball. Most pitches will have a break_angle between about -50o and +50o. An angle greater than 90o in absolute value is almost impossible, since that would imply an upward break, defeating gravity (the myth of the "rising fastball"). Both break_length and break_angle are shown on the Gameday screen. Also the break_angle is indicated with an arrow that points straight down for 0o, down and to the left for a positive angle, or down and to the right for a negative angle. You can use the break_angle to find the x and z components of break_length as follows: break_x = break_length*sin(break_angle) and break_z = break_length*cos(break_angle). Note that break_x has the opposite sign as pfx_x because of the convention used to define the angle. That is, a pitch that breaks away from a RHH (i.e., toward the catcher's right) has a positive pfx_x but a negative break_x.




