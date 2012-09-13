# download.py
# grab selected files from MLB Advanced Media's server
# and replicate the same directory structure locally

import os
from os.path import join, pardir, abspath, isdir
import re
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen
import select_gamedirs
import model
from model import Session, GameDir

server_string = "http://gdx.mlb.com"
start_dir = "/components/game/mlb/"
#server_string = "http://localhost"
#start_dir = "testbaseball/"

# Patterns to grab only specific years, months, days, or games
year_pattern  = "year_2012" #only want this one year
month_pattern = "month_0" 
day_pattern   = "day_"
game_pattern  = "gid_"
default_patterns = [year_pattern, month_pattern, day_pattern, game_pattern]

# These three 
xml_wishlist = ("game.xml", "players.xml", "boxscore.xml")

current_path = abspath(".")

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

def database_has(gamedir_url):
    """Is that url already downloaded AND is it good?"""

    records = Session.query(GameDir).filter(GameDir.url == gamedir_url).all()
    if len(records) > 1:
        raise ValueError, "multiple records in database for url= {0}".format(gamedir_url)
    elif len(records) == 1:
        if records[0].status == 'error' or records[0].status == 'redo':
            path = records[0].path
            print "Deleting and replacing old gamedir {0}".format(path)
            shutil.rmtree(path)
            Session.delete(records[0])
            Session.commit()
            return False
        else:
            return True
    else:
        return False

def download_game(gamedir_url, check_local=database_has):
    """Download the game in directory gamedir_url.
    First grab the directory and get a listing.
    Expect to find a few .xml files and an inning/ directory with an
    inning_all.xml file.
   
    Optionally, take a function to decide whether to proceed"""

    pbp_string = "inning/"
    if check_local(gamedir_url):
        print gamedir_url, "skipping because already have good data"
        return
    links_and_hrefs = dict(get_links(grab_page(gamedir_url), pbp_string))
    if links_and_hrefs:
        os.mkdir(join(current_path, pbp_string))
        dest_path_inning_all = join(current_path, pbp_string, "inning_all.xml")
        grab_page(gamedir_url + "inning/inning_all.xml", dest_path_inning_all)
        for xmlname in xml_wishlist:
            dest_path_etc = join(current_path, xmlname) 
            grab_page(gamedir_url + xmlname, dest_path_etc)
        gamedir_row = GameDir(url=gamedir_url, path=current_path, status='not examined', local_copy=True)
    else:
        print gamedir_url, " no inning/ directory"
        gamedir_row = GameDir(url=gamedir_url, path=None, status='error', 
                              status_long="no {0} directory".format(pbp_string), local_copy=False)
    Session.add(gamedir_row)
    Session.commit()



def navigate_dirs(start_url, patterns, fun=download_game):
    """Navigate the directory structure on the server to find
    game directories.
    
    When you hit the end of a pattern, call the function,
    which defaults to download_game"""
    global current_path
    if len(patterns) > 0:
       for linkname, href in get_links(grab_page(start_url), patterns[0]):
          newdir = href.split("/")[-2]
          if newdir not in os.listdir(current_path):
             os.mkdir(join(current_path, newdir))
          current_path = join(current_path, newdir)
          navigate_dirs(start_url + href, patterns[1:], fun)
          current_path = abspath(join(current_path, pardir))
    else:
       fun(start_url)

def download_with_patterns(patterns=default_patterns, local_dir='downloads'):

    global current_path
    if not isdir(local_dir):
        os.mkdir(local_dir)
    current_path = join(current_path, local_dir)
    navigate_dirs(server_string + start_dir, patterns, download_game) 
    current_path = abspath(join(current_path, pardir))

if __name__ == "__main__":
    global Session
    Session = model.start_postgres('pypitches', 'pypitches')
    download_with_patterns(local_dir='download')
