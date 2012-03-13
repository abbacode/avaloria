import random
import time
from collections import deque
from game.gamesrc.objects.baseobjects import Character, Object
from game.gamesrc.objects.world.items import Item
from game.gamesrc.scripts.world_scripts import character_class_scripts as cscripts
from game.gamesrc.scripts.world_scripts import combat_scripts as combat_scripts
from src.utils import utils, create
from game.gamesrc.objects.menusystem import *
from game.gamesrc.commands.world import character_cmdset as character_cmdset
from game.gamesrc.commands.world import combat_cmdset as combat_cmdset
from game.gamesrc.commands.world import structure_cmdset as structure_cmdset
from game.gamesrc.commands.world import skills as skills_cmdset
from game.gamesrc.commands.world import spells as spells_cmdset


class CharacterClass(Character):
    
    def at_object_creation(self):
        super(CharacterClass, self).at_object_creation()
        #attributes
        self.db.attributes = { 'name': '%s' % self.name, 'level': 1, 'strength': 5, 'dexterity': 5, 'intelligence': 5, 'constitution': 5} 
        attributes = self.db.attributes
        attributes['health'] = ((self.db.attributes['constitution'] * 2) + 25)
        attributes['mana'] = self.db.attributes['intelligence'] * 2
        self.db.attributes = attributes
        attributes['temp_health'] = self.db.attributes['health']
        attributes['temp_mana'] = self.db.attributes['mana']
        attributes['attack_rating'] = self.db.attributes['strength'] / 5
        attributes['armor_rating'] = (self.db.attributes['dexterity'] / 5) + 10
        attributes['balance'] = 3 
        attributes['temp_balance'] = 3
        attributes['attribute_points'] = 20
        attributes['gold'] = 0
        attributes['experience_made'] = 0
        attributes['experience_currency'] = 0
        attributes['experience_needed'] = 200
        attributes['experience_to_next_level'] = 200
        attributes['total_exp_made'] = 0
        attributes['attack_bonus'] = 0
        attributes['healing_bonus'] = 0
        attributes['race'] = None
        attributes['deity'] = None
        attributes['alignment'] = None
        self.db.attributes = attributes
        attributes['temp_attack_rating'] = self.db.attributes['attack_rating']
        attributes['temp_armor_rating'] = self.db.attributes['armor_rating']
        attributes['temp_dexterity'] = self.db.attributes['dexterity']
        attributes['temp_strength'] = self.db.attributes['strength']
        self.db.factions = { 'glade': 0, 'warden': 0, 'unknowns': 0, 'karith': 0, 'legion': 0, 'kaylynne': 0, 'molto': 0 }
        self.db.percentages = { 'constitution_bonus': 0.0, 'spell_damage_bonus': 0.0, 'melee_damage_bonus': 0.0, 'spell_fizzle_chance': 0.25, 'spell_buff_bonus': 0.0 }
        self.db.effects = {}
        self.db.group = None
        self.db.combat_queue = deque([])
        self.db.quest_flags = {}
        self.db.attributes = attributes
        self.db.equipment= { 'weapon': None, 'armor': None, 'shield': None, 'Neck': None, 'Left Finger': None, 'Right Finger': None, 'Back': None, 'Trinket': None}
        self.db.skills = []
        self.db.spells = []
        self.db.in_combat = False
        self.db.unbalanced = False
        self.db.target = None
        #player item creation
        lair = create.create_object("game.gamesrc.objects.world.lair.Lair", key="%s's Lair" % self.key)
        lair.db.owner = self.dbref
        self.db.lair = lair
        self.db.lair_id = lair.dbref
        self.home = lair
        self.location = lair
        starter_chest = create.create_object("game.gamesrc.objects.world.storage.StorageItem", key="Blessed Chest", location=lair)
        starter_chest.locks.add("open:holds(Deity Seal)")
        starter_chest.desc = "A medium sized chest with a very noticeable indendation where the locking mechanism would be.\n"
        starter_chest.desc += "Upon closer examination of the chest, you notice it is sealed with powerful magic." 
        training_manual_kick = create.create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Kick", location=starter_chest)
        training_manual_kick.db.skill = 'kick'
        training_manual_kick.db.level_requirement = 1
        self.db.prelogout_location = self.db.lair_id
        structure_manager = create.create_object("game.gamesrc.objects.world.structures.StructureManager", key="Stone Pedestal", location=self.location)
        dungeon_manager = create.create_object("game.gamesrc.objects.world.structures.DungeonManager", key="Stone Summoning Circle", location=self.location)
        dungeon_manager.db.lair_id = self.db.lair_id
        generator = create.create_object("game.gamesrc.objects.world.generators.DungeonGenerator", location=dungeon_manager, key="Pulsing Red Stone")
        generator.locks.add("get:none()")
        generator.manager = dungeon_manager
        dungeon_manager.db.generator = generator
        structure_manager.db.lair_id = self.db.lair_id
        structure_manager.gen_ids()
        lair.db.structure_manager_id = structure_manager.dbref
        questlog = create.create_object("game.gamesrc.objects.world.quests.QuestManager", key="Adventurer's Journal", location=self)
        questlog.db.character = self
        skill_log = create.create_object("game.gamesrc.objects.world.skills.SkillManager", key="Heavy Leather Tome", location=self)
        skill_log.db.character = self
        spellbook = create.create_object("game.gamesrc.objects.world.spells.SpellManager", key="Spellbook", location=self)
        spellbook.db.character = self
        self.db.spellbook = spellbook
        self.db.skill_log = skill_log
        self.db.quest_log = questlog
        #effect_manager = create.create_object("game.gamesrc.objects.world.spells.EffectManager", key="%s_effect_manager" % self.name, location=lair)
        #effect_manager.db.model = self
        #self.db.effect_manager = effect_manager
        player_lair_exit = create.create_object("game.gamesrc.objects.world.rooms.PlayerLairExit", location=lair)


    def character_summary(self):
        """
        Detailed output of a character.  The character sheet.
        """
        pass

    def at_object_receive(self, moved_obj, source_location):
        quest_log = self.db.quest_log
        if moved_obj.db.quest_item is not False:
            quest_log.check_quest_flags(mob=None, item=moved_obj)
           
    def at_post_login(self): 
        """
#        tutorial_npc = self.search("Weathered Old Man", global_search=False)
 #       if tutorial_npc is None:
  #          tutorial_npc = create.create_object("game.gamesrc.objects.world.npc.Npc", key="Weathered Old Man", location=self.db.lair)
   #         tutorial_npc.db.desc = "An old man whose face is weathered from years, upon years of life.  His hair is white, as are his eyes."
    #        tutorial_npc.db.target = self
     #       tutorial_npc.scripts.add("game.gamesrc.scripts.world_scripts.npc_scripts.TutorialNpc")
        """
        if self.db.in_combat is True:
            self.db.in_combat = False
            self.scripts.validate()

        if self.db.attributes['alignment'] is not None or self.id == 2:
            self.cmdset.add(character_cmdset.CharacterCommandSet)
            self.cmdset.add(combat_cmdset.DefaultCombatSet)
            self.cmdset.add(structure_cmdset.BuildCmdSet)
            self.cmdset.add(skills_cmdset.CombatSkillCmdSet)
            self.cmdset.add(spells_cmdset.SpellsCmdSet)
            self.scripts.validate()
            self.scripts.add(cscripts.CharacterSentinel)
            #self.scripts.add(cscripts.CharacterBuff)
        else:
