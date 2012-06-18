import random
from src.utils import create
from gamesrc.objects.menusystem import *
from prettytable import PrettyTable
from ev import Object

class SkillManager(Object):
    """
    Management object for skills.  Allows for easy storage and retrieval of
    skill information.  This will most likely be stored on the character
    model as a book or some other object that will be un-interactable except
    through specific commands, much like the QuestManager object used to create
    the 'questlog' for the characters.
    """
    def at_object_creation(self):
        self.name = "Skills Journal"
        description = "A leather bound tome that has ancient runic script written around its borders in bright gold lettering.\n"
        description += "The tome contains all the information about the skills you have learned in Avaloria."
        self.db.desc = description
        self.locks.add("get:none()")
        self.db.equippable = False
        self.db.is_equipped = False
        self.db.skills = {}

    def add_item(self, key, obj):
        skills = self.db.skills
        skills[key] = obj
        self.db.skills = skills
        obj.move_to(self, quiet=True)

    def remove_item(self, key):
        skills = self.db.skills
        obj = self.db.skill[key]
        del skills[key]
        obj.delete()
        self.db.skills = skills

    def display_skills(self, caller):
        table = PrettyTable()
        table._set_field_names(["Skill", "Level", "Description", "Damage"])
        skills = self.db.skills
        if len(skills) < 1:
            caller.msg("You have no skills trained.  Try finding or buying some Training Manuals!")
            return
            
        for skill in skills:
            obj = skills[skill]
            if obj.db.damage is None:
                damage = "Passive"
            else:
                damage = obj.db.damage
            table.add_row(['%s' % obj.name, '%s' % obj.db.rank, '%s' % obj.db.desc, '%s' % damage])
        msg = table.get_string()
        caller.msg(msg)
    
    def generate_skill_menu(self,caller):
        skills = self.db.skills
        skills_list = [ skills[skill] for skill in skills]
        start_desc_text = """
{cSkill Advancement{n
Spend your accrued experience points on the skills you know to increase their rank. 
A higher rank means more of successful use, along with increasing other things behind 
the scenes for the specific skill.
        """
        start_node = MenuNode('START', cols=2, links=['%s' % skill.name for skill in skills_list], linktexts=['Increase %s' % skill.name for skill in skills_list], text=start_desc_text ) 
        nodes = []
        nodes.append(start_node)
        for skill in skills:
            skill = skills[skill]
            text = """
{c%s Advancement{n
Increase %s? 

This will cost: {C%s{n Experience Currency. 
You currently have {C%s{n Currency Experience Points.
You are currently at rank: {C%s{n
            """ % (skill.name.title(), skill.name.title(), skill.db.cost_to_level, caller.db.attributes['experience_currency'], skill.db.rank)
            node = MenuNode('%s' % skill, links=['increase_%s' % skill.name, 'END'], linktexts=['Increase %s' % skill.name, 'Exit'], text=text)
            confirm_node = MenuNode('increase_%s' % skill.name, links=['START', 'END'], linktexts=['Back to Skill Selection', 'Exit'], code="self.caller.level_skill('%s')" % skill.name)
            nodes.append(node)
            nodes.append(confirm_node)
        menu = MenuTree(caller=caller,nodes=nodes)
        menu.start()

    def find_item(self, key):
        return self.db.skills[key]

    
        
