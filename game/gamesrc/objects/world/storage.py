import random
from src.utils import create
from game.gamesrc.objects.baseobjects import Object
from game.gamesrc.scripts.world_scripts import storage_scripts
from game.gamesrc.objects.world.items import *
from game.gamesrc.objects.world.generators import LootGenerator
from game.gamesrc.commands.world import character_cmdset

class StorageItem(Object):
    """
    A generic storage item class that will hold all functions/data for storage
    items within the game.
    """
    def at_object_creation(self):
        blackhole = self.search("blackhole", global_search=True)
        self.home = blackhole
        self.locks.add("open:all()")
        self.db.capacity = 3
        self.db.is_locked = False
        self.db.desc = "Some sort of storage object, its features yet undefined"
        self.db.lock_strength = 'easy'
        self.db.is_open = False
        self.generate_contents()
        
    def open_storage(self, caller):
        if self.db.is_open is True:
            caller.msg("%s is already open." % self.name)
            caller.msg("You see: %s" % self.db.content_names)
            return
        self.scripts.add(storage_scripts.OpenState)
        caller.cmdset.add(character_cmdset.ChestCommandSet)
        caller.msg("You open the %s, and have a look inside." % self.name)
        self.db.content_names = ', '.join(['%s' % i.name for i in self.contents])
        if len(self.db.content_names) <= 0:
            caller.msg("The chest is empty!")
            caller.cmdset.delete(character_cmdset.ChestCommandSet)
            return
        caller.msg("{bYou see:{n {g%s{n" % self.db.content_names)
        self.db.is_open = True

    def put_in_storage(self, caller, items):
        for item in items:
            item.move_to(self, quiet=True)
            caller.msg("{CYou store %s in the %s.{n" % (item.name, self.name))
        
    def close_storage(self, caller=None):
        if caller is not None:
            caller.cmdset.delete(character_cmdset.ChestCommandSet)
        self.location.msg_contents("%s shuts itself." % self.name)
        self.db.is_open = False
        self.scripts.validate()

    def generate_contents(self):
        loot_generator = create.create_object("game.gamesrc.objects.world.generators.LootGenerator", location=self)
        rn = random.random()
        if rn < .05:
            rare_item  = loot_generator.create_rare_lootset()
        else:
            rn = random.randrange(1,4)
            loot_set = loot_generator.create_loot_set(item_type='mixed', number_of_items=rn, loot_rating='average')
            for item in loot_set:
                item.move_to(self, quiet=True) 
        loot_generator.delete()
        
        
    def give_contents(self, caller):
        for item in self.contents:
            caller.msg_contents("%s looted a %s from the %s." % (caller.name, item.name, self.name))
            caller.msg("{bYou looted a{n {g%s{n {bfrom the %s.{n" % (item.name, self.name))
            item.move_to(caller, quiet=True)
        self.close_storage(caller)
            

        
        
