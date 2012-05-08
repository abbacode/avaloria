from ev import Room

class DungeonRoom(Room):
    """
    This represents the generic dungeon Room object used but the dungeon
    generation object to create rooms with.
    """

    def at_object_creation(self):
        self.db.level = None
        self.db.last_room = False
#        mob_generator = create.create_object("game.gamesrc.objects.world.generators.MobGenerator", key="%s mob_generator" % self.name)
#        mob_generator.location = self
#        mob_generator.locks.add("view:none()")
 #       self.db.mg = mob_generator


    def spawn_mobs(self, number_of_mobs):
        """
        Function used by the Spawning script to spawn mobs in the rooms created
        for dungeons.
        """ 
        mg = self.db.mg
        mg.db.level = self.db.level
        mg.db.dungeon_type = self.db.dungeon_type
        mob_set = mg.generate_mob_set(number_of_mobs)
        for mob in mob_set:
            mob.location = self
        if self.db.last_room is True:
            boss = mg.generate_boss_mob()
            boss.location = self
            

         


        
