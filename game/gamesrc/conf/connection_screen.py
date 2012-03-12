#
# This is Evennia's default connection screen. It is imported 
# and run from game/gamesrc/world/connection_screens.py. 
#

from src.utils import utils 

DEFAULT_SCREEN = \
"""{b=============================================================={n
 Welcome to {gAvaloria{n, version Alpha! 

 As the game is currently in Alpha, data persistence can not be
 expected and Character wipes WILL happen.  Please keep this in mind
 as you play and try to not get too attached.  The purpose of this 
 testing period is to try and break as many things as possible, and 
 have fun while doing it!

 If you encounter a traceback when attempting to do something, please
 head to code.google.com/p/avaloria/issues and submit a ticket to the
 issue tracker (after checking to see if it's already been reported)
 and copy the entire traceback, and the command issued into the ticket.

 If you have an existing account, connect to it by using the menu
 below.

 Enter {whelp{n for more info. {wlook{n will re-show this screen.
{b=============================================================={n"""
