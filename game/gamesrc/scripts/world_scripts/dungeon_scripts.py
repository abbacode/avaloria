import random
from src.utils import create, utils
from game.gamesrc.scripts.basescript import Script



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
            if rn < .10:
                chest = create.create_object("game.gamesrc.objects.world.storage.StorageItem", key="Treasure Chest")
                chest.location = self.obj
                chest.generate_contents()
                self.db.chest_spawn_attempt = True
            else:
                self.db.chest_spawn_attempt = False
        
