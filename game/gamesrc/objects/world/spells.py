import random
from prettytable import PrettyTable
from src.utils import create, utils 
from ev import Object


class SpellManager(Object):
    """
    The management object that will be the in game representation of a spell book
    This object will physically hold and inventory all character spells.
    """
    def at_object_creation(self):
        self.db.desc = "An Ornately bound book with magical text on the cover that reads: Spells"
        self.db.spells = {}
        self.db.is_equipped = False
        self.db.equippable = False

    def add_item(self, key, obj):
        spells = self.db.spells
        spells[key] = obj
        obj.move_to(self, quiet=True)
        self.db.spells = spells
    
    def remove_item(self, key):
        spells = self.db.spells
        spell = spells[key]
        spell.delete()
        del spells[key]
        self.db.spells = spells

    def find_item(self,key):
        key = key.strip()
        try:
            spells = self.db.spells
            return spells[key.title()]
        except KeyError:
            self.db.character.msg("%s doesnt exist on the spells dictionary. Contact an Admin." % key)
            return

    def display_spells(self,caller):
        spells = self.db.spells
        table = PrettyTable()
        table._set_field_names(["Spell Name", "Description", "School", "Level"])
        for spell in spells:
            obj = spells[spell]
            table.add_row(["%s" % obj.name, "%s" % obj.db.desc, "%s" % obj.db.school, "%s" % obj.db.level])
        msg = table.get_string()
        caller.msg(msg)
 
class Spell(Object):
    """
    This serves as the base spell object which all other spells will inherit from.
    Any general operations should be contained in this class, while specific spell
    operations should be in the child class named after the spell itself.
    """

    def at_object_creation(self):
        self.db.desc = "Some sort of spell, that does something."
        self.db.level = 1
        self.db.character = None
        self.db.damage = None
        self.db.healing = None 
        self.db.school = None
        self.db.effect = "Something"
        self.db.mana_cost = None

    def on_cast(self,caller):
        """
        placeholder hook function
        """
        pass
    
    def update_attributes(self):
        pass

    def level_up(self):
        """
        generic level up function
        """
        self.db.level += 1
        self.update_attributes()
    
    def get_effect(self):   
        character_attributes = self.db.character.db.attributes
        percentages = self.db.character.db.percentages
        if self.db.damage is not None:
            damage = self.db.damage.split('d')
            damage[0] = int(damage[0])
            damage[1] = int(damage[1])
            if damage[0] == 1:
                damage = random.randrange(1,damage[1])
            else:
                damage = random.randrange(damage[0], damage[1] *2)
            
            if percentages['spell_damage_bonus'] != 0.0:
                increase_in_damage = int(damage * percentages['spell_damage_bonus']) + 1
                damage = damage + increase_in_damage
                
            return damage

        if self.db.healing is not None:
           healing = self.db.healing.split('d')
           healing[0] = int(healing[0])
           healing[1] = int(healing[1])
           if healing[0] == 1:
               healing = random.randrange(1,healing[1])
           else:
               healing = random.randrange(healing[0], healing[1] *2)
           return healing 
 