#            self.scripts.add(cscripts.FirstLogin)
            self.scripts.add(cscripts.CharacterSentinel)
        #    self.scripts.add(cscripts.CharacterBuff)
        #prelogout_loc = self.search(self.db.prelogout_location, global_search=True)
        #self.location = prelogout_loc

    def at_disconnect(self):
        self.cmdset.clear()
        self.scripts.delete("character_sentinel")
        self.scripts.delete("character_first_login")
        self.scripts.delete("buff_sentinel")
   
    def at_first_login(self): 
        if self.dbref == 2:
            return
        storage = self.search('storage', global_search=True, ignore_errors=True)[0]
        aspect = storage.search("Aspect of An'Karith", global_search=False, location=storage, ignore_errors=True)[0]
        aspect_copy = aspect.copy()
        aspect_copy.name = 'Aspect of %s' % self.db.attributes['deity']
        aspect.move_to(self, quiet=True)
        aspect.do_dialog(caller=self, type='greeting')

    def refresh_attribute(self, attributes):
        """
        Called to change a single attribute, attributes being a dictionary
        Or potentially a single attribute string.
        """
        for attribute in attributes:
            if attribute == 'attributes':
                self.db.attributes = attributes['%s' % attribute]


    def refresh_attributes(self, health_and_mana=True, base_stats=False):
        """
        Called after stats have been modified.  Sets auxillary stats.
        """
        attributes = self.db.attributes
        percentages = self.db.percentages
        attributes['health'] = (self.db.attributes['constitution'] * 2) + 25
        if percentages['constitution_bonus'] != 0.0:
            bonus_health = int(attributes['constitution'] * percentages['constitution_bonus']) + 1
            attributes['health'] = attributes['health'] + bonus_health
        attributes['mana'] = self.db.attributes['intelligence'] * 2
        if health_and_mana:
            attributes['temp_health'] = self.db.attributes['health']
            attributes['temp_mana'] = self.db.attributes['mana']
        if base_stats is True:
            attributes['attack_rating'] = self.db.attributes['strength'] / 5
            attributes['armor_rating'] = (self.db.attributes['dexterity'] / 5) + 10
            if self.db.equipment['armor'] is not None:
                attributes['armor_rating'] += self.db.equipment['armor'].db.armor_rating
            self.db.attributes = attributes
        attributes['temp_dexterity'] = self.db.attributes['dexterity']
        attributes['temp_strength'] = self.db.attributes['strength']
        attributes['temp_attack_rating'] = self.db.attributes['attack_rating']
        attributes['temp_armor_rating'] = self.db.attributes['armor_rating']
        self.db.attributes = attributes


    """
    The following is all combat related
    """
    def initiative_roll(self):
        roll = random.randrange(1, 20)
        initiative_roll = roll + ((self.db.attributes['level'] / 2) + self.db.attributes['temp_attack_rating'])  
        return initiative_roll

    def attack_roll(self):
        roll = random.randrange(1,20)
        attack_roll = roll + self.db.attributes['temp_attack_rating']
        return attack_roll

    def get_damage(self):
        """
        We try to get weapon dmg, if that is none then we default to our fists
        for 1d4 damage. Also check for a damage bonus and add it in if it is
        present.
        """
        percentages = self.db.percentages 
        if self.db.equipment['weapon'] is not None:
            weapon = self.db.equipment['weapon']
            damage = weapon.damage.split('d')
            damage[0] = int(damage[0])
            damage[1] = int(damage[1])
            if damage[0] == 1:
                damage_roll = random.randrange(damage[0], damage[1])
            else:
                damage_roll = random.randrange(damage[0],(damage[1] *2))
        else:
            damage_roll = random.randrange(1,4)

        if percentages['melee_damage_bonus'] != 0.0:
            self.msg("{mDEBUG: Damage is: %s{n" % damage_roll)
            increase_in_damage = int(damage_roll * percentages['melee_damage_bonus']) + 1
            damage_roll = damage_roll + increase_in_damage
            self.msg("{mDEBUG: Damage after increase: %s{n" % damage_roll)
            
        return damage_roll

    def take_damage(self, damage):
        attributes = self.db.attributes
        attributes['temp_health'] = attributes['temp_health'] - damage
        self.db.attributes = attributes
        return
        
    def begin_attack(self, opponent):
        self.db.target = opponent
        opponent.db.in_combat = True
        opponent.db.target = self
        self.scripts.add(combat_scripts.InCombatState)
    
        
    def unbalance(self, phase):
        attributes = self.db.attributes
        if self.db.unbalanced is not True:
            self.scripts.add(combat_scripts.UnbalancedState)
            self.db.unbalanced = True
        if phase == 1:
            attributes['temp_dexterity'] =  attributes['dexterity'] - int((attributes['dexterity'] * .10) +1)
            attributes['temp_strength'] = attributes['strength'] - int((attributes['strength'] * .10) + 1)
            attributes['temp_armor_rating'] = attributes['armor_rating'] - 1
            self.db.attributes = attributes
        elif phase == 2:
            attributes['temp_dexterity'] =  attributes['dexterity'] - int((attributes['dexterity'] * .30))
            attributes['temp_strength'] = attributes['strength'] - int((attributes['strength'] * .30))
            attributes['temp_armor_rating'] = attributes['armor_rating'] - 2
            self.db.attributes = attributes
        elif phase == 3:
            attributes['temp_dexterity'] =  attributes['dexterity'] - int((attributes['dexterity'] * .50))
            attributes['temp_strength'] = attributes['strength'] - int((attributes['strength'] * .50))
            attributes['temp_armor_rating'] = attributes['armor_rating'] - 3
            self.db.attributes = attributes
        #self.scripts.add(combat_scripts.UnbalancedState)
    
    def balance(self):
        attributes = self.db.attributes
        attributes['temp_dexterity'] = attributes['dexterity']
        attributes['temp_strength'] = attributes['strength']
        attributes['temp_armor_rating'] = attributes['armor_rating']
        self.db.attributes = attributes
        self.scripts.validate()
           
    def loot(self, corpse):
        if corpse.db.corpse is True and corpse.db.lootable is True:
            self.award_gold(corpse.db.attributes['gold'])
            for item in corpse.contents:
                item.move_to(self, quiet=True)
                self.msg("You loot: %s" % item.name)
                self.location.msg_contents("%s looted: %s" % (self.name, item.name), exclude=self)
            if corpse.db.reanimate:
                return
            corpse.delete()
        else:
            self.msg("{rThis does not seem to be a corpse, or has no loot.{n")
        
    def death(self):
        lair = self.search(self.db.lair_id, global_search=True) 
        self.location = lair
        self.regenerate_stats()
        self.db.in_combat = False
        self.scripts.validate()
        #del self.db.cm_id

    def regenerate_stats(self):
        """
        Helper method to regen health etc after death.
        """
        attributes = self.db.attributes
        attributes['temp_health'] = attributes['health']
        attributes['temp_mana'] = self.db.attributes['mana']
        self.db.attributes = attributes
   
    """
    End combat
    Begin setters used in menus.
    """ 

    def set_race(self, race):
        attributes = self.db.attributes
        if 'bardok' in race:
            attributes['race'] = 'bardok'
            attributes['strength'] += 3
            attributes['constitution'] += 5
            self.db.attributes = attributes
            self.msg("{rYou are now one of the Bardok. You have recieved {b+3{n {rto strength and {b+5{n {rto consitution.{n")
            self.refresh_attributes()
        elif 'erelania' in race:
            attributes['race'] = 'erelania'
            attributes['constitution'] += 3
            attributes['intelligence'] += 3
            attributes['dexterity'] += 5
            self.db.attributes = attributes
            self.msg("{rYou are now one of the Erelania.  You have received {b+3{n {rto constitution, {b+3{n {rto intelligence and {b+5{n {rto dexterity.{n")
            self.refresh_attributes()
        elif 'gerdling' in race:
            attributes['race'] = 'gerdling'
            attributes['intelligence'] += 5
            attributes['dexterity'] += 3
            attributes['strength'] += 3
            self.db.attributes = attributes
            self.msg("{rYou are now one of the Gerdling.  You have received {b+5{n {rto intelligence, {b+3{n {rto dexterity and {b+3{n {Rto strength.{n")
            self.refresh_attributes()
        elif 'earthen' in race:
            attributes['race'] = 'earthen'
            attributes['strength'] += 5
            attributes['constitution'] += 5
            self.db.attributes = attributes
            self.msg("{rYou are now one of the Earthen.  You have received {b+5{n {rto strength and {b+5{n {rto constitution.{n")
            self.refresh_attributes()

    def set_deity(self, deity):
        attributes = self.db.attributes
        if 'ankarith' in deity:
            attributes['deity'] = "an\'karith"
            attributes['strength'] += 1
            attributes['intelligence'] += 5
            self.db.attributes = attributes
            self.msg("{rYou are now a devout follower of the Eternal Nightbringer, An'Karith.  You have received {b+1{n to strength and {b+5{n to intelligence.{n")
            self.refresh_attributes()
        elif 'slyth' in deity:
            attributes['deity'] = "slyth"
            attributes['dexterity'] += 5
            attributes['constitution'] += 2
            self.db.attributes = attributes
            self.msg("{rYou are now a devout follower of the new God, Slyth of the Glade.  You have received {b+5{n to dexterity and {b+2{n to constitution.{n")
            self.refresh_attributes() 
        elif 'green warden' in deity:
            attributes['deity'] = "green warden"
            attributes['intelligence'] += 5
            attributes['constitution'] += 3
            self.db.attributes = attributes
            self.msg("{rYou are now a devout follower of the The Green Warden, God and protector of the forests. You have received {b+5{n {rto intelligence and {b+3{n {rto constitution.{n")
            self.refresh_attributes()
        elif 'kaylynne' in deity:
            attributes['deity'] = "kaylynne"
            attributes['intelligence'] += 5
            attributes['strength'] += 2
            self.db.attributes = attributes
            
            msg = "{rYou are now a devout follower of Kaylynne, bolstering her small following of disciples.\n"
            msg += "You receive {b+5{n {rto intelligence and {b+2{n {r to strength.{n"
            self.msg(msg)
            self.refresh_attributes()

    def set_gender(self, gender):
        attributes = self.db.attributes
        attributes['gender'] = gender
        self.db.attributes = attributes

    def set_alignment(self, alignment):
        attributes = self.db.attributes
        attributes['alignment'] = alignment
        self.db.attributes = attributes
        self.move_to(self.db.lair, quiet=True)
        self.at_post_login()

    def equip_item(self, ite=None, slot=None):
        """ 
        Equip items, either specified or not.  If no item is given, then
        we simply try to equip the first item we find in our inventory for
        each slot type respectively.
        """
        equipment = self.db.equipment
        if equipment[slot] is not None:
            self.msg("You must unequip %s before you may equip %s." % (equipment[slot].name, ite.name))
            return
 
        if ite is None:
            wep_equipped = 0
            armor_equipped = 0
            for item in self.contents:
                if item.db.slot is not None:
                    if 'weapon' in item.db.slot and wep_equipped == 0:
                        equipment['weapon'] = item
                        wep_equipped = 1
                        item.on_equip()
                    elif 'armor' in item.db.slot and armor_equipped == 0:
                        equipment['armor'] = item
                        armor_equipped = 1
                        item.on_equip()

            if wep_equipped != 1:
                self.msg("You had no weapons to equip.")
            else:
                self.db.equipment = equipment
                self.msg("You now wield %s in your main hand." % self.db.equipment['weapon'])

            if armor_equipped != 1:
                self.msg("You had no armor to equip")
            else:
                self.db.equipment = equipment
                self.msg("You are now wearing %s for armor." % self.db.equipment['armor'])
            return
                
        if 'weapon' in slot:
            equipment['weapon'] = ite
            self.db.equipment = equipment
            self.msg("You now wield %s in your main hand." % self.db.equipment['weapon'])
        elif 'armor' in slot:
            equipment['armor'] = ite
            self.db.equipment = equipment
            self.msg("You are now wearing %s for armor." % self.db.equipment['armor'])
        else:
            self.msg("{r%s is not equippable in any slot!{n" % ite)
    
    def unequip_item(self, ite=None):
        """
        Unequip the item the specified, or if none, unequip everything
        """
        equipment = self.db.equipment
        if ite is None:
            slots = ['weapon_slot', 'armor_slot']
            for slot in slots:
                if 'weapon_slot' in slot:
                    weapon = equipment['weapon']
                    self.msg("{wUnequipped %s{n" % equipment['weapon'])
                    weapon.on_unequip()
                    equipment['weapon'] = None
                elif 'armor_slot' in slot:
                    armor = equipment['armor']
                    self.msg("{wUnequipped %s{n" % equipment['armor'])
                    self.msg("{w%s Armor rating lost{n" % armor.db.armor_rating)
                    armor.on_unequip()
                    equipment['armor'] = None
            self.db.equipment = equipment
        else:
            if 'weapon' in ite:
                self.msg("{wUnequipped %s{n" % equipment['weapon'])
                obj = equipment['weapon']
                obj.on_unequip()
                equipment['weapon'] = None
            elif 'armor' in ite:
                obj = equipment['armor']
                self.msg("{wUnequipped %s{n" % equipment['armor'])
                self.msg("{w%s Armor rating lost{n" % obj.db.armor_rating)
                obj.on_unequip()
                equipment['armor'] = None
        self.db.equipment = equipment
        
            
    def display_attributes(self, feedback=True):
        table = ['Name', 'Race', 'Gender', 'Level', 'Strength', 'Intelligence', 'Constitution', 'Dexterity', 'Health', 'Mana']
        self.easy_display(table, "Attributes")
    
    def display_stats(self, feedback=True):
        table = ['Attack_Rating', 'Temp_Armor_Rating', 'Experience_made', 'Experience_needed', 'Gold', 'total_exp_made']
        self.easy_display(table, "Other Stats")
    
    def display_equipped(self, feedback=True):
        table = ['Armor', 'Weapon']
        self.easy_display(table, "Equipment")
    
    def easy_display(self, table, title):
        if 'Skills' in title:
            m ='{{c{0:<9} {1:<32} {2:<10} {3:<10}{{n'.format("Name", "Description", "Damage", "Level")
            self.msg(m)
        elif 'Other Stats' in title:
            m = '{{c{0:<22} {1:<15}{{n'.format("Statistic", "Value")
            self.msg(m)
        elif 'Attributes' in title:
            m = '{{c{0:<22} {1:<15}{{n'.format("Attribute", "Value")
            self.msg(m)
        elif 'Equipment' in title:
            m = '{{c{0:<22} {1:<15}{{n'.format("Slot", "Item")
            self.msg(m)
            
        m = "{C--------------------------------------------------------------------{n"
        self.msg(m)
        m = ""
        for field in table:
            item = field
            if 'Skills' in title:
                if len(self.db.skills) < 1:
                    self.msg("You have not trained any skills.")
                    return
                pass
            else:
                field = field.strip()
                field_name = field.lower()
                field += ":"
            if 'Equipment' in title:
                m += '{{c{0:<15}{{n {{C|{{n  {1:<25}{{C|{{n\n'.format(field.title(), self.db.equipment[field_name])
            else:
                if '_' in field:
                    split_list = field.split('_')
                    proper_field = ' '.join(split_list)
                    if 'Temp' in proper_field:
                        split_list = proper_field.split('Temp')
                        proper_field = ' '.join(split_list)
                        proper_field = proper_field.lstrip()
                else:
                    proper_field = field
                try:
                    m += '{{c{0:<22}{{n {{C|{{n  {1:<10}{{C|{{n\n'.format(proper_field.title(), self.db.attributes[field_name].title())
                except AttributeError:
                    try:
                        m += '{{c{0:<22}{{n {{C|{{n  {1:<10}{{C|{{n\n'.format(proper_field.title(), self.db.attributes['temp_%s' % field_name])
                    except KeyError:
                        m += '{{c{0:<22}{{n {{C|{{n  {1:<10}{{C|{{n\n'.format(proper_field.title(), self.db.attributes[field_name])
                        
                    
        self.msg(m)
        self.msg("{C--------------------------------------------------------------------{n")
            
           
    def add_attribute_points(self, attribute, points):
        attributes = self.db.attributes
        attributes['%s' % attribute] += int(points)
        attributes['attribute_points'] -= points
        self.db.attributes = attributes
        self.refresh_attributes(health_and_mana=False, base_stats=True)
        self.msg("{CYou have added %s attribute points to %s.{n" % (points, attribute))
        self.msg("{CAvailable Attribute Points: %s{n" % self.db.attributes['attribute_points'])
        self.display_attributes()
         
    def create_attribute_menu(self, caller):
        """
        attribute_points = int(self.db.attributes['attribute_points'])  
        if int(to_add) > attribute_points:
            self.msg("{rNot enough Attribute Points to do that! (requested: %s, you have:%s){n" % (to_add,self.db.attribute_points))
            return
        attr = attr.strip()
        attributes = self.db.attributes
        for attribute in attributes:
            if attr in attribute:
                attributes[attribute] = attributes[attribute] + int(to_add)
        if 'constitution' in attr or 'con' in attr:
            attributes['health'] = (attributes['constitution'] * 2 ) + 25
            attributes['temp_health'] = attributes['constitution'] * 2
        elif 'intelligence' in attr or 'int' in attr:
            attributes['mana'] = attributes['intelligence'] * 2
            attributes['temp_mana'] = attributes['intelligence'] * 2
        elif 'dexterity' in attr or 'dex' in attr:
            attributes['armor_rating'] = attributes['dexterity'] / 5
        elif 'strength' in attr or 'str' in attr:
            attributes['attack_rating'] = attributes['strength'] / 8
        else:
            self.msg("{rThe attribute you passed: %s, was invalid.{n" % attr)
            return
        self.db.attributes = attributes
        
        int_ap = int(self.db.attributes['attribute_points']) - int(to_add)
        attributes['attribute_points'] = int_ap
        self.db.attributes = attributes
        m = "{b%s points added to %s.  Attribute Points Remaining: %s{n" % (to_add, attr, self.db.attributes['attribute_points'])
        self.msg(m)
        self.display_attributes()
        """
        attributes = self.db.attributes
        nodes = []
        welcome_text = """
Which attributes would you like to improve?
        """
        node0 = MenuNode('START', links=['strength', 'constitution', 'intelligence', 'dexterity', 'END'], linktexts=['Spend points in Strength', 'Spend points in Constitution', 'Spend points in Intelligence', 'Spend points in Dexterity', 'Exit'], text = welcome_text)
        str_text = "Select the amount of points to spend on this attribute:"
        nodes.append(node0)
        strength_node = MenuNode('strength', links=['strength-1', 'strength-2', 'strength-3'], linktexts=['Add 1 point to Strength', 'Add 5 points to Strength', 'Add 10 points to Strength'], text=str_text) 
        nodes.append(strength_node)
        constitution_node = MenuNode('constitution', links=['constitution-1', 'constitution-2', 'constitution-3'], linktexts=['Add 1 point to Constitution', 'Add 5 points to Constitution', 'Add 10 points to Constitution'], text=str_text)
        nodes.append(constitution_node)
        intelligence_node = MenuNode('intelligence', links=['intelligence-1', 'intelligence-2', 'intelligence-3'], linktexts=['Add 1 point to Intelligence', 'Add 5 points to Intelligence', 'Add 10 points to Intelligence'], text=str_text)
        nodes.append(intelligence_node)
        dexterity_node = MenuNode('dexterity', links=['dexterity-1', 'dexterity-2', 'dexterity-3'], linktexts=['Add 1 point to dexterity', 'Add 5 points to dexterity', 'Add 10 points to dexterity'], text=str_text)
        nodes.append(dexterity_node)
        for thing in [ 'strength', 'constitution', 'intelligence', 'dexterity']:
            for x in range (1, 4):
                if x == 1:
                    points = 1
                    node = MenuNode('%s-%s' % (thing, x), links=['START', 'END'], linktexts=['Back to Selection', 'Exit Attribute Menu'],code="self.caller.add_attribute_points(\'%s\',%s); self.goto(self.startnode)" % (thing, points))
                elif x == 2:
                    points = 5
                    node = MenuNode('%s-%s' % (thing, x), links=['START', 'END'], linktexts=['Back to Selection', 'Exit Attribute Menu'], code="self.caller.add_attribute_points(\'%s\',%s)" % (thing, points))
                elif x == 3:
                    points = 10
                    node = MenuNode('%s-%s' % (thing, x), links=['START', 'END'], linktexts=['Back to Selection', 'Exit Attribute Menu'], code="self.caller.add_attribute_points(\'%s\',%s)" % (thing, points))
                nodes.append(node)     
        menu = MenuTree(caller=caller, nodes=nodes)
        self.msg("{CAvailable Attribute Points: %s{n" % self.db.attributes['attribute_points'])
        menu.start()
        
                     
        
    def award_gold(self, gold_to_add, from_structure=None):
        attributes = self.db.attributes
        attributes['gold'] = int(attributes['gold']) + int(gold_to_add)
        self.db.attributes = attributes
        if from_structure is not None:
            self.msg("{yYou have been awarded %s gold from your %s.{n" % (gold_to_add, from_structure.name))
        else:
            self.msg("{yYou have been awarded %s gold.{n" % gold_to_add)    
    
    def spend_gold(self, gold_to_spend):
        attributes = self.db.attributes
        if self.db.attributes['gold'] < int(gold_to_spend):
            self.msg("{rYou do not have enough gold to do that.{n")
            return 1
        else:
            attributes['gold'] = int(attributes['gold']) - int(gold_to_spend)
            self.db.attributes = attributes
            return 0
    
    def buy_from_merchant(self, item, merchant):
        merchant_object = self.search(merchant, global_search=False)
        item = merchant_object.search(item, global_search=False)
        self.spend_gold(item.value)
        merchant_object.sell_item(item, self)
            
    def level_skill(self, skill):
        manager = self.db.skill_log
        skills = manager.db.skills
        print skills
        if skill in skills.keys():
            character_skill = skills[skill]
            character_skill.level_up()

    def spend_exp(self, exp):
        attributes = self.db.attributes
        if attributes['experience_currency'] < exp:
            self.msg("{r Not enough experience to do that!{n")
            return 1
        attributes['experience_currency'] -= exp
        self.db.attributes = attributes
        return 0

    def award_exp(self, exp_to_award):
        attributes = self.db.attributes
        attributes['total_exp_made'] = int(attributes['total_exp_made']) + int(exp_to_award)
        attributes['experience_currency'] += int(exp_to_award)
        difference = int(attributes['experience_needed']) - exp_to_award
        if difference == 0:
            self.level_up(zero_out_exp=True)
            return
        elif difference < 0:
            #self.msg("Added %s to %s" %(attributes['experience_needed'], difference))
            attributes['experience_needed'] = int(attributes['experience_needed']) + difference
            #get a positive number for the amount made into the next level
            positive_difference = difference * -1
            exp_made = positive_difference
            attributes['experience_made'] = exp_made
            attributes['experience_needed'] = attributes['experience_needed'] - exp_made
            self.db.attributes = attributes
            self.level_up(difference=positive_difference)
            return
        attributes['experience_made'] = (int(attributes['experience_made']) + exp_to_award)
        attributes['experience_needed'] = (int(attributes['experience_needed']) - exp_to_award)
        self.db.attributes = attributes
        self.msg("{gYou have been awarded %s experience.{n" % exp_to_award)
        return

    def add_quest_flag(self, flag):
        quest_flags = self.db.quest_flags
        quest_flags[flag] = False
        self.db.quest_flags = quest_flags

    def accept_quest(self, quest):
        manager = self.db.quest_log
        quest_obj = self.search(quest, global_search=True, ignore_errors=True)[0]
        
        exclusions = quest_obj.db.exclusions
        attributes = self.db.attributes
        split_list = exclusions.split(":")
        if len(split_list) < 1:
            attribute = split_list[0]
            exclude = split_list[1]
            if 'deity' in attributes:
                if attributes['deity'] in exclude:
                    self.msg("{rYou are a devout follower of %s and therefore have moral and religious objections to what this person asks of you.{n" % attributes['deity'])
                    return 
        storage = self.search('storage', global_search=True)
        quest_object = storage.search(quest, global_search=False, ignore_errors=True)[0]
        if quest_object.db.prereq is not None:
            if ';' in quest_object.db.prereq:
                found = 0
                split_list = quest_object.prereq.split(';')
                for item in split_list:
                    item = item.strip()
                    try:
                        completed_keys = manager.db.completed_quests.keys()
                        completed_keys.index(item.title())
                        found = 1
                    except Exception:
                        continue
                if found != 1:
                    self.msg("{RPre req not met.{n")
                    return
            else:
                if quest_object.prereq in manager.db.completed_quests.keys():
                    pass
                else:
                    self.msg("{RPre requisite not met.{n")
                    return 
        character_quest = quest_object.copy()
        character_quest.name = quest_object.name
        character_quest.add_help_entry()
        manager.add_quest(character_quest)
        character_quest.move_to(manager, quiet=True)
        self.db.quest_log = manager
        self.msg("{yYou have accepted: %s" % character_quest.name)

    def level_up(self, zero_out_exp=False, difference=0):
        attributes = self.db.attributes
        attributes['level'] = int(attributes['level']) + 1
        if zero_out_exp is True:
            attributes['experience_made'] = 0
        attributes['experience_needed'] = int((int(attributes['total_exp_made']) * .50) + attributes['total_exp_made'])
        attributes['experience_to_next_level'] = attributes['experience_needed']
        attributes['experience_needed'] = attributes['experience_needed'] - attributes['experience_made']
        attributes['attribute_points'] = attributes['attribute_points'] + (int(attributes['intelligence'] / 2))
        self.db.attributes = attributes
        self.msg("{bYou have gained a level of experience! You are now level %s! {n" % attributes['level'])


    """
    Effects Management
    """
    def add_effect(self, to_add):
        effects = self.db.effects
        effect = { 'name': to_add.name, 'description': to_add.db.desc, 'attribute_affected': to_add.db.attribute_affected_display }
        effects['%s_buff' % to_add.db.attribute_affected] = effect
        self.db.effects = effects
    
    def remove_effect(self,effect):
        effects = self.db.effects
        del effects[effect]
        self.db.effects = effects

    def find_effect(self, effect_to_find):
        if effect_to_find in self.db.effects:
            effect = effects[effect_to_find]
            return effect
        else:
            return None
    def display_effects(self):
        effects = self.db.effects
        if len(effects.keys()) < 1:
            self.msg("{cNothing is affecting you currently.{n")
            return
        m ='{{c{0:<20} {1:<100} {2:<10}{{n'.format("Name", "Description", "Attr Affected", )
        self.msg(m)
        m = "{C----------------------------------------------------------------------------------------------------------------------------------------------{n"
        self.msg(m)
        m = ""
        for effect in effects:
            m += "{{c{0:<20}{{n {1:<100} {2:<10}{{n\n".format( effects[effect]['name'], effects[effect]['description'], effects[effect]['attribute_affected'],)
        self.msg(m)
        m = "{C----------------------------------------------------------------------------------------------------------------------------------------------{n"
        self.msg(m)

        


