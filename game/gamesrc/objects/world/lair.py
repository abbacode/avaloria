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


    def aggregate_lair_bonuses(self):
        pass

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
            character_attributes[attr] += cab[attr]
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
        print "Successfully created a henchman"

    def figure_available_henchman(self):
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        structures_built = structure_manager.db.already_built.split(';')
        avail_henchman = self.db.available_henchman
        if 'Gold Mine' in structures_built:
            avail_henchman.append('Imp')
        if 'Training Grounds' in structures_built:
            avail_henchman.append('Goblin')
        if 'Cave of Magi' in structures_built:
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
        print "through figuring henchmen"
        print self.db.available_henchman
        low_level_range = "1,4"
        mid_level_range = "3,8"
        high_level_range = "6,12"
        print "level ranges committed"


        rn = random.random()
        print "checking attraction"
        if rn > attraction and len(self.db.available_henchman) > 0:
            choice = random.choice(self.db.available_henchman)
            print "attraction triggered."
            try: 
                if choice not in self.db.henchmen.keys():
                    print "Creating a new henchmen"
                    self.create_henchman(archtype=choice)
                    character.msg("{CYour lair has attracted a %s to your cause.{n" % choice)
                else:
                    print "finding structure to figure levels"
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
                    print "levels found"
                    num_henchmen = random.randrange(int(split_list[0]), int(split_list[1]))
                    self.add_henchman(choice, num_henchmen)
                    if num_henchmen == 1:
                        character.msg("{CYour lair attracts another %s to your cause.{n" % choice)
                    else:
                        character.msg("{CYour lair attracts %s more %s to your cause.{n" % (num_henchmen, choice))
            except IndexError:
                print "Indexing Error"
                return
        else:
            print "attraction not triggered"
        
        self.db.available_henchman = []

    def assign_henchman(self, henchman, structure, quantity, caller):
        """
        assign's a given henchman to the given structure.
        
        lair_henchmen - represents the lair's view of the henchmen quantity levels.
        henchmen - represents the structures internal view of henchmen quantity levels.
        """
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        structure_obj = structure_manager.find(structure)
        lair_henchmen = self.db.henchmen
        quantity = int(quantity)
        if structure_obj:
            henchmen = structure_obj.db.assigned_henchmen
            if int(henchman['count']) < int(quantity):
                caller.msg("You do not have enough followers to assign that many.")
                return 
            if henchman['name'] in henchmen:
                henchmen_count = henchmen[henchman['name']]['count']
                henchmen_count = int(henchmen_count)
                henchmen_count += quantity
                henchmen[henchman['name']]['count'] = henchmen_count
                structure_obj.db.assigned_henchmen = henchmen
                lair_henchmen_count = lair_henchmen[henchman['name']]['count']
                lair_henchmen_count = int(lair_henchmen_count)
                lair_henchmen_count -= quantity
                lair_henchmen[henchman['name']]['count'] = lair_henchmen_count
                self.db.henchmen = lair_henchmen
            else:
                henchmen[henchman['name']] = henchman
                lair_henchmen_count = henchman['count']
                henchmen[henchman['name']]['count'] = quantity
                structure_obj.db.assigned_henchmen = henchmen
                caller.msg(henchmen)
                #lair_henchmen_count = henchman['count']
                caller.msg(lair_henchmen_count)
                lair_henchmen_count = int(lair_henchmen_count)
                lair_henchmen_count = lair_henchmen_count - quantity
                caller.msg(lair_henchmen)
                caller.msg(lair_henchmen_count)
                lair_henchmen[henchman['name']]['count'] = lair_henchmen_count
                self.db.henchmen = lair_henchmen
            structure_obj.after_henchmen_assignment(henchmen[henchman['name']])
            caller.msg(lair_henchmen)
            caller.msg("{CYou have successfully assigned %s %s to the %s.{n" % (quantity, henchman['name'], structure_obj.name))
        else:
            return
            
    def unassign_henchman(self, henchman, structure, quantity, caller):
        """
        unassign a henchman or hechmen from the given structure
        """
        structure_manager = self.search(self.structure_manager_id, global_search=False)
        structobj = structure_manager.find(structure)
        lair_henchmen = self.db.henchmen
        quantity = int(quantity)
        if structobj:
            henchmen = structobj.db.assigned_henchmen
            if int(henchmen[henchman['name']]['count']) < quantity:
                caller.msg("{RYou can't unassign more henchmen than are assigned to %s.{n" % structobj.name)
                return
            try:
                henchmen_count = henchmen[henchman['name']]['count']
                henchmen_count = int(henchmen_count)
                henchmen[henchman['name']]['count'] = henchmen_count - quantity
                lair_henchmen_count = lair_henchmen[henchman['name']]['count']
                lair_henchmen_count = int(lair_henchmen_count)
                lair_henchmen[henchman['name']]['count'] = lair_henchmen_count + quantity
            except KeyError:
                caller.msg("{R%s is not assigned to %s.{n" % (henchman['name'], structobj.name))
                return
            structobj.db.assigned_henchmen = henchmen
            self.db.henchmen = lair_henchmen
            structobj.after_henchmen_assignment(henchmen[henchman['name']])
            caller.msg("{CYou have successfully unassigned %s %s back to your lair pool" % (quantity, henchman['name']))
        
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

    def display_henchmen(self, caller):
        """
        display detailed henchmen levels in the lair
        and managed structures.
        """ 
        table = PrettyTable(["Type", "Quantity", "Attributes"])
        table2 = PrettyTable(["Structure", "Henchmen Type", "Quantity"])
        struct_manager = self.search(self.structure_manager_id, global_search=False)
        struct_henchmen = {}
        lair_henchmen = self.db.henchmen
        structs = struct_manager.structures
        for struct in structs:
            struct_henchmen[struct] = structs[struct].db.assigned_henchmen
            print structs[struct].db.assigned_henchmen
        for struct in struct_henchmen:
            for h in struct_henchmen[struct]:
                table2.add_row([struct, struct_henchmen[struct][h]['name'], struct_henchmen[struct][h]['count']])
        for h in lair_henchmen:
            attributes = ["Str: %s" % lair_henchmen[h]['str'], "Con: %s" % lair_henchmen[h]['con'], "Dex: %s" % lair_henchmen[h]['dex'], "Int: %s" % lair_henchmen[h]['int']]
            table.add_row([h, lair_henchmen[h]['count'], attributes])

        caller.msg(table.get_string())
        caller.msg(table2.get_string())
        
        
    def update(self):
        print "Beginning run: %s" % self.dbref
        structure_manager = self.search(self.db.structure_manager_id, global_search=False)
        dungeon_manager = self.search(self.db.dungeon_manager_id, global_search=False)
        character = self.db.owner
        self.attract_followers()
        print 'Through attract followers'
        
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

 