class Skill(Object):
    """
    Basic skill object that sets some typical things a skill will have.
    """

    def at_object_creation(self):
        """
        effect needs to be some sort of identifier for what the skill does.
        perhaps attack could be one type of effect.  So a say a skill like
        'kick' would have an attack effect which dictates what it will do.
        effect will most likely be a string in which sentinels will be placed
        so that the skill parser knows wtf to do with it.
        """
        self.db.desc = "Some sort of skill."
        self.db.effect = None
        self.db.level_req = 1
        self.db.class_req = None
        #rank corresponds to skill level
        self.db.rank = 1
        self.db.rank_modifier = .01
        self.db.experience_spent= 0
        self.db.passive = False #is the skill passive?
        self.db.cost_to_level = 100 #cost in exp.
        self.db.increment = int(self.db.cost_to_level * .1) + 1
        self.db.character = None
        self.db.lootable = False
        self.locks.add("view:none()")

    def on_use(self):
        """
        Placeholder for the function that will be called when the skill is actually
        used in game.
        """
        pass

    def update_attributes(self):
        """
        Placehold for the hook that will be called after a level_up has a occured.
        this will update any attributes it needs to on the skill as defined within
        the hook function
        """
        modifier = self.db.rank_modifier
        modifier += .01 
        self.db.rank_modifier = modifier

    def award_exp(self, exp):
        exp = int(exp)
        cost = int(self.db.cost_to_level)
        exp_spent = int(self.db.experience_spent)
        if exp > cost:
            difference = exp - cost
            exp_spent += exp
            self.level_up(difference)
        elif exp < cost:
            cost = cost - exp
            exp_spent += exp
        else:
            exp_spent += exp
            self.level_up()
        self.db.experience_spent = exp_spent
        self.db.cost = cost
        
        
    def level_up(self):
        character = self.db.character
        return_code = character.spend_exp(self.db.cost_to_level)
        if return_code != 0:
            return
        self.db.rank = self.db.rank + 1
        self.db.cost_to_level = self.db.increment + self.db.cost_to_level
        self.db.increment = int(self.db.cost_to_level * .1) + 1
        character.msg("%s increased! (%s)" % (self.name, self.db.rank))
        self.update_attributes()
    
    def push_to_combat_queue(self):
        character = self.db.character
        if character.db.in_combat is False:
            character.msg("Can't do that unless you are in combat with something.")
            return
        character.msg("{CYou prepare to use the skill: {c%s{n!" % self.name)
        msg = 'skill:%s' % self.name
        cq = character.db.combat_queue
        cq.append(msg)
        character.db.combat_queue = cq

    def get_effect(self):
        modifier = self.db.rank_modifier
        if 'attack' in self.db.effect:
            damage = self.db.damage.split('d')
            value_one = int(damage[0])
            value_two = int(damage[1])
            if value_one == 1:
                damage = random.randrange(1,value_two)
                rank_modifier_damage = int(value_two * modifier)
                if rank_modifier_damage == 0:
                    rank_modifier_damage += 1
                damage = damage + rank_modifier_damage     
            else:
                damage = random.randrange(value_one, (value_two * 2))
                rank_modifier_damage = int((value_one * 2) * modifier)
                if rank_modifier_damage == 0:
                    rank_modifier_damage += 1
                damage = damage + rank_modifier_damage     
            return damage
   
    def unbalance(self, amount, attributes):
       attributes['temp_balance'] = attributes['temp_balance'] - amount
       return attributes

    def get_weapon_damage(self, weapon):
       modifier = self.db.rank_modifier
       damage = weapon.damage.split('d')
       damage[0] = int(damage[0])
       damage[1] = int(damage[1])
       if damage[0] == 1:
           damage_roll = random.randrange(damage[0], damage[1])
           rank_modifier_damage = int(damage[1] * modifier)
           if rank_modifier_damage == 0:
               rank_modifier_damage += 1
           damage_roll = damage_roll + rank_modifier_damage     
       else:
           damage_roll = random.randrange(damage[0],(damage[1] * 2))
           rank_modifier_damage = int(damage[1] * modifier)
           if rank_modifier_damage == 0:
               rank_modifier_damage += 1
           damage_roll = damage_roll + rank_modifier_damage     
       return damage_roll

       