class SpellBook(Object):
    """
    This will serve as a one time use item that teaches a character a specific spell.
    """
    def at_object_creation(self):
        self.db.spell = None
        self.db.cost = None
        self.db.desc = "A clearly magical presence surrounds this arcane tome.  Maybe it has something to teach you?"
        self.db.level_requirement = None

    def on_use(self, caller):
        manager = caller.db.spellbook
        spells = manager.db.spells
        if self.db.level_requirement is not None:
            if caller.db.attributes['level'] < self.db.level_requirement:
                caller.msg("{RYou are not high enough level to learn this spell.{n")
                return
        if 'heal' in self.db.spell:
            if 'heal' not in spells.keys():
                healing_spell_obj = create.create_object("game.gamesrc.objects.world.spells.Heal", key="Heal")
                healing_spell_obj.db.character = caller
                manager.add_item(healing_spell_obj.name.title(), healing_spell_obj)
                caller.msg("{CYou have learned the spell: {G%s{n{C.{n" % healing_spell_obj.name)
            else:
                caller.msg("You already know that spell.")
        if 'fireball' in self.db.spell:
            if 'fireball' not in spells.keys():
                fireball_spell_obj = create.create_object("game.gamesrc.objects.world.spells.Fireball", key="Fireball")
                fireball_spell_obj.db.character = caller
                manager.add_item(fireball_spell_obj.name, fireball_spell_obj)
                caller.msg("{CYou have learned the spell: {G%s{n{C.{n" % fireball_spell_obj.name)
            else:
                caller.msg("You already know that spell.")
        if 'mageshield' in self.db.spell:
            if 'mage shield' not in spells.keys():
                mageshield_spell_obj = create.create_object("game.gamesrc.objects.world.spells.MageShield", key="Mage Shield")
                mageshield_spell_obj.db.character = caller
                manager.add_item(mageshield_spell_obj.name, mageshield_spell_obj)
                caller.msg("{CYou have learned the spell:{n {G%s{n{C.{n" % mageshield_spell_obj.name)
            else:
                caller.msg("You already know that spell.")
        elif 'strength' in self.db.spell:
            if 'strength of the bear' not in spells.keys():
                strength_spell = create.create_object("game.gamesrc.objects.world.spells.StrOfBear", key="Strength Of The Bear")
                strength_spell.db.character = caller
                manager.add_item(strength_spell.name, strength_spell)
                caller.msg("{CYou have learned the spell:{n {G%s{C.{n" % strength_spell.name)
            else:
                caller.msg("You alredy know that spell.")
        elif 'magic missile' in self.db.spell:
            if 'magic missile' not in spells.keys():
                mm_spell = create.create_object("game.gamesrc.objects.world.spells.MagicMissile", key="Magic Missile")
                mm_spell.db.character = caller
                manager.add_item(mm_spell.name, mm_spell)
                caller.msg("{CYou have learned the spell:{n {G%s{C.{n" % mm_spell.name)
            else:
                caller.msg("You alreadyg know that spell.")
        caller.db.spellbook = manager
                
                       
#HEALING TYPES
class Heal(Spell):
    """
    Typical healing spell that heals characters.
    """
    def at_object_creation(self):
        Spell.at_object_creation(self)
        self.db.desc = "A divination spell that allows the caster to heal damage from themselves and others."
        self.db.healing = "1d6"
        self.db.school = "divination"
        self.db.mana_cost = 5

    def on_cast(self, caller, target=None):
        if target is not None:
#            caller.msg("target: %s" % target)
            if hasattr(target, 'attributes'):
                target = target
            else:
                target = caller.location.search(target, global_search=False)
            target_attributes = target.db.attributes
        character_attributes = caller.db.attributes
        healing_amount = self.get_effect()
        if character_attributes['temp_mana'] <=0:
            caller.msg("{RYou do not have enough mana to cast: %s.{n" % self.name)
            return

        if target is not None:
            target_attributes['temp_health'] = target_attributes['temp_health'] + healing_amount
        else:
            character_attributes['temp_health'] = character_attributes['temp_health'] + healing_amount
        if target is not None:
            if target_attributes['temp_health'] > target_attributes['health']:
                target_attributes['temp_health'] = target_attributes['health']
        else:
            if character_attributes['temp_health'] > character_attributes['health']:
                character_attributes['temp_health'] = character_attributes['health']
        if target is None:
            caller.location.msg_contents("{B%s mutters arcane language and begins to faintly glow.{n" % caller.name)
            caller.msg("{GYou cast {B%s{n{G on yourself, healing {B%s{n{G health.{n" % ( self.name, healing_amount ))
            character_attributes['temp_mana'] = character_attributes['temp_mana'] - self.db.mana_cost
        else:
            caller.location.msg_contents("%s mutters some arcane language and gestures towards %s, making them glow faintly." % (caller.name, target.name))
            target.msg("{G%s casts {B%s{n{G on you, healing you for{B%s{n{G health.{n" % (caller.name, self.name, healing_amount))
            character_attributes['temp_mana'] = character_attributes['temp_mana'] - self.db.mana_cost
            
        if target is not None:
            target.db.attributes = target_attributes

        caller.db.attributes = character_attributes 

    def update_attributes(self):
        if self.db.rank == 5:
            self.db.healing = '4d10'
        elif self.db.rank == 4:
            self.db.healing = '3d8'
        elif self.db.rank == 3:
            self.db.healing = '3d6'
        elif self.db.rank == 2:
            self.db.healing = '2d6'
