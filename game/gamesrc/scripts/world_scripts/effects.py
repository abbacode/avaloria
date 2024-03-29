from ev import Script


class Effect(Script):
    """
    Damage over time effect.
    """

    def at_script_creation(self):
        self.key = "effect_script"
        self.interval = 0
        self.repeats = 0
        self.desc = "I control some sort of effect"
        


class CastDelay(Script):
    """
    Delays the firing of character and mob spells
    """
    def at_script_creation(self):
        self.key = 'delayer'
        self.interval = 2
        self.repeats = 1
        self.start_delay = True

    def at_start(self):
        self.obj.db.caller.msg("{CYou begin to mutter your incantations for: {c%s.{n" % self.obj.name.title())

    def at_stop(self):
        character = self.obj.db.caller
        self.obj.db.caller.msg("{CYou cast the spell: {c%s{n!" % self.obj.name.title())
        if character.db.target:
            self.obj.on_cast(self.obj.db.caller, character.db.target)
        elif self.obj.db.target:
            self.obj.on_cast(self.obj.db.caller, self.obj.db.target)
        else:
            self.obj.on_cast(self.obj.db.caller)
"""
HEALING EFFECTS
-Scripts that are fired off for healing effects
"""

class HealthBuff(Effect):
    """
    Script added to a character to buff health.
    """

    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.key = "hp_buff"
        self.interval = 300
        self.start_delay = True
        self.repeats = 1
        self.persistent = True
        
    def at_start(self):
        character_attributes = self.obj.db.attributes
        character_attributes['health'] = character_attributes['buffed_health']
        self.obj.db.attributes = character_attributes

    def at_stop(self):
        self.obj.refresh_attributes(health_and_mana=True, base_stats=False)
        self.obj.remove_effect('%s' % self.key)
        self.obj.msg("Your health buff fades")
        

class ManaBuff(Effect):
    """
    Script added to a character to buff health
    """
    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.key = 'mp_buff'
        self.interval = 300
        self.start_delay = True
        self.repeats = 1
        self.persistent = True

    def at_start(self):
        character_attributes = self.obj.db.attributes
        character_attributes['mana'] = character_attributes['buffed_mana']
        self.obj.db.attributes = character_attributes

    def at_stop(self):
        self.obj.refresh_attributes(health_and_mana=True, base_stats=False)
        self.obj.msg("Your mana buff fades.")
        self.remove_effect('%s' % self.key)
     
        
         
"""
DMG EFFECTS
-Scripts fired when a damaging skill or ability is used.
"""
class RendEffect(Effect):
    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.interval = 5
        self.repeats = 3
        self.start_delay = True

    def at_start(self):
        self.obj.db.target.msg("{CBlood pours onto the ground from the wounds you have caused.{n")

    def at_repeat(self):
        attributes = self.obj.db.attributes
        if hasattr(self.obj, 'mob_type'):
            #Do stuff for pcs
            pass
        else:
            if self.obj.db.corpse:
                self.obj.scripts.validate()
                return
            character = self.obj.db.target
            character_skill_manager = character.db.skill_log
            rend_skill = character_skill_manager.find_item('rend')
            dmg = rend_skill.get_effect()
            target = self.obj
            target.take_damage(dmg)
            target.location.msg_contents("{c %s's wounds are gushing blood!{n" % target.name, exclude=[character])
            character.msg("{C%s bleeds for {R%s {Cpoints of damage.{n" % (target.name, dmg))
            

class StunEffect(Effect):
    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.interval = 3
        self.repeats = 1
        self.start_delay = True
        
    def at_start(self):
        self.obj.db.target.msg("{C%s is dazed and confused!{n" % self.obj.name)
        
    def at_repeat(self):
        self.obj.stunned = False
        self.obj.db.target.msg("{C%s is no longer stunned!{n" % self.obj.name)
                   
class CrippleEffect(Effect):

    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.interval = 60
        self.repeats = 1 
        self.start_delay = True
    
    def at_start(self):
        mob_attributes = self.obj.db.attributes
        reduction = int(0.10 * mob_attributes['temp_dexterity'])
        mob_attributes['temp_dexterity'] = mob_attributes['temp_dexterity'] - reduction
        self.obj.db.attributes = mob_attributes
        self.obj.db.crippled = True
        self.obj.refresh_armor_rating()

    def at_repeat(self):
        self.obj.update_stats()
        self.obj.db.crippled = False
    

        
class FireballDot(Effect):

    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.interval = 2
        self.repeats = 5
        self.start_delay = True

    def at_start(self):
        self.obj.db.target.msg("{CYour fireball ignites %s!" % self.obj.name)
        
    def at_repeat(self):
        attributes = self.obj.db.attributes
        if hasattr(self.obj, 'mob_type'):
            #Do stuff for pcs
            pass
        else:
            if self.obj.db.corpse is True:
                self.obj.scripts.validate()
                return
            
            character = self.obj.db.target
            character_spell_manager = character.db.spellbook
            fireball_spell = character_spell_manager.find_item('fireball')
            dmg = fireball_spell.get_effect()
            target = self.obj
            target.take_damage(dmg)
            target.location.msg_contents("{c %s is engulfed in flames!{n" % target.name,  exclude=character)
            character.msg("{CThe flames lick %s for %s damage.{n" % ( self.obj.name, dmg))


    def is_valid(self):
        if self.obj.db.corpse is True:
            return False
        else:
            return True 


    """
    BUFF Effects - 
    """


class ArmorClassBuff(Effect):
    """
    This script will be added to any target that has an armor buff cast upon them.
    """
    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.key = 'armor_buff'
        self.interval = 600
        self.repeats = 1
        self.persistent = True
        self.start_delay = True

    def at_stop(self):
        attributes = self.obj.db.attributes
        attributes['temp_armor_rating'] = attributes['armor_rating']
        attributes_dict = {'attributes': attributes }
        self.obj.msg("{GYou feel your magical barrier fade.{n")
        self.obj.refresh_attribute(attributes_dict)
        self.obj.remove_effect('temp_armor_rating_buff')
        
       
class StrengthBuff(Effect):
    """
    This script will be added to any target that has a strength buff cast upon them
    """
    def at_script_creation(self):
        Effect.at_script_creation(self)
        self.key = 'strength_buff'
        self.interval = 600
        self.repeats = 1
        self.persistent = True
        self.start_delay = True

    def at_stop(self):
        attributes = self.obj.db.attributes
        attributes['temp_strength'] = attributes['strength']
        attr_dict = { 'attributes': attributes }
        self.obj.msg("{GYou feel your magical strength fade.{n")
        self.obj.refresh_attribute(attr_dict)
        self.obj.remove_effect('temp_strength_buff') 