class TrainingBook(Object):
    """
    This item will be what actually teaches skills to the character.  They will
    be sold by merchants/trainers and also potentially found in the world.  They
    are a one time use object that merely copies the skill object out of storage
    and stores it on the character.
    """
    def at_object_creation(self):
        self.db.desc = "An ornate leather tome, with intricate gold embossed designs.  While touching the book, you can sense it wants you to open it."
        self.db.skill = None
        self.db.value = None
        self.db.level_requirement = None
    
    def on_use(self, caller):
        """
        Here we check what skill we train, then we copy/create the skill object and
        append it to the caller's skill list.
        IMPORTANT: Every skill must set its character attribute to the caller object
        as this attribute is used extensively throughout the skill system, and is what
        ties the skill floating in the ether to the character.
        """
        manager = caller.db.skill_log
        if 'kick' in self.db.skill:
            if 'kick' not in [ manager.db.skills.keys() ] :
                kick_skill_obj = create.create_object("game.gamesrc.objects.world.skills.Kick", key='kick')
                kick_skill_obj.db.character = caller
                manager.add_item(kick_skill_obj.name, kick_skill_obj)
                caller.msg("{CYou have learned a new skill: Kick.{n")
            else:
                caller.msg("You already know this skill.")
        elif 'brawling' in self.db.skill:
            if 'brawling' not in [ manager.db.skills.keys() ]:
                brawling_skill_obj = create.create_object("game.gamesrc.objects.world.skills.Brawling", key='brawling')
                brawling_skill_obj.db.character = caller
                manager.add_item(brawling_skill_obj.name, brawling_skill_obj)
                caller.msg("{CYou have learned a new skill: Brawling.{n")
            else:
                caller.msg("You already know this skill.")
        elif 'rend' in self.db.skill:
            if 'rend' not in [manager.db.skills.keys() ]:
                rend_skill_obj = create.create_object("game.gamesrc.objects.world.skills.Rend", key='rend')
                rend_skill_obj.db.character = caller
                manager.add_item(rend_skill_obj.name, rend_skill_obj)
                caller.msg("{CYou have learned a new skill: Rend.{n")
            else:
                caller.msg("You already know this skill.")
        elif 'strike' in self.db.skill:
            if 'strike' not in [ manager.db.skills.keys() ]:
                strike_skill_obj = create.create_object("game.gamesrc.objects.world.skills.Strike", key='strike')
                strike_skill_obj.db.character = caller
                manager.add_item(strike_skill_obj.name, strike_skill_obj)
                caller.msg("{CYou have learned a new skill: Strike.{n")
            else:
                caller.msg("You already know this skill.")
        elif 'spellweaving' in self.db.skill:
            if 'spellweaving' not in [ manager.db.skills.keys()]:
                spellweaving_skill_obj = create.create_object("game.gamesrc.objects.world.skills.SpellWeaving", key='spellweaving')
                spellweaving_skill_obj.db.character = caller
                manager.add_item(spellweaving_skill_obj.name, spellweaving_skill_obj)
                caller.msg("{CYou have learned a new skill: Spellweaving{n")
            else:
                caller.msg("You already know this skill.")
        elif 'toughness' in self.db.skill:
            if 'toughness' not in [manager.db.skills.keys()]:
                percentages = caller.db.percentages
                toughness_skill_obj = create.create_object("game.gamesrc.objects.world.skills.Toughness", key='toughness')
                toughness_skill_obj.db.character = caller
                manager.add_item(toughness_skill_obj.name, toughness_skill_obj)
                percentages['constitution_bonus'] = .01
                caller.db.percentages = percentages
                caller.refresh_attributes(health_and_mana=False)
                caller.msg("{CYou have learned a new skill: Toughness{n")
            else:
                caller.msg("You already know this skill.")
        caller.db.manager = manager
        self.delete()

"""
BEGIN SKILL CLASS DECLARATION
"""
 
