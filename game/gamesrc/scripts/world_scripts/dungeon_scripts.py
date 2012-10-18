import random
from src.utils import create, utils
from game.gamesrc.scripts.basescript import Script
from game.gamesrc.conf import config as avconfig

AVCONFIG = avconfig.config


class MobSpawner(Script):
    """
    This script is place on a DungeonRoom object upon creation and spawns 
    all the mobs for the particular room.
    """

    def at_script_creation(self):
        """
        Lets set some pertinent info
        """
        self.key = 'mob_spawner'
        self.persistent = True
        self.interval = 5
        self.desc = "Mob spawning Script"
        self.start_delay = True
        self.repeats = 1
        self.db.mobs_spawned = False

    def at_repeat(self):
        if self.db.mobs_spawned is False:
            number_of_mobs = random.randrange(1,4)
            utils.run_async(self.obj.spawn_mobs(number_of_mobs))
            self.db.mobs_spawned = True
            self.obj.scripts.validate()

    def is_valid(self):
        if self.db.mobs_spawned is False:
            return True
        else:
            return False

    def at_stop(self):
        mg = self.obj.db.mg
        if mg is not None:
            mg.delete()


class TreasureSpawner(Script):
    """
    Will determine what type of 'room loot' a dungeon room may or may not have
    """
    
    def at_script_creation(self):
        self.key = 'treasure_spawner'
        self.desc = 'i heard u like treasure'
        self.interval = 60
        
    def at_start(self):
        self.db.chest_spawn_attempt = False
        
    def at_repeat(self):
        rn = random.random()
        check = self.obj.search("Treasure Chest", global_search=False)
        if check is None:
            pass
        else:
            return
        
        if self.db.chest_spawn_attempt is False:
            if rn < AVCONFIG['chest_spawn_rate']:
                chest = create.create_object("game.gamesrc.objects.world.storage.StorageItem", key="Treasure Chest")
                chest.location = self.obj
                chest.generate_contents()
                self.db.chest_spawn_attempt = True
            else:
                self.db.chest_spawn_attempt = False
        
class DarkState(Script):
    """
    The darkness state is a script that keeps tabs on when 
    a player in the room carries an active light source. It places 
    a new, very restrictive cmdset (DarkCmdSet) on all the players
    in the room whenever there is no light in it. Upon turning on 
    a light, the state switches off and moves to LightState. 
    """
    def at_script_creation(self):
        "This setups the script"
        self.key = "darkness_state"
        self.desc = "A dark room"
        self.persistent = True         
        self.interval = 1

    def at_start(self): 
        "called when the script is first starting up."
        for char in [char for char in self.obj.contents if char.has_player]:
            if char.is_superuser:
                char.msg("You are Superuser, so you are not affected by the dark state.")
            else:   
                char.cmdset.add("game.gamesrc.commands.world.character_cmdset.DarkCmdSet")
            char.msg("The room is pitch dark! You are likely to be eaten by a Grue.")

    def is_valid(self):
        "is valid only as long as noone in the room has lit the lantern." 
        return  self.obj.is_lit()

    def at_stop(self):
        "Someone turned on a light. This state dies. Switch to LightState."
        for char in [char for char in self.obj.contents if char.has_player]:        
            char.cmdset.delete("game.gamesrc.commands.world.character_cmdset.DarkCmdSet")        
        self.obj.db.is_dark = False
        self.obj.scripts.add("game.gamesrc.scripts.world_scripts.dungeon_scripts.LightState")

class LightState(Script):
    """
    This is the counterpart to the Darkness state. It is active when the lantern is on.
    """
    def at_script_creation(self):
        "Called when script is first created."
        self.key = "tutorial_light_state"
        self.desc = "A room lit up"
        self.persistent = True 
        self.interval = 1

    def is_valid(self):
        "This state is only valid as long as there is an active light source in the room."        
        return self.obj.is_lit()

    def at_stop(self):
        "Light disappears. This state dies. Return to DarknessState."        
        self.obj.db.is_dark = True
        self.obj.scripts.add(DarkState)