#BUFFS
class MageShield(Spell):
    """
    Active buff to Armor Rating. Castable on self and others.
    """
    def at_object_creation(self):
        Spell.at_object_creation(self)
        self.desc = "Create an invisible, magical barrier around yourself or allies buffing your Armor Class"
        self.db.school = "Abjuration"
        self.db.mana_cost = 10
        self.db.effect = 'buff armor class'
        self.db.attribute_affected = 'temp_armor_rating'
        self.db.attribute_affected_display = "Armor Rating"
        self.db.duration = 60 * 10
        self.db.buff_amount = 3
    
    def on_cast(self, caller, target=None):
        character_attributes = caller.db.attributes
        if character_attributes['temp_mana'] < self.db.mana_cost:
            caller.msg("{rNot enough mana!{n")         
            return
        character_attributes['temp_mana'] = character_attributes['temp_mana'] - self.db.mana_cost
        if target is not None and not target.db.corpse:
            if hasattr(target, 'mob_type'):
                caller.msg("You can't cast this on an enemy.")
            if hasattr(target, 'attributes'):
                target = target
            else:
                target = caller.search(target, global_search=False, ignore_errors=True)[0]
            target_attributes = target.db.attributes
            
        if target is None:
            caller.msg("{GAs you speak, your entire body faintly glows casting a magical light around you{n.")
            caller.location.msg_contents("{y%s speaks in a gutteral tone as a faint magical shield shimmers into place around them.{n" % caller.name, exclude=caller)
            character_attributes['temp_armor_rating'] = character_attributes['temp_armor_rating'] + self.db.buff_amount
            caller.db.attributes = character_attributes
            caller.add_effect(self)
            caller.msg("{GA protective barrier of magical energy forms around you. ( + %s to Armor Rating ){n" % self.db.buff_amount)
            caller.scripts.add("game.gamesrc.scripts.world_scripts.effects.ArmorClassBuff")
        else:
            caller.location.msg_contents("{y%s speaks in a gutteral tone, and gestures towards %s causing a faint magical shield to appear around them.{n" % (caller.name, target.name), exclude=caller)
            target_attributes['temp_armor_rating'] = target_attributes['temp_armor_rating'] + self.db.buff_amount
            target.db.attributes = target_attributes
            target.add_effect(self)
            target.msg("{gA protective barrier of magical energy forms around you. ( + %s to Armor Rating ){n" % self.db.buff_amount)
            target.scripts.add("game.gamesrc.scripts.world_scripts.effects.ArmorClassBuff")
            