class Kick(Skill):

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "A strong kick that deals minimal damage."
        self.db.damage = "1d4"
        self.db.effect = "attack for %s" % self.db.damage 
        

    def on_use(self, caller):
        if caller.db.in_combat is not True:
            caller.msg("{rCan't kick things until you are in combat with them.{n")
            return
        target = caller.db.target
        attack_roll = caller.attack_roll()
        if caller.has_player:
            if attack_roll >= target.db.armor_rating:
                character_attributes = caller.db.attributes
                damage = self.get_effect()
                target.take_damage(damage)
                character_attributes = self.unbalance(1, character_attributes)
                caller.db.attributes = character_attributes
                caller.msg("{bYou kick %s right where it counts for{n {r%s{n{b points of damage!{n" % (target.name, damage))
            else:
                caller.msg("{rYour kick misses.{n")
                return
        else:
            if attack_roll >= target.db.armor_rating:
                character_attributes = target.db.attributes
                damage = self.get_effect()
                target.take_damage(damage)
                target.db.attributes = character_attributes
                caller.location.msg_contents("{b%s kicks %s ferociously!{n" % (caller.name, target.name), exclude=[caller])
                target.msg("{b%s{n kicks you for {r%s{n points of damage!" % (caller.name, damage))
            else:
                caller.location.msg_contents("{b%s's kick misses wildly!{n" % caller.name)
            

    def update_attributes(self):
        modifier = self.db.rank_modifier
        modifier += .01 
        self.db.rank_modifier = modifier

class Rend(Skill):
    """
    attack that applies a bleed effect on the target.
    """

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "A melee attack that causes the target to also bleed."
        self.db.effect = "attack and add a bleed effect"
        self.db.character = None
        self.db.damage = "1d4"

    def on_use(self, caller):
        target = caller.db.target
        attack_roll = caller.attack_roll()
        if caller.has_player:
            if attack_roll >= target.db.attributes['temp_armor_rating']:
                character_attributes = caller.db.attributes
                damage = self.get_effect()
                target.take_damage(damage)
                character_attributes = self.unbalance(1, character_attributes)
                caller.db.attributes = character_attributes
                caller.msg("{CYou cut a wide sweep across %s's unprotected limbs for {R%s{C points of damage!{n" % (target.name, damage))
                target.scripts.add("game.gamesrc.scripts.world_scripts.effects.RendEffect")
            else:
                caller.msg("{RYour attempt to Rend %s failed.{n" % target.name)
                return
        else:
            pass




    
        
        
"""
Passives
""" 
class Brawling(Skill):
    """
    Brawling is a passive skill that buffs your auto-attack melee damage by a percentage
    dependent on skill level.  Currently the highest level is 20 and it buffs up the
    percentage by 10% every 5 points into the skill
    """
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to fight."
        self.db.effect = "buff damage by a percentage"
        self.db.character = None
        self.db.passive = True
        
    def update_attributes(self):
        character = self.location.location
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['melee_damage_bonus'] = self.db.rank_modifier
        character.db.percentages = percentages

class SpellWeaving(Skill):
    """
    Spellweaving is a damage modifier skill that buffs spell damage, much like brawling
    buffs melee damage.
    """
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to cast spells."
        self.db.effect = "buff spell damage by a percentage"
        self.db.character = None
        self.db.passive = True
        
    def update_attributes(self):
        character = self.location.location
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['spell_damage_bonus'] = self.db.rank_modifier
        character.db.percentages = percentages

class Toughness(Skill):
    """
    Toughness is a constitution buff that gives the player more hit points..
    """

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "You have stronger resolve than most. +HP"
        self.db.effect = "buff constitution by a percentage"
        self.db.character = None
        self.db.passive = True
    
    def update_attributes(self):
        character = self.location.location
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['constitution_bonus'] = modifier
        character.db.percentages = percentages
        character.refresh_attributes(health_and_mana=False)

class Dodge(Skill):
    """
    Dodge is a percentage based buff to your innate dodge %.
    """
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "You have honed your dexterity and can dodge attacks."
        self.db.effect = "buff dodge by a percentage"
        self.db.character = None
        self.db.passive = True

    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['dodge'] = modifier + .05
        character.db.percentages = percentages