class FriendList(Object):
    """
    Represents  a players friendlist.  This object is attached to the Player object.

    TODO: Fix up display of friends list.  It looks like shit cause I just wanted to
    get the framework in for the system before I made it pretty.
    """
    def at_object_creation(self):
        self.db.friends = []
        self.db.player = None

    def list_friends(self, caller):
        friends = self.db.friends
        caller.msg("{c|== Friends ==|{n")
        for friend in friends:
            friend = self.search(friend.name, global_search=True, player=True)
            if friend.character:
                character = friend.character
                msg = "{y%s{n --\t {g%s{n\t -- {C%s{n" % (friend.name, character.db.attributes['level'], character.location)
            else:
                continue #they aren't online and dont need to be shown.
                
            caller.msg(msg)
    
    def add_friend(self, caller, friend):
        character_obj = self.search(friend, global_search=True)
        if not character_obj:
            friend_player_obj = self.search(friend, global_search=True, player=True, ignore_errors=True)[0]
        else:
            friend_player_obj = character_obj.player

        friends = self.db.friends
        friends.append(friend_player_obj)
        self.db.friends = friends
        caller.msg("{C%s has been added to your friends list.{n" % friend_player_obj.name)

    def remove_friend(self, caller, friend):
        friend_player_obj = self.search(friend, global_search=True, player=True)
        friends = self.db.friends
        friends.remove(friend_player_obj)
        self.db.friends = friends
        

class CharacterGroup(Object):
    """
    Represents a group of characters.  Placeholder for now.
    """
    def at_object_creation(self):
        self.db.members = []
        self.db.experince_bonus = None
        self.db.loot_manager = None
        

  
    def generate_initial_members(self, inviter, invitee):
        self.name = "party_%s" % self.id
        members = self.db.members
        members.append(inviter)
        members.append(invitee)
        self.db.members = members
 
    def generate_comm_locks(self):
        members = self.db.members
        
        
    def create_comm_channels(self):
        try:
            party_chat = create.create_channel("Party Chat [%s]" % self.id, ('p', 'group'), 'Party Chat', "send:attr(group, %s);listen:attr(group, %s)" % (self.name, self.name)) 
        except:
            for member in members:
                member.msg("{rParty chat channel failed to open.  Contact an admin, this shouldn't happen.{n")


