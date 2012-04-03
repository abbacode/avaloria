import random
from game.gamesrc.objects.baseobjects import Object
from src.utils import utils


class Item(Object):
    """
    This is a default item object.  This object is used as base for
    all items in the game: armor, weapons, rings, trinkets, potions
    etc.  You get the idea
    """

    def at_object_creation(self):
        
        self.db.desc = "A generic item, why it actually looks like...nothing at all"
        blackhole = self.search("blackhole", global_search=True)
        self.home = blackhole
        self.db.quest_item = False
        self.db.item_level = None
        self.db.value = None
        self.db.weight = None
        self.db.type = None
        self.db.slot = None
        self.db.equipable = False
        self.db.is_equipped = False
        self.db.attribute_bonuses = {'strength': 0, 'dexterity':0, 'intelligence': 0, 'constitution': 0 }
        self.db.lootset = None
    
    def is_equipable(self):
        return self.db.equipable

    def is_equipped(self):
        return self.db.is_equipped
                

class LightSource(Item):
    """
    An object that emits light.
    """
    def at_object_creation(self):
        Item.at_object_creation(self)
        self.db.desc = "A typical, simple torch."
        self.db.burntime = 60*5
        self.db.is_active = False
   
    def reset(self):
        if self.db.burntime < 0:
            self.db.is_active = False
        try:
            loc = self.location.location
        except AttributeError:
            loc = self.location
        loc.msg_contents("{R%s has burned out." % self.name)
        try:
            self.location.location.scripts.validate()
        except AttributeError:
            self.location.scripts.validate()



    
        
class Weapon(Item):
    """
    An object that is a weapon (i.e can be equipped and used to hurt
    things.)  Damage, attribute bonuses etc are stored here.
    """
    
    def at_object_creation(self):
        
        Item.at_object_creation(self)
        self.db.type = 'weapon'
        self.db.desc = "A weapon type object, its shape still unseen"
        self.db.damage = "2d6"
        self.db.weapon_type = None
        self.db.slot = 'weapon'
        self.db.equipable = True

    def at_inspect(self, looker):
        if 'common' in self.db.item_level:
            looker.msg("{W%s {n" % self.key)
            msg = "{wThis is a common, every day weapon.{n" 
            looker.msg(msg)
            msg = "Damage:\t{r%s{n\n" % self.db.damage
            msg += "Value: {y%s{n" % self.db.value
            looker.msg(msg)
        elif 'uncommon' in self.db.item_level:
            looker.msg("{g%s {s" % self.key)
            msg = "{wThis is an uncommon weapon.{n"  
            looker.msg(msg)
            msg = "Damage:\t{r%s{n\n" % self.db.damage
            msg += "Value: {y%s{n" % self.db.value
            looker.msg(msg)
            string = ""
            looker.msg("{WAttribute Bonuses:{n")
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)
        elif 'rare' in self.db.item_level:
            looker.msg("{b%s {n" % self.key)
            msg = "{wThis is a very rare weapon. {n" 
            string = ""
            looker.msg(msg)
            msg = "Damage:\t{r%s{n\n" % self.db.damage
            msg += "Value: {y%s{n" % self.db.value
            looker.msg(msg)
            looker.msg("{WAttribute Bonuses:{n")
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)      
        elif 'artifact' in self.db.item_level:
            looker.msg("{m%s {n" % self.name)
            msg = "{yThis is a very rare and very powerful weapon. {n"
            looker.msg(msg)
            string = ""
            looker.msg("{WAttribute Bonuses:{n")
            msg = "Damage:\t{r%s{n\n" % self.db.damage
            msg += "Value: {y%s{n" % self.db.value
            looker.msg(msg)
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)
    
    def on_equip(self):
        """
        adds bonuses from item to character stats
        """
        character_attributes = self.location.db.attributes
        for bonus in self.db.attribute_bonuses:
            if self.db.attribute_bonuses[bonus] > 0:
                character_attributes[bonus] = self.db.attribute_bonuses[bonus] + character_attributes[bonus]
        self.location.db.attributes = character_attributes
        self.db.is_equipped = True
        self.location.refresh_attributes(health_and_mana=False, base_stats=True)
    
    def on_unequip(self):
        """
        removes bonuses given from items when unequipped
        """
        character_attributes = self.location.db.attributes  
        for bonus in self.db.attribute_bonuses:
            if self.db.attribute_bonuses[bonus] > 0:
                character_attributes[bonus] = character_attributes[bonus] - self.db.attribute_bonuses[bonus]
        self.location.db.attributes = character_attributes
        self.db.is_equipped = False
        self.location.refresh_attributes(health_and_mana=False, base_stats=True)


