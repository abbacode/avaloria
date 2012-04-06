from math import ceil
from src.utils import create, utils
from game.gamesrc.objects.baseobjects import Object

class Structure(Object):
    """
    This class is what represents the structures that characters
    can build in their lairs to give them bonuses and make them
    gold.
    """

    def at_object_creation(self):
        
        self.db.level = 0
        self.db.gold_per_day = None
        self.db.cost = None
        self.db.gold_put_in = 0
        self.db.gold_to_level = 50
        self.db.total_gold_spent = 0
        self.db.attribute_bonuses = {'strength': 0, 'dexterity': 0, 'constitution': 0, 'intelligence': 0}
        self.db.lair_attribute_bonuses = {}
        self.db.skill_bonuses = {}

    """
    Upkeep related functions
        destroy - destroys the structure and removes it from the manager.
        This will currently eat any gold put into the structure. TODO: make
        it not do that.
        award_gold - utility function to allow money to be put into the struct.
        withdraw_gold - take money out of the structure, gives it back to the character.
        de_level - remove a level.  can recurse to remove multiple levels.
        level_up - add a level + bonuses.
    """
    def destroy(self):
        manager = self.location.search(self.db.structure_manager_id, global_search=False)
        character = self.location.search(manager.db.character_id, global_search=False)
        already_built = ""
        #tickle the manager so it knows we got rid of this.
        for word in manager.db.already_built.split(';'):
            word = word.strip()
            if word in self.name:
                continue
            elif word is None:
                break
            else:
                already_built += "%s;" % word
        manager.db.already_built = already_built            
        character.msg("{bYou have destroyed: %s.{n" % self.name)    
        self.delete()

    def award_gold(self, gold_to_add):
        manager = self.location.search(self.db.structure_manager_id, global_search=False)
        character = self.location.search(manager.db.character_id, global_search=False)
        lair = character.db.lair
        lair.add_currency(int(gold_to_add))
        self.db.gold_put_in = int(self.db.gold_put_in) + int(gold_to_add)
        self.db.total_gold_spent = int(self.db.total_gold_spent) + int(gold_to_add)
        character.msg("{bYou have put forth {y%s{n {bgold towards the construction of %s" % (gold_to_add, self.name))
        if int(self.db.gold_put_in) >= int(self.db.gold_to_level):
            self.level_up()

    def withdraw_gold(self, gold_to_take):
        manager = self.location.search(self.db.structure_manager_id, global_search=False)
        character = self.location.search(manager.db.character_id, global_search=False)
        self.db.gold_put_in = int(self.db.gold_put_in) - int(gold_to_take)
        self.db.total_gold_spent = int(self.db.total_gold_spent) - int(gold_to_take)
        if self.db.gold_put_in <= 0:
            self.de_level()

    def de_level(self):
        manager = self.location.search(self.db.structure_manager_id, global_search=False)
        character = self.location.search(manager.db.character_id, global_search=False)
        if int(self.db.level) == 0:
            character.msg("{RThis structure is already at level 0, it can't go any lower.{n")
            return  
        self.db.level = int(self.db.level) - 1
        character.msg("{B%s has decreased in level.  It is now level:{n {y%s{n" % ( self.name, self.db.level))
        if self.db.gold_put_in < 0:
            excess_gold = (int(self.db.gold_put_in) * -1)
            self.db.gold_to_level = int(ceil(int(self.db.gold_to_level) * .9)) + 1
            self.db.gold_put_in = self.db.gold_to_level - excess_gold
            if self.db.gold_put_in >= self.db.gold_to_level :
                self.de_level()
            
    def level_up(self):
        manager = self.location.search(self.db.structure_manager_id, global_search=False)
        character = self.location.search(manager.db.character_id, global_search=False)
        self.db.level = int(self.db.level) + 1
        if self.db.gold_put_in > self.db.gold_to_level:
            self.db.gold_put_in = int(self.db.gold_put_in) - self.db.gold_to_level
        else:
            self.db.gold_put_in = 0
        increased_gold_req = int(ceil(int(self.db.gold_to_level) * .10))
        self.db.gold_to_level = int(self.db.gold_to_level) + increased_gold_req
        if self.db.level > 1:
            character.msg("{B%s just increased in level! It is now level: %s{n" % (self.name, self.db.level))
        else:
            self.name = '{B%s{n' % self.db.completed_name
            character.msg("{B%s has completed construction!{n" % self.name)
        if 'Gold Mine' in self.name:
            self.set_gold_per_day()

        
        attribute_bonuses = self.db.attribute_bonuses
        lair_attribute_bonuses = self.db.lair_attribute_bonuses
        for bonus in attribute_bonuses:
            if attribute_bonuses[bonus] != 0:
                attribute_bonuses[bonus] = attribute_bonuses[bonus] + 1
                character.msg("{G%s bonus is now +%s" % (bonus.title(), attribute_bonuses[bonus]))
        for bonus in lair_attribute_bonuses:
            if lair_attribute_bonuses[bonus] != 0:
                lair_attribute_bonuses[bonus] = lair_attribute_bonuses[bonus] + 1
                character.msg("{G%s lair bonuse is now +%s." % (bonus.title(), lair_attribute_bonuses[bonus]))
                
        self.db.attribute_bonuses = attribute_bonuses
        character_attributes = character.db.attributes
        lair_attributes = character.db.lair.db.attributes
        attribute_list = self.apply_attribute_bonuses(character_attributes, lair_attributes)
        print attribute_list
        character.db.attributes = attribute_list[0]
        character.db.lair.db.attributes = attribute_list[1]
        character.refresh_attributes()

    def set_gold_per_day(self):
        if 'Gold Mine' in self.name:
            if self.db.level >= 20:
                self.db.gold_per_day = 20
            elif self.db.level >= 17:
                self.db.gold_per_day = 17
            elif self.db.level >= 14:
                self.db.gold_per_day = 14
            elif self.db.level >= 11:
                self.db.gold_per_day = 11
            elif self.db.level >= 8:
                self.db.gold_per_day = 8
            elif self.db.level >= 5:
                self.db.gold_per_day = 5
            elif self.db.level >= 2:
                self.db.gold_per_day = 2

    def generate_attr_bonuses(self):
        if 'Gold Mine' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 0, 'intelligence': 0, 'constitution': 0 }
        elif 'Barracks' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 0, 'intelligence': 0, 'constitution': 0 }
            self.db.lair_attribute_bonuses = { 'has_barracks': True, 'attack_rating': 1, }
        elif 'Defenses' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 1, 'intelligence': 0, 'constitution': 0 }
            self.db.lair_attribute_bonuses = { 'defense_rating': 1}
        elif 'Training Grounds' in self.name:
            self.db.attribute_bonuses = { 'strength': 1, 'dexterity': 1, 'intelligence': 0, 'constitution': 0 }
        elif 'Cave of Magi' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 0, 'intelligence': 1, 'constitution': 0 }
        elif 'Alchemist Lab' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 0, 'intelligence': 1, 'constitution': 1 }
        elif 'Treasury' in self.name:
            self.db.gold_per_day = 10
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 0, 'intelligence': 0, 'constitution': 0 }
        elif 'Reinforced Doors' in self.name:
            self.db.attribute_bonuses = { 'strength': 0, 'dexterity': 1, 'intelligence': 0, 'constitution': 1 }
        else:
            pass
    
    def apply_attribute_bonuses(self, character_attributes, lair_attributes):
        """
        This method should properly massage structure bonuses on to the character model.
        Right now I have no earthly idea what its doing or why its doing it.  Seems to be
        a relic from a quick stand up to just get things function to a point.
        """
        for ab in self.db.attribute_bonuses:
            if self.db.attribute_bonuses[ab] > 1:
                character_attributes[ab] = character_attributes[ab] - (self.db.attribute_bonuses[ab] -1 )
            character_attributes[ab] = character_attributes[ab] + self.db.attribute_bonuses[ab]
        for ab in self.db.lair_attribute_bonuses:
            if self.db.lair_attribute_bonuses[ab] > 1:
                lair_attributes[ab] = lair_attributes[ab] - (self.db.lair_attribute_bonuses[ab] - 1)
            lair_attributes[ab] = lair_attributes[ab] + self.db.lair_attribute_bonuses[ab]
        return [character_attributes, lair_attributes]
            
    def at_inspect(self, looker):
        msg="""
{bStructure Inspection Details:{n
------------------------------------

Name: %s
Level: {b%s{n
Total Gold Spent: {y%s{n
Gold to Level: {y%s{n
Gold spent towards level: {y%s{n
Gold Per Day: {y%s{n
Attribute Bonuses:
%s
------------------------------------
        """ % (self.name, self.db.level, self.db.total_gold_spent, self.db.gold_to_level, self.db.gold_put_in, self.db.gold_per_day, self.db.attribute_bonuses)
        looker.msg(msg)

