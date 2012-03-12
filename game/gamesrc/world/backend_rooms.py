#HEADER
from src.utils import create, search

#CODE (create the backend room that contains all items in the game)
room = create.create_object("game.gamesrc.objects.baseobjects.Room", key="storage", aliases=["items"])
caller.msg("Backend Room created, id: %s" % room.dbref)

room = create.create_object("game.gamesrc.objects.baseobjects.Room", key="blackhole", aliases=["trash"])
room.scripts.add("game.gamesrc.scripts.world_scripts.backend_scripts.TrashMan")
caller.msg("Blackhole Room created, id: %s" % room.dbref)

#CODE (Creating the crossroads)
xroads = create.create_object('game.gamesrc.objects.baseobjects.Room', key='The Crossroads', aliases=['xroads'])
x_desc = "In a large, man made clearing all the paths coverge into one giant crossroads.  This area is a new\n "
x_desc += "addition to the landscape of Avaloria.  As the world resources that propel the various nations to\n "
x_desc += "an uncertain future dwindle, more and more people are showing up here at these crossroads to trade\n "
x_desc += "swap rumors, and share stories.  It has only been in the past 50 or so years that the races even\n "
x_desc += "began to mingle with one another. There is a sense of change in the air, and you are not the only\n "
x_desc += "who notices."
xroads.desc = x_desc
blacksmith = create.create_object("game.gamesrc.objects.baseobjects.Room", key="Hammer and Anvil", aliases=['crossroads_shops'])
desc = "From the outside, the building is fairly rudimentary and unimpressive.  It is nothing more then a hastily constructed log\n"
desc += "cabin with a freshly skinned animal hide serving as a doorway.  From inside the building notice the unmistakenable\n"
desc += " glow of an anvil fire.  This would be the place to buy arms and armor.\n"
blacksmith.desc = desc
exit_from_xroads = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Hammer and Anvil", location=xroads, destination=blacksmith)
exit_to_x_roads = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Crossroads", location = blacksmith, destination=xroads)

herbalist = create.create_object("game.gamesrc.objects.baseobjects.Room", key="Henry's Herbs", aliases=['crossroads_shops'])
desc = "Outside this shop there are rows and rows of potted plants and freshly cleaned flasks behind a small fence.\n"
desc += "Inside the building is a small service area and a doorway to the back room where small operations may be performed.\n"
desc += "A small hunched over old man sits behind the service counter."
herbalist.desc = desc

exit_from_xroad = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Henry's Herbs", location=xroads, destination=herbalist)
exit_to_x_roads = create.create_object("game.gamesrc.objects.baseobjects.Exit", key="Crossroads", location=herbalist, destination=xroads)

