import random
import time
from collections import deque
from prettytable import PrettyTable
from ev import Object, Character, utils, create_object, create_channel
from src.objects.models import ObjAttribute
from src.utils import logger
from game.gamesrc.objects.world.items import Item
from game.gamesrc.scripts.world_scripts import character_class_scripts as cscripts
from game.gamesrc.scripts.world_scripts import combat_scripts as combat_scripts
#from src.utils import utils, create
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
        attributes['balance'] = 6
        attributes['temp_balance'] = 6
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
        self.db.attributes = attributes
        attributes['temp_attack_rating'] = self.db.attributes['attack_rating']
        attributes['temp_armor_rating'] = self.db.attributes['armor_rating']
        attributes['temp_dexterity'] = self.db.attributes['dexterity']
        attributes['temp_strength'] = self.db.attributes['strength']
        attributes['temp_constitution'] = self.db.attributes['constitution']
        attributes['temp_intelligence'] = self.db.attributes['intelligence']
        self.db.factions = { 'slyth': 0, 'warden': 0, 'unknowns': 0, 'karith': 0, 'legion': 0, 'kaylynne': 0, 'molto': 0 }
        self.db.percentages = { 'dodge': 0.05, 'block': 0.0, 'heavy armor': 0.10, 'medium armor': 0.10, 'light armor': 0.10, 'bludgeon': 0.10, 'blades': 0.10, 'heavy': 0.10, 'dexterity_bonus': 0.0, 'intelligence_bonus': 0.0, 'strength_bonus': 0.0, 'constitution_bonus': 0.0, 'spell_damage_bonus': 0.0, 'melee_damage_bonus': 0.0, 'spell_fizzle_chance': 0.25, 'spell_buff_bonus': 0.0 }
        self.db.effects = {}
        self.db.group = None
        self.db.combat_queue = deque([])
        self.db.quest_flags = {}
        self.db.flags = {'tutorial_done': False, 'tutorial_started': False, }
        self.db.attributes = attributes
        self.db.equipment= { 'weapon': None, 'armor': None, 'shield': None, 'neck': None, 'left finger': None, 'right finger': None, 'back': None, 'trinket': None}
        self.db.skills = []
        self.db.spells = []
        self.db.in_combat = False
        self.db.unbalanced = False
        self.db.crippled = False
        self.db.grouped = False
        self.db.target = None
        #player item creation
        lair = create_object("game.gamesrc.objects.world.lair.Lair", key="%s's Lair" % self.key)
        lair.db.owner = self
        self.db.lair = lair
        self.db.lair_id = lair.dbref
        self.home = lair
        self.location = lair
        starter_chest = create_object("game.gamesrc.objects.world.storage.StorageItem", key="Blessed Chest", location=lair)
        starter_chest.locks.add("open:holds(Deity Seal)")
        starter_chest.desc = "A medium sized chest with a very noticeable indendation where the locking mechanism would be.\n"
        starter_chest.desc += "Upon closer examination of the chest, you notice it is sealed with powerful magic." 
        training_manual_kick = create_object("game.gamesrc.objects.world.skills.TrainingBook", key="Training Manual: Kick", location=starter_chest)
        training_manual_kick.db.skill = 'kick'
        training_manual_kick.db.level_requirement = 1
        self.db.prelogout_location = self.db.lair_id
        structure_manager = create_object("game.gamesrc.objects.world.structures.StructureManager", key="Stone Pedestal", location=self.location)
        dungeon_manager = create_object("game.gamesrc.objects.world.structures.DungeonManager", key="Stone Summoning Circle", location=self.location)
        dungeon_manager.db.lair_id = self.db.lair_id
        generator = create_object("game.gamesrc.objects.world.generators.DungeonGenerator", location=dungeon_manager, key="Pulsing Red Stone")
        generator.locks.add("get:none();drop:none()")
        generator.manager = dungeon_manager
        dungeon_manager.db.generator = generator
        structure_manager.db.lair_id = self.db.lair_id
        structure_manager.gen_ids()
        lair.db.structure_manager_id = structure_manager.dbref
        questlog = create_object("game.gamesrc.objects.world.quests.QuestManager", key="Adventurer's Journal", location=self)
        questlog.db.character = self
        skill_log = create_object("game.gamesrc.objects.world.skills.SkillManager", key="Heavy Leather Tome", location=self)
        skill_log.db.character = self
        spellbook = create_object("game.gamesrc.objects.world.spells.SpellManager", key="Spellbook", location=self)
        spellbook.db.character = self
        self.db.spellbook = spellbook
        self.db.skill_log = skill_log
        self.db.quest_log = questlog
        #friends list is atteched to the player
        player_lair_exit = create_object("game.gamesrc.objects.world.rooms.PlayerLairExit", location=lair)

    def rebuild_model(self):
        """
        Build a new character model to grab in new things that have been coded.
        We generate a new character model, check its attributes versus this model.
        If we find differences, we add the necessary attribute to the model.

        TODO: Allow for parsing dictionaries for new key/value pairs.
              Ignore objects, or find a way to instantiate the particular object needed.

        This will currently support adding of any *completely* new data structure other than 
        object references.  May need to update the call to this to be asynchronously done.
        """
        nc = create_object("game.gamesrc.objects.world.character.CharacterClass")
        valid_attributes = [(attr.key, attr.value, attr) for attr in ObjAttribute.objects.filter(db_obj=nc)]
        self_attributes = [(attr.key, attr.value, attr) for attr in ObjAttribute.objects.filter(db_obj=self)]
        self_attribute_keys = [x[0] for x in self_attributes]
        valid_attribute_num = len(valid_attributes)
        my_attribute_num = len(self_attributes)
        if valid_attribute_num != my_attribute_num:
            logger.log_infomsg("CharacterClass->rebuild_model: Possible Character model changes, checking further.")
            for attribute in valid_attributes:
                if attribute[0] not in self_attribute_keys:
                    logger.log_infomsg("CharacterClass->rebuild_model: %s is not found on %s, setting attribute now." % (attribute[0], self.name))
                    self.set_attribute(attribute[0], attribute[1])
        #delete the extra crap made on generating a new character
        lair = nc.db.lair
        lair.delete()
        nc.delete()
        return


    def character_summary(self):
        """
        Detailed output of a character.  The character sheet.
        """
        pass

    def do_tutorial(self):
        flags = self.db.flags
        self.msg("You disappear in a puff of smoke.")
        self.location.msg_contents("%s disappears in a puff of smoke" % self.name, exclude=self)
        tutorial1 = self.search("tutorial1", global_search=True)
        self.move_to(tutorial1, quiet=True)
        flags['tutorial_started'] = True
        self.db.flags = flags

        
    def at_object_receive(self, moved_obj, source_location):
        questlog = self.db.quest_log
        if moved_obj.db.quest_item:
            questlog.check_quest_flags(mob=None, item=moved_obj)
        try:
            if 'rare' in moved_obj.db.lootset:
                questlog.check_quest_flags(mob=None, item=moved_obj)
        except:
            pass
           
    def at_post_login(self): 
        if self.db.in_combat is True:
            self.db.in_combat = False
            self.scripts.validate()

        if self.db.attributes['deity'] is not None or self.id == 2:
            self.cmdset.add(character_cmdset.CharacterCommandSet)
            self.cmdset.add(combat_cmdset.DefaultCombatSet)
            self.cmdset.add(structure_cmdset.BuildCmdSet)
            self.cmdset.add(skills_cmdset.CombatSkillCmdSet)
            self.cmdset.add(spells_cmdset.SpellsCmdSet)
            self.scripts.validate()
            self.scripts.add(cscripts.CharacterSentinel)
        self.rebuild_model()

    def at_disconnect(self):
        self.cmdset.clear()
        self.db.grouped = False
        self.scripts.delete("character_sentinel")
   
    def at_first_login(self): 
        if self.dbref == 2:
            return
        aspect = self.search("Aspect of An'Karith", global_search=False, location=self.location, ignore_errors=True)[0]
        aspect.aliases = [aspect.name]
        aspect.name = '{Y!{n Aspect of %s' % self.db.attributes['deity'].title()
        aspect.db.real_name = "%s" % self.db.attributes['deity'].title()
        self.cmdset.add(character_cmdset.CharacterCommandSet)
        self.cmdset.add(combat_cmdset.DefaultCombatSet)
        self.cmdset.add(structure_cmdset.BuildCmdSet)
        self.cmdset.add(skills_cmdset.CombatSkillCmdSet)
        self.cmdset.add(spells_cmdset.SpellsCmdSet)
        self.scripts.add(cscripts.CharacterSentinel)


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
            try:
                if self.db.effects['temp_armor_rating_buff']:
                    attributes['armor_rating'] += self.db.effects['temp_armor_rating_buff']['buff_amount']
            except KeyError:
                pass
            if self.db.equipment['armor'] is not None:
                attributes['armor_rating'] += self.db.equipment['armor'].db.armor_rating
            self.db.attributes = attributes
        attributes['temp_dexterity'] = self.db.attributes['dexterity']
        attributes['temp_strength'] = self.db.attributes['strength']
        attributes['temp_constitution'] = self.db.attributes['constitution']
        attributes['temp_intelligence'] = self.db.attributes['intelligence']
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

    def armor_unbalance_check(self):
        armor = self.db.equipment['armor']
        if armor is None:
            return 
        skillmanager = self.db.skill_log
        armor_type = armor.db.armor_type
        if armor_type.title() not in skillmanager.skills.keys():
            armor_per = self.db.percentages[armor_type]
            rn = random.random()
            if rn > armor_per:
                self.msg("{cYou are wearing armor you are not proficient in, causing loss of balance{n")
                if self.db.attributes['temp_balance'] == 0:
                    return
                self.db.attributes['temp_balance'] -= 1
        else:
            return 

    def do_glancing_blow(self):
        damage = self.get_damage()
        damage = damage / 2
        self.msg("{cYou are using a weapon you are not proficient in, causing glancing blows.")
        return damage

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
            #self.msg("{mDEBUG: Damage is: %s{n" % damage_roll)
            increase_in_damage = int(damage_roll * percentages['melee_damage_bonus']) + 1
            damage_roll = damage_roll + increase_in_damage
            #self.msg("{mDEBUG: Damage after increase: %s{n" % damage_roll)
            
        return damage_roll

    def take_damage(self, damage):
        attributes = self.db.attributes
        attributes['temp_health'] = attributes['temp_health'] - damage
        self.db.attributes = attributes
        return
        
    def begin_attack(self, opponent):
        if hasattr(opponent, 'mob_type'):
            self.db.target = opponent
            opponent.db.in_combat = True
            opponent.db.target = self
            self.scripts.add(combat_scripts.InCombatState)
        else:
            self.msg("That is not able to be attacked.")
            return
    
        
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
                if item.db.lootable:
                    item.move_to(self, quiet=True)
                    self.msg("You loot: %s" % item.name)
                    self.location.msg_contents("%s looted: %s" % (self.name, item.name), exclude=self)
            if corpse.db.reanimate:
                corpse.db.lootable = False
                return
            self.db.target = None
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
   
    def post_combat(self):
        self.db.target = None
    """
    End combat
    Begin setters used in menus.
    """ 
    def post_creation(self):
        self.move_to(self.db.lair, quiet=True)
        #cflags['in_menu'] = False
        self.at_first_login()
       # aspect = self.search("Aspect of %s" % self.attributes['deity'], global_search=False, location=self.location, ignore_errors=True)[0]
       # aspect.do_dialog(caller=self, type='greeting')
        
    def set_weapon_skill(self, skill):
        """
        Set which weapon we specialize in.
        """
        manager = self.db.skill_log
        if 'blades' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.Blades", key="blades")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['blades'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in bladed weaponry.")
        elif 'heavy' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.Heavy", key="heavy")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['heavy'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in heavy weaponry.")
        elif 'bludgeon' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.Bludgeon", key="bludgeon")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['bludgeon'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in bludgeoning weaponry.")


    def set_armor_skill(self, skill):
        """
        Set armor spec.
        """
        manager = self.db.skill_log
        if 'light' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.LightArmor", key="Light Armor")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['light armor'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in Light Armor.")
        elif 'medium' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.MediumArmor", key="Medium Armor")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['medium armor'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in Medium Armor.")
        elif 'heavy' in skill:
            skill_object = create_object("game.gamesrc.objects.world.skills.HeavyArmor", key="Heavy Armor")
            skill_object.db.character = self
            manager.add_item(skill_object.name, skill_object)
            self.db.percentages['heavy armor'] += skill_object.db.rank_modifier
            self.msg("You have become proficient in Heavy Armor.")
               
            

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
            self.msg("{RYou are now a devout follower of the Eternal Nightbringer, An'Karith.  You have received {b +1 {R to strength and {b +5 {R to intelligence.{n")
            self.refresh_attributes()
        elif 'slyth' in deity:
            attributes['deity'] = "slyth"
            attributes['dexterity'] += 5
            attributes['constitution'] += 2
            self.db.attributes = attributes
            self.msg("{RYou are now a devout follower of the new God, Slyth of the Glade.  You have received {b +5 {R to dexterity and {b +2 {R to constitution.{n")
            self.refresh_attributes() 
        elif 'green warden' in deity:
            attributes['deity'] = "green warden"
            attributes['intelligence'] += 5
            attributes['constitution'] += 3
            self.db.attributes = attributes
            self.msg("{RYou are now a devout follower of the The Green Warden, God and protector of the forests. You have received {b +5 {n {Rto intelligence and {b +3 {n {Rto constitution.{n")
            self.refresh_attributes()
        elif 'kaylynne' in deity:
            attributes['deity'] = "kaylynne"
            attributes['intelligence'] += 5
            attributes['strength'] += 2
            self.db.attributes = attributes
            
            msg = "{RYou are now a devout follower of Kaylynne, bolstering her small following of disciples.\n"
            msg += "You receive {b +5 {n {R to intelligence and {b +2 {n {R to strength.{n"
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
        self.at_first_login()

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
            lring_equipped = 0
            rring_equipped = 0
            back_equipped = 0
            trinket_equipped = 0
            shield_equipped = 0

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
                    elif 'left finger' in item.db.slot and lring_equipped == 0:
                        equipment['left finger'] = item
                        lring_equipped = 1
                        item.on_equip()
                    elif 'right finger' in item.db.slot and rring_equipped == 0:
                        equipment['right finger'] = item
                        rring_equipped = 1
                        item.on_equip()
                    elif 'back' in item.db.slot and back_equipped == 0:
                        equipment['back'] = item
                        back_equipped = 1
                        item.on_equip()
                    elif 'trinket' in item.db.slot and trinket_equipped == 0:
                        equipment['trinket'] = item
                        trinket_equipped = 1
                        item.on_equip()
                    elif 'shield' in item.db.slot and shield_equipped == 0:
                        equipment['shield'] = item
                        shield_equipped = 1
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
        elif 'left finger' in slot:
            equipment['left finger'] = ite
            self.db.equipment = equipment
            self.msg("You are now wearing %s on your left finger." % ite.name)
        elif 'right finger' in slot:
            equipment['right finger'] = ite
            self.db.equipment = equipment
            self.msg("You are now wearing %s on your right finger." % ite.name)
        elif 'back' in slot:
            equipment['back'] = ite
            self.db.euqipment = equipment
            self.msg("You are now wearing %s on your back." % ite.name)
        elif 'shield' in slot:
            equipment['shield'] = ite
            self.db.equipment = equipment
            self.msg("You are now using %s as a shield" % ite.name)
        elif 'trinket' in slot:
            equipment['trinket'] = ite
            self.db.equipment = equipment
            self.msg("You are now using %s as your trinket." % ite.name)
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
            elif 'right finger' in ite:
                obj = equipment['right finger']
                self.msg("{wUnequipped %s{n" % equipment['right finger'])
                obj.on_unequip()
                equipment['right finger'] = None
            elif 'left finger' in ite:
                obj = equipment['left finger']
                self.msg("{wUnequipped %s{n" % equipment['left finger'])
                obj.on_unequip()
                equipment['left finger'] = None
            elif 'back' in ite:
                obj = equipment['back']
                self.msg("{wUnequipped %s{n" % equipment['back'])
                obj.on_unequip()
                equipment['back'] = None
            elif 'trinket' in ite:
                obj = equipment['trinket']
                self.msg("{wUnequipped %s{n" % equipment['trinket'])
                obj.on_unequip()
                equipment['trinket'] = None
            elif 'shield' in ite:
                obj = equipment['shield']
                self.msg("{wUnequipped %s{n" % equipment['shield'])
                obj.on_unequip()
                equipment['shield'] = None
        self.db.equipment = equipment
        
            

    def pretty_table(self, type='Attributes'):
        table = PrettyTable()
        str_bonus = self.db.attributes['temp_strength'] - self.db.attributes['strength']
        int_bonus = self.db.attributes['temp_intelligence'] - self.db.attributes['intelligence']
        con_bonus = self.db.attributes['temp_constitution'] - self.db.attributes['constitution']
        dex_bonus = self.db.attributes['temp_dexterity'] - self.db.attributes['dexterity']
        not_equipped = ""
        if type == 'Attributes':
            table._set_field_names(["Attributes", "Value (Base)", "Bonus"])
            table.align["Attributes"] = "r"
            table.align["Value"] = "l"
            table.add_row(["Name:", self.db.attributes['name'], " "]) 
            table.add_row(["Race:", self.db.attributes['race'], " "])
            table.add_row(["Gender:", self.db.attributes['gender']," "])
            table.add_row(["Level:", self.db.attributes['level'], " "])
            table.add_row(["Strength:", "%s (%s)" % (self.db.attributes['temp_strength'], self.db.attributes['strength']), "+%s" % str_bonus])
            table.add_row(["Intelligence:", "%s (%s)" % (self.db.attributes['temp_intelligence'], self.db.attributes['intelligence']), "+%s" %int_bonus])
            table.add_row(["Constitution:", "%s (%s)" % (self.db.attributes['temp_constitution'],self.db.attributes['constitution']), "%s" % con_bonus])
            table.add_row(["Dexterity:", "%s (%s)" % (self.db.attributes['temp_dexterity'], self.db.attributes['dexterity']), "+%s" % dex_bonus])
            table.add_row(["Health:", "%s (%s)" % (self.db.attributes['temp_health'], self.db.attributes['health']), " "])
            table.add_row(["Mana:", "%s (%s)" % (self.db.attributes['temp_mana'], self.db.attributes['mana']), " "])
        elif type == 'Stats':
            armor_diff = self.db.attributes['temp_armor_rating'] - (self.db.attributes['dexterity'] / 5) 
            table._set_field_names(["Other Stats", "Value", "Bonuses"])
            table.add_row(["Gold:", self.db.attributes['gold'], " "])
            table.add_row(["Armor Rating:", self.db.attributes['temp_armor_rating'], "+%s" % armor_diff])
            table.add_row(["Attack Rating:", self.db.attributes['attack_rating'],  " "])
            table.add_row(["Experience Made:", self.db.attributes['experience_made'], " "])
            table.add_row(["Experience Needed:", self.db.attributes['experience_needed'], " "])
            table.add_row(["Total Experience:", self.db.attributes['total_exp_made'], " "])
            table.add_row(["Experience Currency:", self.db.attributes['experience_currency'], " "])
            table.align["Other Stats"] = "r"
        elif type == 'Equipment':
            equipment = self.db.equipment
            not_equipped = ""
            table._set_field_names(["Item", "Slot", "Bonuses", "Value"])
            for slot in equipment:
                if equipment['%s' % slot] is not None:
                    table.add_row(['%s' % equipment['%s' % slot].name, "%s" % slot, '%s' % equipment['%s' % slot].attribute_bonuses, '%s' % equipment['%s' % slot].db.value])
                else:
                    not_equipped += '%s, ' % slot
        not_equipped = not_equipped.rstrip(', ') 
        string = table.get_string()
        self.msg(string)
        if not_equipped != "":
            self.msg("{CSlots unused: [ {n%s{C ]{n" % not_equipped)
    
    def add_attribute_points(self, attribute, points):
        attributes = self.db.attributes
        if points > attributes['attribute_points']:
            self.msg("{RNot enough attribute points.{n")
            return
        attributes['%s' % attribute] += int(points)
        attributes['attribute_points'] -= points
        self.db.attributes = attributes
        self.refresh_attributes(health_and_mana=False, base_stats=True)
        self.msg("{CYou have added %s attribute points to %s.{n" % (points, attribute))
        self.msg("{CAvailable Attribute Points: %s{n" % self.db.attributes['attribute_points'])
        self.pretty_table()
         
    def create_attribute_menu(self, caller):
        attributes = self.db.attributes
        nodes = []
        welcome_text = """
Which attributes would you like to improve?
%s
        """ % self.pretty_table()
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
                    node = MenuNode('%s-%s' % (thing, x), links=['START', 'END'], linktexts=['Back to Selection', 'Exit Attribute Menu'],code="self.caller.add_attribute_points(\'%s\',%s)" % (thing, points))
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
        print "triggering merchant.sell_item"
        merchant_object.sell_item(item, self)
            
    def level_skill(self, skill):
        manager = self.db.skill_log
        skills = manager.db.skills
        print skills
        if skill in skills.keys():
            character_skill = skills[skill]
            character_skill.level_up()
        manager.generate_skill_menu(self)

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
            self.db.attributes = attributes
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
                    if item.title() in [key.title() for key in manager.db.completed_quests.keys()]:
                        found = 1
                if found != 1:
                    self.msg("{RPre req not met.{n")
                    return
            else:
                if quest_object.prereq.title() in [key.title() for key in manager.db.completed_quests.keys()]:
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
        self.msg("{CYou have gained a level of experience! You are now level %s! {n" % attributes['level'])

    def negotiate_group_invite(self, inviter, invitee):
        """
        dictate actions when asked to join a group
        """
        prompt_yesno(self, question="{C%s would like you adventure with you.  Will you join them?{n" % inviter.name,
                    yescode="self.caller.accept_group_invite('%s')" % inviter.name, nocode="self.caller.deny_group_invite('%s')" % inviter.name, default="Y")
        
    def accept_group_invite(self, caller):
        caller = self.search(caller, global_search=False)
        if caller.db.grouped:
            group = caller.db.group
            group.join(caller, self)
        else:
            group = create_object("game.gamesrc.objects.world.character.CharacterGroup")
            group.generate_initial_members(caller, self)
        self.cmdset.add("game.gamesrc.commands.world.character_cmdset.GroupCommandSet")
        self.db.grouped = True


    def deny_group_invite(self, caller):
        caller = self.search(caller, global_search=False)
        caller.msg("{R%s declines your invitation.{n" % self.name)
        return

    def on_quest(self, quest, completed=False):
        """
        return true if on said quest,
        false otherwise.
        """
        manager = self.db.quest_log
        print "objects.world.character.CharacterClass => %s" % quest
        if completed:
            print "in completed"
            quest = manager.find_quest(quest, completed=True)
        else:
            print "non completed"
            quest = manager.find_quest(quest)
        if quest is None:
            return False
        else:
            return True

    def has_skill(self, skill):
        manager = self.db.skill_log
        if skill in manager.skills.keys():
            return True
        else:
            return False
    
    def has_spell(self, spell):
        manager = self.db.spellbook
        if spell in manager.spells.keys():
            return True
        else:
            return False
    
    """
    Effects Management
    """
    def add_effect(self, to_add):
        effects = self.db.effects
        effect = { 'buff_amount': to_add.db.buff_amount, 'name': to_add.name, 'description': to_add.db.desc, 'attribute_affected': to_add.db.attribute_affected_display, 'duration': (to_add.db.duration / 60) }
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
        table = PrettyTable()
        table._set_field_names(["Name", "Description", "Attribute Affected", "Duration"])
        for effect in effects:
            table.add_row(["%s" % effects[effect]['name'], "%s" % effects[effect]['description'], "%s" % effects[effect]['attribute_affected'], "%s minutes" % effects[effect]['duration']])
        msg = table.get_string()
        self.msg(msg)


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
        #caller.msg("{c|== Friends ==|{n")
        msg = "{0:<15}{1:<25}{2:<20}{3:<20}".format("Name", "Logged in as", "Location", "Level")
        caller.msg(msg)
        msg = "{C----------------------------------------------------------------------------------------------------{n"
        caller.msg(msg)
        for friend in friends:
            friend = self.search('*%s'%friend.name, global_search=True, player=True, ignore_errors=True)[0]
            if friend.has_player:
                character = friend
                msg = "{{G{0:<15}{{n{1:<25}{2:<20}{3:<20}".format(friend.name, character.name, character.location, character.db.attributes['level']) 
            else:
                continue #they aren't online and dont need to be shown.
                
            caller.msg(msg)
        msg = "{C-----------------------------------------------------------------------------------------------------{n"
        caller.msg(msg)
    
    def add_friend(self, caller, friend):
        character_obj = self.search(friend, global_search=True)
        if not character_obj:
            friend_player_obj = self.search('*%s'%friend, global_search=True, ignore_errors=True)[0]
            friend_player_obj = friend_player_obj.player
        else:
            friend_player_obj = character_obj.player

        friends = self.db.friends
        friends.append(friend_player_obj)
        self.db.friends = friends
        caller.msg("{C%s has been added to your friends list.{n" % friend_player_obj.name)

    def remove_friend(self, caller, friend):
        friend_player_obj = self.search('*%s'%friend, global_search=True, player=True)
        friends = self.db.friends
        friends.remove(friend_player_obj)
        self.db.friends = friends
        

