from game.gamesrc.scripts.basescript import Script


class LairSentinel(Script):
    """
    This script performs routine checks on the lair and structures
    in said lair.  This is where any sort of bonus that accrues over
    time (say gold_per_day from a gold mine strcuture).  Eventually
    this script will send notifications to the character that owns it
    in the event of a player attack on their lair among other things
    """

    def at_script_creation(self):
        self.key = 'lair_sentinel'
        self.desc = 'Makes routine checks on the character lair'
        self.persistent = True
        self.interval = 120
        self.start_delay = True
    
    def at_repeat(self):
        structure_manager = self.obj.search(self.obj.db.structure_manager_id, global_search=False)
        dungeon_manager = self.obj.search(self.obj.db.dungeon_manager_id, global_search=False)
        character = self.obj.search(self.obj.db.owner, global_search=False)
        
        if structure_manager.db.already_built is not None:
            for structure in structure_manager.db.already_built.split(';'):
                if 'Gold Mine' in structure:
                    lair_gold_mine = structure_manager.search('Gold Mine', location=self.obj, global_search=False)
                    if 'Under Construction' in lair_gold_mine.name:
                        return
                    character.award_gold(lair_gold_mine.db.gold_per_day, from_structure=lair_gold_mine)
                
    def is_valid(self):
        return True
            