#Armor item class

class Armor(Item):
    """
    This represents an Armor type object.  This is an equippable item
    that adds to armor and possibly other attributes.
    """

    def at_object_creation(self):
        Item.at_object_creation(self)
        self.db.type = 'armor'
        self.db.armor_rating = 1
        self.db.armor_type = None
        self.db.slot = 'armor'
        self.db.equipable = True
        
    def at_inspect(self, looker):
        if 'common' in self.db.item_level:
            looker.msg("{W%s {n" % self.name)
            m = "{wThis is a normal suit of armor, nothing much is special about it.{n"
            looker.msg(m)
            m = "Armor Value:\t{g%s{n\nValue:\t{y%s{n\nType:\t{g%s{n\n" % (self.db.armor_rating, self.db.value, self.db.armor_type)
            looker.msg(m)
            string = ""
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)  
        elif 'uncommon' in self.db.item_level:
            looker.msg("{g%s {n" % self.name)
            m = "{wThis is a masterwork suit of armor made by an accomplished blacksmith.{n"
            looker.msg(m)
            m = "Armor Value:\t{g%s{n\nValue:\t{y%s{n\nType:\t{g%s{n\n" % (self.db.armor_rating, self.db.value, self.db.armor_type)
            looker.msg(m)
            string = ""
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)  
        elif 'rare' in self.db.item_level:
            looker.msg("{b%s {n" % self.name)
            m = "{wThis is a magically embued set of armor.{n"
            looker.msg(m)
            m = "Armor Value:\t{g%s{n\nValue:\t{y%s{n\nType:\t{g%s{n\n" % (self.db.armor_rating, self.db.value, self.db.armor_type)
            looker.msg(m)
            string = ""
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)  
        elif 'artifact' in self.db.item_level:
            looker.msg("{m%s {n" % self.name)
            m = "{yThis is an ancient, very unique suit of armor that is embued with powerful magic.{n"
            looker.msg(m)
            m = "Armor Value:\t{g%s{n\nValue:\t{y%s{n\nType:\t{g%s{n\n" % (self.db.armor_rating, self.db.value, self.db.armor_type)
            looker.msg(m)
            string = ""
            for bonus in self.db.attribute_bonuses:
                string += "{w%s: +%s {n" % (bonus, self.db.attribute_bonuses[bonus])
            looker.msg(string)  

    def on_equip(self):
        """
        adds bonuses from item to character stats
        """
        character_attributes = self.location.db.attributes
        for bonus in self.db.attribute_bonuses:
            if self.db.attribute_bonuses[bonus] > 0:
                character_attributes[bonus] = self.db.attribute_bonuses[bonus] + character_attributes[bonus]
        #add armor
        character_attributes['armor_rating'] = character_attributes['armor_rating'] + self.db.armor_rating
        character_attributes['temp_armor_rating'] = character_attributes['armor_rating']
        self.db.is_equipped = True
        self.location.db.attributes = character_attributes
            
    def on_unequip(self):
        """
        removes bonuses given from items when unequipped
        """
        character_attributes = self.location.db.attributes
        for bonus in self.db.attribute_bonuses:
            if self.db.attribute_bonuses[bonus] > 0:
                character_attributes[bonus] = character_attributes[bonus] - self.db.attribute_bonuses[bonus]
        #remove armor
        character_attributes['armor_rating'] = character_attributes['armor_rating'] - self.db.armor_rating
        character_attributes['temp_armor_rating'] = character_attributes['armor_rating']
        self.db.is_equipped = False
        self.location.db.attributes = character_attributes
    
        
