from ev import Room, Object
from src.utils import create, search, utils
import random, string

class PlayerLairExit(Object):
    """
    This room type will be attached directly to the player's lair room.
    When this room is added, it will generate a random layout
    of rooms to reach 'The crossroads'.  The crossroads will serve as central hub
    that all players funnel in to at the end of their starting quests.
    """

    def at_object_creation(self):
        self.name = "Portal: The Crossroads"
        self.aliases = ['portal', 'Portal', 'PORTAL']
        self.db.desc = "A swirling, purple-white portal.  You can just barely hear the voices of those on the other side."

    def on_use(self, caller):
        crossroads = self.search('The Crossroads', global_search=True)
        caller.msg("{CYou step through the portal.{n")
        caller.move_to(crossroads)
        caller.msg("{CYou arrive in The Crossroads.{n")


                


class DungeonRoom(Room):
    """
    This represents the generic dungeon Room object used to create most
    of the rooms in the game world.  It sets the at_object_receive and
    at_object_leave() hooks to update the player map on the zone manager
    which is used behind the scenes for multiple things. 
    """

    def at_object_creation(self):
        self.db.level = None
        self.db.quest_item_spawned = False
    
    def at_object_receive(self, moved_obj, source_location):
        if moved_obj.has_player:
            manager = self.db.manager
            if manager is None:
                return
            player_map = manager.db.player_map
            player_map["%s" % moved_obj.name] = self.db.cell_number
            manager.db.player_map = player_map
            self.db.manager = manager
        self.post_object_receive(caller=moved_obj)

    def post_object_receive(self,caller):
        for item in self.contents:
            if hasattr(item, 'mob_type'):
                item.db.should_update = True
            if hasattr(item, 'actions'):
                item.interact(caller, action='greeting')

    def at_object_leave(self, moved_obj, target_location):
        manager = self.db.manager
        if manager is None:
            return
        if moved_obj.has_player:
            player_map = manager.db.player_map
            try:
                del player_map[moved_obj.name]
            except KeyError:
                pass
            manager.db.player_map = player_map
            self.db.manager = manager
        if self.db.cell_number not in manager.db.player_map.keys():
            for item in self.contents:
                if hasattr(item, 'mob_type'):
                    item.db.should_update = False
                    if hasattr(item, 'actions'):
                        action = random.choice(['taunt', 'mock'])
                        item.interact(moved_obj, action)
            
            

class Woodlands(Room):
    """
    A generic woodland room.
    """ 
    
    def at_object_creation(self):
        self.aliases = ['woodlands']
        self.db.spawn_mobs = False
        self.db.hidden_treasure  = False


class DarkRoom(DungeonRoom):
    """
    A room with no light source, which causes the player to be unable to see
    until a torch is lit.
    """
    def at_object_creation(self):
        DungeonRoom.at_object_creation(self)
        self.db.spawn_mobs = True
        self.db.hidden_treasure = True
        self.db.player_map = {}
        self.db.dungeon_type = 'dungeon'
        self.db.is_lit = False
        self.scripts.add("game.gamesrc.scripts.world_scripts.dungeon_scripts.DarkState")
         
    def is_lit(self):
        """
        Checks for a lightsource on all characters in the room.
        """
        return any([any([True for obj in char.contents 
                        if utils.inherits_from(obj, "game.gamesrc.objects.world.items.LightSource") and obj.is_active]) 
                for char in self.contents if char.has_player])
    
    def at_object_receive(self, character, source_location):
        if not self.is_lit():
            character.cmdset.add("game.gamesrc.commands.world.character_cmdset.DarkCmdSet")
        self.scripts.validate()              
        
    def at_object_leave(self, character, source_location):
        character.cmdset.delete("game.gamesrc.commands.world.character_cmdset.DarkCmdSet")
        self.scripts.validate()

class MarshLand(DungeonRoom):
    """
    A generic marshlands room.  this comprises one piece of the marshlands zone
    """

    def at_object_creation(self):
        DungeonRoom.at_object_creation(self)
        self.aliases = ['marshlands']
        self.db.spawn_mobs = True
        self.db.hidden_treasure = True
        self.db.player_map = {}
        self.db.dungeon_type = 'marshlands'
        


