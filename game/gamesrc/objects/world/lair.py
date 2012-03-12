from game.gamesrc.objects.baseobjects import Room
from game.gamesrc.scripts.world_scripts import structure_scripts as structure_scripts

class Lair(Room):
    """
    This is the player lair/base.  This is where the character will build up their
    structures, horde treasure, attract henchmen etc.  Eventually the lair will be used
    as a piece of the picture in the lair combat mechanic.
    """

    def at_object_creation(self):
        self.db.desc="A large cavernous room, as long and as wide as the eye can see. A good place to build an empire."
        self.db.attributes = { 'has_barracks': False, 'level': 1, 'defense_rating': 0, 'deity': None, 'gold_to_next_level': 200, 'gold_to_last_level': 200, 'gold_spent_this_level': 0, 'total_gold_spent': 0, 'attack_rating': 0 }
        self.db.henchmen = {}
        self.db.structures = {}
        self.db.level = 1
        self.db.gold_to_next_level = None
        self.db.gold_spent = None
        self.db.attribute_bonuses = {}
        self.db.owner = None
        self.db.structure_manager_id = None
        self.aliases = ['lair_runner']
        storage = self.search('storage', global_search=True, ignore_errors=True)[0]
        aspect = storage.search("Aspect of An'karith", global_search=False, location=storage, ignore_errors=True)[0]
        aspect_copy = aspect.copy()
        aspect_copy.name = aspect.name
        aspect.move_to(self, quiet=True)
        #self.scripts.add(structure_scripts.LairSentinel)
    
    def at_desc(self, looker):
        looker.msg("{bWelcome to your new home.  Check help for any concerns or questions{n")

    def generate_locks(self):
        self.locks.add("edit:id(%s) or perm(Immortals);get:false();enter:id(%s)" % (self.db.owner, self.db.owner))
        
    def add_currency(self, to_add):
        attributes = self.db.attributes
        attributes['total_gold_spent'] = attributes['total_gold_spent'] + to_add
        difference = attributes['gold_to_next_level'] - to_add
        if difference > 0:
            attributes['gold_to_next_level'] = difference
            attributes['gold_spent_this_level'] += to_add
            self.db.attributes = attributes
            return
        elif difference == 0:
            self.level_up(zero_out=True)
        else:
            self.level_up()
            attributes = self.db.attributes
            attributes['gold_spent_this_level'] = difference * -1
            attributes['gold_to_next_level'] = attributes['gold_to_next_level'] - attributes['gold_spent_this_level']
            self.db.attributes = attributes
       
    def set_deity(self):
        owner = self.search(self.db.owner, global_search=True)
        attributes = self.db.attributes
        attributes['deity'] = owner.db.attributes['deity']
        self.db.attributes = attributes
 
    def level_up(self, zero_out=False):
        attributes = self.db.attributes
        owner = self.search(self.db.owner, global_search=False)
        attributes['level'] += 1
        if zero_out:
            attributes['gold_spent_this_level'] = 0
        attributes['defense_rating'] += 1
        attributes['attack_rating'] += 1
        amount_to_add = int(attributes['total_gold_spent'] * .15)
        attributes['gold_to_next_level'] = attributes['gold_to_last_level'] + amount_to_add
        attributes['gold_to_last_level'] = attributes['gold_to_next_level']
        owner.msg("{CYour lair has reached level %s!" % attributes['level']) 
        self.db.attributes = attributes
 
    def add_henchman(self, henchman, count):
        henchmen = self.db.henchmen
        henchmen[henchman]['count'] += count
        self.db.henchmen = henchmen

    def update_henchman(self, henchman):
        henchmen = self.db.henchmen
        henchmen[henchman.name] = henchman
        self.db.henchmen = henchmen

    def create_henchman(self, archtype=None):
        self.db.henchman_archtypes = ['Imp', 'Goblin', 'Ogre', 'Bandit', 'Hedge Wizards' ]
        if archtype is not None:
            name = self.db.henchman_archtypes.find(archtype)
        if 'Imp' in name:
            henchman = { 'name': name, 'str': 5, 'dex': 25, 'con': 5, 'int': 10, 'health':15, 'mana': 20, 'count': 1 }
        elif 'Goblin' in name:
            henchman = { 'name': name, 'str': 10, 'dex': 15, 'con':15, 'int': 5, 'health': 30, 'mana': 5, 'count': 1 }
        elif 'Ogre' in name:
            henchman = { 'name': name, 'str': 30, 'dex': 5, 'con': 28, 'int': 2, 'health': 100, 'mana': 0, 'count': 1}
        elif 'Bandit' in name:
            henchman = { 'name': name, 'str': 15, 'dex': 19, 'con': 18, 'int': 10, 'health': 40, 'mana': 10, 'count': 1}
        elif 'Hedge Wizards' in name:
            henchman = { 'name': name, 'str': 10, 'dex': 17, 'con': 15, 'int': 35, 'health': 30, 'mana': 70, 'count': 1}
       
        
        
    def update(self):
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        dungeon_manager = self.search(self.db.dungeon_manager_id, global_search=False)
        character = self.search(self.db.owner, global_search=False)

        if structure_manager.db.already_built is not None:
            for structure in structure_manager.db.already_built.split(';'):
                if 'Gold Mine' in structure:
                    lair_gold_mine = structure_manager.search('Gold Mine', location=self, global_search=False)
                    if 'Under Construction' in lair_gold_mine.name:
                        return
                    character.award_gold(lair_gold_mine.db.gold_per_day, from_structure=lair_gold_mine)
 