class Potion(Item):
    """
    This class serves as a base class for any item that is a potion.
    This could be health, mana, buff potions, etc. This is a useable
    world object, and therefore has an on_use hook.
    """

    def at_object_creation(self):
        """
        effect is simply a string used to decide what will happen when the potion
        is consumed.
        attribute_affected is a string with the attribute that will have something
        done to it.
        amount_affected is a number range, or set number that determines how much
        to heal or buff.
        level is used to determine the range of healing/buffing that the potion will
        give.
        """
        Item.at_object_creation(self)
        self.db.type = 'potion'
        self.db.effect = 'buff' #heal,mana_regen,buff etc
        self.db.attribute_affected = 'hp'#str,con,int,dex,hp,mp
        self.db.amount_affected = random.randrange(10,20)#amount of healing/buffing done by the object
        self.db.level = 1 #used to determine amount_affected.
        self.db.duration = 120 #immediate OR an amount of seconds

    def on_use(self, caller):
        character_attributes = caller.db.attributes
        potion =  caller.search(self.dbref, global_search=False)
        if potion is None:
            caller.msg("{rCan't use me until you pick me up!{n")
            return
        
        if 'hp' in self.db.attribute_affected:
            character_current_hp = character_attributes['temp_health']
            base_health = character_attributes['health']
            difference = base_health - character_current_hp

            if 'heal' in self.db.effect:
                if difference < self.db.amount_affected:
                    character_attributes['temp_health'] = character_attributes['health']
                    caller.msg("{bYou gulp the %s and quickly feel a warm, healing sensation throughout your body.{n" % self.name)
                    caller.msg("{rYou have been fully healed.{n")
                    caller.db.attributes = character_attributes
                    self.delete()
                else:
                    character_attributes['temp_health'] = character_attributes['temp_health'] + self.db.amount_affected
                    caller.msg("{bYou drink the %s, healing you for %s.{n" %(self.name, self.db.amount_affected))
                    caller.db.attributes = character_attributes
                    self.delete()
            elif 'buff' in self.db.effect:
                caller.add_effect(self)
                character_attributes['buffed_health'] = character_attributes['health'] + self.db.amount_affected
                caller.msg("{bAs you drink the potion you feel yourself become more resilient.{n")
                caller.msg("{r%s added %s points to your health pool.{n" % (self.name, self.db.amount_affected))
                caller.db.attributes = character_attributes
                caller.scripts.add("game.gamesrc.scripts.world_scripts.effects.HealthBuff")
                self.delete()
        elif 'mp' in self.db.attribute_affected:
            character_current_mp = character_attributes['temp_mana']
            base_mana = character_attributes['mana']
            difference = base_mana - character_current_mp
            if 'mana_regen' in self.db.effect:
                if difference < self.db.amount_affected:
                    character_attributes['temp_mana'] = character_attributes['mana']
                    caller.msg("{bYou drink all of the %s.  It tastes like magic and burning.{n" % self.name)
                    caller.msg("{Your mana is now full.{n")
                    caller.db.attributes = character_attributes
                    self.delete()
                else:
                    character_attributes['temp_mana'] = character_attributes['temp_mana'] + self.db.amount_affected
                    caller.msg("{bYou drink the %s, which restores %s mana.{n" % (self.name, self.db.amount_affected))
                    caller.db.attributes = character_attributes
                    self.delete()
            elif 'buff' in self.db.effect:
                caller.add_effect(self)
                character_attributes['buffed_mana'] = character_attributes['mana'] + self.db.amount_affected
                caller.msg("{bAs you drink the %s, you feel your mana pool grow.{n" % self.name)
                caller.msg("{r%s added %s points to your mana pool.{n" % (self.name, self.db.amount_affected))
                caller.db.attributes = character_attributes
                caller.scripts.add("game.gamesrc.scripts.world_scripts.effects.ManaBuff")
                self.delete()
        
        

    def generate_item_stats(self):
        """
        NOTE: MUST HAVE THE FOLLOWING OBJECT ATTRIBUTES SET BEFORE CALLING:
            *level
            *effect
            *attribute_affected
        This method simply generates the item description and other attributes based
        on the level, effect, and attribute_affected attributes that are set beforehand
        after obeject creation.  So for example:
            potion = create.create_object("game.gamesrc.objects.world.items.Potion", key=whatever)
            potion.level = x
            potion.effect = "x"
            potion.attribute_affected = "x"
            potion.generate_item_stats()
        """
        if self.db.level is None:
            return
        if self.db.effect is None:
            return
        if self.db.attribute_affected is None:
            return

        #Generate amount_affected
        if self.db.level == 1: 
            if 'hp' in self.attribute_affected:
                if 'heal' in self.db.effect:
                    self.name = "Small Health Vial"
                    self.db.amount_affected = random.randrange(18,27)
                    self.db.desc = "A small vial of clearish red liquid.  You feel magic slightly radiated from the bottle."
                if 'buff' in self.db.effect:
                    self.name = "Potion of Minor Fortitude"
                    self.db.amount_affected = random.randrange(5,10)
                    self.db.duration = 120
                    self.db.desc = "A small vial of yellow liquid that has a very strong odor."
            elif 'mp' in self.attribute_affected:
                if 'mana_regen' in self.db.effect:
                    self.name = "Minor Mana Potion"
                    self.db.amount_affected = random.randrange(8,18)
                    self.db.desc = "A small vial of blueish liquid that sparkles, even if no light is present."
                elif 'buff' in self.db.effect:
                    self.name = "Minor Potion Of Insight"
                    self.db.duration = 120
                    self.db.amount_affected = random.randrange(5,10)
                    self.db.desc = "A small vial of very deep blue liquid."
        elif self.db.level == 10:
            if 'hp' in self.attribute_affected:
                if 'heal' in self.db.effect:
                    self.name = "Health Vial"
                    self.db.amount_affected = random.randrange(30,50)
                    self.db.desc = "A medium sized vial of red colored liquid.  It is unmistakenly imbued with magical energy."
                if 'buff' in self.db.effect:
                    self.name = "Potion of Fortitude"
                    self.db.duration = 300
                    self.db.amount_affected = random.randrange(12,18)
                    self.db.desc = "A medium sized vial of yellow liquid, with a pungent odor."
            elif 'mp' in self.attribute_affected:
                if 'mana_regen' in self.db.effect:
                    self.name = "Mana Potion"
                    self.db.amount_affected = random.randrange(40, 60)
                    self.db.desc = "A medium sized vial of blue liquid, that smells of the ocean and sparkles regardless of light being present."
                elif 'buff' in self.db.effect:
                    self.name = "Potion of Insight"
                    self.db.duration = 300
                    self.db.amount_affected = random.randrange(12, 18)
                    self.db.desc = "A medium sized vial of deep blue colored liquid.  Merely smelling it makes you mind expand"
        elif self.db.level == 20: 
            if 'hp' in self.attribute_affected:
                if 'heal' in self.db.effect:
                    self.name = "Large Vial of Health"
                    self.db.amount_affected = random.randrange(50,80)
                    self.db.desc = "A large vial of thick red liquid, magically imbued with healing properties."
                if 'buff' in self.db.effect:
                    self.name = "Large Potion of Fortitude"
                    self.db.duration = 600
                    self.db.amount_affected = random.randrange(20,28)
                    self.db.desc = "A large vial of dark yellow, pungent smelling liquid."
            elif 'mp' in self.attribute_affected:
                if 'mana_regen' in self.db.effect:
                    self.name = "Large Mana Potion"
                    self.db.amount_affected = random.randrange(60,90)
                    self.db.desc = "A large vial of blue liquid which smells of the Oceans and sparkle in the deepest darkness."
                if 'buff' in self.db.effect:
                    self.name = "Strong Potion of Insight"
                    self.db.duration = 600
                    self.db.amount_affected = random.randrange(30,40)
                    self.db.desc = "A large vial of deep blue colored liquid.  You can feel the magic contained within as you hold it."
                