class StrOfBear(Spell):
    """
    Active Buff to strength.  Castable on self and others.
    """
    def at_object_creation(self):
        Spell.at_object_creation(self)
        self.desc = "Imbues the target with the strenght of the Bear, inreasing the strength attribute."
        self.db.school = "Abjuration"
        self.db.buff_amount = 3
        self.db.attribute_affected = "temp_strength"
        self.db.attribute_affected_display = "Strength"
        self.db.mana_cost = 10
        self.db.rank = 1

    def on_cast(self, caller, target=None):
        character_attributes = caller.db.attributes
        if character_attributes['temp_mana'] < self.db.mana_cost:
            caller.msg("{rNot enough mana!{n")         
            return
        character_attributes['temp_mana'] = character_attributes['temp_mana'] - self.db.mana_cost
        if target is not None:
            if hasattr(target, 'mob_type'):
                caller.msg("You can't cast this on an enemy.")
            if hasattr(target, 'attributes'):
                target = target
            else:
                target = caller.search(target, global_search=False, ignore_errors=True)[0]
            target_attributes = target.db.attributes
        if target is None:
            caller.msg("{GYou whisper gently to the surrounding life around you, finding the proper spirit.{n")
            caller.location.msg("{G%s whispers softly to themselves, and green orbs of light hit their body.{n" % caller.name)
            character_attributes['temp_strength'] = character_attributes['temp_strength'] + self.db.buff_amount
            caller.msg("{GYou are imbued with the Strength of the Bear. (+%s to Strength){n" % self.db.buff_amount)
            caller.db.attributes = character_attributes
            caller.add_effect(self)
            caller.scripts.add("game.gamesrc.scripts.world_scripts.effects.StrengthBuff")
        else:
            caller.location.msg("{G%s whispers gently directing his words towards %s.{n" % (caller.name, target.name))
            target_attributes['temp_strength'] = target_attributes['temp_strength'] + self.db.buff_amount
            caller.location.msg("{GGren orbs begin to gather around %s." % target.name)
            target.db.attributes = target_attributes
            target.add_effect(self)
            target.scripts.add("game.gamesrc.scripts.world_scripts.effects.StrengthBuff")
        
            

#COMBAT SPELLS
class Fireball(Spell):
    """
    Direct Damage ranged attack spell.
    """
    def at_object_creation(self):
        Spell.at_object_creation(self)
        self.desc = "Hurls a magical firey ball of mage-fire towards the target"
        self.db.school = "evocation"
        self.db.mana_cost = 10
        self.db.damage = '2d6'
        
             
    def on_cast(self, caller, target):
        attributes = caller.db.attributes
        if hasattr(target, 'attributes'):
            target = target
        else:
            target = caller.search(target, global_search=False)
        target_attributes = target.db.attributes
        if attributes['temp_mana'] < self.db.mana_cost:
            caller.msg("{rNot enough mana!{n")
            return
        if target.db.corpse:
            caller.msg("{RAlready Dead.{n")
            return
        spell_damage = self.get_effect()
        prep_text = "%s begins to move their hands in a circular fashion, while speaking incoherent arcane language.\n" % caller.name
        prep_text += "A ball of magefire appears in their hand.\n"
        prep_text += "In an instant, the fiery ball is propelled at ludicrous speed towards %s." % target.name
        caller.location.msg_contents(prep_text, exclude=caller)
        attributes['temp_mana'] = attributes['temp_mana'] - self.db.mana_cost
        target.take_damage(spell_damage)
        caller.msg("{CYou cast {R%s{n {Con {c%s{n, {Cdealing {R%s{n {Cdamage and engulfing them in flames!{n" % (self.name, target.name, spell_damage))
        caller.db.attributes = attributes
        if target.db.in_combat is False:
            caller.begin_attack(target)
        target.scripts.add("game.gamesrc.scripts.world_scripts.effects.FireballDot")
        
class MagicMissile(Spell):
    """
    Low dmg spell
    """

    def at_object_creation(self):
        Spell.at_object_creation(self)
        self.desc = "Propels arcance bolts of magic-energy towards the target."
        self.db.school = "evocation"
        self.db.mana_cost = 5
        self.db.damage = "1d4"
        
    def on_cast(self, caller, target):
        attributes = caller.db.attributes
        if hasattr(target, 'attributes'):
            target = target
        else:
            target = caller.search(target, global_search=False)
        target_attributes = target.db.attributes
        if attributes['temp_mana'] < self.db.mana_cost:
            caller.msg("{RNot enough mana!")
            return
        if target.db.corpse:
            caller.msg("{RAlready Dead.")
            return
        spell_damage = self.get_effect()
        prep_text = "%s speaks in ancient arcance tougue, while purple and blue magical energy swirls around their fingers." % caller.name
        caller.location.msg_contents(prep_text, exclude=caller)
        attributes['temp_mana'] = attributes['temp_mana'] - self.db.mana_cost
        target.take_damage(spell_damage)
        caller.msg("{CYou cast {R%s{C on {c%s {Cdealing {R%s {Cdamage." %(self.name, target.name, spell_damage))
        caller.db.attributes = attributes
        if target.db.in_combat is False:
            caller.begin_attack(target)
       
            

