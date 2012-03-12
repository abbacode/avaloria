import random
from src.utils import create, utils
from game.gamesrc.scripts.basescript import Script
from game.gamesrc.objects.world.generators import MobGenerator

class ZoneMobSpawner(Script):
    """
    put on zone rooms to spawn mobs for that particular zone.
    runs continually, replacing killed mobs as needed.
    """

    def at_script_creation(self):
        self.persistent = True
        self.key = 'zone_mob_spawner'
        self.desc = 'spawn mobs and keep em spawned'
        self.interval = 300


    def at_repeat(self):
        """
        roll a dice to see if mobs spawn in this room.
        if they do, pick a number (1-3) and spawn that many.
        flip boolean to true.
        continually monitor, once all mobs are gone, respawn.
        """
        self.obj.calculate_mob_levels()
        self.obj.spawn_quest_items()
            
