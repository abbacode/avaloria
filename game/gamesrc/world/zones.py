#HEADER
from src.utils import create, search
from game.gamesrc.objects.world.rooms import Zone


#CODE (Tutorial)
zone = create.create_object(Zone, key="Tutorial Zone Object")
zone.aliases = ['zone_runner']
zone.db.zone_name = "Tutorial Area"
zone.db.zone_type = 'tutorial'
zone.db.quest_items = ["Training Manual", "Spell Tome"]
zone.db.enemy_npcs = ["Battle Dummy"]
zone.db.mobs_spawn = False
zone.refresh_mg_dungeon_type()
zone.generate_zone_path()
zone.spawn_enemy_npcs()
#CODE (Marshlands)
zone = create.create_object(Zone, key="Marshlands Zone Object")
zone.aliases = ['zone_runner']
zone.db.zone_name = "Marshlands"
zone.db.quest_items = ['Family Heirloom']
zone.db.enemy_npcs = ['Synesh Algreense']
zone.db.mobs_spawned = False
zone.generate_zone_path() #actually sets up the room path.
zone.spawn_enemy_npcs()
#zone.cleanup()