class Blades(Skill):
    """
    Blades represents your innate skill with bladed weapons.
    """

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use bladed weaponry."
        self.db.effect = "weapon failure/success rate"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .45
    
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['blades'] = modifier
        character.db.percentages = percentages
    
        
class Heavy(Skill):
    """
    Heavy represents your innate skill with heavy 2 handed weaponry.
    """

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use heavy (2 handed) weaponry."
        self.db.effect = "weapon failure/success rate"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .45
             
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        perentages['heavy'] = modifier
        character.db.percentages = percentages

class Bludgeon(Skill):
    """
    Represents your innate skills with Bludgeoning weaponry.
    """
    
    def at_object_creations(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use Bludgeoning weaponry."
        self.db.effect = "weapon failure/success rate"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .45
        
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['bludgeon'] = modifier
        character.db.percentages = percentages

class LightArmor(Skill):
    """
    Represents your innate ability to use light armor.
    """
    
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use light armor (Leather, Scale)"
        self.db.effect = "armor exhaustion chance"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .50

    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['light_armor'] = modifier
        character.db.percentages = percentages

class MediumArmor(Skill):
    """
    Represents your innate ability to use Medium Armor.
    """
    
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use medium armor (chain mail, banded mail)."
        self.db.effect = "armor exhaustion chance"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .50
        
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['medium_armor'] = modifier
        character.db.percentages = percentages

class HeavyArmor(Skill):
    """
    Represents your innate ability to use heavy armor.
    """
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to use heavy armor (plate, half plate)."
        self.db.effect = "armor exhaustion chance"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .50
       
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += .01
        self.db.rank_modifier = modifier
        percentages['heavy_armor'] = modifier
        character.db.percentages = percentages


class Block(Skill):
    """
    Represents your innate ability to block melee hits with shield.
    """
    
    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "Your innate ability to block incomming melee attacks"
        self.db.effect = "block chance"
        self.db.character = None
        self.db.passive = True
        self.db.rank_modifier = .15
        
    def update_attributes(self):
        character = self.db.character
        percentages = character.db.percentages
        modifier = self.db.rank_modifier
        modifier += 0.01
        self.db.rank_modifier = modifier
        percentages['block'] = modifier
        character.db.percentages = percentages
      

    
    
class Strike(Skill):
    """
    A quick, efficient melee strike.  Requires a melee weapon to use. Quite damaging at
    later levels.
    TODO: Code the update_attributes method so it can level.
    """

    def at_object_creation(self):
        Skill.at_object_creation(self)
        self.db.desc = "A quick, efficient melee strike."
        self.db.damage = "1d4"
        self.db.effect = "attack for 1d4 plus weapon damage"


    def on_use(self, caller):
        if caller.db.equipment['weapon'] is None:
            caller.msg("{rYou must equip a melee weapon to use the {b[Strike]{n{r skill{n")
            return
        target = caller.db.target
        weapon = caller.db.equipment['weapon']
        weapon_damage = self.get_weapon_damage(weapon)
        strike_damage = self.get_effect()
        total_skill_damage = weapon_damage + strike_damage
        attack_roll = caller.attack_roll()
        
        if caller.has_player:
            if attack_roll >= target.db.armor:
                character_attributes = caller.db.attributes
                target.take_damage(total_skill_damage)
                character_attributes = self.unbalance(1, character_attributes)
                caller.msg("{bYou arc your weapon high, and bring it down on %s with fury for{n {r%s{n{b points of damage!{n" % (target.name, total_skill_damage))  
                caller.db.attributes = character_attributes
            else:
                caller.msg("{rYou attempted to strike %s but miss.{n" % target.name)
        else:
            if attack_roll >= target.db.armor:
                target.take_damage(total_skill_damage)
                caller.location.msg_contents("%s strikes %s furiously with their weapon." % (caller.name, target.name))
            else:
                caller.location.msg_contents("%s misses with their Strike." % caller.name)

                
            

                 
        
        