class IceLance(Spell):
    """
    Direct Damage ranged attack spell.
    """
    pass      

        
##Character/Mob Buff Manager

class EffectManager(Object):
    """
    THis object is responsible for managing all spell effects, and any effect in
    general on characters/mobs/and npc's.
    """
    def at_object_creation(self):
        self.db.model = None # character, mob or npc object i am attached to.
        self.db.effects = {} # a dict full of dictonaries with effect info.
        self.locks.add("view:none()")
        

    def find_effect(self, effect_to_find):
        if effect_to_find in self.db.effects:
            effect = effects[effect_to_find]
            return effect
        else:
            return None

    def add_effect(self, to_add):
        """
        Add something to the manager for tracking purposes.
        """
        effects = self.db.effects        
        effect = { 'description': to_add.db.desc, 'duration': to_add.db.duration, 'count': 0, 'attribute_affected': to_add.db.attribute_affected }
        effects[to_add.name] = effect
        self.db.effects = effects
        
    def remove_effect(self, effect_to_remove):
        """
        remove an effect once its duration has run its course.
        """
        effects = self.db.effects
        model = self.db.model
        #effect = self.find_effect(effect_to_remove)
        effect = effect_to_remove
        if 'hp' == effects[effect]['attribute_affected']:
            model_attributes = model.db.attributes
            model_attributes['buffed_health'] = 0
            model_attributes['temp_health'] = model_attributes['health']
            model.msg("{bYou feel your magically enhanced health pool fade away.{n")
            model.db.attributes = model_attributes
            del effects[effect]
            self.db.effects = effects
        elif 'mp' == effects[effect]['attribute_affected']:
            model_attributes = model.db.attributes
            model_attributes['buffed_mana'] = 0
            model_attributes['temp_mana'] = model_attributes['mana']
            model.msg("{bYou feel your magically enchanced mana pool fade away.{n")
            model.db.attributes = model_attributes
            del effects[effect]
            self.db.effects = effects
        elif 'armor' in effects[effect]['attribute_affected']:
            model_attributes = model.db.attributes
            model_attributes['temp_armor_rating'] = model_attributes['armor_rating']
            model.msg("{bYour magical shield fades away.{n")
            model.db.attributes = model_attributes
            del effects[effect]
            self.db.effects = effects 

    def check_effects(self):
        """
        Check effect counters and increment if not done yet
        """
        if len(self.db.effects) < 1:
            return

        effects = self.db.effects
        for effect in effects:
            if effects[effect]['count'] >= effects[effect]['duration']:
                self.remove_effect(effect)
            else:
                effects[effect]['count'] += 1 
                self.db.effects = effects
         
    def display_effects(self):
        effects = self.db.effects
        character = self.db.model
        if len(effects.keys()) < 1:
            character.msg("{cNothing is affecting you currently.{n")
            return
        m ='{{c{0:<9} {1:<32} {2:<10} {3:<10}{{n'.format("Name", "Description", "Attr Affected", "Duration" )
        character.msg(m)
        m = "{C--------------------------------------------------------------------------------------------------------------------{n"
        character.msg(m)
        m = ""
        for effect in effects:
            m += "{{c{0:<9}{{n {1:<80} {2:<10} {3:<10}{{n".format( effect, effects[effect]['description'], effects[effect]['attribute_affected'], effects[effect]['duration'])     
        character.msg(m)
        m = "{C--------------------------------------------------------------------------------------------------------------------{n"
