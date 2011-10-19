# download.py
# grab selected files from MLB Advanced Media's server
# and replicate the same directory structure locally

# FIXME: may not create directories properly with Windows-style
# backslashes. 
# Should use os.path.join to be agnostic, but these strings are queries
# for urlopen as well...

import os
import re
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen

server_string = "http://gdx.mlb.com"
start_dir = "/components/game/mlb/"
#server_string = "http://localhost"
#start_dir = "testbaseball/"

# Patterns to grab only specific years, months, days, or games
year_pattern  = "year_2011" #only want this one year
month_pattern = "month_0" 
day_pattern   = "day_"
game_pattern  = "gid_"
patterns = [year_pattern, month_pattern, day_pattern, game_pattern]

# These three 
xml_wishlist = ("game.xml", "players.xml", "boxscore.xml")

errorlog = open("download.log", 'w')

def get_links(string, pattern):
   """string is an HTML page or tag soup. 
   Scan all links in that page and yield those that resemble pattern."""
   soup = BeautifulSoup(string)
   for link in soup.findAll("a"):
      if re.match(pattern, link.string.lstrip()):
         yield link.string.lstrip(), link['href']

def grab_page(url, filename=None):
   """Grab page at url and either return it as a string or save it to file"""
   response = urlopen(url)
   html = response.read()
   if filename is None:
      return html
   else:
      with open(filename, 'w') as handle:
         handle.write(html)

def download_game(gamedir_url):
   """Download the game in directory gamedir_url.
   First grab the directory and get a listing.
   Expect to find a few .xml files and an inning/ directory with an
   inning_all.xml file"""

   pbp_string = "inning/"
   links_and_hrefs = dict(get_links(grab_page(gamedir_url), pbp_string))
   if links_and_hrefs:
      os.mkdir(pbp_string)
      os.chdir(pbp_string)
      grab_page(gamedir_url + "inning/inning_all.xml", "inning_all.xml")
      os.chdir('..')
      for xmlname in xml_wishlist:
         grab_page(gamedir_url + xmlname, xmlname)
   else:
      print >>errorlog, gamedir_url, " no inning/ directory"



def navigate_dirs(start_url, patterns, fun=download_game):
   """Navigate the directory structure on the server to find
   game directories"""
   if len(patterns) > 0:
      for linkname, href in get_links(grab_page(start_url), patterns[0]):
         newdir = href.split("/")[-2]
         print newdir
         if newdir not in os.listdir("."):
            os.mkdir(newdir)
         os.chdir(newdir)
         navigate_dirs(start_url + href, patterns[1:], fun)
         os.chdir("..")
   else:
      fun(start_url)



def say_hello(dir, handle):
   print "hello, baseball"
   for linkname, href in get_links(handle):
      print linkname, href

def gogogo():
   os.chdir("downloads")
   navigate_dirs(server_string + start_dir, patterns, download_game) 
   os.chdir("..")

def test1():
   os.mkdir("test1")
   os.chdir("test1")
   download_game("http://localhost/testbaseball/year_2011/month_06/day_09/gid_2011_06_09_bosmlb_nyamlb_1/")
   os.chdir("..")

def test2():
   os.mkdir("test2")
   os.chdir("test2")
   navigate_dirs("http://localhost/testbaseball/", download.patterns)
   os.chdir("..")


if __name__ == "__main__":
   gogogo()
   #test()
