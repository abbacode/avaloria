#HEADER
from src.utils import create, search
from game.gamesrc.objects.world.rooms import Zone

#CODE (Marshlands)
zone = create.create_object(Zone, key="Marshlands Zone Object")
zone.aliases = ['zone_runner']
zone.db.zone_name = "Marshlands"
zone.db.enemy_npcs = ['Synesh Algreense']
zone.db.mobs_spawned = False
#zone.db.x_axis_labels = ['A', 'B', 'C', 'D', 'E']
#zone.db.y_axis_labels = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
#zone.generate_map(10) # 20 room grid
zone.generate_zone_path() #actually sets up the room path.
zone.spawn_enemy_npcs()
#zone.cleanup()
