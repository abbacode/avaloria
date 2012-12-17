from ev import Room
from game.gamesrc.scripts.world_scripts import structure_scripts as structure_scripts
import random
from prettytable import PrettyTable

class Lair(Room):
    """
    This is the player lair/base.  This is where the character will build up their
    structures, horde treasure, attract henchmen etc.  Eventually the lair will be used
    as a piece of the picture in the lair combat mechanic.
    """

    def at_object_creation(self):
        self.db.desc="A large cavernous room, as long and as wide as the eye can see. A good place to build an empire."
        self.db.attributes = { 'attraction': 0.15,'has_barracks': False, 'level': 1, 'defense_rating': 0, 'deity': None, 'gold_to_next_level': 200, 'gold_to_last_level': 200, 'gold_spent_this_level': 0, 'total_gold_spent': 0, 'attack_rating': 0, 'health': 500, 'temp_health': 500, 'action_points': 10}
        self.db.henchmen = {}
        self.db.available_henchman = []
        self.db.structures = {}
        self.db.level = 1
        self.db.gold_to_next_level = None
        self.db.gold_spent = None
        self.db.attribute_bonuses = {}
        self.db.character_attribute_bonuses = { 'last_strength': 0, 'last_dexterity': 0, 'last_intelligence': 0, 'last_constitution': 0, 'temp_strength': 0, 'temp_constitution': 0, 'temp_dexterity': 0, 'temp_intelligence': 0, 'temp_attack_rating': 0, 'temp_armor_rating': 0 }
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
        self.locks.add("edit:id(%s) or perm(Immortals);get:false();enter:id(%s)" % (self.db.owner.name, self.db.owner))


    def aggregate_character_bonuses(self):
        manager = self.search(self.db.structure_manager_id, global_search=False)
        cab = self.db.character_attribute_bonuses
        structs = manager.db.structures
        for struct in structs:
            struct_obj = structs[struct]
            for attr in struct_obj.db.attribute_bonuses:
                if struct_obj.db.attribute_bonuses[attr] == 1:
                    cab['temp_%s' % attr] += 1
                else:
                    cab['last_%s' % attr] = cab['temp_%s' % attr]
                    cab['temp_%s' % attr] += (struct_obj.db.attribute_bonuses[attr] - cab['temp_%s' % attr])
        self.db.character_attribute_bonuses = cab
        
    def apply_character_bonuses(self):
        cab = self.db.character_attribute_bonuses                 
        character = self.db.owner
        character_attributes = character.db.attributes
        print cab, character_attributes
        for attr in cab:
            if attr.startswith('last_'):
                continue
            if cab[attr] > 1:
                if character_attributes[attr] == character_attributes['%s' % attr.lstrip('temp_')]:
                    pass
                elif cab[attr] == cab['last_%s' % attr.lstrip('temp_')]:
                    character_attributes[attr] = character_attributes[attr] - cab[attr]
                else:
                    character_attributes[attr] = character_attributes[attr] - (cab[attr] - 1) 
                print character_attributes[attr], attr
            character_attributes[attr] += cab[attr]
            print character_attributes
        character.db.attributes = character_attributes
        
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
        owner = self.search(self.db.owner.name, global_search=True)
        attributes = self.db.attributes
        attributes['deity'] = owner.db.attributes['deity']
        self.db.attributes = attributes
 
    def level_up(self, zero_out=False):
        attributes = self.db.attributes
        owner = self.search(self.db.owner.name, global_search=False)
        attributes['level'] += 1
        attributes['health'] += int((attributes['health'] * .20))
        attributes['temp_health'] = attributes['health']
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
        """
        'afo' - this is the amount of the type of henchmen it takes to get the attribute_mod_amount
        """
        self.db.henchman_archtypes = ['Imp', 'Goblin', 'Ogre', 'Bandit', 'Hedge Wizards' ]
        henchmen = self.db.henchmen
        if archtype is not None:
            name = archtype
        else:
            name = random.choice(self.db.henchman_archtypes)
        print name
        if 'Imp' in name:
            henchman = { 'name': name, 'str': 5, 'dex': 25, 'con': 5, 'int': 10, 'health':15, 'mana': 20, 'count': 1 , 'attribute_mod': 'dexterity', 'attribute_mod_amount': 1, 'afo': 2}
        elif 'Goblin' in name:
            henchman = { 'name': name, 'str': 10, 'dex': 15, 'con':15, 'int': 5, 'health': 30, 'mana': 5, 'count': 1 , 'attribute_mod': 'defense', 'attribute_mod_amount': 1, 'afo': 2}
        elif 'Ogre' in name:
            henchman = { 'name': name, 'str': 30, 'dex': 5, 'con': 28, 'int': 2, 'health': 100, 'mana': 0, 'count': 1, 'attribute_mod': 'strength', 'attribute_mod_amount': 1, 'afo': 2}
        elif 'Bandit' in name:
            henchman = { 'name': name, 'str': 15, 'dex': 19, 'con': 18, 'int': 10, 'health': 40, 'mana': 10, 'count': 1, 'attribute_mod': 'constitution', 'attribute_mod_amount': 1, 'afo': 4}
        elif 'Hedge Wizards' in name:
            henchman = { 'name': name, 'str': 10, 'dex': 17, 'con': 15, 'int': 35, 'health': 30, 'mana': 70, 'count': 1, 'attribute_mod': 'intelligence', 'attribute_mod_amount': 1, 'afo': 2}
        henchmen[name] = henchman
        self.db.henchmen = henchmen

    def figure_available_henchman(self):
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        structures_built = structure_manager.db.already_built.split(';')
        avail_henchman = self.db.available_henchman
        if 'Gold Mine' in structures_built:
            avail_henchman.append('Imp')
        if 'Training Grounds' in structures_built:
            avail_henchman.append('Goblin')
        if 'Magi' in structures_built:
            avail_henchman.append('Hedge Wizards')
        if 'Treasury' in structures_built:
            avail_henchman.append('Ogre')
        if 'Alchemist' in structures_built:
            avail_henchman.append('Bandit')
        
        self.db.available_henchman = avail_henchman
            
    def attract_followers(self):
        attraction = self.db.attributes['attraction']
        character = self.search(self.db.owner.name, global_search=True)
        self.figure_available_henchman()
        low_level_range = "1,4"
        mid_level_range = "3,8"
        high_level_range = "6,12"


        rn = random.random()
        if rn <= attraction:
            choice = random.choice(self.db.available_henchman)
            try: 
                if choice not in self.db.henchmen.keys():
                    self.create_henchman(archtype=choice)
                    character.msg("{CYour lair has attracted a %s to your cause.{n" % choice)
                else:
                    if 'Imp' in choice:
                        structure = self.search('Gold Mine', global_search=False)
                    elif 'Goblin' in choice:
                        structure = self.search('Training Grounds', global_search=False)
                    elif 'Ogre' in choice:
                        structure = self.search('Treasury', global_search=False)
                    elif 'Hedge Wizards' in choice:
                        structure = self.search('Cave of Magi', global_search=False)
                    elif 'Bandits' in choice:
                        structure = self.search('Alchemist Lab', global_search=False)
                     
                    if structure.db.level <= 5:
                        split_list = low_level_range.split(',')
                    elif structure.db.level <= 10:
                        split_list = mid_level_range.split(',')
                    elif structure.db.level <= 15:
                        split_list = high_level_range.splt(',')

                    num_henchmen = random.randrange(int(split_list[0]), int(split_list[1]))
                    self.add_henchman(choice, num_henchmen)
                    if num_henchmen == 1:
                        character.msg("{CYour lair attracts another %s to your cause.{n" % choice)
                    else:
                        character.msg("{CYour lair attracts %s more %s to your cause.{n" % (num_henchmen, choice))
            except IndexError:
                print "Indexing Error"
                return
        
        self.db.available_henchman = []

    def assign_henchman(henchman, structure, quantity, caller):
        """
        assign's a given henchman to the given structure.
        
        lair_henchmen - represents the lair's view of the henchmen quantity levels.
        henchmen - represents the structures internal view of hechmen quantity levels.
        """
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        structure_obj = structure_manager.find(structure)
        lair_henchmen = self.db.henchmen
        if structure_obj:
            henchmen = structure_obj.db.assigned_henchmen
            if henchman['count'] < quantity:
                caller.msg("You do not have enough followers to assing that many.")
                return 
            if henchman['name'] in henchmen:
                henchmen[henchman['name']]['count'] += quantity
                lair_henchmen[henchman['name']]['count'] -= quantity
            else:
                henchmen[henchman['name']] = henchman
                henchmen[henchman['name']]['count'] = quantity
                lair_henchmen[henchman['name']]['count'] -= quantity
            structure_obj.db.assigned_henchmen = henchmen
            structure_obj.after_henchmen_assignment(henchmen[henchman['name']])
        else:
            return
            
    def display_summary(self, caller):
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        built_structures = structure_manager.db.already_built.split(';')
        owner = self.search(self.db.owner.name, global_search=True)
        msg = "{{CName:{{n {0:<20}{{COwner: {{n{1:<25}{{CLevel: {{n{2:<30}{{n\n".format(self.name, owner.name, self.db.attributes['level'])
        caller.msg(msg)
        msg = "{{GCurrent Structures: {{n{0:<100}{{n\n".format(built_structures)
        caller.msg(msg)
        if len(self.db.henchmen.keys()) < 1:
            caller.msg("{GHenchman:{n No Henchman.{n")
        else:
            caller.msg("{GHenchman:{n")
            for henchman in self.db.henchmen:
                print henchman
                msg = "{{G{0:<30}{{C{1:<15}{{n".format(self.db.henchmen[henchman]['name'], str(self.db.henchmen[henchman]['count']))
                caller.msg(msg)
        attribute_bonuses = self.db.attribute_bonuses
        msg = "\n{{GAttribute Bonuses:{{n {0:<60}{{n".format(attribute_bonuses)
        caller.msg(msg)
        
        
        
    def update(self):
        structure_manager = self.search(self.db.structure_manager_id, global_search=False)
        dungeon_manager = self.search(self.db.dungeon_manager_id, global_search=False)
        character = self.db.owner
        self.attract_followers()
        
        if structure_manager.db.already_built is not None:
            for structure in structure_manager.db.already_built.split(';'):
                if structure == ' ':
                    continue
                if 'Gold Mine' in structure:
                    lair_gold_mine = structure_manager.search('Gold Mine', location=self, global_search=False)
                    print structure
                    if 'Under Construction' in lair_gold_mine.name:
                        return
                    character.award_gold(lair_gold_mine.db.gold_per_day, from_structure=lair_gold_mine)

 