class CharacterGroup(Object):
    """
    Represents a group of characters. This object also holds the "party" chat channel used for group
    communication.  This object once it is created is stored as an attribute on the Character Model
    for whichever characters are a part of the group.  This object is also where any loot arbitration,
    and bonus management should happen.

    A safe rule of thumb is, if it deals with grouping specifically, or a function of the group itself, 
    the code should be in this class.
    """
    def at_object_creation(self):
        self.db.members = []
        self.db.experience_bonus = None
        self.db.loot_manager = None
        self.db.channel = None
        self.db.leader = None
        self.location = self.search('Limbo', global_search=True)
        

  
    def generate_initial_members(self, inviter, invitee):
        self.name = "party_%s" % self.id
        members = self.db.members
        members.append(inviter)
        members.append(invitee)
        self.db.members = members
        inviter.db.group = self
        inviter.db.grouped = True
        inviter.cmdset.add("game.gamesrc.commands.world.character_cmdset.GroupCommandSet")
        print "DEBUG -> CharacterGroup.generate_initial_members: adding GroupCommandSet to Inviter"
        invitee.db.group = self
        self.db.leader = inviter.name
        self.create_comm_channels()
        channel = self.db.channel
        channel.connect_to(inviter)
        channel.connect_to(invitee)
        channel.msg("{CAdventuring Party formed! {GLeader{n: %s {CMembers: %s{n" % (self.db.leader, members))
        self.db.members = members

 
    def generate_comm_locks(self):
        members = self.db.members
        
        
    def create_comm_channels(self):
        members = self.db.members
        try:
            party_chat = create_channel("Party Chat [%s]" % self.id, 'Party Chat', locks="send:attr(group, %s);listen:attr(group, %s)" % (self.name, self.name)) 
            self.db.channel = party_chat
        except:
            for member in members:
                member.msg("{rParty chat channel failed to open.  Contact an admin, this shouldn't happen.{n")

    def join(self, inviter, invitee):
        channel = self.db.channel
        members = self.db.members
        if len(members) == 5:
            inviter.msg("{RMaximum amount of characters in the group.{n")
            return
        members.append(invitee)
        invitee.db.group = self
        channel.connect_to(invitee)    
        channel.msg("{c%s joins the party.{n" % invitee.name)
        self.db.channel = channel
   
    def leave(self, character):
        channel = self.db.channel
        members = self.db.members
        channel.msg("{c%s has left the party.{n" % character.name)
        character.db.group = None
        channel.disconnect_from(character)
        members.remove(character)
        character.db.grouped = False
        character.cmdset.delete("gamesrc.commands.world.character_cmdset.GroupCommandSet")

    def disband(self):
        channel = self.db.channel
        members = self.db.members
        channel.msg("{RParty disbanded.{n")
        for member in members:
            member.db.group = None
            channel.disconnect_from(member)
        channel.delete()
        self.delete()

    def promote(self, character):
        channel = self.db.channel
        channel.msg("{C%s is now party leader!{n" % character.name)
        self.db.leader = character.name
        
        


