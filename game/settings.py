# 
# Evennia MU* server configuration file
#
# You may customize your setup by copy&pasting the variables you want
# to change from the master config file src/settings_default.py to
# this file. Try to *only* copy over things you really need to customize
# and do *not* make any changes to src/settings_default.py directly.
# This way you'll always have a sane default to fall back on
# (also, the master file may change with server updates).
#

from src.settings_default import * 

###################################################
# Evennia base server config 
###################################################

###################################################
# Evennia Database config 
###################################################
DATABASE_ENGINE = 'mysql'
DATABASE_NAME = 'evennia'
DATABASE_USER = 'muduser'
DATABASE_PASSWORD = 'muSHmud*'
DATABASE_HOST = 'localhost'
DATABASE_PORT = '3306'

DATABASES = {
    'default':{
        'ENGINE':'django.db.backends.mysql',
        'NAME':'evennia',
        'USER':'muduser',
        'PASSWORD':'muSHmud*',
        'HOST':'localhost',
        'PORT':'3306'
        }}

###################################################
# Evennia in-game parsers
###################################################
SERVERNAME = "Avaloria"
###################################################
# Default command sets 
###################################################
CMDSET_OOC = "game.gamesrc.commands.basecmdset.OOCCmdSet"
###################################################
# Default Object typeclasses 
##################################################
BASE_CHARACTER_TYPECLASS = "game.gamesrc.objects.world.character.CharacterClass"
CMDSET_UNLOGGEDIN = "contrib.menu_login.UnloggedInCmdSet"

###################################################
# Batch processor 
###################################################

###################################################
# Game Time setup
###################################################

###################################################
# Game Permissions
###################################################
#PERMISSION_PLAYERS_DEFAULT = "Builders"
###################################################
# In-game Channels created from server start
###################################################

###################################################
# IMC2 Configuration
###################################################

###################################################
# IRC config
###################################################

###################################################
# Config for Django web features
###################################################

###################################################
# Evennia components (django apps)
###################################################