#BEGIN STRUCTURE MANAGER DECLARATION    
class StructureManager(Object):
    """
    This object is what is responsible for interfacing with the character
    and allows the characters to build structures in their lair.  This will
    be a permanent addition to their Lair room object.
    Main variables:
        self.db.valid_structures - a list of the currently available
        structures in the game, used for validation of use input.
        self.db.base_prices - a dictionary with the buildings from valid_structures
        and their beginning price.
        self.db.already_built - a ';' delimited string of structures already
        built in the lair.

    This object controls all aspects of building/destroying and maintaining
    structures that characters create.
    """
    def at_object_creation(self):
        self.desc = "You see a large, red stone gripped by an talon-like Pedestal.  As you look at the object, you hear it's voice warmly invite you to touch it."
        self.db.valid_structures = ['Gold Mine', 'Defenses', 'Reinforced Doors', 'Barracks', 'Training Grounds', 'Cave of Magi', 'Throne Room',
                                    'Alchemist Lab', 'Topside Portal', 'Treasury', 'Merchant Stalls', 'Outpost', 'Torture Pit', 'Soul Magnet' ]
        self.db.base_prices = { 'Gold Mine': 100, 'Defenses': 25, 'Reinforced Doors': 25, 'Barracks': 150, 'Training Grounds': 200, 'Cave of Magi': 500, 'Throne Room': 1000, 'Alchemist Lab': 650, 'Topside Portal': 1250, 'Treasury': 2000, 'Merchant Stalls': 450, 'Outpost': 500, 'Torture Pit': 2500, 'Soul Magnet': 4000 }
        self.db.already_built = "" 
    
    #generate necessary ids for relationships and set locks.    
    def gen_ids(self):
        lair = self.location.search(self.db.lair_id, global_search=True)
        lair.structure_manager_id=self.dbref
        self.db.character_id = lair.db.owner
        self.character = self.location.search(self.db.character_id, global_search=True)
        self.locks.add("edit:id(%s);get:none()" % self.character.dbref)

    #display a list of things we can build, excluding what we already have.
    def show_buildable_list(self):
        message = "{gCurrent Buildable Structures:{n"
        self.character.msg(message)
        m = "{b---------------------------------{n\n"
        for struct in self.db.valid_structures:
            try:
                already_done = self.db.already_built.index(struct)
            except ValueError:
                m += '{{b{0:<20}{{n {{yCost: {1:<15}{{n\n'.format(struct, self.db.base_prices[struct])
                continue    
        self.character.msg(m)
        m = "{b---------------------------------{n"
        self.character.msg(m)

    #display a list of structures already built.  Uses the already_built string on the manager. 
    def show_already_built(self):
        self.character.msg("{gStructures you have built:{n")
        m = "{b---------------------------------{n"
        self.character.msg(m)
        m = ""
        for structure in self.db.already_built.split(';'):
            obj = self.location.search(structure, global_search=False)
            if obj is None:
                break
            m += '{{b{0:<20}{{n {{yLevel: {1:<15}{{n\n'.format(structure, obj.db.level)
        self.character.msg(m)
        m = "{b---------------------------------{n"
        self.character.msg(m)

    def begin_construction(self, gold_to_start, structure):
        """
        This is the main construction method.  It sets all relevant fields, updates
        the character gold pool, takes into account if we level to level 1 right away
        and also holds all validation checks for whether the user supplied us with bunk
        information.  I.E tries to build something not allowed etc.
        The basic break down of operations is:
            1.) Check to see if the structure wanting to be built is valid (using 
                self.db.valid_structures list.
            2.) Check to see if we have already built it, if we have let the player know.
            3.) Check to see if the character has enough gold to even perform the initial
                construction.
            4.) Spend the characters gold, create the object and set all necessary
                structure fields such as location and name.
            5.) Award the structure gold and then figure out if its level 1 or 0 after.
            6.) Let the character know whether constructure has begun, or its be completed.
        """

        valid = False
        self.struct_name = None
        gold_to_start = int(gold_to_start)
        
        #check if the structure passed is valid
        for item in self.db.valid_structures:
            if structure in item:
                valid = True
                self.struct_name = item
                break
            else:
                continue
        
        if valid is not True:
            self.character.msg("{rThe structure you want to build doesn't exist in Avaloria!{n")
            return
        
        #check if we have already built it. 
        already_built = False
        if structure in self.db.already_built:
            already_built = True    
        
        if already_built is True:
            self.character.msg("{bLooks like you built this already, maybe try dumping money into it and leveling it up?{n")
            return

        #check if the character has enough money.   
        if int(self.character.db.attributes['gold']) < gold_to_start:
            self.character.msg("{rYou do not have enough gold to put {y%s{n {rgold into this building's construction!{n"    % gold_to_start)
            return

        self.character.spend_gold(gold_to_start)
        structure = create.create_object("game.gamesrc.objects.world.structures.Structure", key="{rUnder Construction: %s{n" % self.struct_name)
        structure.aliases = [ self.struct_name ]
        structure.db.completed_name = self.struct_name
        self.db.already_built += "%s;" % self.struct_name
        self.character.msg("{bBegan construction of the:{n {r%s{n!" % self.struct_name)
        structure.location = self.location
        structure.db.cost = self.db.base_prices[self.struct_name]
        structure.db.gold_to_level = structure.db.cost
        structure.db.structure_manager_id = self.dbref
        structure.award_gold(gold_to_start)
        self.post_construction(structure)
        if structure.db.level > 0:
            structure.key = "{b%s{n" % self.struct_name

    def post_construction(self, structure):
        if 'Mine' in structure.name:
            structure.db.desc = "A small mineshaft with a mine cart outside of it.  Looks like some sort of small creature could operate it."
            structure.db.desc += " There are small glints of gold within the shaft itself."
            structure.db.gold_per_day = 1
            structure.generate_attr_bonuses()
        elif 'Defenses' in structure.name:
            structure.db.desc = "Every corner of the lair is fortified, walls are stronger against break-in."
            structure.generate_attr_bonuses()
        elif 'Barracks' in structure.name:
            structure.db.desc = "This large building has large spires on either side of a massive wooden doorway."
            structure.db.desc += "This structure allows for the recruitment of henchmen or minions"
            structure.generate_attr_bonuses()
        elif 'Reinforced Doors' in structure.name:
            structure.db.desc = "The doors exiting your lair are completely reinforced, making it difficult to get in."
            structure.generate_attr_bonuses()
        elif 'Training Grounds' in structure.name:
            structure.db.desc = "A large pit that is clearly used for sparring and battles to the death."
            structure.generate_attr_bonuses()
        elif 'Topside Portal' in structure.name:
            structure.db.desc = "A portal to the world of men above you."
            structure.generate_attr_bonuses()
        elif 'Throne Room' in structure.name:
            structure.db.desc = "A room dedicated to your magnificence."
            structure.generate_attr_bonuses()
        elif 'Treasury' in structure.name:
            structure.db.desc = "A large room dug out of the cavernous walls to hold your gold."
            structure.generate_attr_bonuses()
        else:
            pass
        
        character_attributes = self.character.db.attributes
        lair_attributes = self.character.db.lair.db.attributes
        attribute_list = structure.apply_attribute_bonuses(character_attributes, lair_attributes)
        questmanager = self.character.db.quest_log
        questmanager.check_quest_flags(item=self) 
        self.character.db.attributes = attribute_list[0]
        self.character.db.lair.db.attributes = attribute_list[1]
        self.character.refresh_attributes()

class DungeonManager(Object):
    """
    Manages dungeons built by the DungeonGenerator
    """
    def at_object_creation(self):
        self.db.level = 1
        self.db.desc = "A Large circular stone archway, with runes etched across the outside of it."
        self.locks.add("get:none()")
        self.db.dungeon = []

    def create_dungeon(self):
        generator = self.db.generator
        generator.generate_rooms()
    
    def on_use(self,caller):
        self.location.msg_contents("{rAs you touch the glowing red stone, a portal begins to emerge..{n")
        utils.run_async(self.create_dungeon)
        self.location.msg_contents("{bA glowing red portal swirls into existence.{n")

    def delete_previous_dungeon(self):
        dungeon = self.db.dungeon
        for room in dungeon:
            room.delete()
        self.db.dungeon = []