class Zone(Object):
    """
    Management object for rooms.  Not shown to players, purely used for certain
    behind the scenes need (like mob pathfinding).  Basically all rooms in a zone
    are contained within the zone object.  This will allow the zone object to act
    as a management object from which mobs can be spawned, addtional rooms can be 
    added etc etc.
    """
    def at_object_creation(self):
        self.db.zone_name = None
        self.aliases = ['zone_manager']
        self.db.enemy_npcs = []
        self.db.map = {}
        self.db.path_map = {}
        self.db.grid_size = None
        self.db.valid_zones = ['dungeon', 'woodlands', 'marshlands']
        self.db.zone_type = 'marshlands'
        self.db.player_map = {}
        self.db.quest_items = []
        labels = string.ascii_uppercase
        self.db.x_axis_labels = list(labels)
        self.db.y_axis_labels = [x for x in range(0, len(self.db.x_axis_labels))]
        mob_generator = create.create_object("game.gamesrc.objects.world.generators.MobGenerator", key="%s mob_gen" % self.name)
        mob_generator.location = self
        mob_generator.db.dungeon_type = self.db.zone_type
        self.db.is_dungeon = False
        self.db.mob_generator = mob_generator
        self.set_zone_level()


    def find_by_cell(self, cell):
        map = self.db.path_map
        for key,value in map.items():
            if key == cell:
                return value

    def spawn_enemy_npcs(self):
        for npc in self.db.enemy_npcs:
            object = self.search('%s' % npc, global_search=True)
            rooms = self.search('%s_enemy_npc_spawn' % self.db.zone_type, global_search=True, ignore_errors=True)
            if rooms is None:
                return
            room = random.choice(rooms)
            copy = object.copy()
            copy.aliases = ['reanimator', 'mob_runner']
            copy.name = object.name
            copy.move_to(room, quiet=True)
            
    def spawn_quest_items(self):
        try:
            storage = self.search('storage', global_search=True, ignore_errors=True)[0]
        except:
            return

        spawn_rooms = self.search('%s_quest_item_spawn' % self.db.zone_type, global_search=True, ignore_errors=True)
        print "spawn_rooms list: %s " % spawn_rooms
        for room in spawn_rooms:
            if room not in self.db.path_map.values():
                print "removing %s" % room
                spawn_rooms.remove(room)

        for item in self.db.quest_items:
            obj = storage.search('%s' % item, global_search=False, ignore_errors=True)[0]
            if type(spawn_rooms) == type(list()):
                room = random.choice(spawn_rooms)    
            else:
                room = spawn_rooms
            if item not in [ object.name for object in room.contents ]:
                obj_copy = obj.copy()
                obj_copy.name = obj.name
                obj_copy.move_to(room, quiet=True)
            else:
                print "spawn logic not triggered"
        
    def generate_zone_path(self):
        path_map = self.db.path_map
        rooms = self.search('marshlands_room', global_search=True, ignore_errors=True)
        print rooms
        for room in rooms:
            path_map["%s" % room.db.cell_number] = room
            room.db.manager = self
        self.db.path_map = path_map

    def calculate_mob_levels(self):
        mobs = self.search("%s_mobs" % self.db.zone_type, global_search=True, ignore_errors=True)
        path_map = self.db.path_map
        counters = {}
        mob_map = {}
        for mob in mobs:
            cell = mob.location
            if cell is None:
                continue
            else:
                mob_map["%s" % mob.dbref] = cell
        for key in path_map:
            try:
                if key in self.db.mob_counters.keys() and key is not None:
                    try:
                        counters['%s' % key] += 1
                    except KeyError:
                        counters['%s' % key] = 1
                else:
                    print "No key in mob counters"
            except AttributeError:
                counters['%s' % key] = 0
        print "%s: %s" % (self.name, counters)
        for key in mob_map:
            try:
                counters['%s' % mob_map[key].db.cell_number] = counters['%s' % mob_map[key].db.cell_number] + 1
            except KeyError:
                counters['%s' % mob_map[key].db.cell_number] = 1
       
        print "%s: %s (counters)" % (self.name, counters )
        for counter in counters:
            print counters[counter]
            if counter is None:
                continue
            if int(counters[counter]) < 3:
                self.replenish_mobs(counter) 
    
        self.db.mob_map = mob_map
        self.db.mob_counters = counters
    
    def update(self):
        self.calculate_mob_levels()
        self.spawn_quest_items()

    def replenish_mobs(self, cell):
        rn = random.random()
        room = self.find_by_cell(cell)
        mg = self.db.mob_generator
        zone_lvl_split = self.db.zone_level.split(';')
        low_end = int(zone_lvl_split[0])
        high_end = int(zone_lvl_split[1])
        mg.db.level = self.db.zone_level
        num_mobs = random.randrange(3,7)
        mob_set = mg.generate_mob_set(num_mobs)
        
        print mob_set
        for mob in mob_set:
            if mob is None:
                print "normal mob gen failed somewhere"
                continue
            mob.move_to(room, quiet=True)
            room.msg_contents("You feel as if someone is watching you...")

        if self.db.is_dungeon is True:
            if room.db.last_room:
                mob = mg.generate_boss_mob()
                print "trying to move boss mob"
                mob.move_to(room, quiet=True)    
                self.db.mobs_spawned = True
        
        
        
    def set_zone_level(self):
        if self.db.zone_type == "marshlands":
            self.db.zone_level = "1;10"
        if self.db.zone_type == "crypt":
            self.db.zone_level = "1;5" 
        if self.db.zone_type == "ruins":
            self.db.zone_level = "2;7"
        
